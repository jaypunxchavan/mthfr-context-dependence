# PHASE 2 diagnostics III — corrections to this session's own log

**Written by:** `scripts/147_phase2_diag3_corrections3.py` (task D17), from inside the script, so every number is interpolated from a computed variable.
**Corrects:** `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` — **READ ONLY, never edited.**
All 12 D17 gates PASS, including a gate that D14's recomputed per-bin mean|delta| reproduces its own saved output to 2e-6 on all 2 bin-view combinations.

---

## K7 — D12 flag 5 cites `G_P254F`'s rho as A222V's observed rho

**Old text, at these REAL line numbers of this session's log:**

- line 350:
  > 5. **A222V is only barely more extreme than predicted under linear distance** (-0.054407 predicted vs -0.096244 observed), so the K3 conclusion - that only the linear form leaves A222V more extreme than predicted - rests on a fairly small margin. Stated, not smoothed over.

**The error.** `-0.096244` is **`G_P254F`'s rho**, the most negative observed NULL rho. A222V's own observed rho is **-0.088118** (full) and **-0.090022** (H).

**Corrected statement.** Under the linear-in-sequence-distance model, A222V's predicted rho at its own covariates is **-0.054407** against its observed **-0.088118**, so A222V is 0.033711 MORE NEGATIVE than that model predicts, with `r_A` = -0.033711, k = 9 of 78 and signed rank 10/79. The margin is not the small one the old sentence described: it is measured against A222V's own observation, not against the single most extreme null, and A222V sits 0.008126 short of `G_P254F`. Within its own site, under the same model, A222V's rank is 2/19 — ***a rank fraction over n = 19, not a test***.

**Cite this, not the old sentence.**

---

## K8 — D14 flag 2's inference does not follow

**Old text, at these REAL line numbers:**

- line 683:
  > 2. **That cuts against the more extreme reading of "spatial-overlap with no long-range content"** and is why I am not going to let D15 be read that way unless its own numbers say so. The bin means are what they are: a smooth gradient, no 0 A cliff.

**Corrected statement.** D14 bins **backgrounds** by `d3_CA` and summarises `rho_b` inside each bin; it answers *does rho_b depend on where the background sits?* It does not filter, restrict or otherwise touch the set of **target variants**, and every D14 bin is computed on all usable rows. D15 varies the **target-variant** axis (`d3_222(p) > R`) and answers a different question: *does the gradient survive when the scored target variants are forced distal?* These are two different axes, so D14's absence of a step at the 0 A bin edge is **silent** about the target-variant axis and cannot cut against a long-range claim. It did not: D15 found the gradient falling to +0.401 (full) and +0.241 (H) at R = 30 A, outside the matched-deletion range. **The two results are compatible and both stand.**

**Cite this, not the old sentence.**

---

## K9 — D14 flag 3: the Arm S bin is not a low-shift bin

**Old text, at these REAL line numbers:**

- line 670:
  > - **mean|delta| is NOT monotone in the bins and moves in the opposite direction at the near end**: Arm S 0.0891, (0,12] 0.0694, (12,20] 0.0961, (20,30] 0.0566, (30,45] 0.0470, (45,inf) 0.0452. The near-222 bins are the LOW-shift bins and the far bins are also low, with a peak at (12,20]. The bins are not matched for shift; this is printed in every bin for exactly that reason.

**Recomputed per-bin `mean|delta|`** on D14's own bin definitions, from script 125's rows, and gated against D14's saved output to 2e-6 on all 2 bin-view combinations:

| rank (highest first) | bin (`d3_CA`) | mean&#124;delta&#124; (full) | mean&#124;delta&#124; (H) |
|---|---|---|---|
| 1 | (12, 20] | 0.096069 | 0.094655 |
| 2 | {exactly 0}  (Arm S) | 0.089085 | 0.089728 |
| 3 | (0, 12] | 0.069361 | 0.073960 |
| 4 | (20, 30] | 0.056589 | 0.060150 |
| 5 | (30, 45] | 0.046972 | 0.048621 |
| 6 | (45, inf) | 0.045204 | 0.046668 |

**Corrected statement.** The distance-0 **Arm S** bin's `mean|delta|` is **0.089085**, the **second highest** of the six bins, not a low one. Only **4 of 6** bins sit below it ((0, 12], (20, 30], (30, 45], (45, inf)). The **(0,12]** bin (0.069361) **is** the lowest of all six, so the old phrase is true of the 3D-nearest null bin and false of the Arm S bin it was used to describe. The **(12,20]** bin (0.096069) is the **highest** of all six, so the old sentence's 'peak at (12,20]' was correct. The bins are not matched for shift, which is why `mean|delta|` is printed in every one of them.

**Cite this, not the old sentence.**

---

## K10 — D13 flag 4's scale error

**Old text, at these REAL line numbers:**

- line 534:
  > 4. **A222V is INSIDE the Arm S raw-rho range, not outside it.** Only one of 18 same-site comparators is more extreme. That is a much weaker same-site statement than the frozen 1-of-78 result against the null set, and it is reported as the rank fraction it is.

**Corrected statement.** The same-site comparison places A222V at **2/19** and the frozen null comparison places it at **2/79**. Both are **ordinal position 2**. The old sentence's "the frozen 1-of-78 result" also mis-states the frozen denominator: `p_spec` uses 79 = 1 + |N|, with 1 of 78 nulls at or below. The two comparisons are not directly comparable in *strength* because they answer different questions at different n — 18 same-site substitutions at residue 222 versus 78 backgrounds elsewhere — but neither is "much weaker" than the other as an ordinal statement. What separates them is the reference set, not the rank.

**Cite this, not the old sentence.**

---

## Limits of these corrections

- K7 and K10 concern **how a number is described**, not the number itself: every value quoted in the old sentences is reproduced exactly.
- K8 is a **category error** about which axis a result varies on, and it is corrected by pointing at what D15 measured, not by re-running anything.
- K9 is a **factual error about the bins**, caught by recomputing them and gating that recomputation against D14's own saved output.
- The frozen `PHASE2_PREREG.md` verdict is untouched by this file.

---

*Generated by `scripts/147_phase2_diag3_corrections3.py`; no resampling. Full verbatim output: `PHASE2_DIAG3_D17_FULL_OUTPUT.txt`.*
