# C1′ — Channel-Independent Shift-Side Mechanism Null — Execution Log

Session start: 2026-09-27.
Task doc: `docs/tasks/c1-prime-independent-channels/C1_PRIME_INDEPENDENT_CHANNELS.md`.
Binding rules: `AGENTS.md` (repo root), read in full before any work.

Format (same as every prior session):

```
## [TASK ID] — [one-line title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
---
```

Scope guard from the task doc: this session adds ONE new script
(next free number) and this log. It does not modify, re-run, or delete
anything from `[C1]`'s original script or output CSV, does not touch
A2/D1/D2/B1/E1/E2/F1/F2/G1–G3/H1–H6, and does not touch `RESULTS.md`,
`PROJECT_SUMMARY_FINAL.md`, or any other protected file.

---

## [C1′a] — Pre-registered design + calibration to the project's own measured reliabilities (scripts/108)

Status: PASS
Time started / finished: 14:16 / 14:31 (2026-09-27)

What I did:
- Read `AGENTS.md` (binding, full) and the task doc
  `C1_PRIME_INDEPENDENT_CHANNELS.md` in full; created this log before
  any other work.
- Read `scripts/106_c1_mechanism_only_null_shift.py` in full — its
  machinery is what C1′ must reuse (frame construction, f_bar pool,
  `own_context.fit_interaction` / `stats_ext.rebuild_interaction_fit`
  / `stats._spearman` / `stats.position_cluster_bootstrap` imports,
  V1–V4 verification pattern, C1d three-way verdict rule).
- Pinned BOTH calibration targets from disk before designing anything
  (no invented numbers):
  - ESM target = **0.8826369680851056** — `r_xx_median` read from
    `data/processed/task105_difference_score_reliability.csv` (D1's
    G2-gated cross-checkpoint reliability; on record as 0.88).
  - Assay target = **0.6363275925044801** — `rel_own` read from
    `data/processed/task47_c3a_disattenuation.csv` (C3a's
    synonymous-variant reliability, 1 − var(syn 0.02111, n=570) /
    var(analysis 0.05804); on record as 0.6363).
  Both are additionally re-read and gated against the pre-registered
  constants at run time (G0 targets PASS).
- Wrote `scripts/108_c1prime_channel_independent_null.py` with the
  full pre-registered docstring BEFORE running anything: the task
  doc's exact 7 design steps; noise = additive zero-mean Gaussian
  (shape assumed, magnitude calibrated — disclosed); five distinct rng
  streams (severity seed 0 = script 106's discipline, ESM seed 1,
  assay seed 2, calibration seeds 3/4); calibration = deterministic
  bisection on σ of the channel's cross-draw reliability measured
  D1's way (5 replicates on the same s_v vector, median over 10
  pairwise Spearmans), inner tolerance 0.002, gate tolerance ±0.02
  (fixed pre-run per task doc); all gates (G0–G3, C2a/C2b, C3a/C3b,
  V1a–V1d, V4, I1/I1b); the C1d three-way verdict rule applied fresh
  to this construction's own CI; N_BOOT env default 10000, smoke 300,
  seed 0; output `data/processed/task108_c1prime_channel_null.csv`.
  **Pre-run structural disclosure written into the docstring before
  any output existed**: because both ESM arms equal s_v + noise, the
  difference shift_sim cancels s_v identically, so with independent
  streams the two simulated statistics share NO random term and this
  null is EXPECTED to center near zero — stated pre-run so a
  near-zero outcome cannot be dressed up post-hoc either way.
- Ran smoke `N_BOOT=300` (EXIT=0), then full `N_BOOT=10000` (EXIT=0,
  32.3 s), foreground, `venv/bin/python3`.

