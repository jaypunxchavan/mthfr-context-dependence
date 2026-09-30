# PHASE 2 diagnostics II — corrections file

**Written by:** `scripts/140_phase2_diag3_corrections.py` (Diagnostics III, task D12), from inside the script, so every number below is interpolated from a computed variable and none is hand-typed.
**Corrects:** `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II_LOG.md` — **READ ONLY, never edited.**
**D12-G1 (HARD):** every row of the reproduction table reproduced before any correction was written. PASS.
**Scope:** corrections only. Nothing frozen is redefined. No new science. No variant is selected.

---

## K1 — D10c's two partial correlations are label-swapped

**Old text, at these REAL line numbers of the Diagnostics II log** (located with `grep -n`; the line numbers in the task doc were not trusted and were not used):

- line 550:
  >     PARTIAL  Spearman(rho, dist | mean|delta|) = -0.146323470
- line 558:
  >     PARTIAL  Spearman(rho, dist | mean|delta|) = -0.161717649
- line 552:
  >     PARTIAL  Spearman(rho, mean|delta| | dist) = +0.629666674
- line 560:
  >     PARTIAL  Spearman(rho, mean|delta| | dist) = +0.603747329

**The defect, in `scripts/138_phase2_diag2_joint.py`** — `partial(x, y, z)` returns the partial of `x` and `y` **given `z`**:

```
scripts/138_phase2_diag2_joint.py:374
   374: def partial(x, y, z):
scripts/138_phase2_diag2_joint.py:375
   375: rxy = float(spearmanr(x, y).statistic)
scripts/138_phase2_diag2_joint.py:376
   376: rxz = float(spearmanr(x, z).statistic)
scripts/138_phase2_diag2_joint.py:377
   377: ryz = float(spearmanr(y, z).statistic)
scripts/138_phase2_diag2_joint.py:378
   378: den = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
scripts/138_phase2_diag2_joint.py:379
   379: return (rxy - rxz * ryz) / den, rxy, rxz, ryz
scripts/138_phase2_diag2_joint.py:388
   388: obs, rxy, rxm, rmd = partial(x, m, d)  # rho ~ dist | mean|delta|
scripts/138_phase2_diag2_joint.py:389
   389: obs2, rxy2, rxd, ryd = partial(x, d, m)# rho ~ mean|delta| | dist
scripts/138_phase2_diag2_joint.py:404
   404: print(f"PARTIAL  Spearman(rho, dist | mean|delta|) = {obs:+.9f}")
scripts/138_phase2_diag2_joint.py:408
   408: print(f"PARTIAL  Spearman(rho, mean|delta| | dist) = {obs2:+.9f}")
```

`partial(x, m, d)` is `rho ~ mean|delta| | dist`; it is printed under the label `rho ~ dist | mean|delta|`. `partial(x, d, m)` is `rho ~ dist | mean|delta|`; it is printed under the label `rho ~ mean|delta| | dist`. **The two printed labels are transposed. The values are correct; only the labels are wrong.** The pairwise line (138:401-403) is correctly labelled.

**Recomputed two independent ways** (a) the standard three-pairwise-Spearman formula, (b) rank-transform + OLS residualisation on `[1, rank(z)]` + Pearson of residuals:

| view | partial | (a) formula | (b) rank-residualisation | \|a−b\| | bootstrap 95% CI (a) | excludes 0 | **TARGET** | verdict |
|---|---|---|---|---|---|---|---|---|---|
| full | `rho ~ dist \| shift` | +0.629666674 | +0.629666674 | 2.220e-16 | [+0.472642, +0.742385] | yes | +0.629667 | **AGREE** |
| full | `rho ~ shift \| dist` | -0.146323470 | -0.146323470 | 5.551e-17 | [-0.404796, +0.107532] | no | -0.146323 | **AGREE** |
| H | `rho ~ dist \| shift` | +0.603747329 | +0.603747329 | 1.110e-16 | [+0.452424, +0.720011] | yes | +0.603747 | **AGREE** |
| H | `rho ~ shift \| dist` | -0.161717649 | -0.161717649 | 2.776e-17 | [-0.416825, +0.083508] | no | -0.161718 | **AGREE** |

