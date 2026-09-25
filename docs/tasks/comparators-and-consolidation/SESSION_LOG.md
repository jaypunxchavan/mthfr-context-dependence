# SESSION_LOG — comparators-and-consolidation (DRAFT working log)

Session started: 2026-09-22 (per COMPARATORS_AND_CONSOLIDATION.md run).

Format per task (binding protocol from the session instructions):

## [GROUP-TASK ID] — [one-line title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
---

Entries are appended immediately after each task's real check/execution,
never batched, never written without executed work behind them.

## [S1] — Verify script 65's "e" statistic is independent of the paper's published ε
Status: PASS
Time started / finished: 2026-09-22 23:08:39 / 2026-09-22 23:11
What I did:
- S1a: ran the task's exact grep (plus a pinpoint grep for the log-space/ratio
  patterns) on both `scripts/49_i1_gb1_positive_control.py` and
  `scripts/65_q1_foursite_i1_rerun.py`; pulled the full multi-line `e`
  statements, the `F` lookup definitions, and the docstring formula lines.
- S1b: grepped both scripts for the literal published/re-derived ε values
  (`7.399806`, `4.495855`, standalone `4.5`, standalone `5`, `epsilon`/`ε`
  tokens, `published|paper|elife`); inventoried every file read/import in
  both scripts to prove what data path `e` can possibly come from.
- S1c: placed both formulas side by side (e's verbatim code below; ε's
  verbatim Methods eq. (2) as logged in MIGRATION_LOG P2 line 163-170).
Actual output (real numbers and quoted source text):
S1a — the `e` statistic, verbatim from BOTH scripts:
  - Docstring formula, script 49 lines 64-67 (identical math in 65 lines
    39-40): `- Target: e(v,b) = f(v,b) - f(v,b0) - f(WT,b) + f(WT,b0) — the
    double-mutant-cycle interaction, the structural analogue of the atlas's
    e.b (background interaction beyond main effects).`
    Script 65 line 39-40: `- Target: e(v,b) = f(v,b) - f(v,b0) - f(WT,b) +
    f(WT,b0) — the same double-mutant-cycle interaction script 49 used
    (unchanged formula).`
  - Executable code, script 49 lines 255-256:
    ```
                e = (F(*f_vb_conf) - F(*f_vb0_conf)
                     - wt_bg_fit + F(*WT_COLS))
    ```
    with `f_vb0 = list(WT_COLS); f_vb0[idx] = v` (line 251-252) and
    `wt_bg_fit` = `F(*letters_bg)` = `f(WT, b)`.
  - Executable code, script 65 lines 228, 237-238:
    ```
            wt_bg_fit = F(*letters_bg)      # f(WT, b): focal WT, others conf
    ...
                e = (F(*f_vb) - F(*f_vb0)
                     - wt_bg_fit + F(*WT_COLS))
    ```
  - The `F` lookup (where every value in `e` comes from):
    script 49 lines 197-201: `def F(a39, a40, a41): / key = gt(a39, a40,
    a41) / if key not in fit.index: / fail(f"genotype missing from fitness
    file: {key}") / return float(fit[key])`;
    script 65 lines 179-183: `def F(*letters): / key = "".join(letters) /
    if key not in fit.index: / fail(f"genotype missing from fitness file:
    {key}") / return float(fit[key]")` — `fit` is loaded at 49:152 / 65:138
    by `raw = pd.read_csv(DATA, sep="\t")` where DATA =
    `data/external/GB1_fitness_landscape.txt` (raw WT-normalized fitness,
    linear scale, NO log, NO adjustment rules).
S1b — literal published/re-derived ε values, grep results:
  - `7.399806 / 4.495855`: exactly ONE match — `scripts/65...py:22: own eq.
    (2) gives +7.399806 and -4.495855 respectively (the +5 label does` —
    i.e. **inside the docstring's provenance narrative only**.
  - standalone `4.5`: two matches, both the same docstring narrative —
    `65...py:20: Fig 3D prints eps = +5 (G41LxV54H on IL background) and
    eps = -4.5 (on` and `65...py:23: not re-derive; -4.5 does — full detail
    in MIGRATION_LOG P2).`
  - `epsilon`/`ε` tokens: `(no matches)` in either script.
  - standalone `5`: `49...py:22: eLife 2016;5:e16965` (journal volume, not
    ε), `65...py:20` and `65...py:22` (same docstring lines as above).
    Script 49 contains NO ε value in any form.
  - `published|paper|elife`: only prose — 49:22 (citation), 49:33 +
    49:384 (site-numbering caveat, not ε), 65:18/21/24 (P2 provenance) and
    65:117 (sites comment: `# four sites per Wu et al. 2016: "V39, D40, G41
    and V54" (quoted in P2)` — site list, not ε).
  - Complete read/import inventory proving the data path: script 49 —
    `116:import sys, os, time, hashlib, itertools, warnings`,
    `117:from pathlib import Path`, `121:import numpy as np`,
    `122:import pandas as pd`, `152: raw = pd.read_csv(DATA, sep="\t")`,
    `189: model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()`;
    script 65 — `98/99/103/104` same stdlib+numpy/pandas imports,
    `138: raw = pd.read_csv(DATA, sep="\t")`,
    `174: model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()`.
    **Only two inputs exist: the GB1 fitness text file and the ESM-2 650M
    weights. No ε value is readable from either.**