Actual output (verbatim key lines, full run; smoke identical to
displayed precision except CIs/p, as expected for a deterministic
construction):
```
  G0 targets PASS: ESM 0.8826369680851056 (task105 r_xx_median) | assay 0.6363275925044801 (task47 rel_own)
  G1 PASS: frame = 10757 rows / 654 positions; all hgvs_pro map to raw fit rows
  G2 PASS: real anchor reproduced live: rho = -0.08811806424891734 (tol 1e-9)
  G3 PASS: f_bar pool n=11344 range=[0.0000, 1.9354] non-negative
  pipeline constants (real, reused): b_A=0.46891682222397274 r_A=0.0016033484529922113 (p.Ala222Val row 3010)
  s_v: rng.choice(f_bar) seed 0, n=10757, mean 0.598375 median 0.650647 var(ddof=1) 0.111566 — the ONE shared term
  [ESM channel] closed-form sigma (Pearson ref) = 0.12179807092995748
  [ESM channel] bisected sigma = 0.11996599641915845
  [ESM channel] achieved primary reliability (median of 5 choose 2 pairwise Spearmans on s_v) = 0.8826369729054466  vs target 0.8826369680851056  (diff +0.000000)
  [assay channel] closed-form sigma (Pearson ref) = 0.2525111759153038
  [assay channel] bisected sigma = 0.2535446946969483
  [assay channel] achieved primary reliability (median of 5 choose 2 pairwise Spearmans on s_v) = 0.636327605242084  vs target 0.6363275925044801  (diff +0.000000)
  C2a ESM primary achieved 0.8826369729054466 vs target 0.8826369680851056 diff +0.000000 (gate |diff| <= 0.02)
  C2a PASS: ESM-channel reliability achieved within +/-0.02
  C2b assay primary achieved 0.636327605242084 vs target 0.6363275925044801 diff +0.000000 (gate |diff| <= 0.02)
  C2b PASS: assay-channel reliability achieved within +/-0.02
  C3a ESM secondary achieved (analysis arm pair Spearman) 0.8819028266313074 vs target 0.8826369680851056 diff -0.000734 (gate |diff| <= 0.02)
  C3a PASS
  C3b assay secondary achieved (analysis arm pair Spearman) 0.6308102571843673 vs target 0.6363275925044801 diff -0.005517 (gate |diff| <= 0.02)
  C3b PASS
```

Verdict: PASS. Both calibration gates hit their targets to the printed
precision (diff +0.000000, i.e. ≤ 1e-7 against a pre-registered ±0.02
tolerance); the deterministic bisection converged on the first attempt
with no re-search, no re-seeding, and no tolerance change. The
secondary (single analysis-arm-pair) realizations also landed inside
±0.02 on their first and only draw (−0.000734 / −0.005517).

Files created/modified: `scripts/108_c1prime_channel_independent_null.py`
(created); `data/processed/task108_c1prime_channel_null.csv` (created);
this log (created + this entry). Nothing else.

Anything unexpected or worth flagging:
- **First smoke attempt crashed before any statistic**: `KeyError:
  'rel_own_eb'` — I had used the wrong column name when re-reading the
  assay target from task47's CSV (actual column is `rel_own`). Fixed
  the column name, re-ran smoke. This was an input-schema bug found at
  G0, not a gate failure; no number had been produced, no rule or
  threshold changed. Disclosed here per AGENTS §6.
- Closed-form σ (Pearson) vs bisection σ (Spearman) differ ~1.5%
  (0.121798 vs 0.119966 ESM; 0.252511 vs 0.253545 assay) — expected,
  the search governs as pre-registered; both printed.
- Smoke and full runs produce IDENTICAL point values (deterministic
  seeds); only CIs/p change with N_BOOT — as it should be.
---

## [C1′b] — Verification gates before trusting any correlation (calibration + cross-channel independence + adapted V1)

Status: PASS
Time started / finished: 14:31 / 14:32 (2026-09-27) — gates execute
inside the same runs as C1′a (smoke 14:31, full 14:32, both EXIT=0).