Target CIs (not gates, Monte-Carlo error ~0.01): full [+0.472642, +0.742385] and [-0.401778, +0.106788]; H [+0.451631, +0.719109] and [-0.416825, +0.083508].

**D11.4's partials were labelled correctly** and are unchanged. `scripts/139_phase2_diag2_3d.py:719-720,735,739` stores `partial(x, g, m)` in `p1` and labels it `rho, d3_CA | mean|delta|`, and `partial(x, m, g)` in `p2` and labels it `rho, mean|delta| | d3_CA`. Recomputed: full `rho ~ d3_CA | shift` = +0.651428; H `rho ~ d3_CA | shift` = +0.627446; full `rho ~ shift | d3_CA` = -0.108073; H `rho ~ shift | d3_CA` = -0.123827.

**Corrected statement.** Within the null set N (n = 78), once the OTHER covariate is held fixed, it is **shift, not distance, that carries the association with rho**: `Spearman(rho, shift | dist)` = -0.146 (full) and -0.162 (H), both with bootstrap CIs that include zero; while `Spearman(rho, dist | shift)` = +0.630 (full) and +0.604 (H), both with CIs that exclude zero. There is **no sign flip**: the shift partial keeps the raw pairwise sign (Spearman(rho, shift) = -0.407 -> -0.146), and the reason the partial is so much weaker is that shift and distance are themselves strongly associated (-0.450), not that conditioning reverses anything. The log's 'sign flip' explanation and its 'reverse of D4's reading' are consequences of the transposed labels and do not exist. The same holds with 3D distance: `rho ~ shift | d3_CA` = -0.108 (full), CI includes zero, against `rho ~ d3_CA | shift` = +0.651, CI excludes zero.

**Cite this, not the old sentence.**

---

## K2 — D10b's counts contradict D9's printed residuals

**Old text, at these REAL line numbers:**

- line 529:
  > D10b -- NEIGHBOURHOOD RESTRICTED RANKS on D9's PRIMARY residuals
- line 224:
  >   k=10 nearest (full): # at or below =  1 of 10  -> rank fraction 2/11 = 0.1818
- line 532:
  >   k=10 nearest (full):  # at or below =  8 of 10  ->  rank fraction (1 + 8)/(1 + 10) = 0.8182   at or below: AV_195, AV_220, AV_233, AV_242, G_I192T, G_L178T, G_P254F, G_Y197V
- line 225:
  >   k=10 nearest (   H): # at or below =  3 of 10  -> rank fraction 4/11 = 0.3636
- line 533:
  >   k=10 nearest (   H):  # at or below =  9 of 10  ->  rank fraction (1 + 9)/(1 + 10) = 0.9091   at or below: AV_195, AV_209, AV_220, AV_233, AV_242, G_I192T, G_L178T, G_P254F, G_Y197V
- line 226:
  >   k=20 nearest (full): # at or below =  1 of 20  -> rank fraction 2/21 = 0.0952
- line 534:
  >   k=20 nearest (full):  # at or below = 18 of 20  ->  rank fraction (1 + 18)/(1 + 20) = 0.9048   at or below: AV_145, AV_155, AV_175, AV_195, AV_220, AV_233, AV_242, AV_292, AV_293, AV_302, AV_311, G_E168S, G_E279K, G_G317Q, G_I192T, G_L178T, G_P254F, G_Y197V
- line 227:
  >   k=20 nearest (   H): # at or below =  3 of 20  -> rank fraction 4/21 = 0.1905
- line 535:
  >   k=20 nearest (   H):  # at or below = 19 of 20  ->  rank fraction (1 + 19)/(1 + 20) = 0.9524   at or below: AV_145, AV_155, AV_175, AV_195, AV_209, AV_220, AV_233, AV_242, AV_292, AV_293, AV_302, AV_311, G_E168S, G_E279K, G_G317Q, G_I192T, G_L178T, G_P254F, G_Y197V
- line 583:
  > **D10b — the neighbourhood rank fractions are worse than D0's raw-ρ version.** A222V sits at rank fraction 0.818 (full) and 0.909 (H) among the 10 nearest, against 0.182 / 0.364 on raw ρ. Rank fractions, not tests.