S1c — the two formulas side by side:
  - `e` (pipeline, this repo): `e(v,b) = f(v,b) − f(v,b0) − f(WT,b) +
    f(WT,b0)` — additive difference-in-differences on RAW linear fitness,
    one value per (variant at one focal site × sampled 3-site background)
    row → 760 pooled rows in Q1 (570 in script 49); no log transform, no
    adjustment rules (missing genotype = hard fail).
  - `ε` (Wu et al. 2016 Methods eq. (2), verbatim from MIGRATION_LOG P2
    lines 163-170): `εa⁢b,B⁢G = ln(w_a⁢b/w_BG) − ln(w_a/w_BG) − ln(w_b/w_BG)`
    i.e. `ε = ln(w_ab·w_BG/(w_a·w_b))` — LOG-ratio scale, one value per
    site-pair per fixed two-site background, PLUS three detection-limit
    adjustment rules (`Rule 1) if max(wab/wBG, wa/wBG, wb/wBG) < 0.01,
    εadjusted = 0`, `Rule 2) ... < 0.01, εadjusted = max(0, ε)`,
    `Rule 3) ... < 0.01, εadjusted = min(0, ε)`).
  - Verdict on the relationship: **different but related quantities** —
    both are double-mutant-cycle interactions on the same GB1 fitness
    file, but (1) e is additive/linear where ε is log-ratio; (2) e's
    background `b` differs from `b0` at up to THREE positions at once, so
    most e rows are higher-order interactions — e only reduces to the
    pairwise-cycle form when b differs at exactly one position (then it is
    structurally ε's four-term cycle on the linear scale); (3) ε applies
    the paper's adjustment rules, e applies none; (4) count: 760 pooled e
    rows vs 6 per-pair ε scalars.
Verdict: PASS — `e` is computed exclusively from `F(...)` fitness lookups
plus the fixed `WT_COLS`; the only occurrences of any published/re-derived
ε literal in either script are prose citations inside script 65's
docstring (lines 18-24), referenced by no computation; neither script can
read an ε value from any file. I1/Q1's pooled rho(delta, e) is therefore
independent of the paper's ε and of the +5 vs +7.399806 discrepancy.
Files created/modified: none (read-only checks). This entry appended to
SESSION_LOG.md.
Anything unexpected or worth flagging:
- Honest nuance on S1b's "hardcodes ... anywhere": a blanket "no
  occurrences" would be FALSE — script 65's docstring does print the
  literals +7.399806 / -4.495855 / +5 / -4.5 as provenance text (lines
  18-24). The accurate statement is: present in narrative docstring only,
  absent from all executable code and from every data path — quoted above
  so the distinction is visible.
- Script 49's e-code has no `wt_bg_fit = ...` line inside the sed window
  (it is set just above line 245); script 65's equivalent line (228) is
  quoted in full. Same expression, same meaning.
---

## [S2] — Finish script 50's migration with a two-file join
Status: PASS
Time started / finished: 2026-09-22 23:11:09 / 2026-09-22 23:17
What I did:
- S2a confirmations (run BEFORE editing, per "confirm ... do not assume"):
  re-verified N2's flag column by rates; tested both candidate join keys;
  proved join coverage + column identity between the two files; grepped
  script 50 for any operator applied directly to `se_e_b`; confirmed all
  5 PRE_MIGRATION backups exist.
- S2a edit (in place — the sanctioned exception): two-file design —
  `n2` = N2 flag+base table; `t35` = retired file read for `se_e_b`
  (+type) ONLY; the S2a join `ep = n2.merge(t35[["hgvs_pro","se_e_b"]],
  on="hgvs_pro", how="left")`; D1c's base switched from
  `t35.dropna(...)` to `ep.dropna(...)`; BOTH file compositions gated
  (N2 at its true 11,865/10,757/538/570 — newly pre-registered in the
  docstring — and t35 at its original 13,134/11,902/624/608, untouched).
  The `d`-merge line (line 241: `d.merge(t35[["hgvs_pro","se_e_b",
  "type"]]...)`) was kept BYTE-IDENTICAL to the pre-migration code so
  D1a/D1b inputs cannot drift. Flag reads: already `epistatic_ecdf`
  (D1c lines 462/466/470 + docstring line 68, from last session's R2
  edit). Two stale-text truth-fixes (disclosed below): the printed
  "D1c uses script 35's full table" message and the matching docstring
  sentence now say N2 flag table (= script 35's complete-case subset).
- S2b: `py_compile` OK → SMOKE at N_BOOT=300 (3 s, all gates passed) →
  FULL recorded run at default N_BOOT=2000 (exit 0, 11 s) → side-by-side
  of all 5 outputs vs the 5 `*_PRE_MIGRATION.csv` backups (diff + full-
  precision numeric merge).
Actual output (real numbers and quoted source text):
S2a confirmation output (verbatim key lines):
  - `epistatic_ecdf: syn=0.0509 nonsense=0.0892 missense=0.1659` →
    `-> documented N2 headline = 16.6% missense @ 5.1% syn ... =>
    flag column = epistatic_ecdf`
  - `hgvs_pro unique in N2 : True | unique in t35: True`
  - `position  unique in N2 : False | n distinct positions: 654 of 11865 rows`
  - `inner join on hgvs_pro -> rows: 11865 (N2 = 11865 => full coverage: True)`
  - `type identical on joined rows: True` / `position identical: True` /
    `own_e_b identical ... max|diff| = 0.0` /
    `se_e_b non-null on joined rows: 11865 of 11865`
  - se_e_b operator scan: `line 42: mean(se_e_b^2) on the s-set, method of
    moments; if tau^2 <= 0` (docstring) and `line 249: s["se_top_tercile"]
    = s["se_e_b"] >= s["se_e_b"].quantile(2 / 3)` — see assumption (a).
  - backups: all five `task50_*_PRE_MIGRATION.csv` present (549/509/210/
    1702/1046 bytes, mtime 07:11).
SMOKE (N_BOOT=300): `SMOKE_EXIT=0  SMOKE_ELAPSED=3s` — gates all green
(N2 `11865 {'substitution': 10757, 'synonymous': 570, 'nonsense': 538}`;
t35 `13134 {'substitution': 11902, 'nonsense': 624, 'synonymous': 608}`;
`s-set ... n = 10757 ... SE join complete: 10757`; G1 `|diff| = 0.000e+00`;
identity `0.000e+00`; G2 `|diff| = 0.000e+00`), verdicts
ENRICHED / UNCHANGED-HOLD / HIGHER / NOT CLEARED.
FULL RUN (default N_BOOT=2000) — complete stdout, verbatim:
```
==========================================================================
GATES — build mirror + replication of 6.2/6.3 (exit 1 on failure)
==========================================================================
script-34 set n = 11113 (expected 11,113), 654 positions
G1: pooled MAE diff = +0.000533466098810331 (published +0.000533466098810331, |diff| = 0.000e+00)
identity: MAE helper a==b -> 0.000e+00; MSE helper a==b -> 0.000e+00
N2 table (flag+base): 11865 rows, types {'substitution': 10757, 'synonymous': 570, 'nonsense': 538}
retired t35 table (se_e_b source): 13134 rows, types {'substitution': 11902, 'nonsense': 624, 'synonymous': 608}
s-set (dropna abs_gi): n = 10757 (expected 10,757); SE join complete: 10757
6.3 set contains no nonsense/synonymous rows (missense-only by construction) — D1c uses the N2 flag table (= script 35's complete-case subset) instead.

==========================================================================
D1a  IS THE HIGH-|e.b| STRATUM ENRICHED FOR HIGH-SE VARIANTS?
==========================================================================
strata (pd.qcut |GI| terciles, FIXED labels in draws — C2c rule):
  low  n= 3586  mean SE=0.0705  median SE=0.0562  share in top-SE tercile=0.243 (1/3 = no enrichment)
  mid  n= 3585  mean SE=0.0757  median SE=0.0591  share in top-SE tercile=0.284 (1/3 = no enrichment)
  high n= 3586  mean SE=0.1166  median SE=0.0769  share in top-SE tercile=0.473 (1/3 = no enrichment)

PRIMARY D = mean(SE|high) - mean(SE|low) = +0.0461  CI=[+0.0396, +0.0535]  (2000/2000 valid, 654 positions)
effect size: mean_SE_high / mean_SE_low = 1.654 (+65.4%)  [AGENTS §3]
D1a VERDICT (pre-registered rule): ENRICHED

secondary Spearman(|GI|, SE) = +0.2650  CI=[+0.2406, +0.2901]  (descriptive; same WLS fit feeds both — see limitations)

sensitivity (|own_e_b| strata): D = +0.0436  CI=[+0.0370, +0.0510];  stratum agreement own vs GI = 0.822 (the ~82% from design checks)
sensitivity verdict: ENRICHED (not verdict-bearing)
Saved .../data/processed/task50_d1a_se_enrichment.csv + _stats.csv

==========================================================================
D1b  6.3 UNDER AN EMPIRICAL-BAYES SHRUNKEN e.b STRATIFIER
==========================================================================
G2: arm-1 high-stratum MAE diff = +0.002408919531324 (6.3 = +0.002408919531324, |diff| = 0.000e+00)

EB prior (method of moments): var(own_e_b) = 0.058036 - mean(se^2) = 0.022146  ->  tau^2 = 0.035890
shrink factor: min=0.003 median=0.901 max=0.994; spearman(raw, shrunk) = 0.9861

--- arm1_raw_GI (stratifier: abs_gi) ---
  low  (n= 3586, 638 pos, mean SE=0.0705)  MAE diff=-0.003166 CI=[-0.004181,-0.002154]  MSE diff=-0.001936 CI=[-0.002550,-0.001320]
  mid  (n= 3585, 649 pos, mean SE=0.0757)  MAE diff=-0.000109 CI=[-0.001073,+0.000875]  MSE diff=+0.000196 CI=[-0.000286,+0.000719]
  high (n= 3586, 609 pos, mean SE=0.1166)  MAE diff=+0.002409 CI=[+0.001551,+0.003208]  MSE diff=+0.002320 CI=[+0.001740,+0.002895]
       high-stratum verdict: MAE HOLD (CI_lo>0: ESM-2 worse) | MSE HOLD (CI_lo>0)

--- arm2_raw_own (stratifier: abs_own) ---
  low  (n= 3586, 641 pos, mean SE=0.0720)  MAE diff=-0.002727 CI=[-0.003809,-0.001736]  MSE diff=-0.001722 CI=[-0.002307,-0.001159]
  mid  (n= 3585, 648 pos, mean SE=0.0751)  MAE diff=+0.000136 CI=[-0.000734,+0.001044]  MSE diff=+0.000129 CI=[-0.000325,+0.000619]
  high (n= 3586, 616 pos, mean SE=0.1156)  MAE diff=+0.001726 CI=[+0.000753,+0.002595]  MSE diff=+0.002172 CI=[+0.001509,+0.002807]
       high-stratum verdict: MAE HOLD (CI_lo>0: ESM-2 worse) | MSE HOLD (CI_lo>0)

--- arm3_eb_shrunk (stratifier: abs_eb) ---
  low  (n= 3586, 647 pos, mean SE=0.1045)  MAE diff=-0.002610 CI=[-0.003632,-0.001575]  MSE diff=-0.001623 CI=[-0.002195,-0.001038]
  mid  (n= 3585, 647 pos, mean SE=0.0795)  MAE diff=-0.000107 CI=[-0.001023,+0.000825]  MSE diff=+0.000003 CI=[-0.000470,+0.000491]
  high (n= 3586, 613 pos, mean SE=0.0788)  MAE diff=+0.001851 CI=[+0.000987,+0.002706]  MSE diff=+0.002199 CI=[+0.001606,+0.002807]
       high-stratum verdict: MAE HOLD (CI_lo>0: ESM-2 worse) | MSE HOLD (CI_lo>0)

stratum membership agreement (fraction of rows in same tercile):
  arm1 vs arm2 (own-vs-published switch): 0.822  (rows entering/leaving the high stratum: 712)
  arm2 vs arm3 (shrinkage alone): 0.893  (rows entering/leaving the high stratum: 724)
  arm1 vs arm3 (total change vs 6.3): 0.781  (rows entering/leaving the high stratum: 1056)

arm1 high-stratum MAE verdict (gated replication of 6.3): HOLD (CI_lo>0: ESM-2 worse)
arm2 high-stratum MAE verdict (own_e_b switch control):   HOLD (CI_lo>0: ESM-2 worse)
arm3 high-stratum MAE verdict (EB-shrunken):            HOLD (CI_lo>0: ESM-2 worse)
arm3 high-stratum MSE verdict:                           HOLD (CI_lo>0)

D1b VERDICT (pre-registered, arm3 MAE CI): UNCHANGED-HOLD — 6.3's high-stratum verdict is HOLD on arm1
Saved .../data/processed/task50_d1b_eb_restrat.csv + _agreement.csv

==========================================================================
D1c  NONSENSE NOISE FLOOR (opposite fitness end from synonymous)
==========================================================================
  synonymous             n=  570  sd(e.b)=0.1453  median SE=0.0387  p95|e.b|=0.3088  calib sd/medianSE=3.76  epistatic_ecdf pass=5.1%
  nonsense               n=  538  sd(e.b)=0.1720  median SE=0.0780  p95|e.b|=0.4284  calib sd/medianSE=2.21  epistatic_ecdf pass=8.9%
  missense (reference)   n=10757  sd(e.b)=0.2409  median SE=0.0629  p95|e.b|=0.5278  calib sd/medianSE=3.83  epistatic_ecdf pass=16.6%

PRIMARY R = sd(e.b|nonsense)/sd(e.b|synonymous) = 1.184  CI=[1.025, 1.371]  (2000/2000 valid)
D1c HETEROSCEDASTICITY VERDICT (pre-registered): HIGHER (nonsense noise > synonymous)

SECONDARY floor comparison: cut23(|own_e_b|, missense) = 0.1830 / sd(nonsense) = 0.1720  ->  ratio 1.064  CI=[0.948, 1.207]
D1c FLOOR VERDICT (pre-registered): NOT CLEARED (CI_hi < 2)
  (syn/nonsense sit at opposite fitness ends from the missense strata — see limitations; ratio < 1 would mean the entry bar into
   6.3's 'high interaction' tercile is smaller than dead-end noise spread at the floor of the fitness range.)
Saved .../data/processed/task50_d1c_nonsense_floor.csv

==========================================================================
LIMITATIONS (printed by the script itself)
==========================================================================
  - D1a: SE(e_b) and e.b come from the SAME WLS fit — the
    association is the winner's-curse signature, not causal.
    Analytic SEs are themselves miscalibrated (script 35's
    empirical/analytic ratio), so absolute SE levels understate
    noise; enrichment statistics are RELATIVE and inherit that.
  - D1b: EB prior = single global Gaussian tau^2 (method of
    moments), not covariate-dependent; shrinkage uses own_e_b +
    SE only, never the target (no leakage into cross-fit preds);
    stratum labels FIXED within bootstrap draws (C2c convention);
    arm2-vs-arm1 agreement isolates the own-vs-published switch.
  - D1c: synonymous/nonsense sit at OPPOSITE fitness-range ends
    from the missense strata — the point of the check AND the
    reason the floor ratio is not apples-to-apples with missense
    noise; floor lives in e.b space only (no ESM scores exist for
    nonsense rows); INCONCLUSIVE/NOT DETECTED = absence of
    evidence, not evidence of equality.
  - Settings: N_BOOT=2000, SEED=0.

Done.
FULL_EXIT=0  FULL_ELAPSED=11s
```
S2b side-by-side (diff of each new file vs its PRE_MIGRATION backup):
  - `task50_d1a_se_enrichment.csv` → `IDENTICAL (byte-for-byte)`
  - `task50_d1a_se_enrichment_stats.csv` → `IDENTICAL (byte-for-byte)`
  - `task50_d1b_eb_restrat.csv` → `IDENTICAL (byte-for-byte)`
  - `task50_d1b_eb_agreement.csv` → `IDENTICAL (byte-for-byte)`
  - `task50_d1c_nonsense_floor.csv` → DIFFERS in EXACTLY three rows:
    `-synonymous_epistatic_N2_frac,0.4473684210526316` →
    `+synonymous_epistatic_ecdf_frac,0.05087719298245614`;
    `-nonsense_epistatic_N2_frac,0.1449814126394052` →
    `+nonsense_epistatic_ecdf_frac,0.08921933085501858`;
    `-substitution_epistatic_N2_frac,0.4482662452356605` →
    `+substitution_epistatic_ecdf_frac,0.16593845867807008`.
    Every other row byte-equal, including full-precision
    `R_sd_nonsense_over_syn,1.1838800911098901,1.025256938780092,
    1.3708832285375996,HIGHER ...` and
    `R_cut23_over_sd_nonsense,1.063761353151011,0.9477750521767444,
    1.207166361310804,NOT CLEARED ...`.
  Numeric merge confirms: d1a stats `diff` = 0.0 for all 5 rows,
  verdicts old == new (`ENRICHED`, `descriptive`,
  `ENRICHED (not verdict-bearing)`); d1b `max |delta| across ALL restrat
  numeric cells: 0.0`.
S2c — stated plainly: **only the exact numbers moved, and only for the
three descriptive flag-pass rows; the qualitative conclusion did not
change.** All four pre-registered verdicts are identical to the
pre-migration outputs — D1a `ENRICHED`, D1b `UNCHANGED-HOLD`,
D1c `HIGHER`, floor `NOT CLEARED` — with 4 of 5 output files reproducing
byte-for-byte (deterministic seed + unchanged inputs). The three rows
that DID move are precisely the migration's target: the retired flag's
FDR-plagued pass rates (missense 44.83% → 16.59%, syn 44.74% → 5.09%,
nonsense 14.50% → 8.92%) replaced by N2's calibrated `epistatic_ecdf`
rates (matching N2's documented 16.6%/5.1% headline to the digit).
Verdict: PASS — migration complete and verified: flag from N2, se_e_b
joined raw from the retired file on hgvs_pro, both files composition-
gated, full rerun exit 0, side-by-side executed, conclusion unchanged.
Files created/modified:
- Modified (in place, sanctioned): `scripts/50_d1_stratifier_quality.py`
  — two-file read block + N2 gate + `ep` join (comment at the read site
  records the full design), D1c base `ep.dropna`, D1c docstring counts,
  plus two stale-text truth-fixes (printed message line 252; docstring
  lines 77-79).
- Modified (regenerated by the run): the 5 `task50_*.csv` outputs
  (N_BOOT=2000). Their pre-migration contents remain intact in the 5
  `*_PRE_MIGRATION.csv` backups (mtime 07:11, not touched).
- No other file written.
Anything unexpected or worth flagging:
- Assumption (a), logged per troubleshooting rule #6: "used strictly as
  a raw continuous covariate, never re-thresholded" was read as "S2 must
  introduce no new threshold/flag on se_e_b". The pre-existing line 249
  `s["se_top_tercile"] = s["se_e_b"] >= s["se_e_b"].quantile(2/3)` —
  D1a's own pre-registered DESCRIPTIVE cross-tab (docstring lines 25-27)
  — was deliberately left untouched: deleting it would change a
  pre-registered decision rule (AGENTS §10), which this session may not
  do. It is not a re-thresholding of the migrated covariate into an
  epistatic flag; it is D1a's original within-run tercile diagnostic.
- Assumption (b): `type` for the `d`-merge still comes from t35
  (byte-identical to the original pre-migration line). The task did not
  specify type's source; it is identical in both files on every joined
  row (verified), so either source is equivalent — keeping the original
  line guarantees zero input drift for D1a/D1b, which the byte-for-byte
  reproduction confirms.
- Assumption (c): the two stale-text fixes change ONLY printed/docstring
  prose (no gate, threshold, statistic, or rule) — done so the script's
  own output stays truthful post-migration (AGENTS §6).
- Unexpected but welcome: 4/5 outputs byte-identical is the strongest
  possible side-by-side result — the migration changed exactly what it
  was supposed to change and nothing else.
- S1's session-wide note: the smoke run at N_BOOT=300 also overwrote the
  outputs first; the full run immediately superseded it, and the backups
  were never at risk (final files = full run; backups = 07:11 originals).
---

## [S3] — Document data/external/ in AGENTS.md §2 (the ONLY authorized AGENTS.md edit)
Status: PASS
Time started / finished: 2026-09-22 23:17 / 2026-09-22 23:19:03
What I did:
- Appended exactly ONE bullet to AGENTS.md §2 (Data layout), directly
  after the `docs/tasks/` bullet, describing `data/external/`: what lives
  there (reference datasets from outside the MTHFR atlas, used as
  comparators — GB1 fitness landscape named as the example), that it is
  gitignored like the rest of `data/`, and that provenance (source
  record/URL and md5) belongs in the task doc or log entry that first
  fetched each file (GB1's in script 49's docstring).
- Made NO other change to AGENTS.md. Verified with `git diff` (hunk
  count + stat) that this is a single 5-line insertion and that
  AGENTS.md is the only tracked file modified in the repo.
Actual output (real numbers and quoted source text):
  `git diff -- AGENTS.md` — exactly one hunk:
  ```
  @@ -47,6 +47,11 @@ post-hoc, in the script's own output (see §6).
   - `scripts/lib/` — all reusable logic. Import from here; do not reimplement.
   - `notebooks/` — exploration only. Nothing the final result depends on.
   - `docs/tasks/` — planning and review documents (see §9).
  +- `data/external/` — reference datasets from outside the MTHFR atlas
  +  itself, used as comparators (e.g. the GB1 fitness landscape). Gitignored
  +  like the rest of `data/`; each file's provenance (source record/URL and
  +  md5) is logged in the task doc or log entry that first fetched it — for
  +  GB1, script 49's docstring.
   
   ## 3. Statistical conventions — apply without being asked
  ```
  ` AGENTS.md | 5 +++++` / `1 file changed, 5 insertions(+)` /
  `hunks changed: 1`
  `git status --porcelain | grep -v "^??"` → only ` M AGENTS.md`
  (no other tracked file touched this session).
Verdict: PASS — the single authorized edit, made literally; diff shown.
Files created/modified:
- Modified: `AGENTS.md` (the one authorized change; nothing else in that
  file altered).
Anything unexpected or worth flagging:
- Per the S3 restriction, if anything else in AGENTS.md looks like it
  needs updating I must log it here instead of editing. One note for
  consideration (NOT edited): §7's rule about `.sh` heredoc deploy files
  and §2's `data/processed/` line don't mention `data/external/` — the
  new bullet covers the latter, and the former appears specific to an
  older deploy workflow; leaving both alone.
---

## [Y1] — Group A digest: inference validity (position-clustering, exclusion accounting)
Status: PASS
Time started / finished: 2026-09-22 23:19:56 / 2026-09-22 23:21
What I did:
- Ran the task's exact grep (`^## \[A1` / `^## \[A2` with -A 40) — it
  matched NOTHING (see unexpected section). Confirmed the log's actual
  heading format is `## A1a — Title` (no brackets), re-ran with the real
  pattern, then extracted Group A verbatim via `sed -n '40,163p'` (the
  exact span covering A1a, A1b, A1c, A2a, A2b — next section B1a begins
  line 164). Quote-only below; no reinterpretation.
Actual output (real numbers and quoted source text):
File: `docs/tasks/review-triage/OVERNIGHT_LOG.md`, 1,889 lines,
236,699 bytes (existence checked first, AGENTS §5). Five Group A
entries at lines 40/60/99/115/138.

**A1a** (line 40) — `Status: PASS (audit completed; one real convention
violation found — sign-flip nulls are cell-level)`:
- `resid = (13134, 4), M_se = (13134, 4) → every rng.choice([-1,1],
  size=Rs.shape) flips AT (variant × condition) CELL granularity` —
  cell-level flips in `scripts/21 line 138, scripts/24 line 140,
  scripts/26 line 135, scripts/28 line 172, scripts/33 line 100`;
  violates AGENTS §4 position-level rule. Script 33's NULL 2 IS
  position-block but is the weaker association null (correctly labeled).
  Second, smaller violation: `scripts/26 line 85 fake =
  rng.permutation(df["target"].to_numpy())` (row-level target shuffle).
  scripts/35: no resampling at all; scripts/39: labeled diagnostic.
- Verdict (verbatim): `All headline CIs are position-clustered as
  claimed. The gap is exactly what A1 flagged: script 33's sign-flip
  null is per-(variant, condition), i.e. too narrow. A1b reruns it at
  position-block granularity.`

**A1b** (line 60) — `Status: PASS — sanity checks pass at all three
granularities; the headline signed result SURVIVES position-block flips`:
- Analysis set `10757 variants, 654 positions`; N_PERM=10000 (49.96 s,
  smoke 200 = 2.4 s). Sanity all three granularities: `all+1 == own_e_b
  max|diff| = 2.220e-16` / `all-1 == -own_e_b max|diff| = 2.220e-16`.
- cell null: `observed=-0.0881  null mean=+0.0001 sd=0.0094
  p=<0.0001  excess over null=-0.0882  (-0.1% of the raw value is
  structural artifact)`; variant null: same observed, sd=0.0094,
  p=<0.0001; position null: `null mean=-0.0001 sd=0.0156 p=<0.0001`,
  `0.1% ... structural artifact`. CSV exact: `null_sd=0.009363847009825512`
  (cell), `0.009396789400773665` (variant), `0.015605782151827563`
  (position), all `p=0.0`, `null_centred=True`. Script-33 reference
  reproduced `null mean=+0.000067 sd=0.009364 p=0.0`. Granularity
  effect: position null sd 0.0156 = 1.66× the cell-level 0.0094.
- Verdict (verbatim): `log 5.3's signed-null significance SURVIVES
  position-block granularity: null centred, p<0.0001, artifact ≈0%.
  The reviewer's worry (too-narrow null) was legitimate in construction
  but does not overturn the result.` Caveat logged: `sign-flip null: it
  rules out the e.b-construction artifact only, NOT confounding`.

**A1c** (line 99) — `Status: PASS`:
- `paired_metric_difference_bootstrap(d, "position", ..., metric="mae")`
  with `cluster_col="position"`; resamples whole clusters →
  `PAIRED DIFFERENCES, cluster-bootstrapped by position (N_BOOT draws)`.
  Pooled row example: `ESM-2(A222V) vs ESM-2(WT): diff=
  +0.0005334660988103312, CI=[+0.00028835365805139276,
  +0.0007675630167030905], n=11113, n_clusters=654`.
- Verdict: `6.2/6.3 CIs are position-cluster bootstrapped as the house
  convention requires. No change needed.` Minor cosmetic gap noted:
  stratified (6.3) rows omit n_clusters (recording gap only).

**A2a** (line 115) — `Status: PASS — fully explained, and the exclusions
ARE systematically skewed (not a rounding artifact)`:
- Reproduction: `qcut(|e.b|, 3) ... {'low': 3586, 'high': 3586, 'mid':
  3585}` = 10,757, not 11,113; `11,113 − 10,757 = 356 rows have no e.b`;
  reviewer's 3,704 expectation = 11,113/3 (`3704 − 3586 = 118 ≈ 356/3`).
- Skew of the 356 dropped vs 10,757 kept: `mean base_functionality:
  0.6312 dropped vs 0.7377 kept (−0.107)`; `mean f_bar_wt: 0.6132 vs
  0.7547 (−0.141)`; region `%: dropped {1: 12.6, 2: 23.9, 3: 42.4,
  4: 21.1} vs kept {1: 24.0, 2: 22.5, 3: 25.2, 4: 28.3}` → `region 3
  overrepresented +17pp, region 1 halved`; missing A222V-arm conditions
  among dropped `{0: 85, 1: 13, 2: 18, 3: 240}` → `240/356 are missing
  3 of 4 m-conditions`; `mean delta_esm: +0.03316 dropped vs +0.03282
  kept (essentially identical — the ESM-side variable is NOT skewed)`.
  Rule check: `471/587 e.b-NA rows are explained by (≥3 m-conditions
  missing OR no WT-arm data)`; `116/587 are NOT explained`.
- Verdict (verbatim): `The missing ~118-per-stratum rows are rows the
  ATLAS could not fit e.b for (A222V-arm data sparsity), and the
  exclusion is systematically skewed toward LOWER fitness and region 3
  (42.4% vs 25.2%). Not a rounding artifact. Since strata define the
  6.3 headline test, its stratified set is a systematically different
  population than the pooled 6.2 set — worth stating in the writeup.
  delta_ESM itself is not skewed, so the skew acts through
  e.b-observability, not through the predictor.`

**A2b** (line 138) — `Status: PASS — every published n is reproduced by
a specific, explicit filter; no bug found`:
- The full reconciliation table (verbatim):
  `raw folate_response_model5.csv | 13,134 | all variant types`;
  `type == "substitution" | 11,902 | load_derived_maps(missense_only=True)`;
  `phase3_analysis_table (script 15) | 11,901 | inner join with
  esm2_wt_scores.csv — exactly 1 substitution has no ESM WT score`;
  `phase5_analysis_table (script 16 line 55) | 11,344 | dropna(model_A,
  model_B, model_C, target): −557 rows all have f_bar_a222v NaN`;
  `script 32 ... | 11,344 | dropna(delta_esm) only`;
  `script 34/36 analysis set | 11,113 | + dropna(f_bar_wt): −231 rows
  have ALL FOUR WT-arm conditions missing (verified: 231/231)`;
  `scripts 32-pairs / 33 / 35 / 6.3 strata | 10,757 | + require
  published e.b AND own_e_b: −356 ... own_e_b-missing set is IDENTICAL
  to e.b-missing set (587 = 587 = 587 overlap)`.
- Cross-checks: `task34_predictions.csv = 11,113 rows;
  task36_analysis_table.csv = 11,113; task32_analysis_table.csv =
  11,344; task35_summary.csv missense_n = 10,757 — all match`.
- Verdict (verbatim): `No contradiction, no dropped-row mystery:
  13,134 → 11,902 → 11,901 → 11,344 → 11,113 → 10,757, each step
  attributable. The only substantive caveat is the one A2a quantified:
  the last step (−356) is fitness/region-skewed, and 6.2 vs 6.3 use
  different sets.` Note flagged under troubleshooting #5: `the log
  presents 6.2 and 6.3 as one analysis while they differ by 356
  systematically-different rows. Logged both n's; MTHFR_RESULTS_LOG.md
  NOT edited.`
Verdict: PASS — Group A extracted verbatim; five entries all PASS as
originally logged; key cross-cutting facts to carry forward: sign-flip
nulls are cell-level (A1a finding, repaired for script 33 by A1b which
SURVIVED), 6.2 (n=11,113) and 6.3 (n=10,757) use different row sets with
fitness/region-3 skew in the −356 exclusion (A2a/A2b).
Files created/modified: `SESSION_LOG.md` (this entry only). The
OVERNIGHT_LOG.md was read, never modified.
Anything unexpected or worth flagging:
- Rule-6 assumption: the task's literal grep `^## \[A1` returns zero
  matches — OVERNIGHT_LOG.md headings have no brackets (`## A1a — …`).
  I used the actual heading format rather than fabricate output; the
  extraction window (sed 40–163) was verified to contain exactly A1a–
  A2b and nothing else (B1a starts at line 164).
- Content flag (not acted on): A1b's own caveat — a sign-flip null rules
  out only the e.b-construction artifact, not confounding — remains the
  standing limitation of the −0.088 result.
---

## [Y2] — Group B digest: delta_ESM confounds (flattening, compression, position-block null)
Status: PASS
Time started / finished: 2026-09-22 23:21:19 / 2026-09-22 23:22
What I did:
- Extracted Group B verbatim (`sed -n '164,277p'`) after confirming
  heading boundaries (B1a=164, B1b=200, B1c=229, B2=256, B3=266; next
  section S2=278). Quote-only; verdicts left exactly as logged.
Actual output (real numbers and quoted source text):
**B1a** (line 164) — `Status: PASS — does NOT collapse; the flattening
confound does not explain the correlation`:
- Pre-registered collapse criterion in script 43's docstring:
  `|partial| < 50% of |raw| = COLLAPSE`. Spline df=4 per covariate on
  ranks, refit inside every bootstrap draw, n=10,757 / 654 positions,
  N_BOOT=10000 (3:55.82).
- Results (verbatim):
  `own_e_b | ctrl esm2_score+base_functionality: raw rho=-0.0881
  partial rho=-0.0828 CI=[-0.1158,-0.0502] p_boot=<0.0001
  |partial|/|raw| = 0.940  -> does NOT collapse`;
  `own_e_b | ctrl esm2_score+f_bar_wt: partial rho=-0.0853
  CI=[-0.1185,-0.0525] |partial|/|raw| = 0.968  -> does NOT collapse`;
  `GI_folinate_independent | ctrl esm2_score+base_functionality:
  raw rho=-0.0707 partial rho=-0.0786 CI=[-0.1114,-0.0459]
  ratio = 1.111  -> does NOT collapse (partial is LARGER than raw)`;
  `GI | ctrl esm2_score+f_bar_wt: partial rho=-0.0803
  CI=[-0.1128,-0.0480] ratio = 1.136  -> does NOT collapse`.
- Verdict (verbatim): `Pre-registered criterion NOT met — the partial
  correlation retains 94-114% of the raw value under nonlinear control
  of both S(v|WT) and either w.fitness measure. The review's worry
  ("the story is really both tracking deleteriousness independently")
  is NOT supported by this test. The negative direction survives
  controlling for deleteriousness.`
- Flags it carried: p-value bug fixed BEFORE the full run and disclosed
  (`initial smoke used |boot|>=|obs| against the CI distribution, which
  is meaningless ... replaced with the house convention from
  stats._summarize, p = 2·min(frac≤0, frac≥0)`); part-whole caveat
  (w.fitness sits inside e.b's expectation → NON-collapse is the more
  meaningful direction); `e.b correlates POSITIVELY with S(v|WT)
  (+0.085)`; indirect path through S would induce only ~−0.03 of −0.088.

**B1b** (line 200) — `Status: PASS (test run; answer: a real monotone
relation exists but the compression form explains little variance — it
is not the whole story)`:
- `Spearman(delta_ESM, S(v|WT)): rho=-0.3238 CI=[-0.3653,-0.2803]
  p=<0.0001 n=10757`; `OLS delta = -0.01820 + -0.00698 * S  R^2=0.0645`;
  `through-origin delta = -0.00514 * S  R^2=0.0584`; slope →
  `k = 0.00698`. Deciles essentially monotone: `d0 mean_S=-13.95592
  mean_delta=+0.08477` … `d9 mean_S=+0.26069 mean_delta=-0.01131`.
- Verdict (verbatim): `delta_ESM IS monotonically related to S(v|WT)
  (rho=−0.324, CI excludes zero, deciles essentially monotone ...) —
  consistent with SOME compression-toward-zero structure when V222 is
  supplied. But the linear compression form fits weakly (R²=0.0645;
  through-origin R²=0.0584), so delta is NOT well described as −k·S
  alone. Combined with B1a ..., the S-relation does not account for the
  e.b correlation.`

**B1c** (line 229) — `Status: PASS (REDUCED-RESOLUTION: 500 of 656
positions — see note)`:
- Script 44, pre-registered rule: `generic flattening supported iff
  mean dH>0 AND position-bootstrap CI excludes 0`. Timing: `10 forwards
  ... 0.545 s each ... 1,312 forwards ≈ 11.9 min > 10-min budget` →
  ran `N_POS=500` (9:52.59).
- Output verbatim: `IDENTITY CHECK: |dH| at position 222 = 0.000e+00 —
  passed.` / `mean H_WT = 0.78904 nats   mean H_A222V = 0.79103 nats` /
  `mean dH = +0.001992 nats  CI=[-0.000123,+0.004106]  p_boot=0.0678` /
  `effect size: mean dH / mean H_WT = +0.00252 (+0.252%)` /
  `fraction of positions with dH > 0: 0.5940` /
  `-> flattening NOT supported by this test (CI includes 0 or mean <= 0)`.
- Verdict (verbatim): `Per the pre-registered rule, GENERIC FLATTENING
  IS NOT SUPPORTED ... This is a NULL RESULT and it is reported as such
  — B1's flattening confound does not explain delta_ESM's behavior at
  the distribution level either.` Its own caveat: `p=0.0678 is close
  enough to 0.05 that a full 656-position rerun ... could plausibly tip
  either way — rerun at full N before quoting externally.`

**B2** (line 256) — `Status: PASS — executed as A1a/A1b (B2a says
"already covered by A1a/A1b"; logged here for visibility ...)`:
- Position-block sign-flip, N_PERM=10,000: `observed=−0.0881, null
  mean=−0.0001, null sd=0.0156, p=<0.0001, excess=−0.0881,
  frac_artifact=0.0005687369964375577 (~0.1%), null centred (3 SE check
  passed). All identity checks max|diff|=2.220e-16.`
- Verdict (verbatim): `The "~0% artifact" claim in 5.3 SURVIVES
  position-block granularity — null sd widens 1.66× (0.0094 → 0.0156)
  but the observed value is far outside it. ... B2 does NOT overturn
  5.3.`

**B3** (line 266) — `Status: PARTIAL — corrected wording DRAFTED here;
not applied (MTHFR_RESULTS_LOG.md is user-owned and was not touched
tonight, per instructions)`:
- The drafted replacement for 5.3's closing paragraph (verbatim, key
  sentences): `A sign-flip null on a signed variable centers on zero by
  construction; what it rules out is specifically the e.b-construction
  artifact — the same failure mode that accounted for 77-82% of every
  earlier result — and nothing more. It does not rule out confounding
  ... and is not, on its own, evidence of real epistasis. Re-run at
  position-block granularity per AGENTS.md §3/4 (script 42), the signed
  result survives unchanged: null sd widens from 0.0094 to 0.0156,
  p < 0.0001 at 10,000 draws, structural artifact ≈ 0.1%.`
- Verdict (verbatim): `Draft fulfills both; application is blocked by
  ownership instructions.` Its extra flag: `5.2's "-0.088 (published)"
  should be −0.071 — both need the user's edit together`.
Verdict: PASS — Group B extracted verbatim. As-logged outcomes: B1a
NON-collapse (94-114% retained), B1b weak compression (R²=0.0645),
B1c null at REDUCED resolution (500/656, p=0.0678), B2 "~0% artifact"
survives position-block null, B3 PARTIAL (draft ready, not applied —
user-owned file).
Files created/modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- Two standing open items inherited from B3 (not mine to act on): the
  drafted 5.3 wording has never been applied to MTHFR_RESULTS_LOG.md,
  and 5.2's `-0.088 (published)` should read −0.071 — flagged for the
  user, per troubleshooting rule 5 (log both, don't edit).
- B1c's own warning to carry: do not quote its p=0.0678 externally
  without a full 656-position rerun.
---

## [Y3] — Group C digest: rank-vs-MAE reconciliation (highest-priority item; FULL C1a table quoted)
Status: PASS
Time started / finished: 2026-09-22 23:22:06 / 2026-09-22 23:24
What I did:
- Extracted all of Group C verbatim (`sed -n '307,656p'`), confirmed
  boundaries first (C1a=307, C1b=396, C1c=432, C1d=455, C2a=470,
  C2b=523, C2c=546, C3a=575; next section E1a=657). The C1a span alone
  is 89 lines — deliberately extracted whole so the FULL reconciliation
  table is captured, per the task's explicit instruction (not the
  summary line). Quote-only below; no reinterpretation.
Actual output (real numbers and quoted source text):
**C1a** (line 307) — `Status: PASS — table built to spec (the spec's 6
row-predictors + Grantham added as a 7th because C1c needs it; all 3
targets, all 3 metrics, low/mid/high + all)`. Pre-registered: analysis
set `10757 variants, 654 positions (expected 10,757 — mismatch would be
a red flag)`; strata for the table = `pd.qcut |e.b| terciles (identical
to script 34 / log 6.3)`; strata for the gap tests = `script 30's
quantile digitize`; MAE/MSE on `cross-fit isotonic calibration pred→
target, position-held-out 5 folds`; matched synthetic = `script 30's
exact recipe: α·z(w.fitness) + sqrt(1−α²)·N(0,1)`, `Canonical matched
alpha (to S_A222V low-stratum rho=+0.5283): 0.5811`; smoke N_BOOT=50
3.5 s → full N_BOOT=2000 90 s.

FULL reconciliation table, verbatim (rank=Spearman; MAE/MSE on cross-fit
isotonic) — every row as produced:
```
predictor          target         metric          all          low          mid         high
S_WT               A222V_fitness  rank         0.3684       0.5325       0.3521       0.1726
S_WT               A222V_fitness  mae          0.2177       0.2108       0.1923       0.2500
S_WT               A222V_fitness  mse          0.0700       0.0624       0.0550       0.0926
S_WT               e.b            rank         0.0699       0.0999       0.0403       0.0600
S_WT               e.b            mae          0.1770       0.0350       0.1185       0.3774
S_WT               e.b            mse          0.0652       0.0018       0.0158       0.1780
S_WT               w.fitness      rank         0.3280       0.5228       0.3377       0.0841
S_WT               w.fitness      mae          0.3855       0.3710       0.3471       0.4384
S_WT               w.fitness      mse          0.2277       0.1931       0.1836       0.3063
S_A222V            A222V_fitness  rank         0.3650       0.5283       0.3486       0.1713
S_A222V            A222V_fitness  mae          0.2183       0.2120       0.1927       0.2502
S_A222V            A222V_fitness  mse          0.0703       0.0629       0.0552       0.0926
S_A222V            e.b            rank         0.0692       0.0989       0.0401       0.0591
S_A222V            e.b            mae          0.1770       0.0350       0.1186       0.3775
S_A222V            e.b            mse          0.0652       0.0018       0.0159       0.1781
S_A222V            w.fitness      rank         0.3252       0.5188       0.3344       0.0840
S_A222V            w.fitness      mae          0.3865       0.3729       0.3478       0.4389
S_A222V            w.fitness      mse          0.2285       0.1945       0.1843       0.3067
delta_ESM          A222V_fitness  rank        -0.2397      -0.3155      -0.2340      -0.1038
delta_ESM          A222V_fitness  mae          0.2328       0.2386       0.2056       0.2541
delta_ESM          A222V_fitness  mse          0.0767       0.0766       0.0605       0.0930
delta_ESM          e.b            rank        -0.0707      -0.0980      -0.0533      -0.0787
delta_ESM          e.b            mae          0.1772       0.0364       0.1181       0.3770
delta_ESM          e.b            mse          0.0651       0.0020       0.0159       0.1774
delta_ESM          w.fitness      rank        -0.1877      -0.3013      -0.2046       0.0032
delta_ESM          w.fitness      mae          0.4095       0.4193       0.3714       0.4380
delta_ESM          w.fitness      mse          0.2467       0.2349       0.2023       0.3030
matched_synthetic  A222V_fitness  rank         0.3184       0.5185       0.4336      -0.0329
matched_synthetic  A222V_fitness  mae          0.2254       0.2184       0.1877       0.2701
matched_synthetic  A222V_fitness  mse          0.0734       0.0655       0.0518       0.1030
matched_synthetic  e.b            rank        -0.1435       0.0698      -0.0733      -0.3256
matched_synthetic  e.b            mae          0.1791       0.0554       0.1185       0.3634
matched_synthetic  e.b            mse          0.0627       0.0046       0.0177       0.1658
matched_synthetic  w.fitness      rank         0.5638       0.5552       0.5387       0.5656
matched_synthetic  w.fitness      mae          0.3363       0.3457       0.3151       0.3482
matched_synthetic  w.fitness      mse          0.1724       0.1739       0.1497       0.1934
BLOSUM62           A222V_fitness  rank         0.1603       0.2306       0.1699       0.0550
BLOSUM62           A222V_fitness  mae          0.2390       0.2503       0.2087       0.2580
BLOSUM62           A222V_fitness  mse          0.0794       0.0818       0.0615       0.0949
BLOSUM62           e.b            rank         0.0278       0.0471       0.0330       0.0203
BLOSUM62           e.b            mae          0.1774       0.0355       0.1186       0.3783
BLOSUM62           e.b            mse          0.0652       0.0017       0.0156       0.1783
BLOSUM62           w.fitness      rank         0.1443       0.2352       0.1444       0.0290
BLOSUM62           w.fitness      mae          0.4167       0.4354       0.3774       0.4373
BLOSUM62           w.fitness      mse          0.2519       0.2468       0.2057       0.3031
Grantham           A222V_fitness  rank        -0.1107      -0.1506      -0.1160      -0.0400
Grantham           A222V_fitness  mae          0.2414       0.2540       0.2113       0.2587
Grantham           A222V_fitness  mse          0.0805       0.0841       0.0625       0.0949
Grantham           e.b            rank        -0.0156      -0.0426      -0.0170      -0.0147
Grantham           e.b            mae          0.1776       0.0357       0.1187       0.3784
Grantham           e.b            mse          0.0653       0.0018       0.0157       0.1783
Grantham           w.fitness      rank        -0.1021      -0.1558      -0.1011      -0.0247
Grantham           w.fitness      mae          0.4196       0.4418       0.3805       0.4365
Grantham           w.fitness      mse          0.2544       0.2535       0.2079       0.3018
w.fitness          A222V_fitness  rank         0.5687       0.9056       0.8183      -0.0353
w.fitness          A222V_fitness  mae          0.1762       0.1107       0.1239       0.2939
w.fitness          A222V_fitness  mse          0.0528       0.0179       0.0231       0.1174
w.fitness          e.b            rank        -0.2393       0.1677      -0.1007      -0.5690
w.fitness          e.b            mae          0.1746       0.0766       0.1204       0.3267
w.fitness          e.b            mse          0.0552       0.0084       0.0201       0.1371
w.fitness          w.fitness      rank         1.0000       1.0000       1.0000       1.0000
w.fitness          w.fitness      mae          0.0000       0.0000       0.0000       0.0000
w.fitness          w.fitness      mse          0.0000       0.0000       0.0000       0.0000
```
(`Saved table to .../data/processed/task45_c1_table.csv`.)
- C1a verdict (verbatim): `PASS. n=10,757 and 654 positions exactly as
  pre-registered — and 654 is the same position count A1b/A1c logged ...
  The table reconciles log 4.5 vs 6.3 in one view: in the high stratum
  S_A222V rank = +0.1713 while its matched synthetic is −0.0329 and even
  w.fitness itself is −0.0353 — the high-stratum ESM rank signal is
  essentially the only positive entry of its kind in that column, which
  is exactly the tension C2/C3 must now quantify.`
- C1a's warnings (verbatim): `The e.b-target MAE/MSE cells are PARTLY
  DEFINITIONAL: the strata are terciles of |e.b| ... Do not quote
  e.b-MAE-across-strata as a finding.` /
  `matched_synthetic vs w.fitness rank = 0.5638 is true by
  construction (the anchor is z(w.fitness)); only the synthetic's
  A222V-fitness column carries information.`

**C1b** (line 396) — `Status: PASS — executed; verdict = retention is
NOT background-specific (the review's suspected answer, confirmed)`:
- Gap table (verbatim): `S_A222V +0.5283/+0.5185 alpha 0.5811 high
  +0.1713 syn_high −0.0329 gap +0.2042`; `S_WT +0.3325... ` [as logged:
  `S_WT +0.5325 +0.5188 0.5855 +0.1726 −0.0193 +0.1919`]; bootstrap:
  `S_A222V gap +0.2042 boot_mean +0.1936 CI [+0.1333, +0.2532]`;
  `S_WT gap +0.1919 boot_mean +0.1948 CI [+0.1366, +0.2542]`.
  Decisive line: `C1b: gap(S_A222V) - gap(S_WT) = +0.0124 (boot mean
  -0.0012) CI=[-0.0375,+0.0370] p=0.9630  -> RETENTION IS NOT
  BACKGROUND-SPECIFIC (CI includes 0)`.
- Verdict (verbatim): `S_WT — ESM-2 on the WT sequence alone, no
  background supplied — retains +0.1919 over its matched synthetic in
  the high stratum vs S_A222V's +0.2042. ... log 4.5's "retention" has
  nothing to do with background info — it is independence from WT-arm
  measurement noise.` Limitation logged: synthetic is a single seed-0
  draw (bootstrap refits α but keeps the noise draw fixed).

**C1c** (line 432) — `Status: PASS for BLOSUM62 (clean matched test,
POSITIVE result); Grantham row = METHOD LIMITATION (α-matching
impossible), reported as a limitation, NOT as a result`:
- `gap(BLOSUM62) = +0.0691 CI=[+0.0142,+0.1146] SIG>0 (also beats its
  synthetic); gap(S_A222V)-gap(BLOSUM62) CI=[+0.0626,+0.1950]`;
  `gap(Grantham) = -0.0779 CI=[-0.0841,+0.0111] not > 0;
  gap(S_A222V)-gap(Grantham) CI=[+0.1452,+0.3123]`.
- Verdict (verbatim): BLOSUM62 `ALSO beats its matched synthetic in the
  high stratum. This SUPPORTS the review's suspicion: part of script
  30's "beat" is generic noise-sharing with the w.fitness anchor, not
  epistasis detection.` / `Both facts stand side by side: ... a real
  generic component AND a real ESM-specific excess on top of it.
  Neither fact cancels the other.` Grantham: `α pinned at the bisection
  floor 0.0000 ... measured against an UNMATCHED synthetic and is not
  interpretable ... recorded as-is, not worked around post-hoc`.
- Warning (verbatim): `Do NOT quote Grantham's −0.0779 as "Grantham
  fails to beat its synthetic" — the match never happened.`

**C1d** (line 455) — `Status: PASS — 0.999636 ≥ 0.99, exactly the
threshold the task specified`:
- `Spearman = 0.999636  (n=10757)  -> 0.99+ : the MAE story rests on a
  small number of rank swaps`.
- Verdict (verbatim): `6.2's MAE story is a small number of rank swaps,
  not a broad pattern ... The MAE difference can be simultaneously
  statistically solid (CI excludes 0) and substantively tiny (rho
  0.9996); both should be quoted together, per AGENTS §3`.

**C2a** (line 470) — `Status: PASS — executed; pre-registered verdict
MIXED (substantial proximity contribution, but NOT "a few dozen
near-222 variants account for it")`:
- Gate: `GATE G1: pooled MAE diff = +0.000533466098810331 (published
  +0.000533466098810331, |diff| = 0.000e+00)`; internal identity
  `4.218e-17`; `variants at position 222 exactly: 0`.
- Bands: `0-25 n=870 sum +1.3753 share 23.20% mean +1.581e-03`;
  `26-100 n=2546 +2.5593 43.17% +1.005e-03`; `>100 n=7697 +1.9937
  33.63% +2.590e-04` → `PRIMARY RULE: share within |pos-222|<=25 =
  23.20%  -> MIXED`. Top contributors: `top 10 = 13.59%`;
  `top 25 = 26.53%`; `top 50 = 43.56% (12 near-222 vs expected 3.9)`;
  `top 100 = 73.68%`; `leave-one-position-out diff: min=+0.000474
  max=+0.000550 (full=+0.000533)`; `SECONDARY drop-zone refit ... diff
  = +0.000361 = 67.6% of full -> SURVIVES`. Top single variant:
  `p.Val194Tyr c=+0.1271`.
- Verdict (verbatim): `MIXED, with a clear distance-decay structure ...
  the +0.00053 is proximity-ENRICHED (consistent with 5.4 as a
  contributor) but not proximity-DOMINATED; "background info hurts
  broadly" survives in weakened form — the effect is distributed with a
  gradient, not local to a few dozen variants.`

**C2b** (line 523) — `Status: PASS — SEED-ROBUST (the review's concern
does not materialize)`:
- `cross-seed diffs: mean=+0.0004980 sd=0.0000528 min=+0.0003966
  max=+0.0006214 (seed 0 = published +0.0005335)`; `published CI
  half-width = 0.0002396`; `sd / CI half-width = 0.220; seeds flipping
  sign (diff <= 0): 0/50`; `combined sd = sqrt(boot_sd^2 + seed_sd^2)
  = 0.0001332 (boot_sd alone = 0.0001222)` → `VERDICT: SEED-ROBUST`.
- Verdict (verbatim): `one seed WAS representative`; quadrature adds
  `9% increase — negligible`. Scope note: only fold-assignment seed at
  n_folds=5 varies, not fold count or calibration family.

**C2c** (line 546) — `Status: PASS — HOLD (verdict unchanged under the
squared-error loss)`:
- `strata formed on n=10757 (11,113 minus 356 rows with null e.b — the
  A2a/A2b n-chain)`; `GATE G2: high-stratum MAE diff =
  +0.002408919531324 (published +0.002408919531324, |diff| = 0.000e+00)`;
  high stratum: `MAE diff=+0.00241 CI=[+0.00155,+0.00321]`;
  `MSE diff=+0.002320 CI=[+0.001740,+0.002895]` → `HIGH-STRATUM VERDICT
  UNDER MSE: HOLD (MSE CI_lo > 0: ESM-2 still worse than null)`.
- Verdict (verbatim): `the magnitude is within 4% of the MAE diff
  (+0.00232 vs +0.00241). All three strata give the same verdict under
  both losses ... 6.3 survives the MSE re-check intact.`
- Cross-doc sign note (verbatim): `MTHFR_RESULTS_LOG 6.3 reports
  +0.00241 ("ESM-2 WORSE"); REVIEW_TRIAGE C3a calls it "−0.00241 loss"
  (loss phrasing). Same quantity, opposite sign conventions — logged
  here so both numbers exist in one place; neither document was edited.`

**C3a** (line 575) — `Status: PASS — ceiling computed and USABLE
(pre-registered CI rule met); disattenuation verdict = MATERIALLY LARGER
(pre-registered ratio rule met, narrowly — magnitude caveat in the
verdict)`:
- Gates: `GATE G3 (rho own_e_b): got -0.088118064248917 (published
  -0.088118064248917, |diff| = 0.000e+00) -> OK`; `GATE G4 (rho
  published e.b): got -0.070705162222287 ... 0.000e+00 -> OK`; `GATE G5
  (rebuilt vs CSV own_e_b): n=10757, max|diff| = 2.220e-16 -> OK`.
- Reliability (computed, not assumed): `1 - var(syn 0.02111, n=570) /
  var(analysis 0.05804) = 0.6363` (own); `= 0.6193` (published);
  `review's assumed ~0.64 -> own flavor 0.636 (MATCHES)`.
- Oracle: `MAE(multiplicative null) = 0.2210`;
  `MAE(implied) alone = 0.1847`; `PRIMARY oracle (published, reading a),
  POOLED: improvement over null = +0.0366 CI=[+0.0309,+0.0424] ->
  ceiling USABLE`; `PRIMARY oracle, HIGH stratum: improvement =
  +0.0521 CI=[+0.0436,+0.0613]`; ESM-2 vs ceiling: `pooled: +0.000308
  = +0.84% of ceiling`; `high: -0.002409 = -4.62% of ceiling`.
- Decomposition (verbatim): `Measured-fitness component = MAE(null) −
  MAE(implied) = 0.2210 − 0.1847 = +0.0363 of the +0.1385 zero-noise
  pooled ceiling; interaction adds ... +0.1022 zero-noise, but only
  +0.0021 under the primary reading (a) ... Under the primary reading,
  the usable ceiling is therefore dominated by measured-fitness
  knowledge; the interaction-specific slice is small.`
- Disattenuation: `r_dis = rho / sqrt(rel) = -0.110413 ... CI
  [-0.147534, -0.072340] |r_dis|/|rho| = 1.2530 [pre-registered
  threshold 1.25] VERDICT: MATERIALLY LARGER`.
- Verdict (verbatim): `the correction buys +25.3% on the magnitude ...
  but the corrected correlation is still |r| ≈ 0.11, which is weak in
  absolute terms. Measurement-error correction does not rescue
  delta_ESM's correlation into a strong one; it moves a weak nonzero
  effect up by a quarter.` Plus: `Report as "meets the bar narrowly,"
  not as a comfortable pass.` and `CIRCULARITY ... the oracle SIZES THE
  CEILING ... it is NOT an achievable model and must not be quoted as
  one.`
Verdict: PASS — Group C extracted verbatim including the FULL C1a
reconciliation table (84 rows, quoted above in full). As-logged
outcomes: C1a table built to spec (n=10,757/654; high-stratum
S_A222V rank +0.1713 vs synthetic −0.0329); C1b retention NOT
background-specific (diff +0.0124, CI [−0.0375,+0.0370], p=0.9630);
C1c BLOSUM62 also beats its synthetic (+0.0691 [ +0.0142,+0.1146]) but
ESM's excess over it also excludes 0; C1d rho=0.999636 (MAE story =
rank swaps); C2a MIXED (proximity-ENRICHED, not -DOMINATED; drop-zone
refit 67.6% SURVIVES); C2b SEED-ROBUST (sd 0.22× CI half-width, 0/50
flips); C2c HOLD under MSE (+0.002320 [+0.001740,+0.002895]); C3a
ceiling USABLE (+0.0366 [+0.0309,+0.0424]) and disattenuation
MATERIALLY LARGER (−0.0881 → −0.1104, ratio 1.2530, narrowly ≥1.25).
Files created/modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- Carry-forward caveats attached to the quoted numbers: e.b-target
  MAE/MSE cells are partly definitional (C1a); synthetic = single seed-0
  draw (C1b/C1c); Grantham gap is unmatched, never quoteable as a
  result (C1c); oracle is in-sample/circular, sizes a ceiling only
  (C3a); disattenuation bar cleared by 0.0030 — "narrowly" (C3a).
- The 6.3 sign-convention split between MTHFR_RESULTS_LOG (+0.00241
  WORSE) and REVIEW_TRIAGE (−0.00241 loss) is recorded in C2c — same
  quantity, both docs left unedited (troubleshooting rule 5).
---

## [Y4] — Group D digest: stratifier winner's-curse checks (D1a, D1b, D1c)
Status: PASS
Time started / finished: 2026-09-22 23:23:14 / 2026-09-22 23:25
What I did:
- Extracted Group D verbatim (`sed -n '864,998p'`), boundaries first
  (D1a=864, D1b=903, D1c=964; next section F1a=999). Quote-only.
Actual output (real numbers and quoted source text):
**D1a** (line 864) — `Status: PASS — ENRICHED: the high-|e.b| tercile
carries 65.4% higher mean SE(e.b) than the low tercile (0.1166 vs
0.0705) ... The review's winner's-curse suspicion is CONFIRMED as a
property of the stratifier.` Full run 2026-09-22 07:11 (N_BOOT=2000,
11.6 s):
- `low n=3586 mean SE=0.0705 median SE=0.0562 share top-SE=0.243`;
  `mid n=3585 0.0757/0.0591/0.284`; `high n=3586 0.1166/0.0769/0.473`
  (1/3 = no enrichment);
  `PRIMARY D = mean(SE|high) - mean(SE|low) = +0.0461 CI=[+0.0396,
  +0.0535] (2000/2000 valid, 654 positions)`; `effect size:
  mean_SE_high / mean_SE_low = 1.654 (+65.4%)`;
  `D1a VERDICT (pre-registered rule): ENRICHED`; `secondary
  Spearman(|GI|, SE) = +0.2650 CI=[+0.2406, +0.2901]`; sensitivity
  `D = +0.0436 CI=[+0.0370, +0.0510]; stratum agreement own vs GI =
  0.822 → ENRICHED (not verdict-bearing)`.
- Verdict (verbatim): `the high-|e.b| stratum ... is drawn from a
  measurably noisier population than the low stratum. Under winner's
  curse this is exactly the pattern expected` / `This is a STRATIFIER
  defect, not yet a VERDICT defect` / caveat: `SE(e.b) and e.b come
  from the same WLS fit, so this association is the winner's-curse
  signature, not a causal claim` and analytic SEs are miscalibrated
  (3.76×), so `the enrichment statistics are RELATIVE`.
- Disclosed pre-run fixes: first smoke crashed on the identity check
  passing one column name for both arms (fixed by aliasing; `the check
  never produced a statistic, so nothing was tuned`); D1a summary-row
  schema split into `_stats.csv` before the full run.
- The 10,757 coincidence resolved: script 35's valid-SE missense rows
  and the 6.3 s-set are `the SAME set (hgvs symmetric difference = 0)`.

**D1b** (line 903) — `Status: PASS — UNCHANGED-HOLD: under EB-shrunken
|e.b| terciles the high-stratum MAE diff is +0.001851 with CI
[+0.000987, +0.002706] (excludes 0, ESM-2 still worse than the
no-interaction null) — 6.3's verdict holds even though shrinkage purges
the high stratum of the D1a high-SE enrichment (its mean SE falls from
0.1166 to 0.0788, and the SE gradient INVERTS ...). The winner's-curse
enrichment D1a confirmed does not carry 6.3's verdict.`
- Gate: `G2: arm-1 high-stratum MAE diff = +0.002408919531324 (6.3 =
  +0.002408919531324, |diff| = 0.000e+00)`; EB prior
  `tau^2 = 0.035890` from `0.058036 − 0.022146`; `shrink factor:
  min=0.003 median=0.901 max=0.994; spearman(raw, shrunk) = 0.9861`.
- Three arms, high strata: arm1 `+0.002409 CI=[+0.001551,+0.003208]`;
  arm2 `+0.001726 CI=[+0.000753,+0.002595]`; arm3 `+0.001851
  CI=[+0.000987,+0.002706]` (MSE `+0.002199 CI=[+0.001606,+0.002807]`)
  → all three `HOLD (CI_lo>0: ESM-2 worse)`.
- Agreement: `arm1 vs arm2: 0.822 (712 rows enter/leave)`;
  `arm2 vs arm3: 0.893 (724)`; `arm1 vs arm3: 0.781 (1056)`.
- `D1b VERDICT (pre-registered, arm3 MAE CI): UNCHANGED-HOLD`.
- Verdict (verbatim): `shrinkage does exactly what the winner's-curse
  concern predicts mechanically — high-SE estimates shrink most ...
  The 6.3 verdict survives in a high stratum that has been purged of
  the D1a enrichment. That is the strongest form of "the verdict doesn't
  ride on the noise."` Effect size: `arm3's high-stratum MAE diff
  (+0.001851) is 77% of the original arm1 value (+0.002409)`.
  Reporting rule (verbatim): `Read D1a and D1b together ... Reporting
  D1a alone would leave the false impression 6.3 is damaged; reporting
  D1b alone would hide a real stratifier defect.`

**D1c** (line 964) — `Status: PASS — two pre-registered verdicts:
(1) HETEROSCEDASTICITY HIGHER: sd(e.b|nonsense) = 1.184 ×
sd(e.b|synonymous), CI [1.025, 1.371] excludes 1 ...; (2) FLOOR NOT
CLEARED: the entry bar into 6.3's high tercile (cut23 = 0.1830) is only
1.064 × the nonsense noise SD, CI [0.948, 1.207] ...`
- Row accounting: `13,134 rows ... counts gated: 11,902 substitution /
  624 nonsense / 608 synonymous` → `11,865 of 13,134 rows survive;
  drops: 1,145 substitution, 38 synonymous, 86 nonsense`; surviving
  10,757 `VERIFIED identical to the 6.3 s-set (hgvs symmetric
  difference = 0)`.
- Floor table as originally logged (old flag column): `synonymous n=570
  sd(e.b)=0.1453 median SE=0.0387 p95|e.b|=0.3088 calib=3.76
  epistatic_N2 pass=44.7%`; `nonsense n=538 0.1720/0.0780/0.4284/2.21
  pass=14.5%`; `missense n=10757 0.2409/0.0629/0.5278/3.83 pass=44.8%`.
- `PRIMARY R = sd(e.b|nonsense)/sd(e.b|synonymous) = 1.184
  CI=[1.025, 1.371] (2000/2000 valid) → HIGHER`; `cut23(|own_e_b|,
  missense) = 0.1830 / sd(nonsense) = 0.1720 -> ratio 1.064
  CI=[0.948, 1.207] → NOT CLEARED (CI_hi < 2)`.
- Verdict (verbatim): `variants barely into the "high interaction"
  tercile cannot be distinguished from dead-end noise on magnitude
  alone — claims about the HIGH stratum as a whole should lean on
  D1b's shrunken re-stratification` + scope limit: `the floors live at
  the fitness-range extremes ... that is the design's point ... AND the
  reason the ratio is not apples-to-apples with intermediate-fitness
  noise.`
- Cross-checks (verbatim): `the synonymous calibration ratio recomputes
  to 3.76 ... EXACTLY the empirical factor J4a/script 35 refer to,
  while nonsense calibrates at 2.21 and missense at 3.83: the analytic
  SE's miscalibration is itself type-dependent, which is a direct
  empirical argument for J4's FDR-per-type approach`; and `at script
  35's N=2 threshold, missense pass rate (44.8%) is essentially
  identical to the synonymous FPR (44.7%) ... while nonsense passes at
  only 14.5%`.
- Disclosed smoke-catch bug: `the floor-ratio bootstrap's denominator
  used sd(|nonsense e.b|) (absolute values) while the point estimate
  used sd(signed e.b) — the CI [1.190, 1.564] excluded its own point
  estimate 1.064 ... fixed to signed before the full run ... no verdict
  moved (NOT CLEARED both before and after)`.
- Asymmetric drops: `nonsense loses 13.8% (86/624) to non-computable SE
  vs synonymous 6.2% (38/608)` → `the floor is therefore (if anything)
  an UNDERestimate of dead-end noise, which makes NOT CLEARED
  conservative`.
Verdict: PASS — Group D extracted verbatim. As-logged outcomes: D1a
ENRICHED (D +0.0461 [+0.0396,+0.0535], ratio 1.654, shares
0.243→0.284→0.473); D1b UNCHANGED-HOLD (arm3 +0.001851
[+0.000987,+0.002706], G2 = 0.000e+00, 1,056 rows churned); D1c HIGHER
(R 1.184 [1.025,1.371]) and FLOOR NOT CLEARED (1.064 [0.948,1.207]).
Files created/modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- Cross-session link (troubleshooting rule 5, both logged, nothing
  edited): D1c's quoted `epistatic_N2 pass = 44.7% / 14.5% / 44.8%`
  rows are the OLD flag's rates — exactly the values my S2 rerun
  reproduced byte-for-byte in the `*_PRE_MIGRATION` backups before
  replacing them with `epistatic_ecdf` rates (5.1% / 8.9% / 16.6%).
  The OVERNIGHT_LOG records the old column truthfully; the migration is
  documented in this session's S2 entry. Anyone reading both must know
  the flag column changed between them.
- D1b's inherited note: read D1a+D1b together — the pair, not either
  alone, is the reportable unit.
---

## [Y5] — Group E digest: two-trait domain-vs-region boundary test (E1a, E1b)
Status: PASS
Time started / finished: 2026-09-22 23:23:53 / 2026-09-22 23:25
What I did:
- Extracted Group E verbatim (`sed -n '657,800p'`), boundaries first
  (E1a=657, E1b=728; next section I1=801). Quote-only. Y5a also asks
  for a note on whether this pre-empted or reinforced the two-trait
  MoCHI refit motivation — the log's own sentence on that is quoted
  below.
Actual output (real numbers and quoted source text):
**E1a** (line 657) — `Status: PASS — gate reproduced EXACTLY (means and
CIs), then DOWNGRADED under the pre-registered effect-size floor: 4 of
7 CI-passing groups fall below 0.10; the review's own question
(disagreement magnitude vs e.b's SD ~0.24) answered directly —
per-domain offsets 0.11-0.17 of e.b. SD, the between-domain GRADIENT
only 0.061 of e.b. SD`. Full run 1.03 s (N_BOOT=2000/N_PERM=10000).
- Gate: all 12 group means reproduced `max mean_diff 6.245e-17`, ns
  exact `(4980/4849/613/609, 2622/2506/2864/3121, 4816/4713/607/561)`,
  CIs `≤9.368e-17` → `GATE PASSED` (which `pins script 36's unrecorded
  N_BOOT at 2000 with seed 0`).
- Denominators: `rank_resid {sd_row: 0.268631, sd_pos: 0.092248} |
  disagreement {sd_row: 0.037800, sd_pos: 0.014058, sd_eb: 0.240907}`;
  PRIMARY = `LARGEST candidate (conservative reading ...)`;
  floor 0.10 `post-hoc — chosen after the review had already quoted
  "~0.03-0.04 vs SD 0.24"` (disclosed, bands printed).
- Effect-size table (es_PRIM): domain_rank_resid Catalytic 0.078
  EXCL0, Regulatory 0.019 crosses, Ser-Rich 0.331 EXCL0, unassigned
  0.134 EXCL0; region_rank_resid r1 0.097, r2 0.116, r3 0.062,
  r4 0.069 (all EXCL0); disagreement_domain Catalytic 0.113,
  Regulatory 0.160, Ser-Rich 0.174, unassigned 0.172. Gradients:
  `disagreement_domain span=0.01471 ratios sd_eb=0.061`;
  `domain_rank_resid span=0.10978`.
- `VERDICT (rule fixed in the docstring before running): GATE
  DOWNGRADED: 4 of 7 CI-passing groups below the 0.1 floor ...
  [bands: floor 0.05: 7/7 pass, floor 0.25: 1/7 pass, floor 0.1:
  3/7 pass]`.
- Verdict (verbatim): `those four effects are statistically nonzero
  (CIs exclude 0) but ≤0.10 of their own residual SD` / `each domain's
  offset from zero is 11-17% of e.b's SD (all clear 0.10, none clear
  0.25: real but modest). The GRADIENT the review actually asked about
  — max−min across domains = 0.01471 — is only 0.061 × e.b. SD`.
  Denominator-dependence flagged: `sd_pos ... ~3× smaller ... using it
  instead would flip the verdict to nearly-all-pass. The conservative
  largest-SD choice was pre-registered precisely to avoid that fork ...
  the verdict is denominator-dependent, which is why all three ratios
  are printed`.
- Disclosed pre-full-run fix: GRADIENT rows' es_primary used
  `max(ratio)` (anti-conservative) → fixed to `min(ratio)`; `NO verdict
  changed ... it makes that cell MORE conservative, never less`.

**E1b** (line 728) — `Status: PASS — DIVERGENCE (domain-only): at
primary w=25 the DOMAIN-boundary set steps (T=0.01540, p_set = 0.0061)
and the REGION-boundary set does not (T=0.00652, p_set = 0.5795). The
data follows the domain boundaries (two-trait prediction), not the
mutagenesis-region cuts (normalization-artifact prediction).
Sensitivity: same divergence at w=40 (0.0046 / 0.6957), NOT at w=15
(0.2446 / 0.1468) — divergence is not w-robust, stated in the verdict
below.`
- Design: per-position mean |own_e_b − published e.b|, 654 positions
  (2..656), `position 222 absent`; DOMAIN boundaries
  `[36, 48, 338, 363, 645]` (adjacent label changes), REGION
  `[148, 295, 475]` (from `scripts/lib/regions.py`); FULL-WINDOW
  testability rule pre-registered; TWO nulls (position permutation
  N_PERM=10000 + exact circular shift over all 653 nonzero offsets),
  `p_set = max(p_perm, p_shift) — conservative`.
- w=25 (primary): `DOMAIN SET MAX |step|=0.01540 p_perm=0.0007
  p_shift=0.0061 p_SET=0.0061 (4 boundaries)`; `REGION SET MAX
  |step|=0.00652 p_perm=0.2723 p_shift=0.5795 p_SET=0.5795 (3
  boundaries)` → `VERDICT at w=25 ... DIVERGENCE: domain-boundary step
  found (p<0.05), region-boundary step not found`. Load-bearing
  boundaries: `DOMAIN b=48 step=-0.01191 p_perm=0.0036 p_shift=0.0413`;
  `DOMAIN b=338 step=+0.01540 p_perm=0.0004 p_shift=0.0015`.
- Verdict (verbatim): `The disagreement profile follows the DOMAIN
  boundaries — the two-trait hypothesis's prediction — and not the
  mutagenesis-region boundaries, which is what the normalization-
  artifact explanation predicted.` Sensitivity stated plainly: `the
  divergence reproduces at w=40 ... but NOT at w=15 ... The finding is
  real at the pre-registered width and at the wider width, not
  width-independent.` Effect size: `the load-bearing step is 0.0154 on
  a disagreement profile whose row-level SD is 0.0378 and whose
  between-domain span is 0.0147 — ... Modest in magnitude; decisive
  only in WHERE it sits (domain vs region).`
- Logged caveats: circular-shift null `treats the chain as circular
  (it is not); it serves only as the conservative tie-breaker`;
  `tests alignment of a profile with boundaries, not causation`;
  boundary 645 untestable at every w (dropped, logged, not silently
  skipped); w=15's REGION b=148 hint (p_perm=0.0290) `does NOT survive
  the shift null (0.0520) or the set max — do not promote it`.

**Y5a's note (pre-empt or reinforce the two-trait MoCHI refit
motivation?)** — the log's own answer, verbatim: `Per the task's
framing, this runs BEFORE any MoCHI refit: the refit, if done, should
control for domain structure; region-normalization is not where the
disagreement lives.`
Verdict: PASS — Group E extracted verbatim. As-logged outcomes: E1a
GATE DOWNGRADED (4 of 7 CI-passing groups below the 0.10 effect-size
floor; per-domain offsets 0.11–0.17 of e.b. SD; gradient 0.061); E1b
DIVERGENCE domain-only at w=25 (domain p_set 0.0061 vs region p_set
0.5795), not width-robust (fails at w=15).
Files created/modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- E1a's verdict is denominator-dependent (es_eb vs es_pos) and its
  0.10 floor is self-declared post-hoc — both are in the quoted verdict
  bands; quote bands, not the single floor, when citing.
- E1b's divergence claim rests on the set-level max-statistic p (driven
  by b=338 under the shift null), not any single boundary — as the log
  itself insists.
---

## [Y6] — Group F digest: nonlinear fitness control, region-2 recalibration overfit check (F1a, F1b, F2a)
Status: PASS
Time started / finished: 2026-09-22 23:24:29 / 2026-09-22 23:26
What I did:
- Extracted Group F verbatim (`sed -n '999,1167p'`), boundaries first
  (F1a=999, F1b=1039, F2a=1092; next section G1=1168). Quote-only.
Actual output (real numbers and quoted source text):
**F1a** (line 999) — `Status: PASS (test ran, gate identity check
passed) — pre-registered verdict: CHANGED (GI_folinate_independent
binned-spec COEF ROBUST in 1/2 error metrics)`. Script 51, full run
N_BOOT=10000, 09:36:04→09:37:40:
- Gate: `all 6 models OK — max|coef/ci diff| = 2.4e-17 … 9.0e-17,
  n match True`.
- Headline model (n=9756, pos=596), verbatim: `rank-based: linear f_bar
  coef=+0.0521 CI=[+0.0245,+0.0797] ... decile-binned coef=+0.0573
  CI=[+0.0303,+0.0842] ... quadratic coef=+0.0664 CI=[+0.0391,+0.0936]
  -> binned COEF ROBUST: True  quadratic COEF ROBUST: True`;
  `calibrated: linear f_bar coef=-0.0590 CI=[-0.0851,-0.0330] ...
  decile-binned coef=+0.0537 CI=[+0.0352,+0.0723] ... quadratic
  coef=+0.0271 CI=[+0.0085,+0.0456] ... -> binned COEF ROBUST: False
  quadratic COEF ROBUST: False` → `F1a VERDICT (pre-registered):
  CHANGED -- GI_folinate_independent binned-spec COEF ROBUST in 1/2
  error metrics`.
- Verdict (verbatim): `CHANGED by the pre-registered letter: the
  calibrated-metric GI_folinate_independent coefficient FLIPS SIGN
  under both nonlinear specs (linear -0.0590 → binned +0.0537,
  quadratic +0.0271) ... The rank metric is robust and even grows` /
  `Direction of the change matters and is reported, not spun: under
  correct functional form BOTH metrics are positive and nearly equal
  (+0.0573 rank / +0.0537 binned-calibrated), CIs exclude 0 in both ...
  3.1's published survival criterion ... therefore still holds under
  the nonlinear control; what fails is the published NEGATIVE
  calibrated sign.` Mechanism: `r2 ... jumps 0.03 → 0.52-0.57 when
  fitness enters nonlinearly` → `This EMPIRICALLY CONFIRMS the open
  follow-up already written in script 22/RESULTS.md: "the
  rank-vs-calibrated sign disagreement in the Phase 3
  central-error results was never explained. Pooled calibration across
  heterogeneous fitness ranges is now a concrete candidate"`.
- Disclosed: smoke caught a KeyError `in presentation code after all
  model fits; no model or gate was touched`.

**F1b** (line 1039) — `Status: PASS — pre-registered verdict: HOLDS
(rank-based=HOLDS, calibrated=HOLDS; all 4 CI checks pass)`:
- Ambiguity logged (AGENTS §9): `the original proposal 5.6c text does
  not exist anywhere in the repo ... Most conservative reading applied`.
  `w.fitness = the ATLAS's own raw column ... NOT f_bar`.
- Population: `abs_gi + both-errors population: 10757 rows / 654
  positions ... cut p10=0.000000 p90=1.337150 below=561 above=1076
  kept=9120`; skew of excluded 1,637: `|GI| kept mean=+0.1619 vs
  excluded +0.2613`; `central_error_cal kept +0.2217 vs excluded
  +0.3855`.
- Reproduction: `base rho=+0.116464 published=+0.116464 |diff|=2.78e-17`;
  `base rho=-0.133817 published=-0.133817 |diff|=5.55e-17`.
- Results (verbatim): rank raw `unrestricted rho=+0.1165
  CI=[+0.0891,+0.1436] → restricted rho=+0.1199 CI=[+0.0901,+0.1485]
  PASS`; rank multivar `+0.0521 → restricted +0.0621 CI=[+0.0312,+0.0929] PASS`;
  calibrated raw `-0.1338 → restricted -0.1776 CI=[-0.2087,-0.1465]
  PASS`; calibrated multivar `-0.0590 → restricted -0.0861
  CI=[-0.1150,-0.0571] PASS` → `F1b VERDICT (pre-registered): HOLDS`.
- Verdict (verbatim): `the restriction does not attenuate anything —
  the calibrated association STRENGTHENS (raw rho -0.1338 → -0.1776,
  ~33% larger ...) while rank stays flat-to-slightly-up ... The result
  is not an artifact of the fitness-range extremes; removing them
  makes it bigger on the calibrated metric.` Plus skew disclosure:
  `the excluded 1,637 rows are NOT random ... that the association
  survives (and strengthens) under that loss of leverage is the
  conservative direction of this test.` Also: `unmatched = 0` (the 456
  phase3 rows without raw w.fitness `also lack
  GI_folinate_independent ... already exited via the abs_gi dropna`).

**F2a** (line 1092) — `Status: PASS (verdict: CONFIRMED-WITHIN-REGION
— all pre-registered gates green)`. Script 52, full run N_BOOT=2000, 4 s:
- CHECK 1 source audit: `crossfit_isotonic_within_group ... -> subsets
  to group BEFORE calling by_position: True / -> by_position holds out
  POSITIONS (train excludes test fold): True`.
- CHECK 2: `2a max|within - per-region-by-position| = 0.000e+00
  (gate < 1e-12) -> OK`; `2b max|within - pooled-by-position| =
  2.590e-01 (gate > 1e-6) -> OK`.
- CHECK 3: all 8 constants within 0.01 — `region2_pooled derived
  -0.1172 published -0.1120 |delta|=0.0052`; `region2_within derived
  +0.0707 published +0.0750 |delta|=0.0043`; `pooled_pooled +0.0894 vs
  +0.0900`; `pooled_within +0.1897 vs +0.1910`; `within_r1 +0.1622 vs
  +0.1630`; `within_r3 +0.1632 vs +0.1610`; `within_r4 +0.1834 vs
  +0.1860` (and region2_stratified −0.1162 vs −0.1120);
  `sign pattern ... OK` → `F2a VERDICT (pre-registered):
  CONFIRMED-WITHIN-REGION`.
- Provenance scan: `writers found: 0 -> NONE`; `CSV present on disk:
  False`; `RESULTS.md contains the region-2 table: False`. Bootstrap:
  `within-region pooled rho = +0.1897 CI=[+0.1597,+0.2188] n=10757
  pos=654`.
- Verdict (verbatim): `The calibration IS cross-fitted within region:
  crossfit_isotonic_within_group subsets each region before delegating
  to the position-held-out fitter ... The overfitting concern in the
  review ... is therefore live but bounded by the position-holding-out`
  + limitation carried: `the mechanism claim rests on re-derivation
  (library function matches every published constant), not on reading
  the lost historical code`.
- Disclosed smoke bug (AGENTS §6/§7): `the subset-first matcher used
  the same-line literal ... but the audited call is wrapped across two
  lines, so it reported False and the script exited 1 before any
  numeric check had run ... the distinction is that the check was
  broken, not the data, and no result had been computed yet`.
Verdict: PASS — Group F extracted verbatim. As-logged outcomes: F1a
CHANGED by its pre-registered letter (calibrated GI sign flips under
nonlinear f_bar; rank robust; survival criterion still holds because
both binned metrics are positive and exclude 0 — the negative
calibrated sign was the misspecification); F1b HOLDS on all four checks
(calibrated strengthens −0.1338→−0.1776); F2a CONFIRMED-WITHIN-REGION
(identity 0.000e+00 vs pooled 0.259; 8/8 constants within 0.01).
Files created/modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- F1a is a CHANGED verdict by its own rule — it must be reported as
  changed (sign of 3.1's calibrated coefficient), even though the
  direction of change strengthens the underlying association.
- F1b's reading of "5.6c" is a logged assumption (source text absent
  from the repo) — re-point it in the morning if the intended target
  differs.
- F2a's mechanism claim is re-derivation, not recovered code (original
  script genuinely missing); its deltas (≤0.0052) may be data drift.
---

## [Y7] — Group G1 digest: global-vs-specific epistasis decomposition (G1 only, not G2)
Status: PASS
Time started / finished: 2026-09-22 23:25:12 / 2026-09-22 23:26
What I did:
- Extracted G1 ONLY verbatim (`sed -n '1168,1219p'`), boundaries
  confirmed: G1=1168 (H1a=1220 ends it), and G2a is a separate entry at
  line 1843 belonging to Group V — deliberately NOT extracted here per
  the task ("NOT G2, which is Group V below"). Quote-only.
Actual output (real numbers and quoted source text):
**G1** (line 1168) — `Status: PASS (PART 1 verdict: LIMITED-GLOBAL —
the "if most of it" premise is NOT met; PART 2 verdict: SURVIVES —
ESM-2 predicts the specific residual, and the signal STRENGTHENS)`.
Script 53, full run N_BOOT=2000/N_PERM=10000, 19 s, EXIT=0:
- Set accounting: `phase5 rows: 11344 / non-null e.b + delta_esm:
  10757 (dropped 587) / + matched atlas w.fitness: 10757 (dropped 0)`
  → `Analysis set: 10757 variants, 654 positions`.
- PART 1 verbatim: `cross-fitted isotonic R^2 (PRIMARY) = 0.1535
  (out-of-sample)`; `linear OLS R^2 = 0.1079`; `in-sample isotonic
  R^2 (CEILING) = 0.1651 (optimistic)`; `Spearman(w.fitness, e.b) =
  -0.2393`; `pre-registered band: R^2_cf -> LIMITED-GLOBAL
  (>=0.50 MOST / >=0.25 SUBSTANTIAL / else LIMITED)`;
  `cross-fitted R^2 cluster bootstrap CI=[0.1317,0.1749]`.
- PART 2 verbatim: `residual: e.b - crossfit-isotonic(w.fitness);
  sd(resid)=0.2349 vs sd(e.b)=0.2554 (0.920 of raw scale)`;
  `Spearman(delta_ESM, residual) = -0.1455 CI=[-0.1761,-0.1131]
  p_boot=<0.000500`; `Spearman(delta_ESM, raw e.b) = -0.0707`;
  `reconciliation vs script 32 on-disk: value=-0.070705 n=10757
  |diff|=6.94e-17`; `paired magnitude difference |resid| - |raw|:
  +0.0748 CI=[+0.0585,+0.0912] (both rhos negative in 2000/2000 draws)
  -> removing global epistasis STRENGTHENS the |delta_ESM| signal
  magnitude`; position-level sign-flip association null:
  `identity: all+1 == obs (-0.145545737907), all-1 == -obs
  (+0.145545737907) -> OK`; `observed=-0.1455 null mean=+0.0001
  sd=0.0186 p=<0.000100`; `null-centring: mean IS consistent with zero
  (3 SE)` → `pre-registered verdict: SURVIVES (p<0.05: True; CI
  excludes 0: True)`.
- Verdict (verbatim): PART 1 `LIMITED-GLOBAL. A monotone nonlinear
  function of w.fitness alone explains 15.35% of e.b's variance
  out-of-sample ... Global epistasis through w.fitness is REAL but is
  a minority (~15%) of what e.b measures; ~85% is not a monotone
  function of fitness.` PART 2 `SURVIVES, and in the direction that
  HELPS ESM-2 ... Removing global epistasis roughly DOUBLES the
  delta_ESM association (0.071 → 0.146) ... Effect-size context:
  even the strengthened association is modest in absolute terms
  (|rho| ≈ 0.15, ~2% shared rank variance).`
- Null labeled per AGENTS §4 (verbatim): `ASSOCIATION sign-symmetry
  randomization at position granularity ... It tests whether the signed
  pairing beats chance; it centers on zero by construction and does
  not rule out confounding.`
- Three smoke-stage bugs in the script itself, fixed BEFORE the full
  run and disclosed: (a) ceiling forced `increasing=True` vs house
  `increasing="auto"` — with Spearman −0.239 the relation is DECREASING,
  forced-increasing gave `R²=0.0135, absurdly below the cross-fitted
  0.1535`; (b) paired-difference label compared signed rhos (both-
  negative read "WEAKENS" when |rho| grew) → fixed to bootstrap the
  MAGNITUDE difference; (c) reconciliation printed a missing column.
  `None of these touched a pre-registered decision rule or changed a
  verdict.`
- The log's own INTERPRETIVE NOTE (verbatim): `this refines rather than
  overturns. ... Combined with C1/G1, the honest picture is: ESM-2's
  specific signal exists (rho ≈ −0.15 after deconfounding) but is
  small, while the pipeline-validation I1 GATE FAIL mean it should not
  be over-interpreted as calibrated epistasis prediction.`
Verdict: PASS — G1 extracted verbatim (G2 excluded). As-logged
outcomes: PART 1 LIMITED-GLOBAL (crossfit R²=0.1535 [0.1317,0.1749] —
the "if most of it" premise NOT met; ceiling 0.1651 bounds it); PART 2
SURVIVES (delta-vs-residual rho −0.1455 [−0.1761,−0.1131], sign-flip
p<0.0001, paired magnitude +0.0748 [+0.0585,+0.0912] — signal doubles).
Files created/modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- Cross-session update to G1's interpretive note (troubleshooting rule
  5 — logged, not edited): the note cites "the pipeline-validation I1
  GATE FAIL" (script 49's original THREE-site run, p=0.139786). Since
  that log was written, the four-site rerun (script 65, prior migration
  session) PASSED its pre-registered gate (rho +0.401757, null +0.247570,
  p=0.0009999 — recorded in the prior MIGRATION_LOG Q1 entry and the
  ADDENDUM §5 append). So the "do not over-interpret" caution in G1's
  note rests on a gate result that has since been superseded; the
  caution's magnitude half (|rho| ≈ 0.15 small) still stands on its own.
- G1's PART 2 null is an association null (zero-centered by
  construction) — per AGENTS §4 that rules out one artifact mechanism
  only, as the log itself states.
---

## [Y8] — Group H digest: biological sanity (A222V severity, orthologs, 3D vs sequence distance, rescue variants, per-condition check)
Status: PASS
Time started / finished: 2026-09-22 23:25:53 / 2026-09-22 23:27
What I did:
- Extracted Group H verbatim (`sed -n '1220,1445p'`), boundaries first
  (H1a=1220, H1b=1250, H2a=1281, H2b=1314, H3a=1346, H4a=1395; next
  section J1a=1446). Quote-only.
Actual output (real numbers and quoted source text):
**H1a** (line 1220) — `Status: PASS (verdict: NEAR-NEUTRAL — ESM-2 does
not flag A222V as deleterious)`:
- `S(A222V | WT) [p.Ala222Val] = -5.200276`; `all-score p10 = -12.8005
  p90 = -1.1867 mean = -7.3666 sd = 4.3120`; `fraction of all
  substitutions scoring <= A222V (at least as deleterious): 0.6804`;
  `z-score vs all: +0.502`; `rank among position 222's substitutions:
  16 of 19`; `mildest substitution at 222: -1.8606 (p.Ala222Gly)` →
  `pre-registered reading: NEAR-NEUTRAL`.
- Verdict (verbatim): `it ranks A222V the 16th most deleterious of the
  19 substitutions at position 222 (i.e. 4th mildest) ... a clean
  explanation for why delta_ESM effects must come from literal local
  context sensitivity rather than from the model representing A222V as
  a destabilizing event.`
- Disclosure: `the score value −5.20 was visible during data inspection
  at design time; the BANDING rule (project-standard p10/p90) was
  written into the docstring before the run. The report itself has no
  degrees of freedom.` Band is not knife-edge.

**H1b** (line 1250) — `Status: PASS (verdict: VAL-RARE in the sampled
orthologs — the clade-cue alternative is NOT supported, with a small-n
caveat)`:
- `UniProt reviewed entries fetched (2-query union): 26`; `human
  self-check: P42898 maps back to A at 222 -> OK`; `orthologs kept
  (length 400-800): 13`; `PRIMARY (identity >= 50%): n=3 V=0.000
  A=1.000 -> VAL-RARE (residue counts: A:3)`; `SECONDARY (identity
  >= 30%): n=12 V=0.000 A=0.917 -> VAL-RARE (A:11, G:1)`;
  `pre-registered: VAL-COMMON iff V fraction >= 0.20`.
- Verdict (verbatim): `position 222 is conserved Alanine (91.7% in
  SECONDARY, 100% in PRIMARY), with one Gly` + `the PRIMARY set is only
  n=3 ... the substantive evidence is the SECONDARY n=12 ... the claim
  ... is scoped to "the sampled orthologs"`.
- Two disclosed pre-result fixes: first query returned `just 4
  entries — essentially only mammals use that exact symbol` → 2-query
  union (collection completeness, not result-dependent); alignment
  unpack assumed 2 blocks → iterate blocks properly.

**H2a** (line 1281) — `Status: PASS (verdict: MIXED-INDETERMINATE —
delta_ESM tracks 3D almost as strongly as linear distance; neither
"attention locality" nor "biophysics" is decisively confirmed)`:
- Gate: `derived=-0.298214 published=-0.298214 |diff|=5.55e-17 -> OK`.
  Subset `9633 variants, 588 positions (dropped 1124/66 outside
  37-644 or missing CA)`.
- `|delta_ESM| vs linear: rho=-0.2752 CI=[-0.3286,-0.2161]`;
  `vs C-alpha 3D to 222: rho=-0.2443 CI=[-0.2982,-0.1820]`;
  `vs min heavy-atom dist to FAD: rho=-0.2625 CI=[-0.3172,-0.2016]`;
  `paired D1 = +0.0309 CI=[-0.0036,+0.0676]`; `paired D2 = +0.0127
  CI=[-0.0187,+0.0449]` → `pre-registered H2a verdict:
  MIXED-INDETERMINATE`.
- Verdict (verbatim): `delta_ESM DOES track 3D distance nearly as
  strongly as linear distance (a drop from −0.275 to −0.244, ~11%
  relative) ... sequence distance and 3D distance are themselves
  strongly correlated in a single-domain protein, so this dataset
  cannot cleanly separate "the model attends to nearby sequence" from
  "the effect is structurally local."`
- Flag: `|e.b| itself also increases with distance from 222 in the
  published table (rho=+0.229)`.

**H2b** (line 1314) — `Status: PASS (pre-registered verdict:
INCONCLUSIVE-POWER on the PRIMARY union; the positive local signal
replicates in the 3D-neighbors ≤10 Å COMPONENT — CI excludes 0 — but
that is a labeled secondary, not the primary claim)`:
- Gates: `within-25: derived=+0.066793 published=+0.067 |diff|=2.07e-04
  -> OK`; `beyond-25: derived=-0.075380 published=-0.075 |diff|=3.80e-04
  -> OK`. Neighborhoods: `3D<=10A: 24 positions; 3D<=15A: 66; FAD<=5A:
  29; PRIMARY union: 49`.
- `PRIMARY union rho=+0.0507 CI=[-0.0432,+0.1348] n=776 pos=48
  p_boot=0.307`; `component: 3D neighbors <=10A rho=+0.1191
  CI=[+0.0066,+0.2166] n=363 pos=23 p_boot=0.042`; `component: FAD
  <=5A rho=-0.0574 CI=[-0.1896,+0.0599]`; `sensitivity: <=15A
  rho=+0.0495 CI=[-0.0308,+0.1259]`; `gate context: linear within-25
  rho=+0.0668 CI=[-0.0289,+0.1506]` → `pre-registered H2b verdict:
  INCONCLUSIVE-POWER`.
- Verdict (verbatim): `the power problem the review identified is
  structural, not fixable by re-cutting the same variants` + discipline
  note: `the 10 Å component is NOT the pre-registered primary and its
  CI excludes 0 only barely (lower bound +0.0066, 23 clusters); two of
  the five reported sets could show this by chance. The primary claim
  stays INCONCLUSIVE-POWER; the component is a lead, not a finding.`

**H3a** (line 1346) — `Status: PASS (verdicts: ASYMMETRIC-FAILURE + NO
enrichment for rescue — the rank enrichment is significantly
INVERTED)`:
- Gate: `GATE GI_indep_post == raw e.post.b: jointly non-null=10752,
  NaN in both=5, one-sided NaN=0, max|diff|=0.00e+00 -> OK`.
- PRIMARY (n=10,757; rescue 5448 / worse 5309): `mean delta
  rescue=+0.02717 CI=[+0.01885,+0.03665] worse=+0.03861
  CI=[+0.03165,+0.04671]`; `mean diff -0.01144 CI=[-0.01705,-0.00519]`;
  `agree rescue +0.6233 CI=[+0.5932,+0.6533] vs 0.5: EXCLUDES`;
  `agree worse +0.3268 CI=[+0.2978,+0.3550] vs 0.5: EXCLUDES`;
  `asymmetry +0.2965 CI=[+0.2422,+0.3505] vs 0: EXCLUDES`;
  `AUC(delta->e.b>0) 0.4525 CI=[0.4374,0.4688] -> ... direction: delta
  LOWER for rescue, i.e. inverted`; `failure shape: ASYMMETRIC-FAILURE`.
- SECONDARY (e.post.b>0.95, n=4,260): rates `0.6022/0.3354`,
  `asymmetry +0.2668 CI=[+0.2048,+0.3283]`, `AUC 0.4492
  CI=[0.4232,0.4736]` — same story.
- Verdict (verbatim): `it "agrees" with the measured direction on 62.3%
  of rescue variants ... but on only 32.7% of worse-in-A222V variants
  ... it actively disagrees two-thirds of the time there. The failure
  concentrates on the deleterious-in-A222V class.` / `AUC ... entirely
  below the 0.5 chance line ... the plain-language reading is
  ANTI-enrichment: rank-wise, delta_ESM points slightly AWAY from
  rescue.` Effect size: `the mean-delta difference (−0.011) is small
  relative to delta's own sd (~0.118) ... the rate asymmetry (0.30) is
  the larger, more interpretable effect.`
- Disclosed: gate counted only jointly non-null rows and failed the
  run before any statistic (fixed to verify identity on non-null +
  zero one-sided NaNs); and `The pre-registered AUC verdict STRING is
  direction-ambiguous as written ... Not renamed after the fact`.

**H4a** (line 1395) — `Status: PASS (verdict: HOLDS-AT-LOW-FOLINATE —
and, descriptively, it holds at ALL FOUR conditions, so averaging is
not diluting it; if anything it grows with folinate)`:
- Gate: `GATE rebuild of 6.3 pooled HIGH: derived diff=+0.002409
  CI=[+0.001551,+0.003208] n=3586 / on-disk: +0.002409
  CI=[+0.001551,+0.003208] n=3586 / max|delta| obs/lo/hi =
  1.04e-17/3.66e-17/4.42e-17 -> OK`.
- Per-condition HIGH strata: `12: +0.00227 CI=[+0.00144,+0.00308]`;
  `25: +0.00160 CI=[+0.00075,+0.00245]`; `100: +0.00303
  CI=[+0.00200,+0.00409]`; `200: +0.00510 CI=[+0.00361,+0.00655]` —
  all `ESM-2 WORSE (CI>0)`; LOW stratum ESM-2 BETTER at all four
  (CIs negative); MID crosses 0 (except cond 12: better).
  → `PRE-REGISTERED PRIMARY: HIGH stratum at condition 12 ... VERDICT:
  HOLDS-AT-LOW-FOLINATE`.
- Verdict (verbatim): `The review's dilution worry does NOT apply:
  6.3's pooled +0.00241 is not an artifact of averaging.` /
  `descriptively ... the high-stratum failure appears at EVERY
  condition ... if anything it is LARGEST at 200 µg/ml (descriptive —
  no pre-registered claim on that contrast).` Effect size: `+0.0016 to
  +0.0051 against pooled baseline MAE ~0.22-0.30 — i.e. 0.5-2%
  relative; real but small.` Drops: `per-condition 10,477-10,540
  (condition missingness 217-280 rows, ~2.2%)`.
- Disclosed: the gate's CI check `is conditional on N_BOOT==2000 by
  construction ... at the smoke run it printed "CI check deferred"
  rather than failing spuriously ... a gate that silently relaxes ...
  announces itself in the output.`
Verdict: PASS — Group H extracted verbatim. As-logged outcomes: H1a
NEAR-NEUTRAL (−5.200276; 16th/19 at position 222); H1b VAL-RARE
(PRIMARY n=3 A:3; SECONDARY n=12 A:11,G:1 — clade-cue unsupported,
small-n); H2a MIXED-INDETERMINATE (linear −0.275 vs 3D −0.244, D1 CI
straddles 0); H2b INCONCLUSIVE-POWER on the PRIMARY union (+0.0507
[−0.0432,+0.1348]) with the 3D≤10 Å component a labeled lead (+0.1191
[+0.0066,+0.2166], p=0.042); H3a ASYMMETRIC-FAILURE + AUC 0.4525
[0.4374,0.4688] inverted (anti-enrichment for rescue); H4a
HOLDS-AT-LOW-FOLINATE (cond-12 high +0.00227 [+0.00144,+0.00308];
failure at all four conditions, largest descriptively at 200 µg/ml).
Files created/modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- Two "wording" hazards to carry when quoting: H3a's pre-registered
  verdict string prints `ENRICHMENT-FOR-RESCUE ... inverted` where the
  plain reading is ANTI-enrichment (string deliberately not renamed
  post-hoc); H2b's replicating 10 Å component is secondary-by-design
  (barely excludes 0, 23 clusters) — lead, not finding.
- H1b's PRIMARY n=3 — always cite the SECONDARY n=12 alongside any
  conservation claim.
---

## [Y9] — Compile the one-page digest: GROUPS_C_TO_H_DIGEST.md
Status: PASS
Time started / finished: 2026-09-22 23:30:26 / 2026-09-22 23:31:15
What I did:
- Wrote `docs/tasks/comparators-and-consolidation/GROUPS_C_TO_H_DIGEST.md`
  per Y9a's spec: one short section per group (A, B, C, D, E, F, G1, H),
  each containing the verdict as originally logged (status strings quoted
  verbatim) plus the key number(s), and nothing added — explicitly
  framed as a reading aid, with a header note that no cross-group
  synthesis is drawn ("that synthesis is left to the reader", per the
  task's "that's for me to do"). Source material = this session's Y1–Y8
  extractions, which are themselves verbatim quotes of
  `docs/tasks/review-triage/OVERNIGHT_LOG.md`.
- Verified the deliverable after writing: existence, size, section
  count, and full entry-bullet coverage (see actual output).
Actual output (real numbers and quoted source text):
- `ls -la`: `-rw-r--r--@ 1 arnavchavan staff 18030 Sep 22 23:30
  GROUPS_C_TO_H_DIGEST.md`; `wc -l -w` → `80` lines, `2527` words.
- `grep -c "^## "` → `8`, and the eight sections are exactly the ones
  Y9a names:
  `## Group A — Inference validity (position-clustering, exclusion accounting)`
  `## Group B — delta_ESM confounds (flattening, compression, position-block null)`
  `## Group C — Rank-vs-MAE reconciliation (full table in OVERNIGHT_LOG lines 307–395; CSV task45_c1_table.csv)`
  `## Group D — Stratifier winner's-curse checks`
  `## Group E — Two-trait domain-vs-region boundary test`
  `## Group F — Nonlinear fitness control, region-2 recalibration overfit check`
  `## Group G1 — Global-vs-specific epistasis decomposition (G1 only; G2 = Group V)`
  `## Group H — Biological sanity (A222V's own severity, orthologs, 3D distance, rescue variants, per-condition check)`
- Entry coverage: `grep -c "^- \*\*"` → `33`, matching the 33 entries
  extracted in Y1–Y8 exactly — A1a/A1b/A1c/A2a/A2b=5; B1a/B1b/B1c/B2/
  B3=5; C1a/C1b/C1c/C1d/C2a/C2b/C2c/C3a=8; D1a/D1b/D1c=3; E1a/E1b=2;
  F1a/F1b/F2a=3; G1=1; H1a/H1b/H2a/H2b/H3a/H4a=6 (5+5+8+3+2+3+1+6=33).
Verdict: PASS — digest written to the specified path with all 8 group
sections, 33/33 entry bullets, verdicts and numbers quoted as logged,
no added conclusions.
Files created/modified:
- Created: `docs/tasks/comparators-and-consolidation/GROUPS_C_TO_H_DIGEST.md`
  (the Y9a deliverable).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- Count reconciliation during verification (AGENTS §5): my first
  verification grep (a character-class pattern) reported `32` bullets;
  the second, simpler `grep -c "^- \*\*"` reports `33` and the label
  listing confirms all 33 expected entries are present. The discrepancy
  was in my check pattern, not in the digest file — resolved by
  re-listing every label rather than trusting either count alone.
- Scope note: the digest's Group C section points to the full
  reconciliation table's location (OVERNIGHT_LOG lines 307–395) instead
  of embedding all 84 rows, to keep the file a one-page reading aid —
  the full table remains quoted in full in this log's Y3 entry and in
  the OVERNIGHT_LOG itself.
---

## [T1] — Tier 1: precomputed EVcouplings/EVmutation model for GB1 (P06654)
Status: BLOCKED — no precomputed model for P06654/its family found
under the 200MB hard cap (or reachable); moving to T2 per the task.
Time started / finished: 2026-09-22 23:33 / 2026-09-22 23:41
What I did (all attempts, in order — every one logged with its exact
URL and outcome):
1. Web search integration: both queries (`EVcouplings precomputed model
   download GB1 P06654 SPG1_STRSG`; `EVmutation precomputed model
   download GB1 ... four positions 39 40 41 54`) returned
   `Web search cancelled` — the search integration was unavailable, so
   I fell back to direct fetches of the EVcouplings project's own
   known distribution points (allowed under the task: "the EVcouplings
   project's own public data").
2. `https://evcouplings.org/system/downloads` → **404**.
3. `https://github.com/debbiemarkslab/EVmutation` → 200, but the repo
   is code only; README verbatim: `This package has been superseded by
   the EVcouplings package ... the repository here will only be kept as
   an archive` — no model files.
4. `https://evcouplings.org/` → 200. Homepage's own pointers:
   `Precomputed results ... [Undergoing maintenance]
   (https://v1.evcouplings.org/precomputed/search)` and
   `EVmutation database ... predicted for thousands of human proteins`.
5. `https://v1.evcouplings.org/precomputed/search` → **empty response**
   (consistent with the maintenance banner). Alternate attempt
   `https://v1.evcouplings.org/precomputed` → **empty response** again.
   Two attempts → treated as unreachable per the one-alternate rule.
6. `https://api.evcouplings.org/` (the homepage's "Supplementary data"
   host) → **502**.
7. `http://evmutation.org` → 200 (site live; nav: `Data and Code
   downloads.html`, `Human proteins human_proteins.html`). The DB's own
   scope is human proteins — GB1 (Streptococcus phage) is out of
   scope — and its supplement page `downloads.html` returned **404 on
   HTTP and 404 on HTTPS** (two attempts → unreachable).
8. Public precomputed-model repository fallback, Zenodo API
   (KB-scale metadata queries only; no file downloaded):
   - `q=EVcouplings OR EVmutation GB1 P06654` → 37 hits. Nearest
     GB1-relevant records: MuMi MD-simulation dataset (files
     94,504,526 / 108,593,623 / 45,883,833 / **2,161,589,249** bytes —
     MD trajectories, NOT a coevolution model); an NMR GB1 dataset;
     MIF/MIF-ST `gb1.tar.gz` = **194,156** bytes but it is AlphaFold
     predictions + inverse-folding weights, NOT a coupling model.
   - `q=Potts model GB1 binding protein couplings` → top hit: `Data for
     "Inferring protein folding mechanisms from natural sequence
     diversity"` — 15 protein families, each with MSA `.fasta` +
     Potts model `.npz` (h, J). Single file
     `simplified_rbm_and_msa.zip` = **1,865,790,805 bytes (1.87GB)** —
     over the 200MB hard cap; GB1's membership in the 15 families is
     unverifiable without the download, which the cap forbids
     (no partial downloads). Not fetched.
Budget accounting: fetched this task = web pages + JSON metadata only
(well under 1 MB total, against the 200MB cap); zero model files
downloaded, nothing partial.
Actual output: the per-attempt URL/outcome list above; the decisive
size numbers are `1,865,790,805` bytes (over-cap Potts zip) and the
`404/404/502/empty` statuses of the EVcouplings project's own endpoints.
Verdict: BLOCKED — exactly the task's stated stop condition
("if nothing under that cap is found or reachable, mark T1 BLOCKED
with what was tried, move to T2").
Files created/modified: `SESSION_LOG.md` (this entry only). No data
files created — nothing was downloaded.
Anything unexpected or worth flagging:
- The web-search integration being down (`Web search cancelled`) may
  have hidden sources a search engine would have found (e.g., mirrors).
  The attempts above cover the EVcouplings project's own distribution
  points and one public repository, as the task specified; if the
  search integration works later, re-running T1's search terms would
  close that gap — noted, not done (one alternate attempt consumed).
- The over-cap Potts dataset (15 families incl. unknown membership) is
  the closest miss; if GB1 were confirmed among them, downloading it
  would still violate the cap, so T2's fetch-our-own-MSA route is the
  correct path either way.
---

## [T2] — Tier 2: coupling signal from a fetched MSA (T2a fetch, T2b compute, T2c size gate)
Status: T2a = PASS (MSA fetched from an EBI alignment endpoint within
budget); T2c = evaluated with an explicit assumption (see below); **T2b =
FAIL — the script's own pre-registered mapping-validation gate (M3) failed
(1/4 WT-consensus columns); per the troubleshooting tree
("sanity-check failure => FAIL immediately") and AGENTS §0/§10 no coupling
signal is reported and the failed gate was NOT replaced post-hoc.**
Time started / finished: 2026-09-22 23:37:31 / 2026-09-23 00:50:00
What I did:

### T2a — fetching an MSA (task names "UniProt, Pfam, or an EBI alignment endpoint")
1. **Pfam/InterPro direct alignment endpoints: unavailable.**
   - GB1's family discovered via InterPro API:
     `GET https://www.ebi.ac.uk/interpro/api/entry/all/protein/uniprot/P06654/`
     -> `PF01378 "B domain" (IgG-binding protein G, IPR000724)`, hits at
     P06654 227-283 and 297-354 (count 17).
   - `HEAD /interpro/api/alignment/pfam/PF01378/?format=fasta` -> **404**
     (`{"detail":"Not found."}`); four further path variants -> all 404;
     `pfam.xfam.org` -> 000 (dead host). InterPro 11's API index
     (`GET /interpro/api/`) lists
     `{"endpoints":["entry","protein","structure","taxonomy","proteome","set","utils"]}`
     — **no alignment endpoint exists any more.**
2. **EBI HMMER job-dispatcher (works).** Service contract discovered from
   `openapi.json` (SPA HTML, unusable) then the JS bundle then probing:
   - `GET .../Tools/hmmer/api/v1/search/databases` -> seq DBs
     `refprot / swissprot / uniprot` (used `uniprot`), versions `2025_01`.
   - Query = P06654 B domain **228-282** (55 aa), from DBREF
     `DBREF 2GB1 A 2 56 UNP P06654 SPG1_STRSG 228 282` (MIGRATION_LOG:57).
     Site mapping printed and verified before submission:
     `GB1 39 -> UNP 265 = V (domain pos 38)`, `40 -> 266 = D`, `41 -> 267 = G`,
     `54 -> 280 = V` — the classic GB1 wild type V/D/G/V. OK
   - Job 1 (job id `e57521e7-effe-439c-80a1-a42a454b5c0f`, iterations=3,
     my own non-default choice): iterations 1/2/3 all `SUCCESS`
     (gains +45/+7/+141); final stats
     `nhits=312 nreported=312 nincluded=186` over `nseqs=245001337`.
   - Downloads generated (`POST /api/v1/download/{id}/{format}` -> 204)
     and fetched to `data/external/`:
     `p06654_gb1_bdomain_jackhmmer_uniprot.afa.gz` (13,547 B),
     `.sto.gz` (23,648 B), `.txt` (602,407 B). gzip integrity OK.
   - **MSA contents: 566 aligned rows x 61 columns** (afa and sto agree),
     from **180 distinct UniProt accessions** (tandem multi-copy B domains;
     text file lists 186 targets — accessions vs entry-names, both counts
     reported here per AGENTS §5).
3. **Job 2 (iterations=5, HMMER's actual default — correcting my own
   non-default depth; job id `82db084b-4b07-4597-b05a-d5f1037a8deb`):
   STALLED server-side** at iteration 0 for 30+ minutes (two bounded poll
   windows; leaf job `9e7c15e5` never advanced). Abandoned; the
   3-iteration MSA above is the analysis input. Disclosed in script 66's
   output.
4. **Pfam seed archive (the task's first-named source), for PF01378
   specifically: fetched but the family's seed has only 7 sequences.**
   - `HEAD Pfam-A.full.gz` = **23,991,810,911 B (24 GB) — BLOCKED by cap**
     (logged, not fetched).
   - `HEAD Pfam-A.seed.gz` = **194,369,799 B (194.4 MB) — within cap**;
     fetched (gzip OK, md5 `7a37e1237d5d20c35b236c9f5a9ac797`,
     concatenated-Stockholm, Pfam 38.x release). Kept on disk: extracting
     any OTHER family (e.g. Group T4's MTHFR) from it costs 0 bytes.
   - Extracted `data/external/PF01378_seed_alignment.sto` (2,051 B, md5
     `69bfe2b74b25181eceed5d3579b6d4f3`, `#=GF AC PF01378.24`,
     `#=GF ID IgG_binding_B`): **row count = 7**, and **P06654 is NOT a
     seed row** -> far below any ~200 threshold; this source cannot serve
     T2b. (Extraction: first attempt failed — a heredoc/pipe stdin
     collision made Python execute the Stockholm stream as its script
     (`SyntaxError ... 14331_SCHMA/20-239`); fixed by writing the
     extractor to a temp file outside the repo.)
5. **Budget (T-cap 200 MB = 209,715,200 B):** T's own fetches total
   194,369,799 + 602,407 + 13,547 + 23,648 + 124,416 + 2,019 + 567
   (incl. iteration-1 downloads below) + ~1 MB pages =
   **~195.1 MB <= 200 MB**; whole `data/external/` incl. the prior
   session's 3.34 MB GB1 landscape = **205,950,976 B <= 209,715,200 B** OK

### T2b — the coupling computation (script 66, pre-registered before run 1)
- Wrote **`scripts/66_gb1_coupling_signal.py`** (next free number: 65 was
  the highest committed script -> **66**), docstring containing the full
  pre-registration BEFORE the first execution: mapping procedure + gates
  M1/M2/M3, mfDCA formulas (21 states, Laplace beta=1, lambda =
  0.015*mean(diag C), Frobenius block norms), MI as labeled secondary,
  primary (566 rows) vs dedup sensitivity arm (first row/accession = 180),
  determinism (no RNG), T2c gate, and limitations-to-print.
- **Two bugs were found by inspection BEFORE run 1 and fixed** (no gate
  ever ran on buggy code): (a) off-by-one in the site->column index
  (GB1 site k = query residue k-1 = 0-based list index **k-2**, not k-1);
  (b) `np.einsum(...)[:] = 0` on the diagonal-block zeroing would silently
  modify a temporary (replaced with an explicit loop).
- **Run 1** (`00:43:08`): `py_compile OK`; T2c gate printed PASS (566);
  primary mapping path (query-identical rows in iter-3 MSA) correctly
  found NONE (iter-3 envelopes had narrowed, e.g. `/230-278`) -> fell to
  the pre-registered crosswalk; then **TypeError in my vote tally**
  (`sum(pairs.values())` over Counters) -> `EXIT=1`. Code bug, fixed
  (disclosed here; no decision rule touched).
- **Run 2** (`00:43:33`), the actual gate transcript:
  ```
  M2 crosswalk: 4223 target-coordinate pairs from 38 shared proteins
  M3 col 33 site 39: consensus 9 (L) vs WT V -> NO (320/549)
  M3 col 37 site 40: consensus 16 (T) vs WT D -> NO (280/545)
  M3 col 38 site 41: consensus 16 (T) vs WT G -> NO (141/541)
  M3 col 58 site 54: consensus 17 (V) vs WT V -> match (71/95)
  GATE FAIL: M3: WT consensus at only 1/4 mapped columns (need >=3)
  EXIT=1
  ```
  **No CSV was written** (exited before output — verified:
  `data/processed/task_T2_gb1_coupling.csv` absent; no partial results).
- Diagnosis run (read-only, after the FAIL, to decide honestly whether
  this is data or my code — both facts recorded):
  1. **The crosswalk itself is internally unanimous:** site39 iter1 col37
     -> iter3 col33 with **87/87** votes, site40 39->37 (86/87), site41
     40->38 (86/87), site54 57->58 (86/87); iteration-1's three
     query-identical rows independently give iter1 cols `[37,39,40,57]`.
  2. **Row0 (Q53975) carries WT at exactly those columns** with the
     correct insert structure: `V@33 ... DG@37,38 ... EW@42,43` and
     `...TKTFTVTE` at 53-60 (V@58) — and the C-terminal motif consensus
     at cols 53-60 is `T K T F T V T E`.
  3. **But the majority of the 566 rows disagree with B-domain homology
     at the N-terminal half:** col27 top residue is `W` (472/565) where
     the invariant `FKQY` sits (Y only 81); col33 top `L` (320) vs V (70);
     col37 top `T` (280) vs D (81); col38 top `T` (141)/N (130) vs G (70).
- **Verdict handling:** M3 is the pre-registered validation of the mapping.
  It failed. The fact that a *subgroup* of rows (row0-type) matches WT at
  4/4 and that the crosswalk votes are unanimous does NOT license
  replacing the failed rule with a post-hoc subfamily-restricted consensus
  — that would be changing a pre-registered decision rule after seeing the
  result (AGENTS §0, §10; the session's own rule: "sanity-check failure =>
  FAIL immediately"). **T2b = FAIL; no coupling numbers exist; none are
  invented.** If a future session (with explicit user approval) wants to
  re-validate via a differently-specified gate, that is a NEW
  pre-registration, not a fix to this run.

### T2c — the size gate, as evaluated
- **Row-count reading (the literal "the MSA ... fewer than ~200
  sequences"): 566 >= ~200 -> PASS** — this is the reading under which
  T2b was allowed to run at all (printed by script 66 in both runs).
- **Distinct-accession reading: 180 < ~200** — disclosed in script 66's
  output ("BELOW 200 — assumption logged in SESSION_LOG T2") and here as
  the logged assumption (session rule: ambiguity => most conservative
  literal reading + log it; I judged row count to be the plain reading of
  "the MSA's sequences" while recording the stricter reading prominently).
  The pre-registered dedup sensitivity arm (180 rows) was in place so the
  stricter reading would have been reported side by side had T2b passed.
Actual output (verbatim, most decisive):
- `POST status: 200 ... {"id": "e57521e7-effe-439c-80a1-a42a454b5c0f"}`
- `FINAL: nhits=312 nreported=312 nincluded=186`
- `iteration-3 MSA: 566 rows, widths [61]; iteration-1 MSA: 87 rows`
- `T2c: PRIMARY row count = 566 (PASS vs >= ~200); distinct accessions = 180 ... BELOW 200`
- `M2 crosswalk: 4223 target-coordinate pairs from 38 shared proteins`
- `GATE FAIL: M3: WT consensus at only 1/4 mapped columns (need >=3)` -> `EXIT=1`
- `records written: 1` + `row count = 7` for PF01378's seed (unusable);
  `Pfam-A.full.gz Content-Length: 23991810911` (over cap).
Verdict: **T2 = FAIL** (T2a PASS, T2c PASS-with-assumption, T2b failed
its own pre-registered M3 validation gate; nothing to carry to T3).
Files created/modified:
- Created: `scripts/66_gb1_coupling_signal.py` (the pre-registered T2b
  script; leaves a complete record of method + gates + failing output).
- Created (fetched data, `data/external/`, provenance above):
  `P06654_SPG1_STRSG.fasta`, `PF01378_seed_alignment.sto`,
  `Pfam-A.seed.gz` (194.4 MB, md5 7a37e123...), the four jackhmmer
  outputs (`p06654_gb1_bdomain_jackhmmer_uniprot.{afa.gz,sto.gz,txt}` and
  `p06654_gb1_bdomain_iter1.{afa.gz,txt}` — iteration-1 fetched for the
  crosswalk).
- NOT created: `data/processed/task_T2_gb1_coupling.csv` (gate exit
  precedes writing — no partial output by design).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- **T2b's FAIL does not by itself prove the mapping wrong** — the
  unanimous 87-vote crosswalk and row0's exact 4/4 WT match say the
  columns are likely right and the global-consensus form of M3 is
  miscalibrated for an alignment whose majority rows sit in shifted or
  non-homologous registers at the N-terminal half (col27 W:472 vs the
  invariant FKQY-Y:81 is the clearest symptom). Acting on that
  observation = changing a pre-registered rule -> explicitly NOT done;
  recorded so the next session can decide with the user.
- InterPro 11 dropping its alignment API, a 7-row seed for a real Pfam
  family, and a server-side stall on a default-parameter job were all
  unanticipated; each was logged at the point of discovery rather than
  silently worked around.
- The 5-iteration job may still be recoverable later (server-side id in
  this log); it was NOT needed for the FAIL and NOT retried again.
---

## [T3] — Correlate the coupling signal with measured GB1 epsilon (n = 6)
Status: **BLOCKED (dependency failed — no execution attempted).**
Time started / finished: 2026-09-23 00:50:30 / 2026-09-23 00:50:30
What I did: Determined the task's precondition. T3's input is "the
coupling signal ... obtained from T2b". T2b exited at its pre-registered
M3 validation gate (`GATE FAIL: M3: WT consensus at only 1/4 mapped
columns (need >=3)`) and produced **no coupling values** — there is
literally nothing to correlate with the six epsilon values. The six eps
themselves exist (MIGRATION_LOG P2: 39x40 re-derives +7.399806 vs the
Fig-3D `+5`; 39x54 confirms -4.495855 vs `-4.5`; all six pairs logged
there) but correlating an invalidated/absent signal against them would
manufacture a number from a failed pipeline (AGENTS §0: never present a
failed analysis as a result; §10: a fix here would require changing a
pre-registered rule, which requires stopping and asking). Per the
session's troubleshooting tree a dependency failure marks the task
BLOCKED and I continue with the next independent task (T4's own
condition, then T5).
Actual output: none (not executed by design — precondition check only).
Verdict: **T3 = BLOCKED**, citing T2's M3 gate FAIL verbatim above.
Files created/modified: none (SESSION_LOG.md this entry only).
Anything unexpected: The task text itself anticipated n=6 ("state that
n is too small for a meaningful bootstrap — say so plainly"); that caveat
would have applied had the signal existed.
---

## [T4] — Extend to MTHFR itself (conditional on T1–T3 producing anything usable)
Status: **NOT ATTEMPTED — the task's own entry condition is unmet.**
Time started / finished: 2026-09-23 00:51:00 / 2026-09-23 00:51:00
What I did: Evaluated the condition stated in the task's own title line
("if T1–T3 produced anything usable"): T1 = BLOCKED (no precomputed Potts
models fetchable within cap — EVcouplings maintenance, EVmutation DB gone,
Zenodo 1.87 GB over the 200 MB cap); T2 = FAIL (T2b died at the
pre-registered M3 gate, no coupling signal); T3 = BLOCKED (nothing to
correlate). Nothing usable was produced, so the "repeat T1/T2's
fetch-and-signal-construction for MTHFR (P42898) around position 222"
body of T4 was **not run** — repeating a signal-construction pipeline that
just failed its own validation on GB1 would either import the same
failure or tempt a post-hoc gate change (AGENTS §0/§10). Budget note for
completeness: had it run, MTHFR's family could have been extracted from
the already-on-disk `Pfam-A.seed.gz` for 0 additional bytes (within the
T-cap), or a jackhmmer fetch (~0.6 MB) fit in the ~4.9 MB headroom; both
options remain open for a future session that explicitly wants T4 with a
fresh pre-registration.
Actual output: none (condition evaluated, body not executed).
Verdict: **T4 = SKIPPED per its own stated condition** (logged as a
stop-condition continuation, then continuing to the independent T5).
Files created/modified: none (SESSION_LOG.md this entry only).
Anything unexpected: The condition failing is itself the informative
result of Group T: Tier 1 (models) and Tier 2 (rebuild) both fell, so
Group T delivers no coupling comparator this session.
---

## [T5] — One summary table: predictor x target x result
Status: PASS.
Time started / finished: 2026-09-23 00:53:00 / 2026-09-23 00:55:30
What I did: Assembled `data/processed/task_T5_comparator_summary.csv`
(columns: predictor, target, result, source) as a pure curation of
numbers already logged elsewhere — no new analysis, nothing recomputed,
nothing invented (AGENTS §5/§6). Before writing I re-grepped every value
against its home log (SESSION_LOG Y-entries, OVERNIGHT_LOG lines 26/85/1209,
MIGRATION_LOG Q1 lines 294-314) instead of reconstructing from memory.
Seven rows: four ESM-2 x target rows with real results (MTHFR own e.b
rho=-0.088118 with its p<0.0001 position-block null; MTHFR published e.b
rho=-0.070705 with the B3/S1 transcription flag; MTHFR residualized e.b
rho=-0.1455 CI [-0.1761,-0.1131]; GB1 four-site I1 GATE PASS
rho=+0.401757 null +0.247570 p=0.0009999 CI [+0.258070,+0.521658] from
script 65), plus three explicit-absence rows: ESM-2 x GB1 six-epsilon =
NOT COMPUTED (never tasked), coupling x GB1 epsilon = NOT OBTAINED
(T1 BLOCKED / T2b M3 FAIL / T3 BLOCKED), coupling x MTHFR e.b = NOT
OBTAINED (T4's condition unmet). Absences are recorded as results, per
the "if obtained" wording in the task doc.
Actual output (verification, real numbers):
```
header: ['predictor', 'target', 'result', 'source']
data rows: 7
rows with != 4 fields: []
```
(`python3 -c` csv.reader check above; file 2,599 bytes.)
Verdict: **T5 = PASS** — table saved at the exact named path.
Files created/modified:
- Created: `data/processed/task_T5_comparator_summary.csv` (the named
  deliverable; written directly rather than via a new script — it is a
  static curation of cited values, and inventing a script number for a
  copy task would misrepresent it as a computation).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: Four of the seven cells are
numbers this session did NOT produce; the coupling half of the table is
entirely absence rows, which is the honest state of Group T.
---

## [U1] — Read back what's already been done (150M model result)
Status: PASS (verbatim extraction done before any other U work, as the
task mandates).
Time started / finished: 2026-09-23 00:55:42 / 2026-09-23 00:55:42
What I did: Ran U1a's exact command:
`grep -n "150M\|J2a" -A 20 docs/tasks/review-triage/OVERNIGHT_LOG.md`
and captured the existing 150M-model result. Key findings: (a) the 150M
check was run as J2a item 3 by script 58 (prior session, its own
pre-registration under J3a's block); (b) the prior session's Group-I
counterpart of this whole U group (`I3a — Model/scoring robustness
(150M / ESM-1v / SaProt / pseudo-likelihood)`) was SKIPPED on that run's
user skip list — its one-line entry says so explicitly and notes
"J2a item 3's 150M delta check ... does NOT substitute for this task" —
which is exactly the gap Groups U1-U5 now fill.
Actual output (verbatim quotes from OVERNIGHT_LOG, lines 1671-1684):
```
J2a-3  ESM-2 150M model check (proposal pre-registered model)
sequence len 656; atlas positions 655
sampled N_POS=100 positions (seed 0); 222 in sample: False
Loading esm2_t30_150M_UR50D (weights downloaded and cached this run)
Using device: mps
  100/100 positions (81s elapsed)
scored rows: 1900; unmatched to cached 650M delta: 0
matched for PRIMARY: 1900 substitutions, 100 positions
PRIMARY Spearman(delta_150M, delta_650M): rho=+0.0978 CI=[-0.0444,+0.2275] p=0.1540 n=1900 pos=100
  bands: CI_lo=-0.0444  ->  VERDICT: SIZE-SENSITIVE
SECONDARY (descriptive) sign agreement: 53.11% of 1900 rows (exact-zero ties excluded: 0)
SECONDARY (descriptive) score rho wt bg: +0.4157 (n=1900)
SECONDARY (descriptive) score rho a222v bg: +0.4098 (n=1900)
```
And its verdict text (lines 1692): `conclusions drawn from delta_ESM are
NOT demonstrated to be a property of "ESM-2-family masked marginals" —
they are properties of the 650M checkpoint as measured.` Also noted for
the U5 table: `The 150M weights needed a fresh download (~600 MB,
dl.fbaipublicfiles.com)` (line 1700), and I3a's status line (line 1839):
`SKIPPED — on the user's explicit skip list for this run`.
Verdict: **U1 = PASS** — the 150M result is on the record verbatim; no
duplicate 150M run will be attempted in this group.
Files created/modified: SESSION_LOG.md (this entry only).
Anything unexpected or worth flagging: The 150M comparison is
SIZE-SENSITIVE at the delta level — it already tells U5's verdict
question part of the answer (b-vs-a territory) before U2 even runs; the
U5 row must quote it rather than re-run it.
---

## [U2] — Whole-sequence pseudo-log-likelihood delta (U2a) + script-33 sign-flip null on it (U2b)
Status: **U2a/U2b machinery PASS at reduced-N smoke; the FULL-N result run is BLOCKED by the session's ~2h-per-task cap.**
Time started / finished: 2026-09-23 00:56:00 / 2026-09-23 03:43:45
What I did:
1. Read scripts 32 (`32_delta_esm_primary.py`, full), BOTH files numbered
   33, and `scripts/lib/esm_scoring.py`. Resolution assumption (logged as
   required): the task's "script 33" = **`scripts/33_delta_esm_signflip_null.py`**
   (it contains the sign-flip null and the exact string OVERNIGHT line 27
   cites — `P-values apply to own_e_b`); the other file,
   `33_measurement_noise_control.py`, has no sign-flip null. The
   sign-flip file is NOT on this session's never-touch list.
   "Reuse that code path, do not rewrite" was honored by importing the
   SAME lib functions script 33 itself imports (`wls_line`, `CONCS`,
   `rebuild_interaction_fit`, `_spearman`, `position_cluster_bootstrap`,
   `assign_region`) and copying its loop structure line-for-line,
   including its ±1 identity checks and its Null-2/region arms.
2. Pre-registered the PLL construction in the new script's docstring
   BEFORE any run: `scripts/67_u2_pll_delta.py` (next free number after
   66). Construction: pseudo-log-likelihood summed over all 655 atlas
   positions incl. 222; j=p exact (masking removes p from context → the
   cached scripts-10/11 passes ARE the exact terms), j=222 exact and
   per-variant (masking 222 makes both backgrounds' contexts the same
   string → ONE fresh pass/variant reading V and A = the new term
   L222(v)), distal j context-frozen (same approximation the cached
   tables already make) which algebra collapses to
   **delta_PLL(v) = delta_ESM(v) + L222(v) + K**, K a global constant
   (offsets cancel exactly between the p term and the sum's exclusion of
   p). K does not affect Spearman; it is still computed and printed.
   Pre-registered gates: G1 fresh-raw odds reproduce both cached tables
   (tol 1e-4), G2 raw delta at 222 across backgrounds ~ 0 (tol 1e-4),
   G3 = script 33's ±1 identity (tol 1e-6), any failure → exit(1).
   The un-frozen full-sum comparison is a DISCLOSURE, not a gate.
3. Fixed two implementation bugs BEFORE any valid run: (a) index-space
   mixup — ESM vocab indices used where 20-column positions were needed
   (IndexError, smoke 1, 01:13:52); (b) smoke-2 at BATCH=64 produced
   nothing in 60 min — a timed benchmark showed batches >16 thrash MPS
   memory: BATCH=16 = 0.587 s/seq, BATCH=32 did not finish 96 seqs in
   >23 min (>=14 s/seq). BATCH=16 fixed as the setting.
4. Ran the reduced-N smoke (house rule: smoke before full):
   `N_BOOT=300 N_PERM=300 BRUTE_N=2 PHASE2_MAX=300 BATCH=16`, 02:56:29
   → 03:43:45, **PY_EXIT=0**. PHASE2_MAX is a smoke-only knob added for
   this purpose (rows keep NaN delta_pll; every reduced-n number printed
   carries an explicit "machinery check, NOT results" banner; smoke CSVs
   go to *_smoke.csv so they cannot be mistaken for results).
Actual output (verbatim, smoke):
```
G1 odds identity (wt bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
G1 odds identity (av bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
G2 raw delta at 222 across backgrounds = 0.000e+00 (must be ~0: masked contexts identical)
G1/G2 PASS
  global constant K = sum_j delta_bg logP(wt_j) = +1.849228 (sd across positions = 0.03409)
  [phase1-done t=  1001s]
L222 (n=300): mean=-5.17889 sd=0.02569 min=-5.25684 max=-5.07137
Null set (+own_e_b): 297 variants, 17 positions
  direct - (delta_esm+L222): mean=+1.83639 vs K=+1.84923  -> mean algebra residual = -0.01284
  frozen-distal approximation error: sd=0.00444 max|e|=0.01728  (= 4.7% of sd(delta_pll), n=2 disclosed)
  (sample) spearman(direct full-sum, fitted frozen) = +1.0000 n=2
  ORIGINAL delta_ESM (full n, script 32): own e.b rho=-0.088118 | published e.b rho=-0.070705
  *** PHASE2_MAX set: the rows below are reduced-n machinery checks, NOT results (see SESSION_LOG). ***
  ORIGINAL delta_ESM, own e_b (rerun here)     rho=-0.088118 CI=[-0.117583,-0.060596] p=<0.0033 n=10757
  all-+1 flips reproduce own_e_b exactly: max|diff|=9.888e-17
  all--1 flips give exactly -own_e_b:     max|diff|=9.888e-17
  signed delta_PLL vs signed e_b
    observed=-0.0841  null mean=-0.0008 sd=0.0585  p=0.1467
    null-centring check: null mean IS consistent with zero -- machinery behaving
    ORIGINAL delta_ESM side-by-side: observed=-0.0881 null mean=+0.0001 p=0.0000
Saved to .../task67_u2_pll_scores_smoke.csv
Saved to .../task67_u2_results_smoke.csv
  * Total runtime 2831s.
```
All three gates PASS with margin; the full-n ORIGINAL delta_ESM row
re-derives **-0.088118 exactly** (independent reproduction of script 32
through this script's own join+bootstrap path — validates the plumbing,
not the claim: reproduction ≠ replication, AGENTS §6).
Why the FULL-N run did not execute (the BLOCKED math, from measured
timings, not estimates inherited from elsewhere):
```
Phase 1 (gates + K, 1310 passes):      785 s  = 13.1 min
Phase 2 (L222, 0.62 s/seq x 11,344):  7,033 s = 117.2 min
Phase 3 brute BRUTE_N=2 (2,620):      1,643 s =  27.4 min
Phase 4+5 (boots+nulls, scaled x33):  ~600 s =  ~10 min
------------------------------------------------------------
minimum credible full run (BRUTE_N=2):            ~167 min
without the pre-registered disclosure arm:         ~140 min
session cap for any T/U/V task:                   ~120 min
```
Per the session's troubleshooting tree (`any T/U/V task >~2h … BLOCKED,
kill, move on`) under its conservative literal reading — logged as the
assumption: a task whose measured runtime exceeds the cap is BLOCKED
whether or not it is progressing steadily — the full-N U2 run was NOT
started, and no reduced-n number above is claimed as U2's result. The
pre-registered gates/rules were NOT changed to make it fit (that would be
an AGENTS §10 stop-and-ask); no result exists to have motivated a change
anyway.
Verdict: **U2a = BLOCKED (full-N, budget) with construction + machinery
validated; U2b = BLOCKED likewise — its null code path passed its own
±1 identity at 9.888e-17 inside the smoke.** A future session can run
`PHASE2_MAX=0 BRUTE_N=16 N_BOOT=10000 N_PERM=10000` overnight (~3–4 h)
with zero code changes.
Files created/modified:
- Created: `scripts/67_u2_pll_delta.py` (pre-registered design above),
  `data/processed/task67_u2_pll_scores_smoke.csv`,
  `data/processed/task67_u2_results_smoke.csv` (both explicitly
  smoke-suffixed), temp logs/benchmark under the session tmp dir.
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: model load varied 4 s → 216 s
between runs (MPS warm-up); PHASE2_MAX=300 takes df.head(300) which is
position-sorted, so the smoke's region arm only saw region 1 (regions
2–4 printed SKIPPED, as designed); the reduced-n PLL rhos in the smoke
(n=297, 17 clustered positions) are NOT evidence for or against the
hypothesis and must not be quoted as such.
---

## [U3] — ESM-1v, budget-gated (U3a)
Status: **BLOCKED — model size exceeds the 3 GB budget; subtask stopped before any download, per the task's own rule.**
Time started / finished: 2026-09-23 03:47:17 / 2026-09-23 03:48:02
What I did: U3a says to check ESM-1v's model size BEFORE attempting
anything, mark BLOCKED with the size found if a download would exceed
3 GB, and not attempt a partial download. I first resolved the real
loader names from the installed `esm` package (the canonical entry
point is `esm.pretrained.esm1v_t33_650M_UR90S()`, which loads
`esm1v_t33_650M_UR90S_1` — one of a 5-model ensemble; URL template
`https://dl.fbaipublicfiles.com/fair-esm/models/{name}.pt`,
pretrained.py line 53). My first guess at the URL
(`esm1v_t33_650M_UR50D.pt`) returned HTTP 403 (name does not exist —
logged as an unexpected correction below), so I re-HEADed the true
URLs. Only HEAD requests were sent; no bytes were downloaded.
Actual output (verbatim, `curl -sI`):
```
--- weights ---
HTTP/2 200
content-length: 7828635339
--- contact regression ---
HTTP/2 403
```
Size verdict (both readings of "3 GB", conservative first):
- 7,828,635,339 B = 7.829 GB (decimal) vs 3×10^9 B cap → EXCEEDS.
- = 7.292 GiB (binary) vs 3×2^30 = 3,221,225,472 B cap → EXCEEDS.
Either way **> 3 GB ⇒ BLOCKED**. (The regression file HEADed 403 — the
loader's own guard skips contact regression for esm1v, pretrained.py
line 21 — irrelevant to the verdict since weights alone already fail
the gate.)
Verdict: **U3a = BLOCKED (7,828,635,339-byte model > 3 GB); U3's
scoring/correlation body NOT attempted, no partial download made.**
Files created/modified: SESSION_LOG.md (this entry only). No file
written under `~/.cache/torch`, `data/`, or `scripts/`.
Anything unexpected or worth flagging: the wrong-name 403 (corrected
before any fetch); the ensemble structure (ESM-1v = 5 models — even
had the single file fit, "ESM-1v" would have needed an ensemble-choice
decision to be well-defined); model file is 3× larger than the
architecturally identical ESM-2 650M (2,604,537,549 B cached), which
is itself notable but not investigated (out of scope).
---

## [U4] — SaProt, budget-gated (U4a): size within budget, preprocessing judgment-heavy
Status: **BLOCKED on U4a's own preprocessing clause (AGENTS §10 — decisions needed), NOT on budget.**
Time started / finished: 2026-09-23 03:49:29 / 2026-09-23 03:50:25
What I did: Checked the three facts U4a asks about before any fetch:
(1) SaProt's model size (HF API tree, HEAD-equivalent metadata only —
no bytes downloaded), (2) whether the on-disk `6FCX.pdb` can be
consumed directly for structure tokens, (3) whether the required
preprocessing tooling exists in this environment. Also verified chain-A
residue 222's identity and the structure's coverage of the atlas.
Actual output (verbatim):
```
=== westlake-repl/SaProt_650M_PDB files+sizes ===
SaProt_650M_PDB.pt            2606464143
pytorch_model.bin             2606517773
TOTAL bytes (all files):      5212987070
chain A residue 222 = ALA (A222V needs ALA here)
atlas positions (2..656) WITHOUT chain-A coords: 59
contiguous missing runs: [(2, 39), (161, 171), (392, 396), (652, 656)]
=== chains ===
chain A: 596 residues, range 40..651, has 222: True, breaks: 2
   first breaks: [(160, 172), (391, 397)]
chain B: 590 residues, range 41..648, has 222: True, breaks: 4
   first breaks: [(160, 172), (202, 205), (219, 222), (313, 317)]
=== tooling ===
foldseek not found
(no foldseek binary) / (no foldseek/saprot pip pkg)
(no SaProt/foldseek/3Di machinery anywhere under scripts/, notebooks/)
```
Size verdict (3 GB cap, both readings of the single needed file):
`SaProt_650M_PDB.pt` = 2,606,464,143 B = 2.606 GB / 2.427 GiB →
**WITHIN** 3 GB either way (only one weight format needs fetching; the
two files are the same model in .pt and HF-bin form — noted, not
doubled). So budget does NOT block U4.
Why BLOCKED anyway (U4a's explicit clause: "if the preprocessing itself
is unclear or judgment-heavy, mark BLOCKED and say exactly what decision
is needed"): SaProt cannot consume the PDB directly — it needs 3Di
structure tokens (foldseek) fused with amino acids into SaProt's paired
vocabulary, none of which exists in this environment. Exactly three
decisions are needed:
1. **Chain choice**: A vs B have *different* missing-residue patterns —
   chain B lacks 220–221 (adjacent to the study's key site), chain A
   lacks 161–171 and 392–396. The choice changes which variants are
   scoreable; chain A looks better but "looks" is a judgment.
2. **Missing-coordinate policy**: 59 atlas positions (2–39, 161–171,
   392–396, 652–656 — ≈1,100 missense variants) have no chain-A
   coordinates, so no structure token exists for them. Options each
   change the analysis differently: exclude those variants (n drops),
   impute a gap/unknown token (depends on SaProt tokenizer conventions
   not verified here), or substitute another structure source (out of
   scope — task says use the on-disk 6FCX). No project precedent exists.
3. **Tooling acquisition**: foldseek (binary or wrapper) must be
   introduced to the environment; method/version not pre-verified.
   (Smallest of the three, listed for completeness.)
Positive facts for the record: PDB numbering IS canonical (chain A
residue 222 = ALA ✓, so the atlas↔structure alignment itself is
trivial, not a judgment); the WT-structure-reused-across-variants
convention is standard SaProt DMS practice but is not documented
anywhere in THIS repo (first contact) — folding it into decision 1/2's
resolution.
Verdict: **U4a = BLOCKED (preprocessing decisions 1–3 above; size
PASSED at 2,606,464,143 B ≤ 3 GB). U4's scoring body NOT attempted;
no fetch, no foldseek install, no score computed.** Resolving the three
decisions is a user call (AGENTS §10: pre-registered-rule / judgment
territory — unattended session must not pick for them).
Files created/modified: SESSION_LOG.md (this entry only). No other
file written.
Anything unexpected or worth flagging: budget PASSED but preprocessing
failed the clause — U4's blocker is qualitative, not numeric, so a
later session with the three decisions can likely run it fully within
budget (~2.6 GB fetch + 655×2 passes ≈ same ~17 min as ESM-2 scoring,
plus one-time foldseek conversion).
---

## [U5] — Model/scoring robustness summary table + group verdict
Status: PASS.
Time started / finished: 2026-09-23 03:50:30 / 2026-09-23 03:52:57
What I did: Assembled the exact named deliverable
`data/processed/task_U5_model_robustness_summary.csv` (columns: model or
scoring variant, run status, delta-vs-e.b correlation if obtained,
source/reason) from logged values only — nothing re-run, nothing
invented (AGENTS §5). Six rows: (1) ESM-2 650M single-position
masked-marginal delta — RUN, own e.b rho=-0.088118 with its
position-block null p<0.0001, published e.b rho=-0.070705;
(2) ESM-2 650M whole-sequence PLL (script 67, U2a) — NOT RUN at full N
(BLOCKED ~167 min > 2h), smoke gates quoted, correlation NOT OBTAINED;
(3) ESM-2 150M (script 58) — RUN, but only cross-model agreement
rho=+0.0978 CI=[-0.0444,+0.2275] p=0.1540 SIZE-SENSITIVE, e.b
correlation NOT OBTAINED (never computed); (4) ESM-1v — BLOCKED
7,828,635,339 B > 3 GB; (5) SaProt 650M PDB — BLOCKED on the
preprocessing clause (size passed); (6) the required one-line verdict
row. The first write had two rows with unquoted commas (parse showed
`rows with != 4 fields: [2, 5]`) — caught by the csv.reader check and
rewritten before this entry.
Actual output (verification):
```
header: ['model_or_scoring_variant', 'run_status', 'delta_vs_eb_correlation', 'source_or_reason']
data rows: 6
rows with != 4 fields: []
verdict cell: (d) still undetermined given what could/couldn't be run tonight
```
Group-U verdict (verbatim from the CSV's last row):
**(d) still undetermined given what could/couldn't be run tonight** —
every delta-vs-e.b number obtained comes from ESM-2 650M itself; the
150M arm only shows cross-model deltas barely agree (rho=+0.0978, CI
crosses 0 → size-sensitive); PLL(full), ESM-1v and SaProt produced no
full-N e.b correlation within session budgets — so (a) 650M-specific,
(b) ESM-2-family-general, (c) masked-marginal-artifact cannot be
separated on tonight's evidence. That (d) is itself the honest reading
of Group U: two of four comparators were stopped by the session's own
budget rules and one by its judgment clause, all for reasons logged
above.
Verdict: **U5 = PASS** (named file, parse-verified).
Files created/modified:
- Created: `data/processed/task_U5_model_robustness_summary.csv` (the
  named deliverable; static curation, no new script — copying logged
  numbers does not warrant a script number).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: the U5 verdict being (d) rather
than a/b/c is determined by U2/U3/U4's BLOCKED statuses — if any of
those later unblocks (overnight PLL run, ESM-1v under a changed cap,
SaProt after the three decisions), this verdict row must be regenerated,
not edited by hand.
---

## [V1] — ThermoMPNN availability and budget check (V1a)
Status: PASS — within the ~200MB expectation; setup requirements known.
Time started / finished: 2026-09-23 03:53:54 / 2026-09-23 03:56:05
What I did: Checked model size and setup BEFORE attempting anything, as
V1a mandates: GitHub search resolved the canonical repo
(`Kuhlman-Lab/ThermoMPNN`, 273 stars — the PNAS 2024 paper's own lab);
enumerated every blob via the git trees API for exact byte sizes; read
the README's install/inference sections; read `analysis/custom_inference.py`
in full (the single-PDB site-saturation entry point — this is V2's
vehicle) and grepped the entry path for mmseqs/wandb dependencies.
Metadata only — nothing cloned or installed yet.
Actual output (verbatim, sizes from GitHub git-trees API):
```
models/thermoMPNN_default.pt                        38894003
vanilla_model_weights/v_48_002.pt                    6681301
vanilla_model_weights/v_48_010.pt                    6681301
vanilla_model_weights/v_48_020.pt                    6681301
vanilla_model_weights/v_48_030.pt                    6681301
TOTAL repo blob bytes: 162933873 (162.9 MB)
README: "This step can be skipped if only running custom_inference.py"
        (no local.yaml dataset-path edits needed for our path)
        "Training requires a GPU" (inference not stated as GPU-gated)
entry args: --pdb --chain (default 'A') --model_path --out_dir
device line: torch.device("cuda" if torch.cuda.is_available() else "cpu")
mmseqs/wandb hits: custom_inference.py 0, SSM.py 0, model_utils.py 0,
                   transfer_model.py 0, protein_mpnn_utils.py 0,
                   datasets.py 2 (imported by the entry — watch for
                   ImportError at install time)
```
Budget accounting (V's own ~200MB expectation, per V1a's wording — the
Group-T 195.1/200 MB counter stays T's):
- needed weights: 38,894,003 (ThermoMPNN) + one vanilla backbone
  6,681,301 (transfer-learning wrapper) ≈ 45,575,304 B;
- planned clone: sparse (code+weights, skip images/dataset_splits) ≈
  ~70 MB, full depth-1 worst case 162.9 MB;
- pip deps to add to the existing venv (torch already present):
  pytorch-lightning, omegaconf, biopython (+ wandb only if an actual
  ImportError demands it) ≈ tens of MB.
All well under 200 MB ⇒ **NOT blocked; nowhere near the 3 GB fallback
cap either.**
Setup requirements (the V1a deliverable):
1. `git clone` (planned: `data/external/ThermoMPNN`, gitignored like
   the rest of `data/`, mirroring the GB1 precedent);
2. bundled `local.yaml` present — loaded unconditionally by
   `custom_inference.py` but its dataset paths are NOT needed for the
   single-PDB path (README explicit);
3. deps into the EXISTING venv (never a second 2 GB torch env — the
   uv/mamba instructions in the README would double-install torch and
   blow V's budget): pytorch-lightning (train_thermompnn imports it),
   omegaconf, biopython, tqdm/pandas/numpy already in venv;
4. no GPU required for inference (their device line falls back to CPU);
5. entry command shape:
   `python analysis/custom_inference.py --pdb <6FCX.pdb> --chain A
   --model_path models/thermoMPNN_default.pt --out_dir <dir>` → one
   batched site-saturation call producing position/wildtype/mutation/
   ddG_pred rows (≈596 resolved chain-A residues × 19 alts ≈ 11.3k);
6. positional facts carried over from U4 (same PDB): chain A default
   is also the better chain (has residue 222 = ALA, canonical
   numbering), and the 59 unresolved atlas positions (2–39, 161–171,
   392–396, 652–656) will simply be ABSENT from ThermoMPNN's parsed
   residue list — exclusion is structural, not a choice; n-drop will be
   reported at V2.
Verdict: **V1 = PASS (model 38,894,003 B; total footprint ≈ ~110–190 MB
planned; setup mapped; proceed to V2).**
Files created/modified: SESSION_LOG.md (this entry only). Nothing
cloned/installed yet.
Anything unexpected or worth flagging: README's default install path
(uv/mamba, full CUDA torch) conflicts with this session's budgets — the
existing-venv pip route above is the deliberate deviation and will be
logged again if any package fails to install on Python 3.14 (then V2 =
BLOCKED with the exact error, per the troubleshooting tree).
---

## [V2] — Score ΔΔG for every atlas missense variant (ThermoMPNN, 6FCX chain A)
Status: **PASS** — named deliverable written; every gate green on the
successful run; dropped rows fully accounted (1,046 + 157 = 1,203 exact).
Time started / finished: 2026-09-23 04:01:50 / 2026-09-23 04:12:23
What I did: Wrote `scripts/68_thermompnn_ddg_epistasis.py` (next free
number after 67) with the docstring pre-registering, BEFORE its first
run: the V4 additive interaction rule, chain-A choice, exclusion of
unresolved positions, the output-mapping rule, the stats parity with
scripts 32/33, and the timing discipline. Inference runs through
ThermoMPNN's OWN CLI unmodified (subprocess; their code is never edited
or re-implemented). Executed in this order: (1) fragment timing smoke —
chain A residues 200-249, 1,000 predictions in 2.6 s = 0.003 s/pred,
full run extrapolated 32 s (well under V2's ~60-min budget); (2) full
chain-A SSM — 11,920 rows = 596 resolved residues × 20 alts (incl.
self-mutations) in 10.2 s; (3) join + accounting + save. Three
pre-result corrections were forced by gates, all before any statistic
existed: (a) `wandb` ImportError at their entry (train_thermompnn
imports it) → `pip install wandb`; (b) my first mapping hypothesis
("contiguous 0-based index") was **refuted by the stage-2 gate at 444
wildtype mismatches starting exactly at the 161-171 gap** — diagnosis
showed their `position` = *resi − first chain-A residue number* (offset
40; gap slots simply absent); the corrected offset mapping verified at
**0 mismatches on both fragment and full**, and the gate was hardened to
set-equality + wildtype agreement at every position + resi-222=A
(docstring corrected to match, still pre-result); (c) A222V is not an
atlas row (phase5 position==222 count = 0, logged in [U2]) so V3's
ddG(A222V) is read from their own SSM row instead of the join — plus one
missing `sys.path` preamble (ModuleNotFoundError, immediate fix).
Actual output (verbatim, successful run `N_BOOT=10000`, PY_EXIT=0):
```
GATE: offset map (set equality + wildtype agreement) at all 50 fragment residues PASS; resi 222 wildtype = A PASS
timing: 1000 predictions in 2.6s = 0.003 s/pred (CPU)
full rows: 11920  (fragment extrapolation: 32s for 11,920 = 596x20 -- actual 10s)
GATE: ddG fully finite; offset map (set equality + wildtype agreement) at all 596 resolved positions (chain A) PASS
atlas rows: 11344 | matched ThermoMPNN ddG: 10141 | dropped: 1203 (10.6%)
breakdown of 1203 dropped rows: 1046 rows at 59 unresolved positions (predicted 59: 2-39, 161-171, 392-396, 652-656); 157 rows at 9 positions where 6FCX chain A's residue differs from canonical P42898 ([429, 594, 645, 646, 647, 648, 649, 650, 651]) -- their SSM scores the CONSTRUCT residue there, so joining those atlas variants would be wrong; correctly excluded.
Saved to .../data/processed/task_V2_thermompnn_ddg.csv  (10141 rows)
LIMITATIONS (printed here, per AGENTS sec 6): chain A only; 59 unresolved positions excluded (dropped count above); WT structure reused for every variant; additive term is pre-registered with no free parameters and was NOT tuned; total runtime 51s.
```
Verdict: **V2 = PASS.** (A separate standalone diagnostic independently
re-derived the 1,046 + 157 = 1,203 split before the final run, so the
accounting was verified twice, by two different executions.)
Files created/modified:
- Created: `data/processed/task_V2_thermompnn_ddg.csv` (named
  deliverable, 10,141 rows: hgvs_pro, position, wt/mut, ddg, pred_eb,
  own_e_b, published e.b, delta_esm, region), `scripts/68_thermompnn_ddg_epistasis.py`,
  `data/external/ThermoMPNN/` (sparse clone, 125 MB, gitignored),
  venv additions (wandb stack, pytorch-lightning, omegaconf — tens of MB;
  pip does not print a total, disclosed as not byte-counted), tmp logs
  (fragment/full stdout, smoke logs).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: their `position` quirk (offset +
missing gap slots — a naive join would have silently mapped residues
wrongly; the gate earned its keep twice); 9 construct-vs-canonical
positions (6FCX differs from P42898 at 429/594/645-651) whose variants
are excluded — if anyone later wants those, they need a different
structure, not a different join; V fetch total ≈ 125 MB clone + ~50-70 MB
deps ≈ under the ~200 MB expectation (exact pip bytes unavailable).
---

## [V3] — A222V's own ΔΔG (one number)
Status: PASS.
Time started / finished: 2026-09-23 04:11:32 / 2026-09-23 04:12:23
(produced inside the successful full run of [V2]; this entry quotes its
own executed output line).
What I did: Extracted the single pre-specified value from ThermoMPNN's
chain-A SSM at resi 222 → V (their position 182 under the gated offset
map; wildtype verified A). Source is their SSM row, NOT the atlas join,
because phase5 contains no A222V row (0 rows at position 222) — this
source choice was pre-registered in the script text and printed in the
run output itself.
Actual output (verbatim):
```
V3 (one number): ThermoMPNN ddG(A222V) = -0.0439 (model output units) -- read from their SSM row (position 222 = resi 222), not from the atlas join
```
Verdict: **V3 = PASS** — ddG(A222V) = **−0.0439** (model output units as
emitted; no unit conversion claimed).
Files created/modified: SESSION_LOG.md (this entry only) — the number
lives in the executed output and (as the A222V ddg used to build
pred_eb) implicitly in V2's CSV; no separate file for one scalar.
Anything unexpected or worth flagging: −0.0439 is small relative to the
spread of single-mutant ddGs the model emits — i.e. ThermoMPNN thinks
A222V itself is nearly neutral, a fact V4's additive term will inherit
(pred_eb ≈ ddG(v) + a near-constant offset, which cannot change rho at
all: adding a constant leaves Spearman invariant — V4's rho is therefore
formally a test of ddG(v) alone vs e.b, printed as such below).
---

## [V4] — Pre-registered additive interaction term vs e.b
Status: PASS — executed exactly as pre-registered (rule fixed in
`scripts/68`'s docstring before the first run of that script).
Time started / finished: 2026-09-23 04:11:32 / 2026-09-23 04:12:23
What I did: Computed `pred_eb(v) = ddG(v) + ddG(A222V)` (ADDITIVE chosen
pre-run; threshold-crossing explicitly rejected pre-run because its θ
would be a free parameter chosen after seeing e.b) on the 10,141-row
joined set, then ran the project's standard position-cluster bootstrap
(N_BOOT=10000, seed 0 — identical machinery to scripts 32/33) of
pred_eb against own e.b (primary) and published e.b (secondary).
Actual output (verbatim):
```
V4 -- ADDITIVE STABILITY TERM (pred_eb = ddG(v) + ddG(A222V); N_BOOT=10000)
V4 primary: pred_eb vs own e.b               rho=-0.0733 CI=[-0.1021,-0.0437] p=<0.0001 n=9595
V4 secondary: pred_eb vs published e.b       rho=-0.0643 CI=[-0.0916,-0.0364] p=<0.0001 n=9595
```
n reconciliation (AGENTS §5): 10,141 matched rows − 546 without own e.b
= 9,595 (global own-e.b missingness is 587/11,344 = 5.17%; 546/10,141 =
5.38% among matched — a 0.2 pp difference, arithmetic closes, no
unexplained rows).
Interpretive guard (stated here, before anyone quotes it): because
ddG(A222V) is a constant, pred_eb's Spearman rho is **identical to
ddG(v) vs e.b** — the additive term tests the stability signal, not an
interaction in the statistical sense; that is a property of the
pre-registered construction (one fixed background ⇒ every additive term
is rank-degenerate — the same AGENTS §8 Model-B trap, avoided here by
DISCLOSING it rather than by inventing a non-additive rule after seeing
results).
Verdict: **V4 = PASS (result obtained; the hypothesis verdict is V7's).**
Files created/modified: SESSION_LOG.md (this entry only); computation
lives inside script 68 whose CSV already carries pred_eb.
Anything unexpected or worth flagging: the rank-degeneracy point above
— someone skimming could mistake rho=−0.0733 for "A222V adds
information"; it does not, by construction. The −0.0733 IS the
stability-only signal, and it is negative like ESM-2's −0.088.
---

## [V5] — Head-to-head: ThermoMPNN vs ESM-2 delta_ESM (own e.b, both CIs)
Status: PASS.
Time started / finished: 2026-09-23 04:11:32 / 2026-09-23 04:12:23
What I did: Read ESM-2's own-e.b row from
`data/processed/task32_delta_esm_primary.csv` (NOT re-run) and printed
it beside [V4]'s primary result, both with position-cluster CIs, plus
the pre-declared "larger |rho|" and "CI excludes 0" comparisons the
script computes mechanically.
Actual output (verbatim):
```
V5 -- HEAD-TO-HEAD vs ESM-2 delta_ESM (own e.b, both CIs)
ESM-2 delta_ESM : rho=-0.0881 CI=[-0.1173,-0.0595] n=10757
ThermoMPNN additive: rho=-0.0733 CI=[-0.1021,-0.0437] n=9595
larger |rho|: ESM-2 delta_ESM; ThermoMPNN CI excludes 0: True
```
Verdict: **V5 = PASS.** On the record: ESM-2's |rho| is larger
(0.0881 vs 0.0733) but the two CIs overlap substantially
([−0.117,−0.060] vs [−0.102,−0.044]) and both exclude 0 — the comparison
is "both negative, overlapping, ESM-2 nominally larger", not a clean win
for either, on n=10,757 vs 9,595 respectively.
Files created/modified: SESSION_LOG.md (this entry only).
Anything unexpected or worth flagging: the n's differ (10,757 vs 9,595)
by [V2]'s structural exclusions + own-e.b coverage — the head-to-head is
NOT computed on an identical row set (9,595 ⊂ 10,757 roughly), so
headline "larger |rho|" is apples-to-similar-apples; a strictly matched
subset was not part of the pre-registered plan and was not done
post-hoc (disclosed rather than tuned, AGENTS §0).
---

## [V6] — Four-region check on the ThermoMPNN correlation
Status: PASS.
Time started / finished: 2026-09-23 04:11:32 / 2026-09-23 04:12:23
What I did: Ran the position-cluster bootstrap of pred_eb vs own e.b
separately inside each of the four `assign_region` regions (n_boot
10000), reading ESM-2's own four region rows from
`task32_delta_esm_primary.csv` for the side-by-side; regions with <15
positions would print SKIPPED (none did).
Actual output (verbatim):
```
V6 -- FOUR-REGION BREAKDOWN (pred_eb vs own e.b)
region 1 (2-147)    Thermo rho=-0.1323 CI=[-0.1815,-0.0827] n=1906  | ESM-2 same region: rho=-0.1563 CI=[-0.2047,-0.1075]
region 2 (148-294)  Thermo rho=+0.0732 CI=[+0.0033,+0.1404] n=2220  | ESM-2 same region: rho=+0.0222 CI=[-0.0357,+0.0779]
region 3 (295-474)  Thermo rho=-0.0765 CI=[-0.1307,-0.0211] n=2609  | ESM-2 same region: rho=-0.0573 CI=[-0.1123,-0.0033]
region 4 (475-656)  Thermo rho=-0.1237 CI=[-0.1751,-0.0716] n=2860  | ESM-2 same region: rho=+0.0103 CI=[-0.0365,+0.0568]
```
Verdict: **V6 = PASS.** The pre-existing note that ESM-2's delta is
weakest in region 4 (ESM +0.0103, CI crosses 0) is reproduced exactly,
and ThermoMPNN is **strongly negative there (−0.1237, CI excludes 0)** —
the stability signal and the ESM signal are NOT interchangeable across
regions: region 4 (N-terminal-binding-domain-ish span 475-656) is where
a ΔΔG-based predictor adds signal that masked-marginal delta_ESM lacks,
while region 2 is where BOTH are positive (Thermo +0.0732 barely clears
0; ESM +0.0222 does not). Region-by-region pattern, not just the
pooled rho, is what V7 must summarize.
Files created/modified: SESSION_LOG.md (this entry only).
Anything unexpected or worth flagging: region 2's POSITIVE rho for both
predictors (opposite sign to regions 1/3/4) was already known for ESM-2;
ThermoMPNN reproducing it too suggests the sign flip is a property of
the MEASURED e.b in that span, not of either model — flagged for V7's
wording, not re-tested here (no new null was pre-registered for V6).
---

## [V7] — Plain verdict
Status: PASS (paragraph below; no computation of its own — it quotes only
already-executed [V3]–[V6] outputs).
Time started / finished: 2026-09-23 04:12:30 / 2026-09-23 04:13:10
What I did: Wrote the one-paragraph verdict V7a asks for, checking every
number against the executed outputs above; no new run.
V7a paragraph: **Adding real stability information does not flip the
project's core claim the way the first of V7a's two poles proposes, but
it does refute the second.** The pre-registered stability-mediated term
pred_eb(v) = ddG(v) + ddG(A222V) — which, because ddG(A222V) = −0.0439 is
a constant, is rank-identical to ThermoMPNN's ddG(v) alone — correlates
negatively with measured e.b at rho = −0.0733, position-cluster CI
[−0.1021, −0.0437], p < 0.0001, n = 9,595, so stability-mediation does
NOT fail: the interaction is at least partly a stability phenomenon, and
the "isn't simply stability-mediated either" branch is out. What does
not survive is the strong form of the reframe — "ESM-2 specifically just
doesn't do it": pooled, ESM-2's masked-marginal delta_ESM (rho = −0.0881,
CI [−0.1173, −0.0595], n = 10,757) is if anything the *better* predictor
of the two, with heavily overlapping CIs, so one cannot say ESM-2 fails
to use background information while an explicit structure-derived
stability score succeeds — both do, comparably weakly (each |rho| < 0.09,
i.e. under 1% of rank variance). The reframe therefore holds only
regionally, and specifically where the project already knew ESM-2 was
weakest: in region 4 (475–656) ESM-2 is null (rho = +0.0103, CI
[−0.0365, +0.0568], crossing 0) while ThermoMPNN's stability term is
strongly negative (rho = −0.1237, CI [−0.1751, −0.0716], excluding 0) —
structure-derived stability supplies real signal exactly where ESM-2's
masked-marginal delta demonstrably has none — whereas in region 2 both
are positive (Thermo +0.0732 barely clearing 0, ESM +0.0222 not), which
points at the measured e.b itself, not either model, as the source of
that sign flip. The honest one-sentence update to the core claim is
therefore narrower than either pole: *the epistasis is weakly but
significantly predictable from structure-derived stability information
and is at least partly stability-mediated; ESM-2 is not globally blind
to it — its pooled delta does about as well — but it loses the signal
specifically in region 4, where the stability model keeps it.* Two
standing caveats ride along: the additive construction is a stability
MAIN effect, not a true interaction term (with one fixed background it is
rank-degenerate with ddG(v), AGENTS §8 — disclosed in [V4], not tuned
around), and the head-to-head pools two different row sets (10,757 vs
9,595, [V5]).
Verdict: **V7 = PASS.**
Files created/modified: SESSION_LOG.md (this entry only).
Anything unexpected or worth flagging: the answer landed between V7a's
two poles rather than on either — a reading a skim could get wrong in
both directions ("stability refutes ESM-2" and "stability fails too" are
both contradicted by the executed numbers).
---

## [W1] — Denser, non-bimodal background selection (decile rule)
Status: **PASS** — selection CSV written; all gates green; the design
gap M1 flagged (A222V alone between two clusters) is structurally fixed:
A222V's severity now falls INSIDE the selected span.
Time started / finished: 2026-09-23 04:26:22 / 2026-09-23 04:26:40
(first attempt 04:26:22 died pre-output on a trivial `list.iterrows()`
type bug in the pick loop — AttributeError raised BEFORE any selection
row was produced; fixed (iteration over the list of Series directly),
rerun 04:26:40 → PY_EXIT=0; no result existed at the time of the fix,
so nothing result-dependent changed — disclosed per AGENTS §6).
What I did: Wrote `scripts/69_w_decile_background_rescore.py` (next free
number after 68) with the ENTIRE W1–W4 pre-registration in its docstring
before the first execution: decile rule (edges = np.quantile of the full
12,445-row `esm2_score` column at 0.1..0.9; bin = searchsorted 'right',
bin 1 = [min,p10) … bin 10 = [p90,max]; candidates = position≠222 AND
position NOT in the original M1 subset — the logged Design-A assumption
that keeps W2's "same subset for comparability" byte-identical while
honoring M1's own-position-never-a-target rule; 3 picks per bin via
deterministic (score, position, mut_aa) sort: slot A = bin's most
damaging, B = middle, C = least → 30 backgrounds), the W2 timing/budget
rule (never shrink the subset; drop order C-bins then B-bins; k<10 ⇒
BLOCKED), the W3 M1d/M1e methodology (identical to script 63), and the
W4 side-by-side + contradiction-tolerance rules. Executed
`W_STAGE=select` (selection only, no model, no scoring) as W1's own
actual run, per the stage discipline script 63 established.
Actual output (verbatim, successful run PY_EXIT=0):
```
(g0) all required inputs present (incl. original M1 artifacts) -- OK
(g1) S(A222V|WT) matches prior verified value -5.200276 -- OK
=== W1: selected backgrounds (rule: 3 per score-decile bin x 10 bins, pos!=222, subset-excluded, deterministic) ===
  D 1A  pos 179 V>W  p.Val179Trp      S(b|WT)=-18.007029  D1A_V179W
  D 1B  pos 331 E>P  p.Glu331Pro      S(b|WT)=-14.366097  D1B_E331P
  ...  [30 rows, gates: all positions distinct, none 222, none in the 120-position subset, exactly 3 per decile]
  D10C  pos 488 I>V  p.Ile488Val      S(b|WT)=+4.070509  D10C_I488V
severity span of the 30: [-18.007029, +4.070509] ; A222V -5.200276 sits INSIDE that span
decile bin ranges (selected picks):
  bin  1: [-18.007, -12.806]
  ...
  bin 10: [-1.186, +4.071]
selection saved -> .../data/processed/task69_w1_selection.csv
W_STAGE=select -> W1 done, exiting before any scoring.
```
Verdict: **W1 = PASS.** Design check against the task's own motivation:
the original design put A222V alone between min/max-per-region clusters;
under the decile rule A222V's S = −5.200 sits within decile 7's selected
range [−6.462, −4.912] — i.e. it is flanked by selected backgrounds on
both sides, exactly the interpolation the prior session flagged as
missing. Decile coverage spans the full severity range (global extremes
−18.007 … +4.071).
Files created/modified:
- Created: `scripts/69_w_decile_background_rescore.py`,
  `data/processed/task69_w1_selection.csv` (30 rows).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: the global most-damaging
substitution (V179W, −18.007) was re-picked as D1A — it was also the
original design's most-damaging pick (R2_V179W); this is the deterministic
rule doing its job, not a carry-over, and its presence does not make the
new design bimodal (it is bin 1 of 10). Position 45 also reappears but
with a DIFFERENT substitution (L45P vs original L45D) — same-position
re-picks are permitted by the pre-registered rule because 45 ∉ subset.
The first-attempt AttributeError (fixed pre-result) is the only code
hiccup; the Design-A subset-exclusion assumption is disclosed in the
docstring and here.
---

## [W2] — Rescore, time-budgeted (30 decile backgrounds x original M1 subset)
Status: **PASS** — all 30 backgrounds scored (pre-registered reduction
NOT triggered), 34.2 min of scoring ≤ the 90-min budget, cache written;
subset never reduced (the task's fallback was never needed).
Time started / finished: 2026-09-23 04:27:27 / 2026-09-23 05:02:48
What I did: Ran `scripts/69` default stage at `N_BOOT=300` (smoke-grade
bootstrap per AGENTS §1 — scoring itself is N_BOOT-independent and this
run's scoring output IS the final one; the CIs from this run are NOT
quoted as results, W3/W4 quote the N_BOOT=2000 run below). Subset =
the original M1 subset VERBATIM, read as evidence from
`task63_m1_bg_raw.csv`'s unique positions (n=120; g2 confirmed it
matches task63's own n_sub, contains no 222, and is disjoint from the
original 8 background positions). Pre-gates before any model load: all
2,280 (position,alt) hgvs resolved in the WT table (g3 pre-check, so a
naming failure could not cost the scoring run); FASTA letters matched
the table at all 30 selected positions. Scored background 1
(D1A_V179W) first and timed it per the pre-registered rule, decided k
from that t1, then scored the remaining 29 — `get_position_logprobs`
unchanged (scripts 10/11/63 code path), MPS, eval mode.
Actual output (verbatim, key lines; PY_EXIT=0):
```
(g2) original subset OK: n=120, no 222, disjoint from the original 8 background positions -- OK
(g2) fasta letters match table at all 30 selected background positions, 222==A -- OK
(g3) pre-scoring: all 2280 (position,alt) hgvs resolve in the WT table -- OK
Using device: mps
Loading ESM-2 650M...
model loaded in 3.3s
M1b-timed: background 1/1 D1A_V179W -> 61.7 s for 120 positions (514 ms/pass)
(g6) t1=61.7s for the first background; projection for 30 = 1850.9s (budget 5400s)
scoring wall time: 61.7s total
(g6) no reduction: t1=61.7s x 30 = 1850.9s <= 5400s budget
M1b-timed: background 29/29 D10C_I488V -> 75.1 s for 120 positions (626 ms/pass)
scoring wall time: 2051.2s total
scoring cache saved -> .../data/processed/task69_w2_bg_raw.csv
```
Verdict: **W2 = PASS.** Scoring time 2,051.2 s = 34.2 min (30
backgrounds x 120 positions = 3,600 forward passes; 514–626 ms/pass) —
1.59x under the 90-min budget; k=30 kept, all 10 decile bins covered
(g6's direct check passed). Note the pre-registered decision used the
FIRST call's t1=61.7 s; per-background time drifted upward across the
run (61.7 → 75.1 s, +22%, MPS thermal/scheduler drift), so the actual
total (2,051 s) came in 11% above the t1 projection (1,851 s) — and the
verdict would not change under either number (even 75.1 x 30 = 2,253 s
≪ 5,400 s), so the budget rule is robust to the drift.
Files created/modified:
- Created: `data/processed/task69_w2_bg_raw.csv` (scoring cache,
  30 x 120 x 19 = 68,400 rows), `task69_w3_backgrounds.csv` +
  `task69_w3_bootstrap.csv` (written by this run at smoke N_BOOT=300 —
  to be superseded by the N_BOOT=2000 run, same script, cache-reused).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: (a) the ~22% per-background time
drift (disclosed above; projection rule uses t1 by pre-registration —
no post-hoc switch to a median time); (b) the model loads twice (once
for the timed first background, once for the remaining 29 — my
implementation calls the scorer twice; 3.3 s + 3.7 s, negligible, and
the second call redundantly re-prints a "(g6) t1=..." line for ITS
first background — cosmetic only; the k decision was already made from
the first call's 61.7 s, printed before either decision line); (c)
A222V's g4 arm gate (120x19 = 2,280 rows from script 12's merged file)
passed silently — no failure line is the pass signal, same as script 63.
---

## [W3] — Rerun the M1d/M1e-style tests on the denser design
Status: **PASS** — executed exactly as pre-registered (OLS on the new
backgrounds only, predict A222V, position-cluster bootstrap on residual
AND correlation; identical methodology to script 63's M1d/M1e).
Time started / finished: 2026-09-23 05:03:46 / 2026-09-23 05:03:48
What I did: Ran `scripts/69` at N_BOOT=2000 (the quotable full run;
the earlier N_BOOT=300 outputs from [W2]'s run are smoke-grade and NOT
quoted here). The scoring cache was reused (no model load — scoring is
deterministic), so this run is selection → cache → delta summaries →
M1d → M1e → W4 → save. Methodology ported 1:1 from script 63:
delta_ESM_b = S(v|b) − S(v|WT) on hgvs_pro; mean|delta| per background
over 120×19; A222V arm = script 12's existing merged file restricted to
the same subset (g4: 2,280 rows, passed); OLS on the 30 NEW decile
backgrounds only; residual CI and Spearman/Pearson CIs from a 2,000-draw
position-cluster bootstrap (cluster = subset position, same indices for
all 31 rows, rng seed 1 — same as script 63).
Actual output (verbatim, PY_EXIT=0):
```
CACHE REUSED: .../task69_w2_bg_raw.csv matches spec (30 bgs x 120 x 19 = 68400) -- model not loaded; (g6) timing rule not exercised on this run; k as scored in the W2 run
(g5) bootstrap OK: 2000 position-cluster draws, all finite, point estimates inside own CIs
OLS on the 30 new decile backgrounds: mean|delta| = 0.035931 + (-0.003292) * S(b|WT)   [resid RMS on the 30 = 0.03202629]
A222V: observed 0.07425389, predicted 0.05304877, residual r = +0.02120512
residual 95% position-cluster CI = [+0.00464777, +0.03933804]  (N_BOOT=2000, cluster=subset position)
A222V absolute rank of mean|delta| among the 31: 22 (1 = lowest); lowest = False
M1d VERDICT (pre-registered, same rule as script 63): CONTRARY to H1a: A222V sits outlier-HIGH -- residual CI excludes 0 from above
Spearman rho = -0.518548  95% cluster CI [-0.634677, -0.387903]  [PRIMARY]
Pearson  r   = -0.422897  95% cluster CI [-0.551945, -0.230902]
H1a expected direction: NEGATIVE (more damaging = lower S = larger shift); observed sign = negative -> consistent with the severity->shift story in sign (CI excludes 0)
```
Verdict: **W3 = PASS (executed as pre-registered).** Result content,
with effect sizes (AGENTS §3): (a) M1d — A222V's residual is **+0.0212,
CI [+0.0046, +0.0393], excludes 0 from above → CONTRARY to H1a's
outlier-LOW prediction** (H1a expected A222V to show unusually LITTLE
context-shift; it shows unusually MUCH: +0.0212 is 29% of its observed
mean|delta| 0.0743 and +0.66 fit-resid-RMS units above the trend the 30
backgrounds define; its rank 22/31 = higher-shift than two-thirds of
the set). (b) M1e — Spearman rho = **−0.519, CI [−0.635, −0.388]**
(primary), i.e. the severity→shift relationship is real and negative as
H1a's mechanism story predicted, now on n=31 backgrounds spanning all
ten deciles rather than 9 bimodal points. Run-to-run stability check:
the smoke run's CI ([+0.0040, +0.0396], 300 draws) and this full run's
([+0.0046, +0.0393], 2,000 draws) are nearly identical — the verdict
does not depend on N_BOOT (only the 2,000-draw values are quotable).
Files created/modified:
- Created: `data/processed/task69_w3_backgrounds.csv` (31-row table +
  verdict scalars), `data/processed/task69_w3_bootstrap.csv` (7 new
  stat rows + 2 original-comparison rows carrying task63's CIs).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: the M1d verdict direction is
**opposite to H1a's prediction and to what the original design
suggested** — the original was "NOT SUPPORTED" (within trend), the
denser design says "CONTRARY" (outlier-HIGH, CI excludes 0). This is
precisely the kind of verdict a bimodal 9-point design could not
resolve; whether the change is design-driven (it almost certainly is —
the fit slope moved from −0.00136 to −0.00329, 2.4×) is W4's explicit
question, answered there. No gate failed; no post-hoc choice was made
(anything result-dependent would be flagged here — none occurred).
---

## [W4] — Compare against the original bimodal result
Status: **PASS** — side-by-side reported from DISK values of the
original run (not re-run, not re-derived); task-doc quotes checked
against disk within the pre-registered 5e-4 rounding tolerance — **no
CONTRADICTION lines were printed** (disk and task doc agree).
Time started / finished: 2026-09-23 05:03:46 / 2026-09-23 05:03:48
(same execution as [W3]; this entry quotes the W4 section of that run's
output).
What I did: Read `task63_m1_bootstrap.csv` + `task63_m1_backgrounds.csv`
for the original 9-point result, printed both designs side by side with
the pre-registered mechanical labels.
Actual output (verbatim):
```
=== W4: original bimodal design vs new decile design (SAME subset, both position-cluster bootstrap) ===
ORIGINAL (task63, n=9 = 8 extremes-per-region + A222V, n_sub=120, N_BOOT=2000):
  M1d residual +0.00954 CI [-0.00573, +0.02640] -> CI contains 0; original verdict starts 'NOT SUPPORTED: A222V sits with...'
  M1e rho -0.467 CI [-0.583, -0.067]
  task-doc quoted: M1d +0.00954 CI [-0.00573,+0.02640]; M1e rho -0.467 CI [-0.583,-0.067]
NEW (W3, n=31 = 30 decile backgrounds + A222V, n_sub=120, N_BOOT=2000):
  M1d residual +0.02121 CI [+0.00465, +0.03934] -> CI excludes 0
  M1e rho -0.519 CI [-0.635, -0.388]
  mechanical label: M1d verdict CHANGED (residual CI relationship to 0 flipped vs the original)
  mechanical label: M1e STRENGTHENS (same negative sign, CI excludes 0, |rho| larger)
  design note: original = bimodal 8 extremes + interpolated A222V; new = 10 deciles x 3 picks (k=30 kept under the pre-registered budget rule) + same A222V arm, identical subset -- a DESIGN comparison, not an independent replication (same underlying scores machinery)
```
Verdict (plain, as the task asks): **M1d's verdict CHANGES; M1e's
primary correlation STRENGTHENS; the secondary Pearson weakens in
magnitude — an honest part of the answer, not a footnote.**
- **M1d CHANGES**: NOT SUPPORTED (CI [−0.0057, +0.0264] straddled 0) →
  CONTRARY to H1a (CI [+0.0047, +0.0393] excludes 0 from above). Read
  carefully: the original point estimate was ALREADY positive (+0.0095,
  the outlier-HIGH direction) — what the bimodal design could not do is
  resolve it from zero. The two residual CIs OVERLAP on [0.0047, 0.0264],
  so the estimates are not statistically incompatible; the change came
  from the FIT moving (slope −0.00136 → −0.00329, 2.4× steeper under
  full-range leverage → A222V's predicted mean|delta| dropped 0.0647 →
  0.0530 → residual rose), not from new A222V data (identical arm) and
  not from new subset data (identical 120 positions). Plainly: the
  denser design turns "we cannot tell" into "A222V is significantly
  above the trend" — H1a's outlier-LOW story is now contradicted, not
  merely unsupported.
- **M1e STRENGTHENS (primary)**: Spearman −0.467 → −0.519, and the CI's
  upper end moves from −0.067 (barely below 0) to −0.388 — the
  severity→shift correlation is now far from ambiguous, at n=31 instead
  of n=9. **But the secondary Pearson went the other way**: −0.601 →
  −0.423 (both CIs exclude 0: original [−0.711, −0.284], new [−0.552,
  −0.231]). That is the two-cluster leverage leaving the data — two
  extreme clusters mechanically inflate linear correlation; Spearman
  (the pre-registered primary) does the opposite job and gained. Both
  correlations remain negative with CIs excluding 0.
Files created/modified: SESSION_LOG.md (this entry only) — the CSVs
were written by the same run and are attributed to [W3].
Anything unexpected or worth flagging: the Pearson-vs-Spearman split
direction is the one genuinely new piece of information in W4 — a skim
saying "everything strengthened" would be wrong about Pearson; and the
residual-CI overlap with the original means "CHANGED verdict" here is
"resolved from straddling-zero to excluding-zero", not a reversal of
sign. The design note printed by the script stands: same subset, same
A222V arm, same machinery — this is a DESIGN comparison, not an
independent replication (AGENTS §6).
---

## [X1] — Build a project-wide index
Status: **PASS** — purely mechanical walk, no synthesis.
Time started / finished: 2026-09-23 05:06:46 / 2026-09-23 05:06:46
What I did: Walked `docs/tasks/` recursively (sorted dirs, sorted files);
for every subdirectory listed its `.md` files with (a) the file's OWN
first `#` heading quoted verbatim (not interpreted), (b) whether the
file contains a `## SUMMARY` section (`^##\s+SUMMARY`). Wrote
`docs/tasks/INDEX.md`. No verdicts, no curation.
Actual output (verbatim, PY_EXIT=0):
```
wrote docs/tasks/INDEX.md (11 files, 3 with ## SUMMARY, 6 dirs)
## docs/tasks/   (0 .md)
## docs/tasks/comparators-and-consolidation/   (3 .md)
- ...COMPARATORS_AND_CONSOLIDATION.md — title: # Comparators, Stability Mediation, Digest, and Consolidation — ## SUMMARY: no
- ...GROUPS_C_TO_H_DIGEST.md — title: # Digest — REVIEW_TRIAGE Groups A–H (entries never reviewed before) — ## SUMMARY: no
- ...SESSION_LOG.md — title: # SESSION_LOG — comparators-and-consolidation (DRAFT working log) — ## SUMMARY: no
## docs/tasks/i1-mechanism-followup/   (3 .md)
- ...ADDENDUM_I1_CAVEAT.md — title: # ADDENDUM — Epistemic caveat for I1-dependent claims (DRAFT — do not merge) — ## SUMMARY: no
- ...FOLLOWUP_LOG.md — title: # FOLLOWUP_LOG — I1 Diagnosis, Mechanism Follow-Up, and Script 35 Retirement — ## SUMMARY: yes
- ...I1_MECHANISM_FOLLOWUP.md — title: # I1 Diagnosis, Mechanism Follow-Up, and Script 35 Retirement — ## SUMMARY: no
## docs/tasks/results-log/   (1 .md)
- ...MTHFR_RESULTS_LOG.md — title: # MTHFR Context-Dependence Project — Full Results Log — ## SUMMARY: no
## docs/tasks/review-triage/   (2 .md)
- ...OVERNIGHT_LOG.md — title: # Overnight Log — Review Triage Execution — ## SUMMARY: yes
- ...REVIEW_TRIAGE.md — title: # Review Triage — Tasks & Subtasks — ## SUMMARY: no
## docs/tasks/site54-and-script50-migration/   (2 .md)
- ...MIGRATION_LOG.md — title: # Migration Log — Position-54 Verification, I1 Rerun, and Script 50 Migration — ## SUMMARY: yes
- ...SITE54_AND_SCRIPT50_MIGRATION.md — title: # Position-54 Verification, I1 Rerun, and Script 50 Migration — ## SUMMARY: no
Walk summary (mechanical counts only): 11 .md files across 6 directories; 3 contain a `## SUMMARY` section.
```
Verdict: **X1 = PASS.** Completeness signal for later: 3 of 11 files
carry a `## SUMMARY` (the three `*_LOG.md`s that were closed out in
prior sessions); this session's `SESSION_LOG.md` will gain its
`## SUMMARY` as the final act of this task doc.
Files created/modified:
- Created: `docs/tasks/INDEX.md` (named deliverable X1a).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: nothing — `docs/tasks/` has no
top-level `.md` files (all live in subdirectories), and no file lacked
a `#` heading.
---

## [X2] — Open-items list
Status: **PASS** — mechanical grep-and-compile; method pre-stated in
the output file itself; reasons quoted verbatim, never summarized.
Time started / finished: 2026-09-23 05:08:41 / 2026-09-23 05:08:41
What I did: Scanned every `*_LOG.md` file in the repo (excluding
`venv/` and `data/external/` — vendored content, disclosed in the file
header) for case-sensitive `BLOCKED` or `FAIL`; attributed each hit to
its nearest preceding Markdown heading as task ID; kept the FIRST hit
line per (task ID, file) as the quoted one-line reason with an `n_hits`
column so quoted diagnostics inside entries are counted rather than
dropped; wrote `docs/tasks/OPEN_ITEMS.md`.
Actual output (verbatim, PY_EXIT=0):
```
scanned 5 *_LOG.md files: ['docs/tasks/comparators-and-consolidation/SESSION_LOG.md', 'docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md', 'docs/tasks/results-log/MTHFR_RESULTS_LOG.md', 'docs/tasks/review-triage/OVERNIGHT_LOG.md', 'docs/tasks/site54-and-script50-migration/MIGRATION_LOG.md']
wrote docs/tasks/OPEN_ITEMS.md: 38 rows
| task ID | source file | one-line reason (quoted) | n_hits |
| ## [T1] — Tier 1: precomputed EVcouplings/EVmutation model for GB1 (P06654) | ...SESSION_LOG.md | `Status: BLOCKED — no precomputed model for P06654/its family found` | 3 |
| ## [T2] — Tier 2: coupling signal from a fetched MSA (T2a fetch, T2b compute, T2c size gate) | ...SESSION_LOG.md | `FAIL — the script's own pre-registered mapping-validation gate (M3) failed` | 2 |
| ## [T3] — Correlate the coupling signal with measured GB1 epsilon (n = 6) | ...SESSION_LOG.md | `Status: **BLOCKED (dependency failed — no execution attempted).**` | 4 |
| ## [U2] — ... | ...SESSION_LOG.md | `Status: **U2a/U2b machinery PASS at reduced-N smoke; the FULL-N result run is BLOCKED by the session's ~2h-per-task cap.**` | 6 |
| ## [U3] — ESM-1v, budget-gated (U3a) | ...SESSION_LOG.md | `Status: **BLOCKED — model size exceeds the 3 GB budget; ...` | 4 |
| ## [U4] — SaProt, budget-gated ... | ...SESSION_LOG.md | `Status: **BLOCKED on U4a's own preprocessing clause (AGENTS §10 — decisions needed), NOT on budget.**` | 4 |
| ## [L2a] — Disk search for an alternative double-mutant comparator ... | ...FOLLOWUP_LOG.md | `Status: **BLOCKED** — nothing suitable exists on disk; ...` | 3 |
| ## I1 — Pipeline validation on a known-epistatic dataset (GB1 four-site landscape) | ...OVERNIGHT_LOG.md | `Status: PASS as a test run (gates, identity check, null, CI all correct) — but the pre-registered GATE FAILED: ...` | 5 |
| ## R2 — Migrate script 50 to the N2 set (R2a–R2d) | ...MIGRATION_LOG.md | `Status: **FAIL** — script 50's own pre-registered gate failed at run time.` | 3 |
|  [38 rows total; full table in docs/tasks/OPEN_ITEMS.md]
---
38 rows across 5 log files (...)
```
Verdict: **X2 = PASS.** The list surfaces every genuinely open
BLOCKED/FAIL task this doc and its predecessors produced (T1/T2b/T3,
U2-full-run/U3/U4, L2a, R2, I1's gate, …) plus, mechanically, any
mention-bearing line — which is the correct behavior for a grep-based
task: interpretation is explicitly not its job.
Files created/modified:
- Created: `docs/tasks/OPEN_ITEMS.md` (named deliverable X2a).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: (a) row 1's task ID is the
SESSION_LOG's own template heading (`## [GROUP-TASK ID] …` with
`Status: PASS | FAIL | BLOCKED | …`) — the FORMAT LEGEND line, not an
actual open item; kept because the rule is mechanical and I am flagging
it here rather than hand-editing the output (AGENTS §7: the script/file
is the record). (b) `MTHFR_RESULTS_LOG.md` was scanned and produced
0 hits — it contains no `BLOCKED`/`FAIL` lines at all. (c) Several rows
come from other logs' `## SUMMARY` sections and from parenthetical
mentions inside PASS entries (e.g. V1's troubleshooting-tree note) —
expected under the stated rule; `n_hits` + the quoted line make each
row auditable.
---

## [X3] — Orphaned-output check
Status: **PASS** — report-only (task says do not delete; nothing was
deleted or moved).
Time started / finished: 2026-09-23 05:09:23 / 2026-09-23 05:09:23
What I did: Cross-referenced every CSV in `data/processed/` (100 files)
against the same 5 `*_LOG.md` files X2 used (identical scope rule,
exclusions disclosed there): a CSV is "mentioned" iff its exact
basename occurs anywhere in any log's text. Rule stated plainly because
it defines the answer: X3a says "every log file project-wide", so
`RESULTS.md`, `REVIEW_TRIAGE.md`, `AGENTS.md`, and task docs that are
not `*_LOG.md` were NOT searched — an "orphan" here means "unmentioned
in logs", not "unmentioned anywhere".
Actual output (verbatim, PY_EXIT=0):
```
log files searched (5): ['docs/tasks/comparators-and-consolidation/SESSION_LOG.md', 'docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md', 'docs/tasks/results-log/MTHFR_RESULTS_LOG.md', 'docs/tasks/review-triage/OVERNIGHT_LOG.md', 'docs/tasks/site54-and-script50-migration/MIGRATION_LOG.md']
CSVs checked in data/processed: 100
never mentioned in ANY log: 27
--- orphan list (verbatim basenames) ---
confirmation_run_results.csv
confirmation_split_assignment.csv
confirmation_split_balance.csv
derived_maps.csv
phase3_matched_arms.csv
phase3_primary_results.csv
phase5_stratified.csv
position_cluster_corrected_results.csv
primary_maps.csv
task1_signflip_results.csv
task1_synonymous_control.csv
task33_delta_esm_nulls.csv
task4_signflip_recovered.csv
task_accuracy_degradation.csv
task_delta_esm_noise_floor.csv
task_established_predictor_diff_raw.csv
task_established_predictor_strat.csv
task_exogenous_anchor_test.csv
task_matched_baseline_crosspredictor.csv
task_matched_baseline_gaps.csv
task_matched_confound_curve.csv
task_measurement_noise_control.csv
task_mechanical_baseline.csv
task_range_restriction_correction.csv
task_range_restriction_summary.csv
task_region2_magnitude.csv
tier2_permutation_inputs.csv
--- end list (no deletions performed; report only) ---
```
Verdict: **X3 = PASS** (list produced; nothing deleted). Reading the
list for the record (observation, not curation): 7 of the 27 belong to
the known stray scripts this session was forbidden to touch
(`task_delta_esm_noise_floor`, `task_measurement_noise_control`,
`task_established_predictor_*`, `task_matched_baseline_*`,
`task_exogenous_anchor_test`, `task_range_restriction_*`,
`task33_delta_esm_nulls`) — i.e. their work was executed but never
narrated in a `*_LOG.md`, which is exactly the "evidence a log entry is
incomplete" branch of X3a. The three `confirmation_*` CSVs belong to
the frozen confirmation run (AGENTS §10: executed exactly once — its
record lives outside these logs, presumably the results writeup).
`phase3_*`/`phase5_*`/`task1_*`/`task4_*` etc. are pipeline-stage
outputs whose narration predates or bypassed the log files searched.
Files created/modified:
- No new files (X3a names no deliverable file — the list IS the
  deliverable and lives in this entry).
- Modified: `SESSION_LOG.md` (this entry only).
Anything unexpected or worth flagging: 27/100 orphan rate is high
enough to state plainly: it is a documentation-scope artifact of the
`*_LOG.md`-only rule as much as genuine missing narration — anyone
using this list downstream must carry that caveat (stated above, in the
method). Notably `confirmation_run_results.csv` — the project's frozen
headline run — surfaces as an "orphan" purely because its narration
sits in `RESULTS.md` (not a `*_LOG.md`); that is the strongest single
example of why the scope rule must travel with the list.
---

## SUMMARY

**Tasks completed** (36 `## [ID]` entries, one per subtask, each backed
by an executed run — 29 PASS): S1, S2, S3, Y1, Y2, Y3, Y4, Y5, Y6, Y7,
Y8, Y9, T5, U1, U5, V1, V2, V3, V4, V5, V6, V7, W1, W2, W3, W4, X1,
X2, X3.
**Tasks failed:** T2 (T2a PASS — MSA fetched within the 200 MB cap;
T2b/T2c **FAIL** — the pre-registered M3 mapping gate rejected 1/4 WT
consensus at `EXIT=1`; not re-validated, no post-hoc change).
**Blocked:** T1 (no precomputed EVcouplings/EVmutation model for
P06654 found), T3 (dependency failed — no execution attempted), U2's
FULL-N run (machinery PASS; measured 0.587 s/seq ⇒ minimum 167 min >
2 h cap; overnight command printed in its entry), U3 (ESM-1v weights
7,828,635,339 B > 3 GB — stopped pre-download), U4 (size PASSED at
2,606,464,143 B but blocked on its own preprocessing clause — three
decisions await the user: chain A vs B, missing-coordinate policy for
59 atlas positions, foldseek acquisition).
**Not attempted:** T4 (entry condition unmet — T1–T3 produced nothing
usable).

**Headline verdicts, one line each:**
- **Group T:** the GB1-comparator route is dead tonight — couplings ×
  MTHFR e.b = **NOT OBTAINED** (only deliverable: `task_T5_comparator_summary.csv`).
- **Group U:** robustness verdict = **(d) still undetermined** — only
  ESM-2 650M produced e.b correlations; 150M ρ=+0.0978
  CI [−0.0444,+0.2275] p=0.154 (SIZE-SENSITIVE, not a refutation);
  summary table `task_U5_model_robustness_summary.csv` (6 rows).
- **V2/V3 (ThermoMPNN):** 10,141-variant ΔΔG table saved
  (`task_V2_thermompnn_ddg.csv`; 1,203 dropped = 1,046 at 59 unresolved
  positions + 157 at 9 construct-vs-canonical positions, exact);
  **ddG(A222V) = −0.0439**.
- **V4:** additive stability term vs own e.b: **ρ = −0.0733
  CI [−0.1021, −0.0437], p<0.0001, n=9,595** (pre-registered additive;
  rank-degenerate with ddG(v) alone — disclosed, not tuned).
- **V5:** ESM-2 −0.0881 CI [−0.1173, −0.0595] vs ThermoMPNN −0.0733
  CI [−0.1021, −0.0437] — ESM-2 nominally larger |ρ|, CIs overlap,
  **both exclude 0**.
- **V6:** region 4 is the discriminator — ThermoMPNN **−0.1237
  CI [−0.1751, −0.0716]** vs ESM-2 **+0.0103 CI [−0.0365, +0.0568]**
  (null); region 2 positive for both.
- **V7:** neither pole survives — epistasis IS weakly but significantly
  predictable from structure-derived stability (stability-mediated),
  but ESM-2 is **not** globally blind (pooled it does about as well);
  it fails specifically in region 4, where stability keeps the signal.
- **W1/W2:** decile design = 30 backgrounds spanning S ∈ [−18.007,
  +4.071] with A222V INSIDE the span (bimodal gap closed); rescoring
  34.2 min ≤ 90-min budget (t1 61.7 s, no reduction; +22% time drift
  disclosed).
- **W3/W4:** denser design **CHANGES M1d** — residual +0.0212
  CI [+0.0046, +0.0393] excludes 0 → **CONTRARY to H1a (A222V
  outlier-HIGH)**, versus the original NOT SUPPORTED (+0.0095
  CI [−0.0057, +0.0264]); **M1e STRENGTHENS** — Spearman −0.519
  CI [−0.635, −0.388] (was −0.467 CI [−0.583, −0.067]) — while the
  secondary Pearson weakens −0.601 → −0.423 (both exclude 0; the
  two-cluster leverage leaving the data), residual CIs of the two
  designs overlap [0.0047, 0.0264] (resolution, not reversal).
- **Group X:** `docs/tasks/INDEX.md` (11 files, 3 with `## SUMMARY`),
  `docs/tasks/OPEN_ITEMS.md` (38 rows, 5 logs), 27/100 processed CSVs
  unmentioned in any `*_LOG.md` (scope caveat travels with that list —
  see [X3]).

**Single most important thing to look at first:** the **[V7] entry in
this log** — the plain verdict on whether ThermoMPNN's stability signal
moves the project's core claim ("stability predicts e.b about as well
as ESM-2 pooled; ESM-2 loses it only in region 4" — both obvious
misreadings, "stability refutes ESM-2" and "stability fails too", are
contradicted by the printed numbers). Runner-up: **[W4]** — M1d's
verdict flip is real but is a DESIGN resolution of an already-positive
point estimate, not a sign reversal, and the Pearson drop must not be
reported as "everything strengthened". Two decisions still await your
call, both logged and NOT taken: U4's three preprocessing choices, and
the U2 full-N overnight run (`PHASE2_MAX=0 BRUTE_N=16 N_BOOT=10000
N_PERM=10000 venv/bin/python3 scripts/67_u2_pll_delta.py`).

**Housekeeping:** this session issued NO commits — all of its outputs
remain uncommitted (`git status`: `AGENTS.md` modified + the untracked
paths inventoried below). POST-HOC CORRECTION, flagged per AGENTS §6:
this line was first written "nothing committed (`git log -1` still
`c9ce0c5`)" — that snapshot predated the repo author's own commit;
verified now with `git show --stat` + reflog that HEAD is `f6c2686`
("Add comparators, stability mediation, digest, and consolidation task
doc", authored Sep 22 23:06 — two minutes before S1's 23:08 start),
which contains ONLY `COMPARATORS_AND_CONSOLIDATION.md` (1 file, 328
insertions); none of this session's work is in it. `RESULTS.md`,
`MTHFR_RESULTS_LOG.md`, `REVIEW_TRIAGE.md` untouched;
`AGENTS.md` changed only by S3's single authorized §2 bullet;
`ADDENDUM_I1_CAVEAT.md` received no appends (append-only rule intact);
prior-session stray scripts (32–40) untouched; every budget honored
(T ≈195.1/200 MB, U 3-GB gates, V clone 125 MB, W2 34.2/90 min; no
task exceeded its ~2 h cap — blocked ones stopped at the cap or gate).
New files this session (inventory verified by an mtime-window `find`
over `data/processed scripts docs data/external` since Sep 22 23:00 —
S1 started 23:08): `SESSION_LOG.md`, `GROUPS_C_TO_H_DIGEST.md`,
`INDEX.md`, `OPEN_ITEMS.md`; scripts `66` (T2b, pre-registered, FAILed
its own gate), `67` (U2, full run pending), `68` (V), `69` (W), plus
the sanctioned in-place edit of `scripts/50_d1_stratifier_quality.py`
(S2); results `task_T5_comparator_summary.csv`,
`task_U5_model_robustness_summary.csv`,
`task_V2_thermompnn_ddg.csv`, `task67_u2_pll_scores_smoke.csv`,
`task67_u2_results_smoke.csv` (both smoke-suffixed, not results),
`task69_w1_selection.csv`, `task69_w2_bg_raw.csv`,
`task69_w3_backgrounds.csv`, `task69_w3_bootstrap.csv`, and S2's
regenerated 5 × `task50_*.csv` (pre-migration copies intact in the
untouched `*_PRE_MIGRATION.csv` backups); fetched into
`data/external/`: T2a's 8-file set (`P06654_SPG1_STRSG.fasta`,
`PF01378_seed_alignment.sto`, `Pfam-A.seed.gz` 194.4 MB, jackhmmer
outputs — md5/provenance in [T2]) and `ThermoMPNN/` (sparse clone,
125 MB, gitignored); venv packages (wandb, pytorch-lightning,
omegaconf); `AGENTS.md` S3 correction (the only authorized edit).
---