What I did: Ran every pre-registered gate BEFORE the statistic was
computed (the script's own ordering enforces this): the four
calibration gates (C2a/C2b primary, C3a/C3b secondary — output quoted
in [C1′a] above), then the cross-channel independence measurement, the
within-channel arm checks, the two structural channel-separation
identities, the NaN accounting, and the bootstrap identity checks.

Actual output (verbatim, full run):
```
  V1a Spearman(noise_ESM_wt, noise_assay_wt) = -0.009755110529361004  (gate |rho| <= 0.05)
  V1a Spearman(noise_ESM_wt, noise_assay_av) = -0.0001750592580296457  (gate |rho| <= 0.05)
  V1a Spearman(noise_ESM_av, noise_assay_wt) = 0.015330712299388073  (gate |rho| <= 0.05)
  V1a Spearman(noise_ESM_av, noise_assay_av) = 0.014826355197047588  (gate |rho| <= 0.05)
  V1a PASS: all four cross-channel noise pairs independent (worst |rho| = 0.015331) — measured, not asserted
  V1b within-channel: Spearman(ESM_wt, ESM_av) = -0.0041826846119782865 | Spearman(assay_wt, assay_av) = -0.013678118270403307  (gate |rho| <= 0.05)
  V1b PASS: arm noises independent within both channels
  V1c structural: max|shift_sim - (noise_ESM_av - noise_ESM_wt)| = 2.220e-16  (gate < 1e-12) — shift carries NO s_v term and NO assay term by arithmetic
  V1c PASS: shared severity cancels identically in the difference; shift_sim = pure ESM-channel noise difference
  V4 accounting: eb_analog finite = 10757/10757
  V4 PASS
  V1d identity: max|eb_analog - (f_av_assay - b_A*f_wt_assay - cb(f_wt_assay))| = 4.174e-14  (gate < 1e-9)
  V1d PASS: eb_analog is a function of ASSAY-channel quantities + real pipeline constants only — no ESM quantity enters its construction
  channel-separation statement (verified by V1a/V1c/V1d): the ONLY term shared across channels is s_v itself, present in all four arm values by design (task doc step 1); it cancels identically from shift_sim (V1c) and persists only into eb_analog (assay side). No other term references both channels.
  I1 PASS: bootstrap observed == direct Spearman (-0.014142108623773391)
  I1b PASS
```

Verdict: PASS — every gate, no exceptions:
- **Calibration gates**: ESM achieved 0.8826369729054466 vs target
  0.8826369680851056 (diff +0.000000 ≤ ±0.02); assay achieved
  0.636327605242084 vs target 0.6363275925044801 (diff +0.000000
  ≤ ±0.02); secondary analysis-arm pair 0.8819028266313074
  (−0.000734) and 0.6308102571843673 (−0.005517), both ≤ ±0.02.
- **Cross-channel independence**: MEASURED, not asserted — all four
  ESM×assay noise-pair Spearmans printed above; worst |ρ| =
  0.015330712299388073 ≤ 0.05 (pre-registered threshold ≈ 5.2 sd at
  n = 10,757).
- **Adapted V1 (no term references both channels except s_v)**:
  V1b arm noises independent within each channel; V1c shows the
  severity term cancels identically from shift_sim (2.220e-16 < 1e-12)
  so shift carries no s_v and no assay term at all; V1d shows
  eb_analog equals its analytic ASSAY-only form (4.174e-14 < 1e-9) so
  no ESM term enters it; the only shared term in the whole
  construction is s_v in the four arm values — exactly what the task
  doc's step 1 mandates.
- V4: 10757/10757 finite (0 NaN, expected 0); I1/I1b: bootstrap
  observed == direct Spearman to < 1e-12 for both the sim and the
  re-derived real anchor.

Files created/modified: none new (gate output lives in the two runs'
stdout; also written to `task108_c1prime_channel_null.csv` rows
`verify`/`cal`).

Anything unexpected or worth flagging:
- The cross-channel worst pair (0.0153) is smaller than some WITHIN-
  channel noise-arm pairs would be at random (assay within-channel
  −0.0137) — all are ordinary sampling noise well inside the 5.2-sd
  threshold; printed in full so nothing rides on a single number.
- Because C1's V1 measured ARM independence while C1′'s arms share
  s_v BY DESIGN (they must), the V1 adaptation measures NOISE-level
  independence instead (V1a/V1b) plus the two structural identities
  (V1c/V1d). This adaptation is exactly what the task doc's C1′b
  bullet prescribes ("its V1 arm-independence check, adapted to this
  design"); logged as the assumed reading.
---

## [C1′c] — Both constructions side by side + pre-registered verdict

Status: PASS
Time started / finished: 14:32 / 14:33 (2026-09-27)

What I did: Computed the channel-independent statistic fresh
(position-cluster bootstrap, N_BOOT=10000, seed 0, p primary, no
z-score), re-derived the real anchor's CI fresh on the same convention,
QUOTED C1's original numbers from `task106_c1_mechanism_null.csv`
(never recomputed), printed the side-by-side table, and applied the
C1d three-way magnitude rule to THIS construction's own CI (the rule
does not carry over — the CI does).

Actual output (verbatim, full run):
```
  construction                                rho  95% CI                                         p_boot   what it tests
  C1 upper-bound (shared-draw)          +0.936624  [+0.933389, +0.939619]                       <1e-04   both stats = affine fns of the SAME two draws
  C1' channel-independent               -0.014142  [-0.033424, +0.004446]                       0.1366   independent channels calibrated to 0.88/0.6363, share only s_v
  REAL anchor                           -0.088118  [-0.117333, -0.059511]                     <1.0e-04   actual delta_esm vs own_e_b
  [CHANNEL-INDEPENDENT null] rho=-0.014142108623773391  CI [-0.033423649894174616, 0.004445537674694027]  p_boot=0.1366  (n=10757, 654 positions)
  [REAL anchor] rho=-0.08811806424891734  CI [-0.1173334458953319, -0.05951138449511738]  p_boot=<1.0e-04  (n=10757, 654 positions)
  descriptive sensitivity (correction=None, point estimate only, no decision): rho=-0.011941774154894941
  channel-independent |rho| = 0.014142108623773391, 95% CI on |rho| [0.004445537674694027, 0.033423649894174616]
  real observed |rho| = 0.08811806424891734 (canonical -0.08811806424891734)
  SIGN observation: channel-independent rho = -0.014142 (-neg), C1 upper-bound rho = +0.936624 (+pos), real rho = -0.088118 (-neg) — sign reported as its own result, not folded into the verdict
  VERDICT: −0.088 is LARGE relative to the channel-independent reference point — the observed |−0.088| sits ABOVE the channel-independent CI
  COMPARISON: the channel-independent |rho| (0.014142108623773391) is meaningfully SMALLER than C1's upper-bound |rho| (0.9366244249321943) — smaller by 0.925477 at minimum — because decoupling the channels removes the artificial shared-draw inflation: both statistics no longer read the same random numbers. Per the task doc this makes the channel-independent version the stricter, more informative test; the manuscript should cite it as primary, with C1 kept as a disclosed upper-bound sensitivity check.
  context: Y2's sibling reference (severity predictor vs e.b) = +0.590, quoted from Y2's task summary — not recomputed
  saved 33 rows -> task108_c1prime_channel_null.csv
SCRIPT 108 DONE (32.3s)  ind_rho=-0.014142 [-0.033424, +0.004446] | C1_quoted=+0.936624 | real=-0.088118 | verdict: LARGE relative to the channel-independent reference point — the observed |−0.088| sits ABOVE the channel-independent CI
```

Verdict: PASS — the pre-registered three-way rule, applied fresh,
fires ABOVE → "**−0.088 is LARGE relative to the channel-independent
reference**" (|0.08811806424891734| > |CI| hi 0.033423649894174616).
This is the OPPOSITE magnitude reading from C1's original (BELOW →
SMALL), and both are reported side by side: the two constructions
answer different questions — C1 measured what SHARED-DRAW coupling
mechanically injects (upper bound, +0.9366); C1′ measures what
severity + calibrated noise injects across INDEPENDENT channels
(near zero, −0.0141, CI straddling 0, p = 0.1366 — consistent with
the pre-run disclosure that this null centers near 0 by construction).
The collapse from +0.9366 to −0.0141 (≥ 0.925 in magnitude) is
direct evidence that C1's reference was essentially all shared-draw
inflation. Per the task doc, C1′ is the stricter test and the
manuscript should cite it as primary going forward with C1 kept as a
disclosed upper-bound sensitivity check — this recommendation is
narrative output from the pre-registered design, not a post-hoc spin;
the only decision rule executed was the 3-way mapping.