**(i) Which residual vector did script 138's D10b actually use?** Verbatim, with file and real line numbers:

```
scripts/138_phase2_diag2_joint.py:320
   320: d10a_rows.append(dict(name=name, view=view, k=k, p=p_adj, rel=rel,
scripts/138_phase2_diag2_joint.py:321
   321:   thr=thr, r_A=r_A, rank=rank, beta=beta))
scripts/138_phase2_diag2_joint.py:322
   322: if name.startswith("PRIMARY"):
scripts/138_phase2_diag2_joint.py:323
   323: resid_primary[view] = (dict(r), r_A)
scripts/138_phase2_diag2_joint.py:333
   333: banner("D10b -- NEIGHBOURHOOD RESTRICTED RANKS on D9's PRIMARY residuals",
scripts/138_phase2_diag2_joint.py:337
   337: near_by_dist = sorted(N_ids, key=lambda b: (DIST[b], b))
scripts/138_phase2_diag2_joint.py:338
   338: d10b_rows = []
scripts/138_phase2_diag2_joint.py:339
   339: for kk in NEIGH_K:
scripts/138_phase2_diag2_joint.py:340
   340: sub = near_by_dist[:kk]
scripts/138_phase2_diag2_joint.py:341
   341: for view in ("full", "H"):
scripts/138_phase2_diag2_joint.py:342
   342: r, r_A = resid_primary[view]
scripts/138_phase2_diag2_joint.py:343
   343: k = int(sum(1 for b in sub if r[b] <= r_A))
scripts/138_phase2_diag2_joint.py:344
   344: frac = (1 + k) / (1 + kk)
```

`resid_primary[view]` is assigned only inside the D10a loop, under the guard `if name.startswith("PRIMARY")`, and `VARIANTS[0]` is named `"PRIMARY  log1p(dist)"` — the **joint log1p(dist_seq) model**, not D9's shift-only model. D10b reads it at line 342. **D10b ran on the D10a primary joint log1p(dist_seq) residuals while its banner and its prose call them "D9's PRIMARY residuals". The label is wrong; the counts are arithmetically correct for the vector actually used.**

**(ii) The old counts, reproduced, and the vector that produces them:**

| view | k | # at or below | rank fraction | names |
|---|---|---|---|---|
| full | 10 | 8 | 0.8182 | AV_195, AV_220, AV_233, AV_242, G_I192T, G_L178T, G_P254F, G_Y197V |
| full | 20 | 18 | 0.9048 | AV_145, AV_155, AV_175, AV_195, AV_220, AV_233, AV_242, AV_292, AV_293, AV_302, AV_311, G_E168S, G_E279K, G_G317Q, G_I192T, G_L178T, G_P254F, G_Y197V |
| H | 10 | 9 | 0.9091 | AV_195, AV_209, AV_220, AV_233, AV_242, G_I192T, G_L178T, G_P254F, G_Y197V |
| H | 20 | 19 | 0.9524 | AV_145, AV_155, AV_175, AV_195, AV_209, AV_220, AV_233, AV_242, AV_292, AV_293, AV_302, AV_311, G_E168S, G_E279K, G_G317Q, G_I192T, G_L178T, G_P254F, G_Y197V |

The task doc's old counts are 8 / 9 / 18 / 19; all four reproduce exactly, on the **D10a primary joint log1p(dist_seq)** residuals. D9's primary (shift-only) residuals cannot produce them, and the named lists in that vector are incompatible with D9's own printed ten-most-negative tables, which mark `G_P254F`, `AV_195`, `AV_242` and `G_L178T` as **not** at or below A222V's residual.

**(iii) D10b recomputed on D9's primary residuals, as pre-registered** — ***rank fractions, NOT tests***:

| view | k | # at or below | rank fraction | names | TARGET | verdict |
|---|---|---|---|---|---|---|
| full | 10 | 1 | 0.1818 | AV_220 | 1, 0.1818 | **AGREE** |
| full | 20 | 1 | 0.0952 | AV_220 | 1, 0.0952 | **AGREE** |
| H | 10 | 1 | 0.1818 | AV_220 | 1, 0.1818 | **AGREE** |
| H | 20 | 1 | 0.0952 | AV_220 | 1, 0.0952 | **AGREE** |

