# C1′ — A Channel-Independent Version of the Shift-Side Mechanism Null

Source: reviewing `[C1]`'s own disclosed limitation. Its mechanism-only
reference (ρ = +0.937) was built by constructing both the simulated shift
and the simulated e.b-analog as two different affine functions of the
exact same two random draws (`f_wt`, `f_av`). That makes it a legitimate
upper-bound-style stress test, but not a like-for-like companion to Y2,
because in reality `delta_ESM` (computed from ESM-2's internal
representation) and `own_e.b` (computed from real folinate-assay fitness
measurements) are two genuinely different physical/computational channels
that share only the *true* underlying variant severity, not a literal
shared random number. This task builds a tighter version with
independently-noised channels, calibrated to this project's own
already-measured reliabilities rather than an arbitrary noise level.
**Do not discard C1's original result — report both side by side,
labeled as the upper-bound construction and the channel-independent
construction respectively.**

---

## Task C1′a — Design, calibrated to real measured reliabilities

Pre-register this exact design in the new script's docstring before
running anything:

1. For each variant, draw one shared **true severity value** `s_v` from
   the real `f_bar` pool (script 106's exact same pool, same seed
   discipline) — this is the one thing the two channels are allowed to
   share, representing real biology both measurement processes are
   trying to capture.
2. **ESM channel** (feeds the simulated shift): generate
   `f_wt_ESM = s_v + noise_ESM_wt` and `f_av_ESM = s_v + noise_ESM_av`,
   with `noise_ESM_wt` and `noise_ESM_av` drawn independently. Calibrate
   the noise magnitude so that, when this channel's own cross-draw
   reliability is measured the same way the project measured ESM-1v's
   real cross-checkpoint reliability, it reproduces approximately 0.88
   (the already-measured value from D1 — reuse it explicitly, do not
   invent a new number). This is a real calibration step: run a short
   search or closed-form derivation for the noise variance that achieves
   this, and report the achieved value against the 0.88 target as a
   gate.
3. **Assay channel** (feeds the simulated e.b-analog): generate
   `f_wt_assay = s_v + noise_assay_wt` and
   `f_av_assay = s_v + noise_assay_av`, independently noised the same
   way, calibrated instead to reproduce the project's own already-measured
   e.b reliability (≈0.6363, from the synonymous-variant analysis already
   on record — reuse it explicitly).
4. Critically: `noise_ESM_*` and `noise_assay_*` must be drawn from
   **separate random streams** (distinct seeds or a demonstrably
   independent generator state) so that no single random draw feeds both
   channels — verify this with an explicit zero-correlation gate between
   the ESM-channel noise draws and the assay-channel noise draws, not
   just an assertion.
5. Construct `shift_sim = f_av_ESM − f_wt_ESM` (mirrors delta_esm).
6. Construct `eb_analog_sim` from `f_wt_assay`, `f_av_assay` through the
   exact same real `own_context` WLS machinery `[C1]` already used and
   verified (reuse that code path via import, do not reimplement it).
7. Correlate `shift_sim` against `eb_analog_sim` using the project's
   standard position-cluster bootstrap convention, same N_BOOT discipline
   as every other script in this project (smoke first, then full).

## Task C1′b — Verification gates, before trusting any correlation

- Reproduce the calibration targets explicitly: report the achieved
  ESM-channel reliability (target ≈0.88) and assay-channel reliability
  (target ≈0.6363) as gates, with the exact achieved values printed, not
  just "close enough" — if either misses its target by more than a
  reasonable tolerance (state the tolerance explicitly in the docstring
  before running, e.g. ±0.02), treat this as a FAIL requiring a
  recalibration of the noise search, not a silent pass.
- Gate the cross-channel noise independence explicitly (near-zero
  correlation between the ESM-channel and assay-channel noise draws).
- Reuse `[C1]`'s own zero-planted-interaction verification logic (its V1
  arm-independence check, adapted to this design) as an additional gate:
  confirm no term in the construction references both channels except
  through the shared true severity value `s_v`.

## Task C1′c — Report both constructions side by side, with a plain verdict

- Report `[C1]`'s original result (ρ = +0.937, upper-bound/shared-draw
  construction) and this new channel-independent result together, in one
  table, each clearly labeled with what it actually tests.
- State plainly where the real anchor (−0.088) falls relative to the new,
  tighter reference — using the same BELOW/INSIDE/ABOVE magnitude rule
  `[C1]` used, applied fresh to this construction's own CI, not assumed
  to carry over from the first version.
- If the channel-independent reference comes out meaningfully smaller
  than 0.937 (plausible, since decoupling the channels removes the
  artificial shared-draw inflation), say so explicitly and explain why —
  this would mean the channel-independent version is a stricter,
  more informative test than the original, and the manuscript should
  cite this one as primary going forward, with the original kept as a
  disclosed upper-bound sensitivity check rather than the headline
  number.

---

## What NOT to do

Do not modify, re-run, or delete anything from `[C1]`'s original script
or its output CSV — this is a new, additional script, not a replacement.
Do not touch A2, D1, D2, B1, E1, E2, F1, F2, G1–G3, or H1–H6 from the
prior session; those are already closed. Do not touch `RESULTS.md`,
`PROJECT_SUMMARY_FINAL.md`, or any other protected file.