Files created/modified: `data/processed/task108_c1prime_channel_null.csv`
(33 rows, verified on disk); this log. C1's script/CSV untouched
(read-only quoted input).

Anything unexpected or worth flagging:
- **Real-anchor CI cross-check**: this run's fresh real CI
  [−0.1173334458953319, −0.05951138449511738] is EXACTLY C1's
  recorded CI in task106's CSV — same convention and seed reproduce
  digit-for-digit (good); noted so no one mistakes the two for
  independent computations.
- **|ρ|-CI convention caveat (disclosed)**: when the signed CI
  straddles 0 (as here: [−0.0334, +0.0044]), the pre-registered
  min/max-of-|bounds| mapping yields [0.0044, 0.0334] — a positive
  lower bound that is an artifact of taking absolute values, not a
  claim that |ρ| ≥ 0.0044. It does not affect the verdict (0.088 >
  0.033 regardless of what the lower bound is); rule left unchanged
  as pre-registered, disclosed here.
- **Structural-caveat to carry forward (limitation 1 of the script's
  own output)**: the near-zero outcome is substantially a property of
  the mandated design (differencing cancels s_v identically + independent
  streams — an architecture check, disclosed pre-run). Any manuscript
  sentence using C1′ must carry that caveat alongside the verdict;
  C1′ bounds what mechanism-only structure injects across independent
  channels — it does not, by itself, prove the real −0.088 is "real".