**Corrected statement.** Among the 10 sequence-nearest nulls, exactly 1 (AV_220) is at or below A222V's primary shift residual on the full frame and exactly 1 (AV_220) on H — rank fractions 0.1818 and 0.1818. Among the 20 nearest, 1 and 1 respectively, rank fractions 0.0952 and 0.0952. These are rank fractions over tiny n, not tests. The Diagnostics II claim that these fractions are **worse** than the raw-rho version is **withdrawn**: it was never computed on D9's residuals and it does not hold on them.

**Cite this, not the old sentence.**

---

## K3 — "not an extrapolation artifact" is overstated

**Old text, at these REAL line numbers:**

- line 856:
  > `r_A` flips from **−0.066** to **+0.045** and A222V's rank moves from 3/79 to 70/79. The clamped variant does not rescue it, and A222V's leverage (hat 0.383) is *inside* the null range (max 0.442), so this is not an extrapolation artifact.

**Predicted rho at A222V's own covariates, next to the most negative OBSERVED null rho.** Predicted rho is `rho_A222V - r_A`.

| variant | view | fit n | predicted rho at A222V's covariates | r_A | most negative OBSERVED null rho | target as printed in the task doc | round(recomputed, 4) |
|---|---|---|---|---|---|---|---|
| shift-only (LOO fit on N) | full | N (78) | -0.021693 | -0.066425 | -0.096244 (`G_P254F`) | -0.0217 | -0.0217 |
| + linear dist_seq | full | N (78) | -0.054407 | -0.033711 | -0.096244 (`G_P254F`) | -0.0544 | -0.0544 |
| + log1p(dist_seq), dist = 0 | full | N (78) | -0.133345 | +0.045227 | -0.096244 (`G_P254F`) | -0.1333 | -0.1333 |
| + log1p(dist_seq), clamped dist = 2 | full | N (78) | -0.107121 | +0.019003 | -0.096244 (`G_P254F`) | -0.1071 | -0.1071 |
| + log1p(d3_CA), d3 = 0 | full | resolved N (67) | -0.181799 | +0.093681 | -0.096244 (`G_P254F`) | -0.1818 | -0.1818 |
| shift-only (LOO fit on N) | H | N (78) | -0.021330 | -0.068692 | -0.101954 (`G_P254F`) | — (no target given for H) | — |
| + linear dist_seq | H | N (78) | -0.054074 | -0.035948 | -0.101954 (`G_P254F`) | — (no target given for H) | — |
| + log1p(dist_seq), dist = 0 | H | N (78) | -0.137052 | +0.047030 | -0.101954 (`G_P254F`) | — (no target given for H) | — |
| + log1p(dist_seq), clamped dist = 2 | H | N (78) | -0.110092 | +0.020070 | -0.101954 (`G_P254F`) | — (no target given for H) | — |
| + log1p(d3_CA), d3 = 0 | H | resolved N (67) | -0.188736 | +0.098715 | -0.101954 (`G_P254F`) | — (no target given for H) | — |

**Target precision, reported and not adjusted.** The task doc states these K3 targets to four decimal places. Every recomputed value agrees with its target to every digit the target prints (5/5 round-trip matches), but 4/5 of them differ from the printed target by more than the D12-G1 table's 2e-6 tolerance, with raw differences between 5.96e-07 and 4.50e-05. **No tolerance was loosened and nothing was tuned.** The raw differences and the round-trip result are both printed above so a reader can judge for themselves. The substantive conclusion does not turn on the fourth decimal place.

**Corrected statement.** The most negative **observed** null rho is -0.096244 (full) and -0.101954 (H), both `G_P254F` / `G_P254F`. The **predicted** rho at A222V's own covariates is below that on the full frame for every log-form distance variant and for the 3D variant: shift-only (LOO fit on N) -> -0.021693; + linear dist_seq -> -0.054407; + log1p(dist_seq), dist = 0 -> -0.133345; + log1p(dist_seq), clamped dist = 2 -> -0.107121; + log1p(d3_CA), d3 = 0 -> -0.181799. A prediction that lies below every observed value is an extrapolation of the fitted surface whatever the leverage (hat) value is: **a hat value inside the null range does not make a point interpolated.** Only the linear-in-sequence-distance form (-0.054407 against a most negative observed null of -0.096244) leaves A222V more extreme than the model predicts. The Diagnostics II sentence claiming the opposite is withdrawn.

