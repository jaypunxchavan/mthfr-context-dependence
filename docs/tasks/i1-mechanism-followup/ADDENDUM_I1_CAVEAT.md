# ADDENDUM — Epistemic caveat for I1-dependent claims (DRAFT — do not merge)

**Status:** DRAFT for review, per task L3a of
`docs/tasks/i1-mechanism-followup/I1_MECHANISM_FOLLOWUP.md`. This file is
the only sanctioned new prose deliverable. **`MTHFR_RESULTS_LOG.md`,
`RESULTS.md`, and `REVIEW_TRIAGE.md` were not touched** — nothing here is
applied to them. Every number below is quoted from an executed run logged in
`docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (entries L1a, L1b, L1c,
L2a–c, M1a–e, N1a–b, N2a–c); nothing is reconstructed from memory.

---

## 1. What the follow-up established about I1 (the background for everything below)

- **I1's gate failed as-run:** pooled ρ = 0.4467, permutation null mean
  +0.3880 (≈87% of observed is between-site structure), p_one = 0.1398,
  CI [0.2787, 0.5793], N_PERM = 10,000, one-sided positive, α = 0.05.
- **L1c — the load-bearing number:** the smallest true effect this test
  could detect at power ≈0.8 is **ρ_floor = 0.5400** (crit 0.4755 +
  0.8416 × se 0.0767; sensitivities 0.5109 row-level / 0.5418
  empirically-calibrated σ₀ — all above the observed ρ). The comparator's
  known/realized effect in test units (ρ = 0.4467) sits **below the
  floor** → this gate had only **35.3% power** at that effect. Pre-registered
  verdict: **COMPARATOR-UNDERPOWERED**.
- **L1b:** GB1's implied precision is noisier than MTHFR's at the epistasis
  level (cycle SE 0.1334 vs median SE(e_b) 0.0622, ratio 2.14×; S1 3.01×;
  S2 disagrees at 0.041× — verdict NOISIER-BUT-SENSITIVE, must be quoted
  with its sensitivity), and **41.5% (534/1,287) of the fitness lookups
  building I1's e values sit at or below GB1's own detection limit 0.01**
  (median lookup 0.0160) — I1 sampled the comparator's bad-precision regime,
  where its headline R = 0.97 does not describe precision.
- **L2 (the condition L1c triggered) could not be run:** no second
  double-mutant landscape exists anywhere on disk (L2a BLOCKED; the only
  alternative ever named in this repo, a ProteinGym double-mutant set, was
  never downloaded). L2b/L2c therefore SKIPPED. **The question "would this
  pipeline clear a gate on ANY comparator?" is open — it must not be written
  up either as "the pipeline has power" or as "the pipeline has no power."**
- **M1 (mechanism test):** the proposed H1a mechanism is **NOT SUPPORTED** —
  A222V is not outlier-LOW on context-shift vs its own severity (residual
  +0.00954, 95% position-cluster CI [−0.00573, +0.02640] contains 0; rank
  6/9, not lowest). The *generic* severity→shift relation does hold in this
  designed set (Spearman ρ = −0.4667 CI [−0.5833, −0.0667]; Pearson
  −0.6012 CI [−0.7111, −0.2838]).
- **N group:** script 35's SE flag is formally retired (DEPRECATED header;
  J4a FDR 0.91–1.00 at every cutoff, 0.9312 at the 3.76 fix; J4b region
  factors 2.54–5.16, max/min 2.03; raw N=2 synonymous FPR 44.7%). Its
  nonparametric replacement (synonymous-ECDF, `task_N2_nonparametric_…csv`)
  flags 16.6% of missense at 5.1% synonymous FPR (3.26× enriched over the
  noise floor).

---

## 2. Which Part 5/6 claims are conditional on I1 — and the honest one-sentence caveat

**§5.2 / §5.3 (signed δ_ESM vs e_b, ρ = −0.088, "~0% structural artifact,
cleanest number in the project") — CONDITIONAL in interpretation, NOT in
arithmetic.** The sign-flip null's own calibration check (null mean +0.0001 ≈
0) is internal to MTHFR and stands: the −0.088 really is a property of this
dataset, not a construction artifact. What I1 removes is the license to
promote it to a general claim about the pipeline or the model class.

> **Caveat sentence (drop-in):** "The signed −0.088 result is internally
> calibrated and holds for this dataset, but the positive control built to
> show the same pipeline can detect a known interaction was underpowered
> (35.3% power at the comparator's own realized effect; floor ρ 0.540 >
> observed 0.447) and did not clear, so 'AGAINST ESM-2's usefulness' should
> be read as a statement about these measurements, not yet as a demonstrated
> property of the pipeline's detection ability."

**§5.4 (position-222 proximity confound, ρ = −0.298) — NOT conditional.**
It is an internal structure result on MTHFR's own data and never relied on a
positive control; it stands as written (and independently supports caution
about pooling).

**§5.5 (region check: R1/R3 survive their own nulls, R2/R4 don't) — NOT
conditional on I1** (within-dataset sign-flip nulls, not the I1 gate). One
cross-reference: any *region-level epistatic-fraction* prose elsewhere that
used the retired SE flag is affected by the N group (§4 below), but §5.5's
stated p-values (0.001 / 0.006 / 0.156 / 0.768) do not use it.

**§6.2 (ESM-2 WORSE with real background info, +0.00053, CI
[+0.00029, +0.00077]) — CONDITIONAL (never-calibrated form).** The number is
a clean measured difference on this dataset (11,113 variants, CI excludes
0); note that I1 was the positive control for the *correlation* endpoint —
the MAE endpoint of Part 6 never had a positive control at all, so its
"background use doesn't help / hurts" reading was never demonstrated to be
recognizable-by-construction when background use is real.

> **Caveat sentence (drop-in):** "The direction and CI of the MAE result are
> properties of this dataset; whether the evaluation would register correct
> background use as beneficial is untested — no positive control exists for
> the MAE endpoint, and the correlation endpoint's control (I1) failed its
> gate while underpowered."

**§6.3 / §6.4 (high stratum: ESM-2 worse than the additive null, +0.00241,
CI excludes 0; asymmetry favored ESM-2 and it still lost) — CONDITIONAL as a
general claim, unchanged as a within-dataset statement.** The three-stratum
table's arithmetic stands; its reading as "the direct test of the founding
prediction failed" is conditional on the same power caveat, and its strata
are the old `qcut` terciles whose arbitrariness is exactly what script 35
tried and failed to fix — the N2 replacement now provides a principled
alternative stratum.

> **Caveat sentence (drop-in):** "Where measured interaction is strongest
> ESM-2 is reliably worse than assuming no interaction (this dataset,
> CI excludes 0), but with the positive control underpowered (35.3%) the
> result cannot distinguish 'ESM-2 fails on strong interaction' from 'this
> evaluation could not certify success anywhere' — a distinction the planned
> rank-vs-MAE reconciliation and a better-powered control must still make."

**Net:** the *numbers* in Parts 5/6 are not overturned by anything this
follow-up ran; what I1's outcome removes is the inference from those numbers
to **pipeline-level or model-class-level** conclusions. Every negative claim
keeps its dataset scope; the phrase "the pipeline can't detect real
epistasis" remains unproven in both directions (L1c: underpowered; L2: never
retested on a stronger comparator).

---

## 3. Site-54 design caveat on I1 itself (from L1a — must travel with any I1 citation)

Script 49 tested sites **39/40/41 only**, excluding the fourth Gβ5 site.
The exclusion reason ("the file's WT letter V contradicts RCSB 2GB1's T44")
was later **resolved as a numbering confusion**: the four sites are
**V39/D40/G41/V54**, wild-type string "VDGV" matches the file, so the file
is consistent — the concern was about the wrong position (54, not 44).
Critically, **the dropped 41×54 axis carries the source paper's headline
ε ≈ +5** (Wu et al. 2016, Fig 3D). Consequences, stated plainly:

1. I1 ran on a sub-landscape **excluding the comparator's largest known
   interaction**, which biases I1's realized ρ *down* — consistent with, and
   possibly contributing to, L1c's underpowered verdict.
2. The frozen gate was **not** rerun with four sites: doing so would be a
   post-hoc change to an executed-once gate (AGENTS §0/§10) and needs
   explicit authorization. **Decision item for review:** whether to authorize
   a four-site rerun as a pre-registered follow-up (it would also be the
   cheapest way to give L2 a stronger in-house comparator, partially
   clearing L2a's block).

---

## 4. Adjacent items this addendum flags but does not resolve

- **Script 50 reads the retired `task35_epistatic_set.csv`** (N1b grep,
  line 222) — any D1-family number stratified on `epistatic_N2` inherits an
  FDR of 0.91–1.00 and needs either a footnote or a rerun under
  `task_N2_nonparametric_epistatic_set.csv`. Not changed (per task rules);
  user decision.
- **N2b's region pattern:** the old "R1 > R3" ordering does **not** survive
  (new 0.95 orders [3,1,4,2]) but the change is a cutoff-sensitive near-tie
  flip (1.2 pp; swaps back at 0.99) — the coarse structure R1≈R3 ≫ R4 ≫ R2
  holds at every cutoff. Region-fraction prose should quote the new table,
  not the retired one.
- **M1's verdict cuts both ways:** "A222V is special to the model"
  (H1a) is unsupported, but "the model is insensitive to background severity"
  is also unsupported — context-shift *does* scale with rated severity
  (M1e). The weak δ_ESM signal's explanation remains open, as the task doc
  itself instructs.

---

*DRAFT — for review only. Produced 2026-09-22 by the I1-mechanism-followup
run; source of record: `FOLLOWUP_LOG.md` in this directory. Do not merge
without editing Parts 5/6 themselves, which this run was forbidden to touch.*

---

## 5. Independent re-verification of §3 and the four-site rerun (DRAFT — appended, not merged)

**Status:** DRAFT, not merged — **append only**: every byte of the text
above this line is unchanged (append-only word-count/md5 check before and
after recorded in `docs/tasks/site54-and-script50-migration/MIGRATION_LOG.md`,
task Q2). Source of record for every number below: executed runs quoted
verbatim in entries **P1, P2, Q1** of that same `MIGRATION_LOG.md`.
`MTHFR_RESULTS_LOG.md`, `RESULTS.md`, and `REVIEW_TRIAGE.md` remain
untouched by this run.

**P1/P2 — §3's numbering-confusion claim, independently re-derived from
primary sources: CONFIRMED, with one correction flagged.**

- RCSB structure 2GB1 (fetched live and parsed programmatically, not read
  from §3's prose): contiguous author numbering 1–56, no insertion codes,
  SEQRES == ATOM; **residue 54 = VAL**, **residue 44 = THR**; the data
  file's WT 4-mer `VDGV` matches the PDB letters at 39/40/41/54 exactly
  (`VDGV`) and mismatches 39/40/41/44 (`VDGT`). Script 49's embedded
  sequence is byte-identical to the RCSB parse — its only error was
  treating position 44 as the candidate fourth site. The raw file's
  column 4 is fully populated (160,000 rows, 20 letters × 8,000).
- Wu et al. 2016 (article fetched live): verbatim, the four sites are
  "**V39, D40, G41 and V54**" and "WT sequence is **VDGV**" — this closes
  the column→position mapping that §3 depended on.
- **Correction flagged for §3's ε sentence (review item, not applied):**
  Figure 3 was viewed directly and literally prints `ε = 5` (G41L×V54H on
  the IL background), so §3's "ε ≈ +5" faithfully transcribes the figure —
  **but the value does not re-derive from the data**: under the paper's
  own eq. (2) the on-disk landscape gives **ε = +7.399806** (none of the
  paper's three adjustment rules triggers), and the figure's own printed
  fitnesses give **+7.720905**; no rounding reproduces 5. The companion
  `ε = −4.5` (WL background) **does** re-derive (−4.495855 at file
  precision / −4.621831 from the printed values). The dropped 41×54 axis's
  headline-scale epistasis is confirmed either way (400-background scan:
  max +7.4177, min −7.4998, median +1.4053). Both the printed and the
  re-derived values are logged; this append does not adjudicate which
  number is authoritative.

**Q1 — the four-site rerun §3's decision item 2 asked about: authorized
(P1d CONFIRMED / P2b PROCEED) and executed.**

- `scripts/65_q1_foursite_i1_rerun.py`: identical construction to script
  49 (seed 0, K=10 fitness-blind backgrounds, same e formula, same
  within-site variant-profile permutation null, same identity check, same
  (site,variant) cluster bootstrap, **same pre-registered gate**) with
  site 54 included; output `data/processed/task_Q1_foursite_i1_rerun.csv`.
  The frozen 3-site run (`task49_i1_gb1.csv`, md5
  `8b9f484d73cba096571646fcfab7703a`, mtime untouched) was not modified.
- Result (N_PERM = 10,000, N_BOOT = 2,000, run exited 0): **pooled
  ρ = +0.401757** over n = 760 rows / 76 clusters, permutation null mean
  **+0.247570** (does not center on zero — printed by the script itself),
  **p_one = 0.0009999**, cluster CI **[+0.258070, +0.521658]**, identity
  check max|diff| = 0.000e+00 → **GATE PASSES** under the unchanged rule
  (ρ > 0 AND one-sided p < 0.05). Per-site ρ: 39 +0.3365, 40 −0.1280,
  41 +0.3481, 54 +0.3384.
- Honest effect-size framing: the pass is driven by the null shifting
  **down** when site 54 is included (0.3880 → 0.2476), not by raw ρ
  rising (raw ρ actually fell 0.4467 → 0.4018); the excess over null —
  the quantity that matters for a non-centered null — grew **2.63×**
  (0.058660 → 0.154187). The 3-site original failed this same gate
  (p = 0.139786, gate_pass = 0, read from its own CSV).
- What this changes and what it does NOT: §1's L1c
  **COMPARATOR-UNDERPOWERED** verdict and every §2 caveat sentence
  describe the **3-site run as executed** and stand unchanged for it — no
  power analysis was rerun for the four-site design (the authorizing task
  did not request one). The pass adds the first affirmative data point for
  §1/L2's open question ("would this pipeline clear a gate on ANY
  comparator?"): it cleared one, on this comparator, under the same rule —
  n = 1 on the same underlying dataset, so it licenses neither "the
  pipeline has power" as a general claim nor I1's 3-site failure as "the
  pipeline has no power," and it only **partially** unblocks L2a: this is
  **the same comparator corrected (a modification of GB1), not a wholly
  separate dataset**, and must be described that way.
- §3's decision item 2 ("whether to authorize a four-site rerun") is
  hereby **resolved: authorized, run, gate passed** — as a separate
  pre-registered script and output, not a rewrite of the frozen gate.

*DRAFT — appended 2026-09-22 by the site54-and-script50-migration run;
source of record: `docs/tasks/site54-and-script50-migration/MIGRATION_LOG.md`
(entries P1, P2, Q1, Q2). Not merged; the three protected files remain
untouched.*