- No post-hoc choices were made this session; every threshold, seed,
  tolerance, and rule was fixed in the docstring before the first run.
---

## SUMMARY

**Task completed / blocked (why):** ALL THREE tasks completed — C1′a
(design + calibration), C1′b (verification gates), C1′c (side-by-side
report + verdict). Nothing blocked, nothing FAIL, nothing skipped.
One script added (`scripts/108_c1prime_channel_independent_null.py`,
next free number; pre-registered docstring written before the first
run), smoke `N_BOOT=300` then full `N_BOOT=10000` both EXIT=0,
output `data/processed/task108_c1prime_channel_null.csv` (33 rows).
`[C1]`'s script 106 and `task106_c1_mechanism_null.csv` were READ-ONLY
quoted inputs — not re-run, not modified. No protected file touched.

**The two calibration gates — achieved vs targets (gate = ±0.02,
fixed pre-run):**
- ESM channel: achieved **0.8826369729054466** vs target
  **0.8826369680851056** (D1 `r_xx_median`, task105 CSV) — diff
  +0.000000 → C2a PASS. Bisected σ = 0.11996599641915845 (Pearson
  closed-form reference 0.12179807092995748).
- Assay channel: achieved **0.636327605242084** vs target
  **0.6363275925044801** (C3a `rel_own`, task47 CSV; on record as
  0.6363) — diff +0.000000 → C2b PASS. Bisected σ = 0.2535446946969483
  (closed-form 0.2525111759153038).
- Secondary (single analysis-arm pair actually used downstream):
  ESM 0.8819028266313074 (−0.000734) and assay 0.6308102571843673
  (−0.005517) → C3a/C3b PASS, both inside ±0.02 on their only draw.