**Cite this, not the old sentence.**

---

## K4 — form dependence, restated

**Old text, at these REAL line numbers:**

- line 572:
  > **D10a — adding distance destroys the adjusted advantage.** The shift-only adjustment (D9's primary) gives `p_spec_adj = 0.037975`, at or below both frozen thresholds. Adding a distance term in **any** of the three forms tested puts it far **above** both thresholds:
- line 847:
  > **D10a joint adjustment — adding a distance term destroys the adjusted advantage:**

**Recomputed:**

| form | view | k | p_spec_adj | vs frozen numeric threshold | A222V signed rank | TARGET | verdict |
|---|---|---|---|---|---|---|---|
| linear dist | full | 9 | 0.126582 | ABOVE 0.05 | 10/79 | 10/79, 0.126582 | **AGREE** |
| log1p(dist) | full | 69 | 0.886076 | ABOVE 0.05 | 70/79 | 70/79, 0.886076 | **AGREE** |
| linear dist | H | 10 | 0.139241 | ABOVE 0.1 | 11/79 | 11/79, 0.139241 | **AGREE** |
| log1p(dist) | H | 70 | 0.898734 | ABOVE 0.1 | 71/79 | 71/79, 0.898734 | **AGREE** |

The two full-frame values differ by a factor of 7.00. All four are **above** the frozen numeric thresholds (0.05 full, 0.10 H). No version of `p_spec_adj` is a calibrated tail probability, and none of them is a decision rule. The direction — a distance term moves A222V's adjusted standing above the frozen thresholds — is the robust part; the size is a property of the chosen functional form and is not interpretable.

**Corrected statement.** Under a linear distance term A222V's signed rank is 10/79 (`p_spec_adj` = 0.126582 full) and 11/79 (0.139241 H); under `log1p(dist)` it is 70/79 (0.886076 full) and 71/79 (0.898734 H). All four are above the frozen numeric thresholds; the magnitudes differ about 7-fold. Neither form is a calibrated tail probability.

**Cite this, not the old sentence.**

---

## K5 — the garbled sentence in summary section 5

**Old text, at this REAL line number:**

- line 927:
  > - **Against "position-222-specific."** ρ_b tracks distance from 222 with a large, region-robust gradient (Spearman +0.697 within N on sequence distance, +0.732 on 3D distance — the latter is *not* explained by sequence proximity). All three backgrounds that fall at or below A222V's residual lie at 3D ranks 2, 4 and 9. Once distance is in the model, A222V's residual turns **positive** (`p_spec_adj` 0.886 with sequence distance, 1.000 with 3D distance) and every background in the resolved null set lies beyond it. Holding mean|δ| fixed, the distance association survives (−0.146 → CI includes zero only after shift is partialled the *other* way; the partial with shift held fixed is +0.651) while the shift association does not (−0.108, CI includes zero).

The clause "−0.146 → CI includes zero only after shift is partialled the *other* way; the partial with shift held fixed is +0.651" is incoherent: it uses −0.146 as the shift-held-fixed value and +0.651 as the distance-held-fixed value, then describes them in the wrong order relative to what the two partials actually are.

**Corrected statement (full frame, n = 67 for the 3D partial, n = 78 for the sequence ones).** Holding shift fixed, the 3D-distance association is +0.651 with a CI that excludes zero. Holding 3D distance fixed, the shift association is -0.108 with a CI that includes zero. On sequence distance the same reversal holds: `rho ~ dist | shift` = +0.630 (CI excludes zero) against `rho ~ shift | dist` = -0.146 (CI includes zero). **Spatial distance, not shift magnitude, is the axis that carries the association once the other is held fixed.**

**Cite this, not the old sentence.**

---

## K6 — D10 flag 3 and the D10c verdict paragraph

**Old text, at these REAL line numbers:**

- line 585:
  > **D10c — distance, not shift, carries the association.** Holding mean|δ| fixed, `Spearman(ρ, dist | mean|δ|) = −0.146` (full) and `−0.162` (H), **both CIs include zero**. Holding distance fixed, `Spearman(ρ, mean|δ| | dist) = +0.630` (full) and `+0.604` (H), **both CIs exclude zero**. This is the reverse of D4's reading.
- line 596:
  > 2. **D10c reverses the sign of the shift partial relative to the raw pairwise.** Pairwise `Spearman(ρ, mean|δ|)` within N is **−0.407**, but the partial controlling for distance is **+0.630**. That sign flip is not a bug: `Spearman(mean|δ|, dist)` is **−0.450**, i.e. distant backgrounds are the *low-shift* ones, so conditioning on distance induces a negative relationship between the two covariates that flips the residualised association. Anyone reading the partial alone would be misled about direction. The raw pairwise values are printed beside every partial for exactly this reason.
- line 597:
  > 3. **D10c's answer and D10a's answer point opposite ways, and both are reported.** D10c says the distance axis, not the shift axis, carries the association once the other is held fixed. D10a says that *adding* a distance term destroys A222V's adjusted standing. These are consistent — the distance gradient is strong and A222V sits at its extreme end (dist = 0) — but the framing differs and neither is suppressed.
- line 872:
  > Background-level bootstrap CI only, 10,000 draws, SEED=0. **No permutation p is computed, by design**: a partial correlation is a function of three correlations, and shuffling one variable leaves the conditioning variable unpermuted, so a naive shuffle is not a valid null. Note the sign flip — pairwise `Spearman(ρ, mean|δ|)` is **−0.407** but the partial controlling for distance is **+0.630**, because `Spearman(mean|δ|, dist) = −0.450`.

**Which parts are void after K1.**

- The D10c verdict heading **"distance, not shift, carries the association"** is CORRECT once the labels are fixed, but the two numbers printed underneath it were the wrong two: the CI that includes zero belongs to the **shift** partial and the CI that excludes zero to the **distance** partial. The verdict survives; its supporting arithmetic in the log does not.
- **"This is the reverse of D4's reading"** is **VOID.** The shift partial keeps the raw pairwise sign (-0.407 -> -0.146); nothing reverses.
- **Flag 2's "sign flip" and its whole explanation** are **VOID.** They are artefacts of the transposed labels. Conditioning on distance attenuates the shift association here; it does not reverse it.
- **Flag 3, "D10c's answer and D10a's answer point opposite ways", is VOID.** After K1, D10c and D10a **agree**: D10a finds that adding a distance term moves A222V's adjusted standing above the frozen thresholds, and D10c finds that the distance axis is the one carrying the association. Those are the same finding stated twice.
- The two D10c summary-table rows (real lines 869 and 870) have their two columns transposed and must be read with the K1 labels.

**Cite this, not the old sentence.**

---

## What is NOT corrected

- **D11.2, D11.3, D11.5 and the D1/D9/D0 machinery are unchanged.** D12-G1 reproduces all of them.
- **D11.4's partial-correlation labels were correct** (see K1).
- **The frozen `PHASE2_PREREG.md` verdict is untouched by this file.**
- **C1–C9 from Diagnostics II's own D0 are unchanged.**

## Limits of these corrections

- A partial correlation over 78 (or 67) per-background values has a background-level bootstrap CI that does **not** model the fact that the rho_b share one y-vector (`own_e_b`) and are mutually correlated. Disclosed, not corrected.
- No permutation p is computed for any partial, by design: a partial is a function of three correlations, and shuffling one variable leaves the conditioning variable unpermuted, so a naive shuffle is not a valid null. The bootstrap CI is the whole uncertainty statement.
- `mean|delta|` and `rho_b` are both functions of the same `delta_b`. The adjustment is not an independent control.
- Leave-one-out residuals come from overlapping fits on the same points and are not exchangeable draws; a rank count on them is not a calibrated tail probability.
- Reproducing Diagnostics II's machinery here is a **unit test** of this script, not independent evidence for any claim.

---

*Generated by `scripts/140_phase2_diag3_corrections.py`; N_BOOT=10000, SEED=0. Full verbatim output: `PHASE2_DIAG3_D12_FULL_OUTPUT.txt`.*
