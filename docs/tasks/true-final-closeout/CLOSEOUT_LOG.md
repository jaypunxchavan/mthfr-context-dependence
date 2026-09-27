# CLOSEOUT_LOG — true-final-closeout

Session: 2026-09-26, true final closeout (task doc `TRUE_FINAL_CLOSEOUT.md`).

Preamble, stated before any task work:

- Read `AGENTS.md` at the repo root in full first (binding; §0 prime
  directive, §3–§6 statistical conventions, §7 code-safety rules, §9
  planning-docs-are-inputs all apply to this session).
- Read `docs/tasks/true-final-closeout/TRUE_FINAL_CLOSEOUT.md` in full
  before any task work (101 lines).
- This session closes five small items (G1–G5). It does **not** reopen,
  re-run, or re-litigate any conclusion of `DISATTENUATION_LOG.md`'s
  SUMMARY (T1, T5, V1, Y1, Y2, W1, W2, X1, X2, U1 explicitly excluded
  from re-running by the task doc).
- Environment: `venv/bin/python3` only, foreground runs, smoke-then-full
  for anything with a bootstrap (G2 is deterministic — no bootstrap).
- Protected/do-not-touch: `MTHFR_RESULTS_LOG.md`, `AGENTS.md`, and
  `RESULTS.md` **except** its existing "Current State" section, which
  the task doc authorizes this session to hand-edit (second and final
  authorized edit, G5 — to be stated explicitly in that entry).
- Troubleshooting: the decision tree in the task doc (missing package →
  `pip --break-system-packages`; sanity-check fail → STOP/FAIL; missing
  file → `ls`/`find` first, then BLOCKED with the exact path; ambiguity →
  most literal conservative reading + log the assumption; anything else →
  BLOCKED with detail, move to the next independent task).

Entry template (same format as every prior session):

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

Entries begin below.
---
## [G1] — Surface Z3 and Z4 into plain view (pure retrieval, no new computation)

Status: PASS
Time started / finished: 2026-09-26 15:24 / 2026-09-26 15:31
What I did: Read `DISATTENUATION_LOG.md`'s `[Z]` entry in full (L638–688) and the email draft file in full (59 lines). Verified every artifact Z3/Z4 claim exists on disk before quoting (AGENTS §5). Pure retrieval — nothing recomputed, no number generated to fill any gap.

Actual output (real numbers and quoted source text, not a paraphrase):

Disk-verification first (this session, 15:31):
```
-rw-r--r--  1 arnavchavan  staff  4561991 Sep 26 01:31 data/external/clinvar/clinvar_mthfr_esummary.json
-rw-r--r--  1 arnavchavan  staff    63594 Sep 26 01:31 data/processed/task102_clinvar_atlas_overlap.csv
-rw-r--r--  1 arnavchavan  staff     2852 Sep 26 01:35 docs/tasks/disattenuation-and-ledger/EMAIL_DRAFT_nambiar_severity_baseline.md
-rw-r--r--  1 arnavchavan  staff    13484 Sep 26 01:31 scripts/102_z3_clinvar_crossref.py
300 data/processed/task102_clinvar_atlas_overlap.csv
uid,accession,title,classification,class_group,review_status,key,position,esm2_score,esm2_score_a222v_bg,delta_esm,abs_delta_ge_half_sd,abs_delta_ge_1sd,abs_delta_ge_2sd,in_analysis_set
4956128,VCV004956128,NM_005957.5(MTHFR):c.152G>A (p.Arg51Gln),Uncertain significance,primary,"criteria provided, single submitter",R51Q,51,-5.569601211696863,-5.549763601273298,0.0198376104235649,0,0,0,1
```
(300 lines = header + 299 data rows, exactly as the `[Z]` entry states.)

**Z3, quoted exactly as written in `DISATTENUATION_LOG.md`'s `[Z]` entry (L661–676):**