**The cross-channel independence check result:** MEASURED, all four
pairs printed — Spearman(ESM_wt, assay_wt) = −0.009755110529361004;
(ESM_wt, assay_av) = −0.0001750592580296457; (ESM_av, assay_wt) =
+0.015330712299388073; (ESM_av, assay_av) = +0.014826355197047588.
Worst |ρ| = **0.015330712299388073 ≤ 0.05** (pre-registered ≈5.2-sd
threshold) → **V1a PASS**, from five distinct rng streams (severity
0 / ESM 1 / assay 2 / cal 3,4). Accompanied by V1b within-channel
(−0.004183, −0.013678 PASS), V1c severity-cancellation identity
(2.220e-16 < 1e-12 PASS), V1d eb-analog analytic identity
(4.174e-14 < 1e-9 PASS), V4 = 0 NaN, I1/I1b bootstrap identities PASS.

**The channel-independent mechanism-null result, in full:**
ρ = **−0.014142108623773391**, 95% CI
**[−0.033423649894174616, +0.004445537674694027]**, p_boot = **0.1366**
(position-cluster bootstrap, n = 10,757 / 654 positions, N_BOOT = 10000,
seed 0; p is the primary claim, no z-score computed; CI straddles 0 —
consistent with the pre-run disclosure that this null centers near zero
because the differencing shift cancels the shared severity identically).
Descriptive sensitivity (correction=None): −0.011941774154894941.

**Both constructions side by side, and where the real −0.088 anchor
falls relative to each:**
| construction | ρ | 95% CI | p_boot | where −0.088 falls (C1d rule, fresh CI) |
|---|---|---|---|---|
| C1 upper-bound (shared-draw) — QUOTED from task106 CSV, never recomputed | +0.9366244249321943 | [+0.933389201160778, +0.9396189771832062] | <1e-04 | \|0.088\| **BELOW** the CI → "SMALL" (C1's original verdict) |
| C1′ channel-independent (this session) | −0.014142108623773391 | [−0.033423649894174616, +0.004445537674694027] | 0.1366 | \|0.088\| **ABOVE** the \|ρ\| CI [0.004446, 0.033424] → "**LARGE**" |
| REAL anchor (re-derived live, gated 1e-9) | −0.08811806424891734 | [−0.1173334458953319, −0.05951138449511738] | <1.0e-04 | — |

The two references give OPPOSITE magnitude readings (SMALL vs LARGE)
because they answer different questions: C1 quantified shared-draw
coupling (both statistics reading the same random numbers — an upper
bound); C1′ quantifies severity + calibrated measurement noise across
genuinely independent channels (near zero). The ≥0.925 collapse from
+0.9366 to −0.0141 shows C1's headline number was essentially all
shared-draw inflation. The real anchor's CI reproduced C1's recorded
CI digit-for-digit (same convention/seed — a cross-check, not an
independent computation).

**Should C1′ replace the original as primary, or stand alongside it:**
Per the task doc's own mandate: **C1′ should be cited as the PRIMARY
reference going forward (it is the stricter, calibrated, like-for-like
test), with C1 kept on the record as a disclosed upper-bound
sensitivity check — standing alongside it, never replacing or
deleting it** (C1's numbers were quoted, untouched; both are already
reported side by side in [C1′c]). REQUIRED caveat to carry with any
primary use (script limitation 1, disclosed pre-run): C1′'s near-zero
outcome is substantially structural — the differencing shift cancels
s_v identically while the streams are independent — so it is an
architecture check that locates the +0.937 inflation and bounds what
mechanism-only structure injects across independent channels; it does
NOT by itself prove the real −0.088 is non-artifactual.

**The single most important thing to look at first:** the
**[C1′c] side-by-side table and its verdict flip** — the same real
anchor is BELOW C1's upper-bound null (SMALL) but ABOVE the
channel-independent null (LARGE), and that contrast — not either
number alone — is what the manuscript's next sentence must be built
on (C1′ primary + C1 upper-bound sensitivity + limitation 1's
structural caveat), before any wording is drafted.