> ### Z3 — ClinVar cross-reference (threshold pre-registered before fetch)
>
> Design in `scripts/102_z3_clinvar_crossref.py`'s docstring, written after only two probe calls (record count 1,078 + one-record schema; no variant-level data, no classifications, no outcomes):
> - **Fetch budget:** 4 NCBI E-utilities requests (1 esearch + 3 esummary batches), all 1,078 MTHFR records taken whole — server-side filters deliberately *not* trusted (probe showed ambiguous errorlist behavior; whole-gene fetch is cheap). Actual: **4,215,521 bytes (4.22 MB)**, saved `data/external/clinvar/clinvar_mthfr_esearch.json` + `clinvar_mthfr_esummary.json`; the script is cache-on-rerun (re-runs refetch nothing).
> - **Threshold (pre-registered):** "meaningfully differently scored" = |delta_esm| ≥ **0.1182** = one population SD of delta_esm over the 11,344-row manifest — source `task_delta_esm_noise_floor.csv` `sd_delta_esm = 0.11821991945148934`, independently recomputed from the manifest identical to 17 digits, both **before** any variant-level fetch; script re-checks at run time and exits if the value moved. Sensitivity counts at 0.5 SD / 2 SD pre-stated, descriptive only. delta_esm = `esm2_score_a222v_bg − esm2_score` is exactly the background-aware minus background-naive score difference for that variant.
> - **Classes (pre-stated):** PRIMARY = VUS ("Uncertain significance") + "Conflicting classifications of pathogenicity" (legacy spelling "Conflicting interpretations of pathogenicity" mapped in advance); CONTEXT = Pathogenic / Likely pathogenic (reported, no decisions attached).
> - **Matching (pre-stated):** parse `p.<WT3><pos><MUT3>` (parentheses tolerated) → 1-letter triple; matched iff the triple is a manifest key, so transcript/isoform numbering mismatches fail to match and are counted, never silently dropped.
>
> Filtering accounting (every step's n): 1,078 fetched → classes 315 primary / 205 context / 558 other → 763 without a parseable missense p. change (verified separately: includes exactly **51 nonsense `p.*Ter`**) → 315 parseable missense → **299 match the atlas manifest** (wt+pos+mut exact).
>
> Answer at the pre-registered threshold:
> - **VUS + conflicting in our measurement set: 236 → 34 with |delta_esm| ≥ 0.1182 (1 SD)** — plus 97 at ≥0.5 SD, 5 at ≥2 SD.
> - Context P/LP in our set: 29 → **7 ≥ 1 SD**.
> - Largest primary-class shifts: V194L (VUS, delta_esm **+1.2512** ≈ 10.6 SD), A220V +0.6883, V218L +0.3928, T227K +0.3056.
> - Saved: `data/processed/task102_clinvar_atlas_overlap.csv` (299 rows).
> - Disclosed limits (printed by the script): classification is submitters' criteria, not our data; non-match ≠ absent from ClinVar (numbering/isoform or non-missense); the threshold says the background choice moves the score by ≥1 SD — it does **not** say which score is right.

**Z4's `[Z]` entry section, quoted exactly as written (L678–679):**

> ### Z4 — email drafted and saved, not sent
> `docs/tasks/disattenuation-and-ledger/EMAIL_DRAFT_nambiar_severity_baseline.md` — asks the exact two-way question (run-and-not-reported vs genuinely-not-considered), states we accept either answer, discloses precisely what we searched (preprint PDF zero-hit list + released-repo zero-hit terms). **Not sent** — no mail was transmitted by this session.

**Z4's actual drafted email content, quoted verbatim from the file (the deliverable itself, still unsent):**

> **Status: DRAFT ONLY — NOT SENT.** Written 2026-09-26 per task Z4: "Draft an
> email asking their corresponding author... was it run and not reported, or
> genuinely not considered? We will accept either answer." Nothing in this
> repository transmits mail; this file is the deliverable.
>
> To: (corresponding author, preprint `2025.09.14.676130` — fill in name/address)
> Subject: One control question about your MTHFR epistasis preprint
>
> Dear Dr. Nambiar and colleagues,
>
> I'm writing about your preprint on epistasis in MTHFR (2025.09.14.676130).
> We have been reproducing and extending some of your comparisons against the
> Weile et al. MTHFR deep-mutational-scan fitness data, and one question came
> up that we thought it was better to ask you directly rather than characterize
> in a write-up.
>
> Did your analysis include a severity-only baseline — a predictor built only
> from single-mutant effects (for example a site-independent or additive
> severity score, no pair-specific terms) — when evaluating how well the
> epistasis models perform? We ask because a monotone severity-to-fitness
> relationship mechanically induces a positive correlation between such a
> predictor and measured epistasis, so without that control it is hard to tell
> how much of the reported agreement reflects pair-specific interaction signal
> rather than severity structure alone.
>
> To be completely clear about what we are asking: either answer is fine with
> us.
>
> - If such a control was run and simply not reported, we would be glad to cite
>   the number if you can share it (or point us to where it appears).
> - If it was genuinely not considered, that is entirely understandable — we
>   would simply describe the control as not part of the published analysis
>   rather than speculate about it either way.
>
> For transparency, we searched the preprint (main text, methods, supplement)
> and the released `maslov-group/Epistasis` repository and found no
> severity-only baseline, which is exactly why we would rather hear the answer
> from you than state a negative as established fact.
>
> Thank you for your time — and for releasing the code, which made our
> reproduction considerably easier.
>
> Best regards,
> (name)
> (affiliation)

Verdict: **Z3 is a real, completed result — not a blocked task wearing a "Completed" label.** The ClinVar number exists on disk in three places (script output recorded in the `[Z]` entry, the 299-row CSV, the frozen 4.56 MB raw JSON); the headline finding is **34 of the 236 VUS/conflicting ClinVar MTHFR variants in our measurement set are scored ≥1 background-SD differently (|delta_esm| ≥ 0.1182), plus 7 of 29 pathogenic/likely-pathogenic**. Z4 is a real, saved, unsent draft whose full text is now surfaced above. Nothing needed to be — or was — generated to fill a gap.
Files created/modified: `docs/tasks/true-final-closeout/CLOSEOUT_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- The email's `To:` line is intentionally blank (no address was ever fetched — drafting was the whole task); if anyone sends it later, the recipient must be filled in by a human.
- The `[Z]` entry's own disclosure still applies verbatim: the 1,078-record ClinVar count is a 2026-09-26 snapshot; the cached JSON is the frozen evidence for 236/34.
---
## [G2] — AC3's exact precision/hardware grid run on the five ESM-1v members (closes the "unverified by analogy" gap)

Status: PASS
Time started / finished: 2026-09-26 15:32 / 2026-09-26 19:10

What I did:
1. **Design phase (15:32–15:44), reading before writing:** read `scripts/75_numerical_precision_rescore.py` in full (AC3's machinery: `batched_odds`/`score_deltas`/`mask_at`/`spearman`, conditions C0 fp32-b1 / C1 fp32-b8 / C2 fp32-b16 / C3 fp64-b8 forced CPU, thresholds G1 1e-5 / R1 1e-3 / R2 0.01, subset convention `default_rng(0).choice`), `scripts/86_ac4_esm1v_five_members.py`'s producer (`masked_marginal_tf` L258–272: HF `EsmForMaskedLM facebook/esm1v_t33_650M_UR90S_{k}`, batch 1, fp32, mps-preferred device; `delta = av_logodds − wt_logodds` L344; `hf_fetch` download+size-gate+md5 discipline L223–255) and `scripts/lib/esm_scoring.py`.
2. **Pre-write probes (no rescore values existed):** fair-esm `Alphabet.from_architecture("ESM-1b")` batch-converter token ids are **identical** to the HF esm1v tokenizer's `input_ids` on a 106-token probe (33-token vocab, mask id 32); position 222 has **0 rows** in script 75's pool; the N=100 sample joins the member CSVs **100/100 with 0 NaN** for all five members.
3. **Wrote `scripts/103_g2_esm1v_precision_grid.py`** with the design pre-registered in its docstring: what is reused **by import, verbatim** (script 75's functions + conventions via importlib — its `__main__` guard makes module loading side-effect-free; script 86's `hf_fetch`; lib's `get_position_logprobs`) vs. what is new (an ~8-line `HFAdapter` that lets a Transformers model answer script 75's fair-esm call signature, pass-through only; a **TOK gate** — fair-esm vs HF token ids must match on *every* sampled masked sequence, can only block a wrong PASS; data-prep and tier-decision lines re-derived from script 75's `__main__` because they cannot be imported). **N_RESAMPLE default 100** pre-registered as a timing decision (AC3's measured N=500 cost 6025 s/member → ~8.4 h for five members; N=100 → ~100 min; N=100 is also AC3's own fp64 tier-(b) size); tolerances unchanged; reduction rule stated (only on timing, only before any R1/R2 value).
4. **SMOKE=1 run (15:40, 202.6 s):** member 1 fetch + TOK + G1 + timing projections only; weights kept for the full run.
5. **Full run = 3 invocations** (the first two tool executions were **aborted** by interrupts; checkpointing preserved all progress — `task_G2_state.json` + per-member CSVs, written after every 50-row chunk): inv 1 (~15:47) completed member 1 and member 2's fp32 arms; inv 2 (~17:24) completed member 2's fp64 arm, members 3 and 4 entirely, and began member 5's fetch; inv 3 (18:46:20 → 19:08:45, **exit 0**, total runtime 1305.3 s) resumed member 5 from the 44 KB partial fetch, completed it, and ran all comparisons/verdict. On resume, members 1–4 printed "ALL FOUR ARMS COMPLETE … skipped (no download, no scoring)" — no re-download, no re-scoring.

Actual output (real numbers and quoted source text, not a paraphrase):

Smoke (member 1, captured):
```
[AC4] disk before fetch: avail=21,657,698,304 B (20.17 GiB); required >= 3,683,345,165 B
[AC4] fetch done in 93s
[AC4] size gate OK: 2,609,603,341 B == EXPECTED_BIN
[AC4] md5(pytorch_model.bin) = 29521fcaadd7b240d5c15d18b8a531ac
TOK gate (member 1): 200 sampled masked sequences, fair-esm-vs-HF id mismatches = 0 (threshold 0)
G1 identity gate (batched CPU fp32 vs lib get_position_logprobs, 10 variants x 2 ctx): max|diff| = 4.768e-07  (threshold 1e-5)
TIMING SMOKE (fp32, batch 8, n=8): 1.421 s/variant -> projected C0+C1+C2 at N=100 = 426 s (cap 7200)
PROJECTION at N=100: fp32 arms 426 s + fp64 608 s = 1034 s/member (17.2 min) -> x5 members = 86 min of scoring
```
(N=100 kept: 86 min < the pre-registered 2.5 h reduction trigger.)

Member 5, invocation 3 (captured; members 2–4's equivalent lines were printed in the two aborted invocations — see flagging note below):
```
[AC4] fetch done in 112s
[AC4] size gate OK: 2,609,603,341 B == EXPECTED_BIN
[AC4] md5(pytorch_model.bin) = 3cdccbe311c06a1db6d22e7169570ef1
TOK gate (member 5): 200 sampled masked sequences, fair-esm-vs-HF id mismatches = 0 (threshold 0)
G1 identity gate (...): max|diff| = 4.396e-07  (threshold 1e-5)
C0_fp32_b1: 157.0 s (1.570 s/variant) | C1_fp32_b8: 143.5 s (1.435 s/variant) | C2_fp32_b16: 163.1 s (1.631 s/variant)
fp64 tier (a): FULL N | C3_fp64_b8: 612.5 s (n=100)   [fp64 6.398 s/variant, fp64/fp32 = 4.12x]
member 5: staged weights deleted (one-member staging discipline)
```

Final comparison block (verbatim, all five members × four conditions; sample baselines explicitly labeled in the output as SAMPLE baselines, not the published full-set rhos):
```
member 1: Spearman(cached, own_e_b) on these 100 rows ... = -0.055278
  C0_fp32_b1: max|d-cached| = 4.517e-05  median = 5.275e-06  rmse = 1.381e-05 | rho(own_e_b) = -0.0553  n_ok = 100/100 | paired |d rho| ... = 0.0000 | R1 PASS (<=1e-3), R2 PASS (<=0.01)
  C1_fp32_b8: max|d-cached| = 4.517e-05 ... R1 PASS, R2 PASS
  C2_fp32_b16: max|d-cached| = 4.517e-05 ... R1 PASS, R2 PASS
  C3_fp64_b8: max|d-cached| = 3.773e-05 ... R1 PASS, R2 PASS
member 2: ... = -0.152441
  C0/C1/C2: max|d-cached| = 6.086e-05, paired |d rho| = 0.0003 | R1 PASS, R2 PASS (all three)
  C3_fp64_b8: max|d-cached| = 7.020e-05 ... R1 PASS, R2 PASS
member 3: ... = +0.094727
  C0/C1/C2: max|d-cached| = 3.778e-05, paired |d rho| = 0.0000 | R1 PASS, R2 PASS
  C3_fp64_b8: max|d-cached| = 3.107e-05 ... R1 PASS, R2 PASS
member 4: ... = +0.003840
  C0/C1/C2: max|d-cached| = 3.193e-05, paired |d rho| = 0.0000 | R1 PASS, R2 PASS
  C3_fp64_b8: max|d-cached| = 3.880e-05 ... R1 PASS, R2 PASS
member 5: ... = -0.060451
  C0/C1/C2: max|d-cached| = 5.244e-05, paired |d rho| = 0.0000 | R1 PASS, R2 PASS
  C3_fp64_b8: max|d-cached| = 5.966e-05 ... R1 PASS, R2 PASS

R1 (value, all 20 member-conditions <= 1e-3): PASS
R2 (finding, all 20 paired |rho shifts| <= 0.01): PASS
G2 VERDICT: PASS -- all five ESM-1v members' cached deltas reproduce under the same
CPU / fp32-b1 / fp32-b8 / fp32-b16 / fp64-b8 grid to the same tolerances the original
ESM-2 check used (G1 + TOK + R1 + R2; thresholds 1e-5 / 1e-3 / 0.01 unchanged).
```
Margins: worst R1 across all 20 = **7.020e-05** (member 2, C3) = 14× inside 1e-3; worst paired |Δrho| = **0.0003** = 33× inside 0.01. G1 gates captured: 4.768e-07 (member 1), 4.396e-07 (member 5).

**Column-identity verification (AGENTS §5, run after the verdict because C0/C1/C2 printed identical values):**
```
G2: member k: C0==C1 True | C1==C2 True | C0==C3 False | max|C0-C1| 0.000e+00 | max|C0-C3| 3.362e-05..5.645e-05  (all five members)
AC3's own CSV (cross-check): AC3: C0==C1 False | C1==C2 True | C0==C3 False | max|C0-C1| 7.629e-06 | max|C1-C2| 0.000e+00 | max|C0-C3| 1.050e-04
AC3 C0: max|d-cached| = 1.132e-04 | C1: 1.122e-04 | C2: 1.122e-04 | C3: 8.940e-05
```
Verdict on the suspicion: **not a column-copy bug.** Three independent facts prove each arm scored separately: (a) three different wall times for the three fp32 arms (157.0 / 143.5 / 163.1 s); (b) the fp64 column differs from every fp32 column (≤5.6e-5) — a copied column could not do that; (c) AC3's own historical CSV, produced by the sibling machinery, shows `C0≠C1` by 7.6e-6 while `C1==C2` exactly — i.e., this exact code shape demonstrably produces distinct arrays when the arithmetic differs. The honest reading: on this machine's CPU the HF forward gives **bitwise-identical per-row results across batch sizes 1/8/16** (G2), and fair-esm did so only for batch 8 vs 16 with a one-ulp batch-1 difference (AC3). Batch-invariance here is a measured property of the kernels, not an artifact of my code.

Verdict: **PASS.** G2a answered directly: all five ESM-1v members' cached deltas reproduce under AC3's exact four-condition grid to AC3's exact tolerances (G1 1e-5 — captured values ~4.4–4.8e-07; R1 ≤1e-3 — worst 7.02e-05; R2 ≤0.01 — worst 0.0003), with a new TOK gate (0/200 mismatches per member) proving the tokenizer identity the comparison silently assumed. The "unverified by analogy" flag on the five-member precision can now be closed: it is verified directly.

Files created/modified:
- `scripts/103_g2_esm1v_precision_grid.py` (created; reuse-by-import driver with pre-registered docstring)
- `data/processed/task_G2_state.json`, `data/processed/task_G2_member{1..5}_rescore.csv`, `data/processed/task_G2_esm1v_rescore.csv` (500 rows — the combined deliverable)
- `docs/tasks/true-final-closeout/CLOSEOUT_LOG.md` (this entry)

Anything unexpected or worth flagging:
- **Two tool executions were aborted mid-run** (invocations 1 and 2, `{"error":"aborted"}`); the chunk-level checkpointing (state JSON + per-member CSVs written every 50 rows, script 75's own discipline) preserved every completed arm and the resume path re-verified cleanly. Logged because a lost run is otherwise invisible.
- **G1/TOK gate values for members 2–4 were printed only in the two aborted invocations, whose stdout was lost with the aborts.** Their PASS is established structurally, not by observation of the number: both gates `sys.exit(1)` *before any arm runs*, and members 2–4 each have all four arms at 100/100 coverage. The numeric max|diff| values for members 2–4 are **unavailable and are not being invented** — only members 1 and 5 have quoted numbers.
- `transformers` printed a LOAD REPORT (contact-head weights MISSING) on every member load: harmless — the contact regression head is never used for deltas (script 86 saw the same); noted because an unexplained warning should not be silently swallowed.
- Member weights no longer existed anywhere (script 86 deleted its staging; the HF hub cache held only empty refs), so all five were **re-downloaded** (93–112 s each for 2,609,603,341 B, size gate + md5 recorded above) under script 86's one-member-at-a-time disk gate; the staged copies were deleted after each member completed, leaving only the KB-scale tokenizer files in the HF cache.
---
## [G3] — Reconcile the two still-unaddressed dropped findings in writing (G3a H1a-reversal, G3b additive-null MAE) + fix K12/K21 inside DISATTENUATION_LOG (G3c)

Status: PASS — both reconciliation paragraphs written and every number on both sides verified at its deepest source; G3c's two corrections applied and re-verified; one NEW provenance failure discovered during the check and disclosed below (flagged, not edited — outside G3c's authorization).
Time started / finished: 2026-09-26 19:11 / 2026-09-26 19:30

What I did:
1. **G3a/G3b number-gathering (19:11–19:25), reading before writing.** For G3a, fresh deep-source reads: `SESSION_LOG.md` L2704/L2746/L2768/L3006 (W3's M1d/M1e), `FOLLOWUP_LOG.md` L348/L357/L363/L575 (9-background M1d/M1e), `DISATTENUATION_LOG.md` [T] L316–400 (T1a five-member rhos, T1b/T1c model-card facts, T2a Spearman–Brown, T4a pooled-vs-within, T5a the 10.46× table) and its SUMMARY L710–723; `ls ~/.cache/torch/hub/checkpoints/` to confirm which same-corpus ESM-2 sizes actually exist locally before naming them as possible tests (esm2_t30_150M_UR50D.pt 592,774,773 B; esm2_t33_650M_UR50D.pt 2,604,537,549 B; esm2_t36_3B_UR50D.pt 5,678,116,398 B — all present). For G3b: full print of `data/processed/task34_additive_null.csv` (the producing artifact, 14 rows), `MTHFR_RESULTS_LOG.md` L211–252 (§6.1–6.4 verbatim), `OVERNIGHT_LOG.md` L465 (C1d ρ = 0.999636), L563/L566 (C2c), L619/L623/L645 (C3a ceiling), L904/L932/L950 (D1b, mean SE 0.1166 → 0.0788), L1413/L1428/L1871 (H4a), and `DISATTENUATION_LOG.md` L286–292 (S2b-ii/iii prior status).
2. **Wrote the two paragraphs** (G3a below, G3b below) with every figure traceable to the fresh reads; no figure quoted from memory.
3. **G3c applied** (six edits, all in `DISATTENUATION_LOG.md`, all re-verified by grep afterward — output quoted below).
4. **Discovered during step 1** a new provenance failure in `DISATTENUATION_LOG.md` L290 (the prior session's own S2b-iii verification line) — see "Anything unexpected" for the full evidence trail.

### G3a — the H1a-reversal finding vs. the later reliability findings (the deliverable paragraph)

> The H1a-reversal finding does not survive untouched, is *not* contradicted by the reliability findings, and must now carry an explicit single-checkpoint caveat — that is the honest three-part answer, and the seed-stability sub-question is an open reconciliation that cannot be closed with the artifacts that exist. Both sides operate on the same quantity, `delta_esm` (A222V-background minus WT-background score), so the reliability evidence bears directly on the residual's raw material: across the five ESM-1v checkpoints, cross-seed agreement on deltas is only **+0.084365** [+0.052159, +0.122589] pooled (**+0.050813** [+0.030455, +0.065259] within-position) versus **+0.882637** [+0.869559, +0.891790] on raw WT-background scores — a 10.46× gap with CIs nowhere near each other, "the disagreement is introduced almost entirely by the subtraction across backgrounds" (T5a) — and the per-seed delta-vs-own_e_b correlation flips sign across members (**[−0.040820, +0.013434]**, mean −0.015588, all |ρ| ≤ 0.041), establishing that a shift pattern computed from single-checkpoint deltas is weakly seed-reproducible by default. The W3 finding itself — **+0.02121 [+0.00465, +0.03934]** at 31 backgrounds/120 positions, CI excluding 0 from above, versus **+0.00954 [−0.00573, +0.02640]** at 9 backgrounds, CI containing 0; the generic severity→shift relation it is a residual of holding at −0.466667 [−0.583333, −0.066667] and −0.519 [−0.635, −0.388] respectively — was computed on **one ESM-2 checkpoint**, and its position-cluster CI quantifies position-sampling uncertainty *conditional on that checkpoint*: the design has no seed axis, so "CI excludes 0" never covered checkpoint variation. But the demonstrated instability cannot overturn it either: that instability was measured entirely inside the ESM-1v seed family, and T1's verdict (ESM-2 = UR50/D 2021_04; ESM-1v = UR90/S 2020_03 — "different corpora, different runs, separate releases") explicitly blocks transferring its magnitude onto ESM-2 as a number ("an assumption, not a licensed inference"). The finding therefore stands as a within-checkpoint result, replicated across its design axis (9 → 31 backgrounds, CIs overlapping over [0.0047, 0.0264] — "resolution, not reversal" — with the supporting M1e relation strengthening from −0.467 to −0.519) but **unverified, and within ESM-2 unverifiable, across seeds**: ESM-2 has only one checkpoint, so no within-family seed test exists to run. The nearest runnable tests — re-running W3's exact 31-background design on the same-corpus ESM-2 sizes (t30_150M and t36_3B, both present in the local torch cache, verified by ls) or on ESM-1v's five-member ensemble — would each be cross-model evidence about the design's generalizability, not a seed test of this checkpoint, and neither was run this session. **This remains an open reconciliation** in exactly that sense: not a contradiction, not a clean pass — with the honest status sentence "verified across backgrounds and positions on one checkpoint; unverified across seeds." G2's precision-grid PASS (all five members' deltas reproduce: G1 ≤ 4.77e-07, worst R1 7.020e-05 ≤ 1e-3, worst paired R2 0.0003 ≤ 0.01) confirms the deltas' *numerical reproducibility*, which must not be conflated with seed stability — the axis G2 did not and could not test.

### G3b — the additive-null MAE finding vs. the later reliability findings (the deliverable paragraph)

> The additive-null MAE finding stands as a descriptive statistic for this checkpoint — re-verified under three independent robustness axes — but it carries the same single-checkpoint caveat, its ESM-2-specific framing remains subordinated exactly as the corrected conclusion already says, and one head-on link remains genuinely uncomputed. The finding, checked at source: in the highest-interaction stratum ESM-2's MAE exceeds the no-interaction baseline by **+0.00241 [+0.00155, +0.00321]** (n = 3,586 / 609 positions; null MAE 0.2481 vs ESM-2 0.2505) — stratum-specific, not universal: the low stratum favors ESM-2 (−0.00317, CI excluding 0) and the mid stratum crosses zero — and the verdict re-verifies under squared loss (C2c: **+0.002320 [+0.001740, +0.002895]**, within 4% of the MAE value), under an EB-shrunken stratifier that purges the high stratum's high-SE enrichment (D1b: **+0.001851 [+0.000987, +0.002706]**, mean SE 0.1166 → 0.0788), and at low folinate (H4a: **+0.00227 [+0.00144, +0.00308]**, positive at all four folinate conditions) — all excluding zero in the same direction, with §6.4's calibration asymmetry making the loss conservative: ESM-2's predictors were calibrated directly against the true target while the null's were transformed from WT fitness, "a more conservative bar that ESM-2 still failed to clear." The reliability side enters through two doors. First, it was already built into the reference: C3a's reliability-limited oracle (rel = 0.636, from r_own = 0.636328) beats the multiplicative null by **+0.0521 [+0.0436, +0.0613]** in the same high stratum, and against that ceiling ESM-2 does not merely fall short but moves the wrong way — **−4.62% of the available headroom** (−0.002409 while +0.0521 was on offer; +0.84% pooled). Second, T5's 10.46× gap (+0.882637 cross-checkpoint agreement on raw scores vs +0.084365 on deltas) identifies the background subtraction itself as the system's weakly reproducible component — a plausible mechanism for why adding true-background information fails to help exactly where interaction is strongest, consistent with the corrected conclusion's subordination of these findings to "a property of how well any WT-arm-informed signal predicts an A222V-arm-derived target, which is close to tautological once seen clearly." What has never been computed is the causal link: no reliability-round entry re-ran any MAE statistic (the prior session stated this itself), so nothing tests whether the delta's cross-checkpoint instability *explains* the high-stratum loss — and T1 blocks assuming ESM-2's instability magnitude from ESM-1v's. Magnitude honesty belongs in the same breath: ρ(S_A222V, S_WT) = 0.999636, so the MAE story rests on a small number of rank swaps, and +0.00241 is under 1% of the high stratum's baseline MAE. **Verdict: the finding survives, weakened-as-ESM-2-specific exactly as already written down, carrying the single-checkpoint caveat; whether seed-instability causes the MAE loss is a real open item settleable only by a new test (per-stratum MAE for each of ESM-1v's five members — itself cross-model under T1). This too remains an open reconciliation — stated, not papered over: every verified number on both sides is consistent with every other, no result contradicts another, but the head-on link has never been computed.**

### Number checks — both sides, at deepest source (verbatim outputs)

G3a side, finding (fresh reads): `SESSION_LOG.md` L2746 `M1d residual +0.02121 CI [+0.00465, +0.03934] -> CI excludes 0`; L2704 `M1e — Spearman rho = −0.519, CI [−0.635, −0.388]`; `FOLLOWUP_LOG.md` L348 `residual test (r = +0.00954, CI [−0.00573, +0.02640] contains 0 ... rank 6/9`; L357 `Spearman ρ = −0.466667, 95% cluster CI [−0.583333, −0.066667] — excludes 0`.
G3a side, reliability (fresh reads, [T]): L316–317 `Five ESM-1v member rhos: −0.020573, −0.040820, +0.013434, −0.026572, −0.003409 ... mean −0.015588 ... range [−0.040820, +0.013434]`; L328–329 `ESM-2 is a different corpus snapshot (UniRef50 vs UniRef90, 2021_04 vs 2020_03 ...) ... borrowing r_delta = 0.084365 across the family boundary is an assumption, not a licensed inference`; T4a table `POOLED +0.084365 [+]0.052159, +0.122589] | WITHIN-position +0.050813 [+0.030455, +0.065259] | BETWEEN-position +0.099947`; T5a table `RAW ... +0.882637 [+0.869559, +0.881465, +0.891790] | DELTAS +0.084365` with `Ratio 10.46×`; T2a `rho = −0.028508 ... against the Spearman-Brown-predicted ~−0.030 — the prediction holds`.
G3b side, finding (fresh reads): `task34_additive_null.csv` rows — `paired_mae vs multiplicative null: −0.000308 [−0.001024, +0.000431] INDISTINGUISHABLE`; `vs additive null: −0.008714 [−0.013856, −0.003608] ESM-2 LOWER error`; `vs ESM-2(WT bg): +0.000533 [+0.000288, +0.000768] ESM-2 HIGHER error`; `gi_low −0.003166 [−0.004181, −0.002154]`; `gi_mid −0.000109 [−0.001073, +0.000875]`; `gi_high +0.002409 [+0.001551, +0.003208] mae_null 0.248135 mae_esm 0.250544`; `MTHFR_RESULTS_LOG` §6.4 `It still lost in the high stratum ... a more conservative bar that ESM-2 still failed to clear`; OV L566 `high-stratum diff is +0.002320 with CI [+0.001740, +0.002895] ... within 4% of the MAE diff`; OV L904 `under EB-shrunken |e.b| terciles the high-stratum MAE diff is +0.001851 with CI [+0.000987, +0.002706] ... mean SE falls from 0.1166 to 0.0788`; OV L1413 `HIGH@12 ... diff=+0.00227 CI=[+0.00144,+0.00308] -> ESM-2 WORSE`; OV L645 `a reliability-limited oracle (rel 0.636) beats the multiplicative null by +0.0366 pooled ... and by +0.0521 in 6.3's high stratum, CI [+0.0436, +0.0613] ... in the HIGH stratum ESM-2 moves the WRONG WAY for −4.62% of the ceiling`; OV L465 `rho = 0.999636 (n=10,757) → log 6.2's MAE difference ... rides on a predictor pair that is 0.9996 rank-identical`; `DISATTENUATION_LOG` L345 `G5 r_own = 0.6363276`.

### G3c — the two authorized corrections, applied

1. **K12** (ledger row): `vs original +0.0154 [+0.0039, +0.0271]` → `vs original +0.0154 **[−0.0166, +0.0465]** *(CI corrected in place 2026-09-26, true-final-closeout G3c: the prior [+0.0039, +0.0271] exists in no source — DEEPDIVE L2327–2336, RELIABILITY L1036/L1069, script 96's docstring, and script 96's G2 fresh reproduction all say [−0.0166, +0.0465])*` — verified by grep: the row now reads `[−0.0166, +0.0465]`.
2. **K21** (ledger row): label `AD6 depth × interaction_D pooled` → `AD6 **rho(yE, Neff)** *(label corrected in place 2026-09-26, G3c: was "AD6 depth × interaction_D pooled" — wrong statistic; yE = position-mean |delta_ESM|, DEEP L2701/L2731/L2743)*`, status `**not re-read this session**` → `**fresh-verified** — CI [+0.091832, +0.247059] matches the logged CI to 4 dp (closing the old "not re-read this session"); AD6's actual depth × interaction_D statistic is yT3 = mean|interaction_D|: rho **−0.0211 [−0.1034, +0.0584]**, null — do NOT quote K21's number as "interaction tracks depth"`; its `586/62` n-column kept with the `/62` unverified-flag carried into the row (only the label/statistic was authorized for correction).
3. **Now-stale disclosures updated** so the file does not contradict itself: L527's `(flagged, not edited)` → `(originally flagged, not edited — corrected in the ledger row on 2026-09-26 by true-final-closeout G3c)`; L592's `(flagged, not edited)` → `(flagged here; label corrected in the ledger row on 2026-09-26 by true-final-closeout G3c)`; the SUMMARY's conflicts header → `(K12/K21 corrected in place 2026-09-26 by true-final-closeout G3c; the remaining conflicts still flagged, not edited; ...)` and its two bullets rewritten to `K12 — CORRECTED in place 2026-09-26 (G3c)` / `K21 — label CORRECTED in place 2026-09-26 (G3c)`. The third conflict bullet (`MTHFR_RESULTS_LOG.md` §5.2 label; `RESULTS.md` L150 "0.983") untouched — not authorized.

Verdict: **PASS.** G3a and G3b are written, each ending in an explicitly-stated open reconciliation rather than manufactured certainty (G3a: single-checkpoint caveat required, not contradicted, seed-stability untestable within ESM-2; G3b: finding stands, causal link uncomputed); every figure in both was re-read at its deepest source this session; G3c's two corrections are applied and grep-verified.

Files created/modified:
- `docs/tasks/true-final-closeout/CLOSEOUT_LOG.md` (this entry)
- `docs/tasks/disattenuation-and-ledger/DISATTENUATION_LOG.md` (G3c: ledger rows K12/K21, the two discovery-flag lines, and the SUMMARY conflicts header + two bullets — six edits, all verified)

Anything unexpected or worth flagging:
- **NEW provenance failure, discovered by G3's check, flagged NOT edited:** `DISATTENUATION_LOG.md` L290 (the prior session's own S2b-iii verification line) contains three statements that fail verification against its own cited source and against the whole repository: (a) *"ESM-2's MAE higher than the no-interaction baseline in **every** stratum"* — contradicted by the very table it cites (§6.3 low stratum: `MAE(null)=0.2153 MAE(ESM-2)=0.2121 diff=-0.00317 → ESM-2 better (CI excludes 0)`; OV L566 `low: ESM better, CI excludes 0 under both`); (b) *"own-side +0.00446–+0.00866"* — this figure appears **nowhere in the repository except that one line** (checked: full-text grep of `docs/` and `scripts/` for `0.00446`, `0.00866`, `own-side` → single hit = L290; `data/processed/` grep → only coincidental per-variant float substrings; §6.2's actual own-side row in `task34_additive_null.csv` is `+0.000533 [+0.000288, +0.000768]`); (c) *"the floor-vs-baseline difference also excludes 0 (−0.000767)"* — also unique to L290 (grep `0.000767`, `floor-vs-baseline` across docs/scripts → only L290 among findings; the only 0.000767-shaped figure in the project is the own-side CI **upper bound**, sign-positive: `+0.0007675630167030905` in OV/DIGEST/SESSION). L290's cited location `MTHFR_RESULTS_LOG L246–249` is in fact §6.4's calibration-asymmetry prose, not a numbers table. **Action:** both figures excluded from G3b; only verified counterparts quoted; L290 flagged here and in the final SUMMARY. Not edited — G3c authorizes only K12/K21. **Any future session must not cite `+0.00446–+0.00866` or `−0.000767`; the verified own-side figure is +0.00053 [+0.00029, +0.00077], and the stratum pattern is high-worse / low-better / mid-crossing, not "every stratum".**
- These two figures had also propagated into this closeout's inherited prior-session summary context; the check against `MTHFR_RESULTS_LOG`'s actual §6.2/6.3 tables is what caught them. Recorded because it is direct evidence for AGENTS §5's "verify column/figure identity before reporting agreement between two sources."
- The torch-hub cache holds all three same-corpus ESM-2 sizes (t30_150M, t33_650M, t36_3B) plus esmfold_3B_v1 — so G3a's named "nearest runnable test" is locally executable in principle; it was **not** run (new analysis, outside this session's five tasks).
---
## [G4] — Commit the final write-up permanently (confirm existence, committed state, canonical status; resolve the phantom-"v3" block)

Status: PASS — no commit required: `git show --stat` verifies the file was already committed before any G-task work completed (checked, not assumed).
Time started / finished: 2026-09-26 19:30 / 2026-09-26 19:35

What I did, with actual output:
- `ls docs/writeups/` → `PROJECT_SUMMARY_FINAL.md`; `wc -l` → **325 lines**; header verbatim: `# Context-Dependent Variant Effects in MTHFR: Project Summary (Final)`, opening `*This version supersedes all prior drafts. Every number below was verified against its primary source — code, a live-fetched model card, or a directly cloned paper repository — in the round that produced it, not copied forward from an earlier summary.*` Its one-paragraph version leads with this round's own headline: `**five identically trained instances of a related model agree almost perfectly (ρ = 0.88) on what a variant's raw score is, and barely at all (ρ = 0.084) on how that score changes when a genetic background is added — a 10.5-fold gap.**`
- **Committed state (verified via `git show --stat`, per AGENTS §7):** `git ls-files docs/writeups/` lists `docs/writeups/PROJECT_SUMMARY_FINAL.md` (tracked), and HEAD commit `ab3c87f` — *"Add final project summary and true final closeout task doc"*, Sat Sep 26 15:21:57 2026 -0400 — shows `.../true-final-closeout/TRUE_FINAL_CLOSEOUT.md | 101 +++++` and `docs/writeups/PROJECT_SUMMARY_FINAL.md | 325 +++++++++++++++++++++`, `2 files changed, 426 insertions(+)`. The file was therefore committed before any G-task work completed (G1 finished 15:31), and **G4a's commit action is a no-op — no git command was needed or run.**
- **Canonical status:** repo-wide grep for `PROJECT_SUMMARY_FINAL` in `*.md` returns only the task doc's own references (G4a/G5a) — nothing in the repo's content layer pointed at it until this session; G5's RESULTS.md Current State update (next entry) adds exactly that front-door pointer. Confirmation for future sessions: **"the project's final write-up" = `docs/writeups/PROJECT_SUMMARY_FINAL.md` (325 lines, committed in ab3c87f)** — cite it by that path, never by an earlier draft name.
- **G4b — explicit confirmation:** the prior session's BLOCKED item — *"the referenced `v3` does not exist anywhere in this workspace"* (S1c/S2c searches) — is **permanently resolved in its practical sense; no future session should search for a phantom "v3" again.** Stated precisely: no file named `v3` was ever found and none exists (those search records stand as written); what existed was a missing *final write-up to point at*, and that now exists under a real, committed name. The only residual is the literal outside-repo case — the replacement sentence for wherever "v3" actually lives outside this workspace remains supplied verbatim at `DISATTENUATION_LOG.md` L297 for the user to apply — but nothing inside this repo requires a "v3" to exist.
- **AGENTS §9 tension (recorded, per rule):** a planning document instructing a git commit would normally require authorization beyond the doc itself; the user directed this G4 commit explicitly in-session, which is the authority acted on. In the event, no commit was performed (ab3c87f already contains the file), so the tension is recorded for the record rather than exercised.

Verdict: **PASS** — exists ✓, committed ✓ (verified by commit stat), canonical ✓ (and made reachable from RESULTS.md in G5), phantom-"v3" block explicitly resolved ✓.

Files created/modified:
- `docs/tasks/true-final-closeout/CLOSEOUT_LOG.md` (this entry only — no git action taken)

Anything unexpected or worth flagging:
- `ab3c87f`'s timestamp (15:21:57) shows the human placed and committed both the write-up and this task doc at session launch — G4's anticipated commit had already been done before the task ran. Reported as a no-op rather than re-committed, and HEAD was re-checked (`git log --oneline -3`) before asserting it, since a parallel session had moved HEAD during this round.
---
## [G5] — RESULTS.md "Current State" section refresh (the second and final authorized hand-edit)

Status: PASS — section replaced in place; `git diff` proves a single hunk confined to the section; nothing below `## Standing of each claim` touched.
Time started / finished: 2026-09-26 19:35 / 2026-09-26 19:39

**Authorization statement (G5b, stated as required): this is the SECOND and FINAL authorized hand-edit to `RESULTS.md`, executed under the same direct out-of-band user authority as the first one (the "Current State" section added 2026-09-25, logged in `docs/tasks/reliability-and-decompositions/FINAL_CLOSEOUT_LOG.md` [X3]). The standing AGENTS §7 conflict is flagged once more and NOT resolved: §7 says this file is `scripts/22_update_writeup.py`'s output and must never be hand-edited — this edit was made under explicit instruction beyond the planning doc, is recorded inside the section's own provenance note (which now covers both edits), and re-running script 22 would regenerate the file and drop the section. `AGENTS.md` is NOT edited; the conflict stands, exactly as G5b directs. After this edit, no further hand-edit to RESULTS.md is authorized or will be performed.**

What I did:
1. Located the target: header at `RESULTS.md` L5, section content L5–9 (header line + provenance note + one long body paragraph); the next section `## Standing of each claim` begins at L11. File = 166 lines before, 170 after.
2. Replaced file lines 5–9 **only**, using `venv/bin/python3` with boundary assertions that abort before writing if they fail: `assert lines[4].startswith("## Current State (as of 2026-09-25)")` and `assert lines[10].startswith("## Standing of each claim")` — both passed; everything from old L10 on was concatenated back verbatim.
3. Verified with git (strongest available check): `git diff --numstat RESULTS.md` → `7	3	RESULTS.md` (whole-file change = 7 added / 3 removed — exactly the three old non-blank section lines out, new content in); `git diff RESULTS.md | grep -c '^@@'` → `1` (single hunk); the diff's trailing context shows ` ## Standing of each claim` space-prefixed = unchanged.
4. Content requirements (G5a) mapped to the new text, each verbatim:
   - **T5's 10.5× as the lead figure:** "**ρ = +0.882637 on raw WT-background scores but only ρ = +0.084365 on background-induced deltas — a 10.5× gap** (95% CIs [+0.869559, +0.891790] vs [+0.052159, +0.122589], nowhere near each other)" — first bold sentence of the section body, immediately under the header.
   - **Disattenuation chain as labeled counterfactual:** "**The disattenuation chain (−0.303 delta-only, −0.380 full) is a labeled counterfactual, not a finding:** it states what the anchor *would* be if ESM-2 shared the ESM-1v family's reliability, and that premise fails (Meta's model card: different corpora — UR50/D 2021_04 vs UR90/S 2020_03 — different runs, separate releases), so quote its CIs ([−0.440, −0.193] and [−0.555, −0.242]), never the points bare, and never transfer r_delta across that boundary."
   - **Resolved detection floor, AA4's empirical value, never n=10,757 / never the naive formula:** "**cite AA4's empirical detection floor — power 1.00 at ρ = 0.05 (the real floor is below that; the grid cannot say where)**, corroborated by design-effect 0.042727 (ICC 0.0973, k̄ = 16.45) and null-SD 0.026–0.032; never cite n = 10,757 as a power justification, and never the naive 654-position Fisher plug-in (0.109 — empirically falsified by AA4)."
   - **One-line pointer to the final write-up:** header line ends `— the project's final write-up is `docs/writeups/PROJECT_SUMMARY_FINAL.md``, and the section closes "**`docs/writeups/PROJECT_SUMMARY_FINAL.md` (committed in ab3c87f) is the full account; this section is its pointer.**"
   - **Similar length, pointer-and-summary not restatement:** old section ~3,660 chars; new ~2,800 chars. The old body's itemized survived/corrected lists were compressed to one sentence + pointer (all itemized detail remains in `PROJECT_SUMMARY_FINAL.md` and the logs).
5. **Two precision corrections inside the replaced text, disclosed (AGENTS §6):** (a) the old body's "about 0.1% structural artifact" could not be tied to Block H's actual numbers — replaced with the exact reading "essentially 0% structural artifact — null mean +0.0001 vs observed −0.0881"; (b) the old body's "3.45 sample-SDs below their mean" was replaced by the distribution-free T1 verdict (different distributions; exact rank p = 0.333) rather than carried — AGENTS §3 says never to lead with a z, and T1 itself flagged that any "3.45 SDs" quote must be paired with that p. Neither change alters any standing claim.

Actual output — the replaced section as written (verbatim, also visible in `git diff`):

> ## Current State (as of 2026-09-26) — the project's final write-up is `docs/writeups/PROJECT_SUMMARY_FINAL.md`; this round's full record: `docs/tasks/disattenuation-and-ledger/DISATTENUATION_LOG.md`
>
> _Section added by hand on 2026-09-25 by direct instruction (logged in `docs/tasks/reliability-and-decompositions/FINAL_CLOSEOUT_LOG.md` [X3]); replaced on 2026-09-26 as the **second and final** authorized hand-edit under the same direct instruction (logged in `docs/tasks/true-final-closeout/CLOSEOUT_LOG.md` [G5]). AGENTS §7 says this file is `scripts/22_update_writeup.py`'s output and must not be hand-edited — that standing conflict is flagged here, not resolved, and re-running the script would regenerate the file and drop this section._
>
> **Lead figure, no measurement-error model involved:** five identically trained ESM-1v checkpoints agree across seeds at **ρ = +0.882637 on raw WT-background scores but only ρ = +0.084365 on background-induced deltas — a 10.5× gap** ...

followed by the anchor paragraph, the counterfactual paragraph, and the floor/open-items/pointer paragraph (full text on disk; git-verified as the only change).

Verdict: **PASS** — G5a's four content requirements all present, similar length kept, boundary proven by single-hunk `git diff`; G5b's authorization statement made above.

Files created/modified:
- `RESULTS.md` (modified — Current State section, file lines 5–9, only)
- `docs/tasks/true-final-closeout/CLOSEOUT_LOG.md` (this entry)

Anything unexpected or worth flagging:
- The old header's pointers to `RELIABILITY_LOG.md`/`VERIFIED_FINDINGS_TABLE.md` were replaced by the new pointers per G5a's "replace its content"; both files remain valid records, just no longer named in the header (all their load-bearing content is reachable via `PROJECT_SUMMARY_FINAL.md`).
- `RESULTS.md`'s auto-generated banner (L3, "Do not hand-edit; re-run the script instead") is untouched and correct — it names exactly the §7 conflict flagged above.
- **This session's work is uncommitted, deliberately:** G4's authorization covered only `PROJECT_SUMMARY_FINAL.md` (already committed in ab3c87f), so no other commit was made. `git status` currently shows `M docs/tasks/disattenuation-and-ledger/DISATTENUATION_LOG.md` (G3c), `M RESULTS.md` (G5), `?? docs/tasks/true-final-closeout/CLOSEOUT_LOG.md` (this log), `?? EMAIL_DRAFT_nambiar_severity_baseline.md`, `?? scripts/98..103`, plus gitignored `data/processed` checkpoints. Flagged so the batch can be committed deliberately rather than by an unrequested commit (AGENTS §7: message must match the staged tree).
---
## SUMMARY

*Self-contained by design: a reader who has read nothing else should understand the state of the project from this section alone. This SUMMARY wins where it conflicts with anything else for this session's items; `DISATTENUATION_LOG.md`'s SUMMARY remains the cited authority for T/S/V/Y/X, quoted below from it.*

### The single most important thing first — and it is T1, not anything this session produced

**T1's conclusion, stated in full: ESM-2's −0.088118 is not an unusually large draw from the ESM-1v seed distribution — it is a different distribution entirely: Meta's own model card documents ESM-2 (UR50/D 2021_04, Lin et al. 2022) and the ESM-1v seeds (UR90/S 2020_03, Meier et al. 2021) as different corpora, different runs, and separate releases, so the outlier question is moot and cross-family reliability borrowing is not a licensed move.** (The n=5 rank test could not have settled it either way: exact two-sided p = 0.333.) The flagship disattenuation chain (−0.303 delta-only / −0.380 full) therefore rests on reliability measured in the ESM-1v seed family and then borrowed across that boundary — requalify it as a **conditional counterfactual, not a finding**, before anything else, and order any narrative around T5's two numbers, which need no measurement-error model at all.

### T5's two numbers (the money figure)

Same frame (10,757 rows / 654 positions), same convention (median of 10 pairwise member Spearmans), same run:

| cross-seed agreement across the 5 ESM-1v checkpoints | point | 95% CI |
|---|---|---|
| RAW WT-background scores (wt_logodds) | **+0.882637** | [+0.869559, +0.881465, +0.891790] |
| background-induced DELTAS | **+0.084365** | [+0.052159, +0.086318, +0.122589] |

Ratio **10.46× (≈10.5×)**, CIs nowhere near each other: the seeds agree almost perfectly on what a score *is* and barely at all on the difference between backgrounds — the instability is introduced by the subtraction itself.

### S1 in one sentence (sign/target resolution)

The apparent sign contradiction is **two different statistics sharing one target vector**: ProteinGym's severity table correlates each model's **raw WT-background score** with e.b (hence all positive, incl. ESM-2 **+0.085391**), while the headline correlates the **background-shift** `delta_esm = score[A222V bg] − score[WT bg]` with the same e.b (**−0.088118** own / **−0.070705** published) — same model, same target, opposite signs, entirely a statistic difference; every correlation sentence must name (statistic, target, signed/absolute, n).

### S2's three dropped findings, status as of this session

1. **H1a reversal (A222V shifts more than severity predicts):** original wording unverifiable (`MTHFR_RESULTS_LOG_PART2.md` never existed); substance re-verified — NOT supported at 9 backgrounds (+0.00954 [−0.00573, +0.02640], CI contains 0), supported and **opposite in direction** to the reversal claim at 31 backgrounds (+0.02121 [+0.00465, +0.03934]) → CONTRARY-TO-H1A. **Reconciled in writing this session (G3a, full text below): carries a mandatory single-checkpoint caveat; not contradicted, not superseded; seed-stability is an open reconciliation that cannot be closed inside ESM-2 (one checkpoint exists).**
2. **Rank-vs-MAE digest:** verified from source, never carried into any write-up (that is why it was "dropped"); rank half demoted (C1b non-background-specificity + exogenous-anchor collapse), MAE half stood (C2c verdict holds), disattenuation re-confirmed by A2 under the same proxy caveats — the open question ("unqualified vs qualified final claim") is answered: **qualified**, per RESULTS's corrected conclusion.
3. **Additive-null MAE (ESM-2 reliably worse than a no-interaction baseline in the highest-interaction stratum):** verified as a descriptive statistic (re-verified by D1b UNCHANGED-HOLD and C2c MSE-HOLD) but weakened as an ESM-2-specific claim. **Reconciled in writing this session (G3b, full text below): stands with the single-checkpoint caveat; the causal link to seed-instability has never been computed — an open reconciliation, stated plainly rather than papered over.**

### V1's direct answer (the three-round effective-n question)

The resampling unit is the **position** (654 of them; `lib/stats.py` L51–52 — rows travel with their positions), so neither naive Fisher floor applies: the row-level 0.027009 assumes 10,757 independent observations (pseudoreplication), and the 654-point Fisher plug-in 0.109364 is a different statistic, empirically falsified by AA4 (it predicts power 0.2475 at ρ=0.05 where the same pipeline measured 1.00). The floor that fits this pipeline is **AA4's empirical power 1.00 at ρ = 0.05 (real floor below that; grid cannot say where)**, corroborated by design-effect 0.042727 (ICC 0.0973, k̄ = 16.45) and null-SD 0.026–0.032; |−0.088118| sits ~2× above it → "we had the power to detect this" survives **in AA4's empirical form only** — never cite n = 10,757 for it, never cite 0.109.

### Y1's verdict

Site_Independent's **+0.063966 survives** (sign-flip re-derivation p < 0.0001, null centered at ~0 → 0% structural artifact; 7/7 in F7, 5/5 in F5 under Holm) — but Y2's pre-registered simulation on the real f_bar distribution shows mechanism alone (multiplicative truth measured on the additive scale) mechanically produces **ρ = +0.589823 [+0.572604, +0.606830], p < 0.0001 — 9.2× the observed value**: the severity baseline is simultaneously *real* (null- and multiplicity-surviving) and *derivable from mechanism alone*. Correct phrasing: measurement-scale structure, never evidence of interaction.

### X1's leverage-sensitivity result

Pooled rho(yE, Neff) = **+0.171422 [+0.091832, +0.247059]** on all 586 positions **collapses to +0.012518 [−0.082236, +0.106433], p = 0.789** when the 124 highest-Neff positions are dropped (n = 462). **Verdict: the direction claim (ESM tracks depth, ThermoMPNN doesn't) holds; the smooth monotone dose-response reading does not** — pair with X2: the depth effect breaks at the region-4 edge 474|475 (only segment CI excluding 0), not the domain edge 337|344; the boundaries are 43 residues apart and do not coincide.

### This session's five tasks — completed / blocked

| Task | Status | Why (evidence in its log entry above) |
|---|---|---|
| **G1** — surface Z3/Z4 into plain view | **PASS** | Pure retrieval; every artifact disk-verified before quoting; Z3 finding and Z4 email quoted verbatim below |
| **G2** — five-member precision grid | **PASS** | All 20 R1 + all 20 R2 verdicts green, TOK 0/200, G1 ≤ 4.77e-07; closes the final write-up's "unverified by analogy" item; verdict quoted below |
| **G3** — two reconciliations + K12/K21 fixes | **PASS** | Both paragraphs written below against deep-source-verified numbers; K12 CI corrected to [−0.0166, +0.0465] and K21 relabeled to rho(yE, Neff) in place (stale "flagged, not edited" disclosures updated); **new provenance failure found and disclosed**: `DISATTENUATION_LOG.md` L290's "higher in *every* stratum" claim, `+0.00446–+0.00866`, and `−0.000767` exist nowhere in the repo but that one line — flagged, not edited (outside G3c's authorization); never cite those three |
| **G4** — final write-up committed | **PASS (no-op)** | Already committed in `ab3c87f` (`git show --stat` verified); phantom-"v3" block permanently resolved (G4b) |
| **G5** — RESULTS.md Current State refresh | **PASS** | Second and final authorized hand-edit; single-hunk `git diff` (7+/3−) proves the boundary; content requirements mapped in the entry |

**Blocked this session: nothing.** Historical block resolved: the phantom-"v3" search is permanently closed — the final write-up exists at a real, committed path; the replacement sentence for wherever "v3" literally lives *outside* this repo remains at `DISATTENUATION_LOG.md` L297 for the user. Still open by design (not this session's to close): **SaProt epistasis (Z3g–h) awaits the structure-vs-reference population-definition decision reserved for the user** (smoke-scale rows only — not results); B3 clade specificity MIXED (size-matched p = 0.0010, placebo p = 0.2467); Z4's email drafted, **not sent**; this session's files uncommitted.

### Z3's actual ClinVar finding (quoted verbatim from `DISATTENUATION_LOG.md`'s `[Z]` entry, surfaced per G1)

> Filtering accounting (every step's n): 1,078 fetched → classes 315 primary / 205 context / 558 other → 763 without a parseable missense p. change (verified separately: includes exactly **51 nonsense `p.*Ter`**) → 315 parseable missense → **299 match the atlas manifest** (wt+pos+mut exact).
>
> Answer at the pre-registered threshold:
> - **VUS + conflicting in our measurement set: 236 → 34 with |delta_esm| ≥ 0.1182 (1 SD)** — plus 97 at ≥0.5 SD, 5 at ≥2 SD.
> - Context P/LP in our set: 29 → **7 ≥ 1 SD**.
> - Largest primary-class shifts: V194L (VUS, delta_esm **+1.2512** ≈ 10.6 SD), A220V +0.6883, V218L +0.3928, T227K +0.3056.
> - Saved: `data/processed/task102_clinvar_atlas_overlap.csv` (299 rows; 300 lines = header + 299).
> - Disclosed limits (printed by the script): classification is submitters' criteria, not our data; non-match ≠ absent from ClinVar (numbering/isoform or non-missense); the threshold says the background choice moves the score by ≥1 SD — it does **not** say which score is right.

(Threshold pre-registered before any variant-level fetch: 0.1182 = one population SD of delta_esm over the 11,344-row manifest; fetch 4,215,521 bytes, cache-on-rerun.)

### Z4's actual email draft content (quoted verbatim from the file — **DRAFT ONLY, STILL NOT SENT**)

> **Status: DRAFT ONLY — NOT SENT.** Written 2026-09-26 per task Z4: "Draft an email asking their corresponding author... was it run and not reported, or genuinely not considered? We will accept either answer." Nothing in this repository transmits mail; this file is the deliverable.
>
> To: (corresponding author, preprint `2025.09.14.676130` — fill in name/address)
> Subject: One control question about your MTHFR epistasis preprint
>
> Dear Dr. Nambiar and colleagues,
>
> I'm writing about your preprint on epistasis in MTHFR (2025.09.14.676130). We have been reproducing and extending some of your comparisons against the Weile et al. MTHFR deep-mutational-scan fitness data, and one question came up that we thought it was better to ask you directly rather than characterize in a write-up.
>
> Did your analysis include a severity-only baseline — a predictor built only from single-mutant effects (for example a site-independent or additive severity score, no pair-specific terms) — when evaluating how well the epistasis models perform? We ask because a monotone severity-to-fitness relationship mechanically induces a positive correlation between such a predictor and measured epistasis, so without that control it is hard to tell how much of the reported agreement reflects pair-specific interaction signal rather than severity structure alone.
>
> To be completely clear about what we are asking: either answer is fine with us.
>
> - If such a control was run and simply not reported, we would be glad to cite the number if you can share it (or point us to where it appears).
> - If it was genuinely not considered, that is entirely understandable — we would simply describe the control as not part of the published analysis rather than speculate about it either way.
>
> For transparency, we searched the preprint (main text, methods, supplement) and the released `maslov-group/Epistasis` repository and found no severity-only baseline, which is exactly why we would rather hear the answer from you than state a negative as established fact.
>
> Thank you for your time — and for releasing the code, which made our reproduction considerably easier.
>
> Best regards,
> (name)
> (affiliation)

(The file itself: `docs/tasks/disattenuation-and-ledger/EMAIL_DRAFT_nambiar_severity_baseline.md`, 2,852 bytes. **Still unsent — no mail was transmitted by this or any session.**)

### G2's precision-check verdict (verbatim from script 103's final output)

```
R1 (value, all 20 member-conditions <= 1e-3): PASS
R2 (finding, all 20 paired |rho shifts| <= 0.01): PASS
G2 VERDICT: PASS -- all five ESM-1v members' cached deltas reproduce under the same
CPU / fp32-b1 / fp32-b8 / fp32-b16 / fp64-b8 grid to the same tolerances the original
ESM-2 check used (G1 + TOK + R1 + R2; thresholds 1e-5 / 1e-3 / 0.01 unchanged).
```

(Worst R1 across all 20 = 7.020e-05, 14× inside 1e-3; worst paired |Δrho| = 0.0003, 33× inside 0.01; TOK 0/200 mismatches per member; G1 gates captured 4.768e-07 / 4.396e-07. N=100 pre-registered as a timing decision; two tool aborts mid-run disclosed — checkpointed resume, coverage 100/100 everywhere.)

### G3a — the H1a-reversal finding vs. the later reliability findings (full reconciliation paragraph)

> The H1a-reversal finding does not survive untouched, is *not* contradicted by the reliability findings, and must now carry an explicit single-checkpoint caveat — that is the honest three-part answer, and the seed-stability sub-question is an open reconciliation that cannot be closed with the artifacts that exist. Both sides operate on the same quantity, `delta_esm` (A222V-background minus WT-background score), so the reliability evidence bears directly on the residual's raw material: across the five ESM-1v checkpoints, cross-seed agreement on deltas is only **+0.084365** [+0.052159, +0.122589] pooled (**+0.050813** [+0.030455, +0.065259] within-position) versus **+0.882637** [+0.869559, +0.891790] on raw WT-background scores — a 10.46× gap with CIs nowhere near each other, "the disagreement is introduced almost entirely by the subtraction across backgrounds" (T5a) — and the per-seed delta-vs-own_e_b correlation flips sign across members (**[−0.040820, +0.013434]**, mean −0.015588, all |ρ| ≤ 0.041), establishing that a shift pattern computed from single-checkpoint deltas is weakly seed-reproducible by default. The W3 finding itself — **+0.02121 [+0.00465, +0.03934]** at 31 backgrounds/120 positions, CI excluding 0 from above, versus **+0.00954 [−0.00573, +0.02640]** at 9 backgrounds, CI containing 0; the generic severity→shift relation it is a residual of holding at −0.466667 [−0.583333, −0.066667] and −0.519 [−0.635, −0.388] respectively — was computed on **one ESM-2 checkpoint**, and its position-cluster CI quantifies position-sampling uncertainty *conditional on that checkpoint*: the design has no seed axis, so "CI excludes 0" never covered checkpoint variation. But the demonstrated instability cannot overturn it either: that instability was measured entirely inside the ESM-1v seed family, and T1's verdict (ESM-2 = UR50/D 2021_04; ESM-1v = UR90/S 2020_03 — "different corpora, different runs, separate releases") explicitly blocks transferring its magnitude onto ESM-2 as a number ("an assumption, not a licensed inference"). The finding therefore stands as a within-checkpoint result, replicated across its design axis (9 → 31 backgrounds, CIs overlapping over [0.0047, 0.0264] — "resolution, not reversal" — with the supporting M1e relation strengthening from −0.467 to −0.519) but **unverified, and within ESM-2 unverifiable, across seeds**: ESM-2 has only one checkpoint, so no within-family seed test exists to run. The nearest runnable tests — re-running W3's exact 31-background design on the same-corpus ESM-2 sizes (t30_150M and t36_3B, both present in the local torch cache, verified by ls) or on ESM-1v's five-member ensemble — would each be cross-model evidence about the design's generalizability, not a seed test of this checkpoint, and neither was run this session. **This remains an open reconciliation** in exactly that sense: not a contradiction, not a clean pass — with the honest status sentence "verified across backgrounds and positions on one checkpoint; unverified across seeds." G2's precision-grid PASS (all five members' deltas reproduce: G1 ≤ 4.77e-07, worst R1 7.020e-05 ≤ 1e-3, worst paired R2 0.0003 ≤ 0.01) confirms the deltas' *numerical reproducibility*, which must not be conflated with seed stability — the axis G2 did not and could not test.

### G3b — the additive-null MAE finding vs. the later reliability findings (full reconciliation paragraph)

> The additive-null MAE finding stands as a descriptive statistic for this checkpoint — re-verified under three independent robustness axes — but it carries the same single-checkpoint caveat, its ESM-2-specific framing remains subordinated exactly as the corrected conclusion already says, and one head-on link remains genuinely uncomputed. The finding, checked at source: in the highest-interaction stratum ESM-2's MAE exceeds the no-interaction baseline by **+0.00241 [+0.00155, +0.00321]** (n = 3,586 / 609 positions; null MAE 0.2481 vs ESM-2 0.2505) — stratum-specific, not universal: the low stratum favors ESM-2 (−0.00317, CI excluding 0) and the mid stratum crosses zero — and the verdict re-verifies under squared loss (C2c: **+0.002320 [+0.001740, +0.002895]**, within 4% of the MAE value), under an EB-shrunken stratifier that purges the high stratum's high-SE enrichment (D1b: **+0.001851 [+0.000987, +0.002706]**, mean SE 0.1166 → 0.0788), and at low folinate (H4a: **+0.00227 [+0.00144, +0.00308]**, positive at all four folinate conditions) — all excluding zero in the same direction, with §6.4's calibration asymmetry making the loss conservative: ESM-2's predictors were calibrated directly against the true target while the null's were transformed from WT fitness, "a more conservative bar that ESM-2 still failed to clear." The reliability side enters through two doors. First, it was already built into the reference: C3a's reliability-limited oracle (rel = 0.636, from r_own = 0.636328) beats the multiplicative null by **+0.0521 [+0.0436, +0.0613]** in the same high stratum, and against that ceiling ESM-2 does not merely fall short but moves the wrong way — **−4.62% of the available headroom** (−0.002409 while +0.0521 was on offer; +0.84% pooled). Second, T5's 10.46× gap (+0.882637 cross-checkpoint agreement on raw scores vs +0.084365 on deltas) identifies the background subtraction itself as the system's weakly reproducible component — a plausible mechanism for why adding true-background information fails to help exactly where interaction is strongest, consistent with the corrected conclusion's subordination of these findings to "a property of how well any WT-arm-informed signal predicts an A222V-arm-derived target, which is close to tautological once seen clearly." What has never been computed is the causal link: no reliability-round entry re-ran any MAE statistic (the prior session stated this itself), so nothing tests whether the delta's cross-checkpoint instability *explains* the high-stratum loss — and T1 blocks assuming ESM-2's instability magnitude from ESM-1v's. Magnitude honesty belongs in the same breath: ρ(S_A222V, S_WT) = 0.999636, so the MAE story rests on a small number of rank swaps, and +0.00241 is under 1% of the high stratum's baseline MAE. **Verdict: the finding survives, weakened-as-ESM-2-specific exactly as already written down, carrying the single-checkpoint caveat; whether seed-instability causes the MAE loss is a real open item settleable only by a new test (per-stratum MAE for each of ESM-1v's five members — itself cross-model under T1). This too remains an open reconciliation — stated, not papered over: every verified number on both sides is consistent with every other, no result contradicts another, but the head-on link has never been computed.**

### Confirmations the task requires

- **`docs/writeups/PROJECT_SUMMARY_FINAL.md` is committed and referenceable:** 325 lines, tracked, committed in **`ab3c87f`** ("Add final project summary and true final closeout task doc" — verified with `git show --stat`, 2 files changed, 426 insertions). It is **the project's final write-up**, now reachable from `RESULTS.md`'s Current State header and closing line; no future session should search for a phantom "v3" (G4b).
- **`RESULTS.md`'s current-state section is updated:** file lines 5–9 replaced as of 2026-09-26 — T5's 10.5× leads; disattenuation labeled a counterfactual with its CIs and T1 premise failure; AA4's empirical detection floor cited (never n=10,757, never the naive 0.109); one-line pointer to `PROJECT_SUMMARY_FINAL.md`. Single-hunk `git diff` (7+/3−) proves nothing below `## Standing of each claim` moved. This was the **second and final** authorized hand-edit (G5b), standing AGENTS §7 conflict flagged, not resolved.

### The project's final state, in two sentences

**The science:** the project established that ESM-2's background-sensitivity signal (delta_ESM vs own e.b, ρ = −0.088118, n = 10,757 / 654 positions) is real, small (<1% of rank variance), null-surviving, and detectable under an empirically derived power floor — while systematically requalifying every stronger interpretation built on top of it (disattenuation → labeled counterfactual whose cross-family premise fails; severity baseline → real but derivable from mechanism alone; additive-null MAE loss → real, small, stratum-specific, ESM-2-specific framing subordinated), leaving the model-free **10.5× seed-agreement gap (0.882637 on scores vs 0.084365 on deltas)** as the most dependable number in the system. **The record:** all five closeout tasks completed with nothing blocked; the citable endpoint is `docs/writeups/PROJECT_SUMMARY_FINAL.md` (committed, ab3c87f) with `RESULTS.md`'s Current State pointing at it; and what remains genuinely open — SaProt Z3g–h awaiting the user's population-definition decision, B3's MIXED verdict, the drafted-but-unsent Nambiar email, G3's two honestly labeled open reconciliations, this session's uncommitted files, and `DISATTENUATION_LOG` L290's three unverifiable strings — is stated in the record rather than papered over.
---
