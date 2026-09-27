# DISATTENUATION_LOG — session 2026-09-25 (start: see first entry)

Session scope (per DISATTENUATION_AND_LEDGER.md and the launch prompt):
fourth-round external review response. Group S (master ledger) first,
then Groups T/V (disattenuation validity + clustering question), then
U/W/X/Y/Z. Two things are pre-confirmed in the task doc's header and
will NOT be re-run: the ensemble-mean run (RELIABILITY_LOG [A1],
rho = -0.028508 vs Spearman-Brown ≈ -0.030) and the Nambiar full-paper
text search (zero severity-only baseline mentions). Nothing in prior
summaries — including this task doc's own framing of what numbers
mean — is trusted until S1's ledger verifies it against source files;
where code and any characterization disagree, the code wins and the
discrepancy gets flagged, never silently smoothed.

Logging format (same as every prior session):

## [TASK ID] — [one-line title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
---

FIRST ACTION: this file created before any task work, per the launch
prompt's instruction.

Do-not-touch list for this session: RESULTS.md, MTHFR_RESULTS_LOG.md,
MTHFR_RESULTS_LOG_PART2.md, REVIEW_TRIAGE.md, AGENTS.md. Z4's email
is drafted and saved, never sent. Prior logs/task docs are read-only —
contradictions found in them get flagged in THIS log, not edited away.

---

## [S1] — Master correlation ledger (S1a), sign/target contradiction resolved (S1b), "v3" not present in workspace (S1c BLOCKED)
Status: PARTIAL — S1a PASS, S1b PASS, S1c BLOCKED (referenced file does not exist; replacement sentences supplied below)
Time started / finished: 2026-09-25 23:32 / 2026-09-25 23:50
What I did:
- Read AGENTS.md (binding) and DISATTENUATION_AND_LEDGER.md (332 lines) in full before any task work; created this log as the session's first action (preamble above, committed in `7df1941`).
- **Checked VERIFIED_FINDINGS_TABLE.md first** (per launch prompt): it is a 104-row index of headline/near-headline numbers from the eight session logs' SUMMARY sections, each with source file+line. I used it as the *inventory* for where correlation quotes live, and then re-read the load-bearing rows fresh from their source CSVs/logs this session rather than trusting it. Every row of the table below marked with a source was read from that source on 2026-09-25 between 23:32 and 23:47; nothing was copied from a prior summary.
- **S1a scope decision (pre-stated, rule 4).** The instruction says "every correlation quoted anywhere in v3 or the underlying logs." `v3` does not exist in this workspace (search evidence in the S1c entry below), so that portion cannot be scoped. The most literal conservative reading I can implement is: every correlation quoted in (a) the in-repo write-up layer — `RESULTS.md` and the original results log `MTHFR_RESULTS_LOG.md` (on disk: Parts 1–8; see flag below) — and (b) every session log's `## SUMMARY` section, plus (c) every number the task doc / launch prompt reference directly (anchor family, severity table, seeds, ensemble, disattenuation, reliability band, positive controls, Nambiar). Tier-1 rows (a–c load-bearing numbers) were re-read at their deepest on-disk source (CSV or producing log entry); Tier-2 rows (write-up tables whose producing script output exists only in the write-up itself) are cited to the write-up line, freshly read, with the producing script NOT re-read this session — that limitation is stated per-block, not hidden.
- Fresh reads performed: `data/processed/task32_delta_esm_primary.csv` (entire file), `data/processed/task_AB2_proteingym_model_comparison.csv` (97 lines; REF + severity rows via grep with line numbers), `scripts/71_proteingym_model_comparison.py` (computation code), `scripts/12_validate_a222v_scores.py` / `scripts/45_c1_reconciliation.py` (delta_esm definition), `RESULTS.md` (entire file), `MTHFR_RESULTS_LOG.md` (entire file, 362 lines), `GROUPS_C_TO_H_DIGEST.md` (entire file), SUMMARY blocks of OVERNIGHT / SESSION / CLOSEOUT / DEEPDIVE / RELIABILITY / FOLLOWUP / MIGRATION logs (CALIBRATION_LOG confirmed to have no `## SUMMARY`, consistent with VFT's header note), plus targeted entry reads (OV C1d, OV G1, OV C3a, CLOSE AC4d, REL A1/A2/A4c, CAL N3/N4, FOLLOW M1e/M1d, SESS W3, MIG Q1).

### S1a — the ledger

Columns: statistic (predictor) | target | type/sign | n (positions) | ρ | 95% CI | null mean | source. "—" = no such quantity exists for that row (bootstrap-only rows have no null; agreement rows are not against e.b).

**Block A — headline anchor family** (type: `delta_esm = esm2_score_a222v_bg − esm2_score`, script 12 L29 / script 45 L97 — a background-induced SHIFT, not a raw score)

| # | statistic | target | type/sign | n (pos) | ρ | 95% CI | null mean | source (read fresh) |
|---|---|---|---|---|---|---|---|---|
| A1 | delta_esm | own_e_b | shift / signed | 10,757 (654) | **−0.08811806424891734** | [−0.1173334458953319, −0.05951138449511738], p=0.0 | sign-flip +0.0001 (p<0.0001); position-block −0.0001, sd 0.0156, p<0.0001 | task32 CSV L6; AB2 CSV L2 |
| A2 | delta_esm | published GI_folinate_independent (e.b) | shift / signed | 10,757 (654) | **−0.07070516222228716** | [−0.09797203801943542, −0.0438395299914251], p=0.0 | — | task32 CSV L5; AB2 CSV L2 |
| A3 | \|delta_esm\| | own_e_b | shift magnitude / absolute | 10,757 (654) | −0.1049343224172812 | [−0.13465025496724659, −0.07406720520550297], p=0.0 | sign-flip −0.0852 (81% structural artifact) | task32 CSV L8 |
| A4 | \|delta_esm\| | published e.b | shift magnitude / absolute | 10,757 (654) | −0.12190038144795548 | [−0.15257296663364048, −0.09049256160942505], p=0.0 | — | task32 CSV L7 |
| A5 | delta_esm | published e.r | shift / signed | 10,757 | −0.03491612890928576 | [−0.05912259666732518, −0.010439736722995039], p=0.0034 | — | task32 CSV L9 (= results-log 5.4's "−0.035") |
| A6 | own_e_b vs published e.b (agreement) | — | target agreement / signed | 10,757 | Spearman +0.975227810760996; Pearson +0.9808443000750426 | — | — | OV L19 |

**Block B — the severity-baseline table** (type: each model's RAW score column as shipped by ProteinGym — WT-background severity/likelihood, i.e. NOT a shift — signed, × target, position-cluster bootstrap N_BOOT=10,000 per script 71 R3; full CSV = 97 lines / 96 model rows; own target | published target, both from the same row)

| # | model (RAW score) | ρ own_e_b [CI] | ρ published [CI] | source |
|---|---|---|---|---|
| B0 | REF_delta_ESM_our_run (the SHIFT, for contrast) | −0.08811806424891734 [−0.11733344589533189, −0.059511384495117385] p=0.0 | −0.07070516222228716 [−0.0979720380194354, −0.043839529991425104] p=0.0 | AB2 L2 |
| B1 | Site_Independent | +0.06396596794067251 [0.03764640775006493, 0.09056413801620629] p=0.0 | +0.051578586271735324 [0.026641979057754565, 0.07673641037569628] p=0.0004 | AB2 L32 |
| B2 | ESM1v_single | +0.06780795371221343 [0.040927862239273215, 0.09556753765567869] p=0.0 | +0.06131258548847305 [0.036125562878152724, 0.0875973527181565] p=0.0 | AB2 L36 |
| B3 | MSA_Transformer_ensemble | +0.06790133074772664 [0.04288882895852691, 0.09426020076219431] p=0.0 | +0.06413103906196783 [0.03982574930950078, 0.08911477665080889] p=0.0 | AB2 L37 |
| B4 | EVE_ensemble | +0.07460181101612699 [0.04691056859163026, 0.10254176270213508] p=0.0 | +0.06173380540744817 [0.03541892045356264, 0.08824604038570999] p=0.0 | AB2 L44 |
| B5 | GEMME | +0.07576993585430188 [0.04914447998277228, 0.10286173104404038] p=0.0 | +0.06479774614244217 [0.03978397199672187, 0.09045436186849622] p=0.0 | AB2 L47 |
| B6 | DeepSequence_ensemble | +0.07613611980841997 [0.048422632323506715, 0.10398456991029553] p=0.0 | +0.06278475856424923 [0.03637327072988732, 0.08929219235209895] p=0.0 | AB2 L49 |
| B7 | EVmutation | +0.0765388135872782 [0.050795716426816996, 0.10266187118174226] p=0.0 | +0.06245180123067018 [0.03766876451981932, 0.0875663102835194] p=0.0 | AB2 L52 |
| B8 | ESM1v_ensemble | +0.07687349800315775 [0.050368876851309294, 0.104075077314902] p=0.0 | +0.06816858731502308 [0.04261463673239216, 0.09411920305202258] p=0.0 | AB2 L54 |
| B9 | **ESM2_650M** | **+0.0853911031053886 [0.058861369894065874, 0.11229396305341609] p=0.0** | +0.069895293733652 [0.04452527472090113, 0.09568061701980234] p=0.0 | AB2 L67 |
| B10 | ESM2_150M | +0.16223117588303074 [0.13751059376527455, 0.1864730155632388] p=0.0 | +0.1284562479851809 [0.10471893839293045, 0.152125220515805] p=0.0 | AB2 L97 |

(All B rows: n=10,757 / 654 positions; the other 86 model rows exist in the CSV and were not transcribed here — this table carries the seven the write-up quotes plus the two ESM-2 sizes and the two ESM-1v variants.)

**Block C — ESM-1v five seeds, and cross-member agreement** (CLOSE L2174–2190, L2224–2235; CAL L437–445; REL L596–617)

| # | statistic | target | type/sign | n | ρ | 95% CI | notes | source |
|---|---|---|---|---|---|---|---|---|
| C1 | delta, member 1 | own_e_b | shift / signed | 10,757 | −0.020573 | [−0.048467, +0.006286], p=0.1400 | | CLOSE L2174 |
| C2 | delta, member 2 | own_e_b | shift / signed | 10,757 | −0.040820 | [−0.069623, −0.011940], p=0.0046 | only CI excluding 0 (1/5) | CLOSE L2176 |
| C3 | delta, member 3 | own_e_b | shift / signed | 10,757 | +0.013434 | [−0.014563, +0.041385], p=0.3444 | | CLOSE L2178 |
| C4 | delta, member 4 | own_e_b | shift / signed | 10,757 | −0.026572 | [−0.053779, +0.000264], p=0.0524 | | CLOSE L2180 |
| C5 | delta, member 5 | own_e_b | shift / signed | 10,757 | −0.003409 | [−0.031214, +0.024562], p=0.8194 | | CLOSE L2182 |
| C6 | five-seed mean | — | shift / signed | — | −0.015588, sd(ddof=1)=0.021052 | z = −3.45 (ddof=1) / −3.85 (ddof=0) | 1 pos / 4 neg; all \|ρ\| ≤ 0.041 | CLOSE L2187 (R7c); REL A2c |
| C7 | cross-member agreement on DELTA vectors (10 pairs) | — | agreement / signed | — | min 0.003314 / median **0.084365** / max 0.162631 | — | this is the "reliability" r_delta used for disattenuation | CLOSE L2226 |
| C8 | cross-member agreement on WT scores (10 pairs) | — | agreement / signed | — | min 0.859689 / median **0.882637** / max 0.890106 | — | T5's base-score reliability | CLOSE L2225 |
| C9 | CALIBRATED members (calibration_b f1 = 1.23) | own_e_b | shift / signed | 10,757 | +0.049720 / +0.020070 / +0.056799 / +0.039788 / +0.027469; mean +0.038769, sd 0.014045 | — | verdict was IMPROVED (per N4c); **later flagged MECHANICAL by REL A4c** — contradiction kept, not smoothed | CAL L465 (fresh) |
| C10 | cal-vs-raw agreement decomposition | — | agreement / signed | 10 pairs | delta_cal median 0.655966; severity Δφ median 0.664665; **SHIFT-exact component median 0.089806** | — | first-order bar 0.089675, threshold bar 0.168730 → "need cal ≥ 2× raw = 0.168730": **NOT MET → MECHANICAL** | REL L596–617 (fresh) |

**Block D — ensemble-mean and disattenuation** (REL L308–434, fresh)

| # | quantity | value | CI / p | null / notes | source |
|---|---|---|---|---|---|
| D1 | five-member ensemble delta × own_e_b | **−0.028508** | [−0.056495, −0.000239], p_boot=0.0484 (N_BOOT=10,000, seed 0) | sign-flip null mean +0.0002, sd 0.0142, p=0.0442; identity max\|diff\|=1.110e−16; \|observed\|=0.028508 vs mean \|single-member ρ\|=0.020962 | REL L318–330 |
| D2 | Spearman-Brown prediction from C6 + C7 | −0.0301 (= −0.015588096 × sqrt(5/(1+4×0.084365))) | — | agreed with D1 to 3 d.p. (−0.030 vs −0.028508) | REL L310 |
| D3 | ceiling = sqrt(r_delta) | +0.290457 | — | largest \|ρ\| the delta-based headline could reach | REL L403 |
| D4 | disattenuation, delta-only | **−0.303378** | — | δ = −0.028508 / 0.09185054 | REL L398–405 |
| D5 | disattenuation, fully | **−0.380323** | — | δ = −0.028508 / sqrt(0.09185054 × 0.6363); proxy-assumption banner required; A2 registry entries 3/4, 7/9 | REL L405–415 |
| D6 | seed z-score | −3.45 SD (ddof=1) / −3.85 (ddof=0) | — | (−0.015588 − 0) / 0.021052 | REL A2c |
| D7 | own-e.b-only disattenuation (comparators C3a) | **−0.110413** | [−0.147534, −0.072340], ratio 1.2530 | verdict "MATERIALLY LARGER" (review's reading at ratio ≥1.15); REL's own-a2 recompute −0.110467 (r_obs/sqrt(0.6363)) — agrees to 4 d.p. | DIGEST C3a (fresh); OV L627–628; REL L420 |

**Block E — target-vector reliabilities** (OV L594–595, fresh): own e.b reliability = 1 − var(syn 0.02111, n=570)/var(analysis 0.05804) = **0.6363**; published e.b = 1 − var(syn 0.02483)/var(analysis 0.06522) = **0.6193**. (synonymous-variant own e.b: n=570, mean +0.0217, sd 0.1453.)

**Block F — G1 global-control residual** (OV L1184–1198, fresh): cross-fit isotonic R² = 0.1535, cluster CI [0.1317, 0.1749] (pre-registered bands → LIMITED-GLOBAL); Spearman(delta_ESM, e.b − isotonic(w.fitness)) = **−0.1455**, CI [−0.1761, −0.1131], p_boot<0.0005, n=10,757/654, N_BOOT=2,000; re-derivation identity |−0.1455 − (−0.0707)| = 6.94e−17; sign-flip null mean +0.0001, sd 0.0186, p<0.0001; raw-vs-residual magnitude difference +0.0748 [+0.0585, +0.0912]; sd(resid)=0.2349 vs sd(e.b)=0.2554.

**Block G — e.b × model-error sign-flip rows** (RESULTS.md L24–25 and MTHFR_RESULTS_LOG §2.1 L59–60, both freshly read; producing script-21 output NOT re-read this session — Tier 2): rank error +0.1199 / null +0.0977 / excess +0.0222 / 81% artifact / p 0.0003; calibrated error −0.1297 / null −0.1015 / excess −0.0282 / 78% artifact / p<0.0001. Both signed, n=10,757.

**Block H — delta's own nulls** (LOG §5.3 L178–180 fresh; position-block rerun = DIGEST B2, OV): signed obs −0.0881 / null +0.0001 / excess −0.0882 / ~0% structural artifact; absolute obs −0.1049 / null −0.0852 / excess −0.0198 / **81% structural artifact** (the null does NOT center on zero for the absolute arm); position-block rerun: null mean −0.0001, sd 0.0156, p<0.0001, frac_artifact 0.0005687, identity max|diff| = 2.220e−16.

**Block I — positive controls (gate gates)**

| # | statistic | obs | null mean (sd) | p | n | source (fresh) |
|---|---|---|---|---|---|---|
| I1 | GB1 3-site vs fitness | +0.4467, CI [+0.2787, +0.5793] | +0.3880 | 0.1398 | 694 / 5 | OV SUMMARY (fresh) |
| I2 | GB1 4-site vs fitness | +0.401757, CI [+0.258070, +0.521658] | +0.247570 (sd 0.1135) | 0.0009999 (≥1/1000) | 760 / 76 | MIG L699–707 |
| I3 | AAV1 depth gate | +0.1222, CI [+0.0391, +0.2094] | −0.0004 (sd 0.1408) | 0.3849 | 57 | DEEP SUMMARY |
| I4 | GRB2 F8 gate (AA7) | +0.1153, CI [+0.0444, +0.1843] | −0.0003 (sd 0.0371) | 0.0019 | 403 / 25 | DEEP SUMMARY |

**Block J — Nambiar context** (external paper numbers: CALIBRATION task doc L4–9, freshly read): their raw uncalibrated ESM-2 Pearson r ≈ 0.09–0.18; calibration raises to r ≈ 0.26–0.38 (external source, not re-derived here). Our held-out replication (CAL L338–344, fresh): raw ρ −0.0902 [−0.1229, −0.0575] p<0.0001, calibrated +0.0339 [+0.0044, +0.0634], sign-flip null mean +0.0069 sd 0.0105 p_null 0.0033, n=8,494 — M1 NOT MET, M2 NOT MET, M5 HOLD (raw α=1.000, calibrated α=0.397).

**Block K — other headline per-log correlations** (marked ✅ = re-read from its producing log entry this session; unmarked = VERIFIED_FINDINGS_TABLE row cited, not yet re-read in this session — do not quote until its group runs)

| # | statistic | target | type/sign | n | ρ [CI] | notes | source |
|---|---|---|---|---|---|---|---|
| K1 ✅ | ThermoMPNN additive-null model | own_e_b | signed | 9,595 | −0.0733 [−0.1021, −0.0437], p<0.0001 | cross-model comparator | SESS SUMMARY (fresh) |
| K2 ✅ | task32 per-region delta_esm | own_e_b | signed | 2,577 / 2,421 / 2,713 / 3,046 | r1 −0.15634825083466392 [−0.2047, −0.1075]; r2 +0.022240476124091704 [−0.0357, +0.0779]; r3 −0.05730595183541588 [−0.1123, −0.0033]; r4 +0.010345002632234737 [−0.0365, +0.0568] | | task32 CSV L13–16 |
| K3 ✅ | \|delta_esm\| × distance-to-222 | — | signed | 11,344 | −0.298082610698246 [−0.34948848661394805, −0.24502845576769483], p=0.0 | locality | task32 CSV L10 |
| K4 ✅ | \|delta_esm\| × e.b, split at 25 residues | own_e_b | signed | 844 / 9,913 | within25 +0.06679331776408384 [−0.0298, +0.1490], p=0.1666; beyond −0.0753801803209613 [−0.1036, −0.0469], p=0.0 | within-25 CI **includes** 0 | task32 CSV L11–12 |
| K5 ✅ | 150M-vs-650M delta agreement | — | signed | 1,900 | +0.0978 [−0.0444, +0.2275], p=0.154 | | OV SUMMARY |
| K6 ✅ | extrinsic × intrinsic interactions | — | signed | 10,757/654 | −0.0057 [−0.0345, +0.0209], p=0.6048; fitness-partial −0.0964 [−0.1197, −0.0716] | | OV SUMMARY |
| K7 ✅ | within-region pooled ρ | — | signed | 6,141 / 647 | +0.1897 [+0.1597, +0.2188] | provenance caveat: producing script for task_region2_diagnostic.csv is MISSING (OV-recorded) | OV SUMMARY |
| K8 ✅ | H2b epistasis-model union | — | signed | 776 | union +0.0507 [−0.0432, +0.1348] p=0.3148; 10 Å-only +0.1191 [+0.0066, +0.2166] p=0.0378 | | OV SUMMARY |
| K9 ✅ | AE3 clade predictor | — | signed | 10,757/654 | +0.107780 [+0.024259, +0.191756], p=0.0120; Neff-adjusted +0.123565 [+0.039702, +0.206380], p=0.0038 | | DEEP SUMMARY |
| K10 ✅ | B3a size-matched null (clade) | — | null | 1,000 draws | observed +0.107780 vs null mean −0.073628 (sd 0.026905), one-sided p=0.0010; B3b paired excess +0.024461 [−0.046428, +0.093833], p_exceeds=0.2467 | MIXED verdict | REL SUMMARY (fresh) |
| K11 ✅ | B2 depth decomposition | — | signed | 586/62 | region4-cons coupling +0.2865 (CI excl 0) vs REST +0.0599 (CI incl 0), disjoint → differs; conservation partial −0.2373 → **−0.1763** [−0.3218, −0.0222], p=0.0244; in-range pooled +0.0125 [−0.0822, +0.1064], n=462 | continuous + slope NOT the shape (see Group X) | REL SUMMARY (fresh) |
| K12 ✅ | B4b distance control | — | signed | — | residual +0.0097 [−0.0221, +0.0410], p_boot=0.5382 vs original +0.0154 **[−0.0166, +0.0465]** *(CI corrected in place 2026-09-26, true-final-closeout G3c: the prior [+0.0039, +0.0271] exists in no source — DEEPDIVE L2327–2336, RELIABILITY L1036/L1069, script 96's docstring, and script 96's G2 fresh reproduction all say [−0.0166, +0.0465])* | confirmed-but-expected | REL SUMMARY (fresh) |
| K13 ✅ | B1 Mundlak two-way FE | own_e_b | signed | 10,757 | ddg β +0.005173 [−0.016067, +0.008811], p=0.5675; delta_esm β +0.010528 [−0.098844, +0.119936], p=0.8501 | between-position coefficients do NOT differ | REL SUMMARY (fresh); CIs also VFT row 90 |
| K14 ✅ | M1e severity → mean shift across backgrounds | — | signed | 9 backgrounds | −0.466667 [−0.583333, −0.066667]; Pearson −0.601211 [−0.711076, −0.283792] | | FOLLOW L565–575 (fresh) |
| K15 ✅ | W3 denser re-run (31 backgrounds) | — | signed | 31 backgrounds / 120 pos | M1e ρ **−0.519** [−0.635, −0.388]; M1d residual **+0.02121** [+0.00465, +0.03934] | CI excludes 0 from above | SESS L2746–2747 (fresh) |
| K16 ✅ | M1d A222V residual, 9-background design | — | signed | 9 backgrounds | +0.00954 [−0.00573, +0.02640] (contains 0), rank 6/9 | NOT SUPPORTED | FOLLOW L348, L575 (fresh) |
| K17 ✅ | detection floor | — | — | — | ρ_floor = 0.5400 (crit 0.4755 + 0.8416 × se 0.0767); sensitivity 0.5109–0.5711; power 35.3% at n=10,757/654; position-clustering power 79%→48% at n=100 | | FOLLOW SUMMARY; DEEP SUMMARY |
| K18 ✅ | AD5 partner-15 floor (design disagreement) | own_e_b | signed | 413 positions | estimate 0.4143 [0.2714, 0.5571]; shrunken 0.3538 (τ=0.139); bootstrap floor 0.8514; formula floor 0.844 [0.7417, 0.931], power ≈50% @ 10,757 | | SESS SUMMARY |
| K19 ✅ | Holm family (script 97) | — | — | — | 5/5 core survive at α_FWER 0.01; 8/8 at m=8; B2 family FWER-corrected p=0.0129 → NOT retained at m=8; AD5 SPEC A1/3 (relaxed wording 1/3) | | REL SUMMARY (fresh) |
| K20 ✅ | Nambiar 3-model band | own_e_b | signed | 8,494 | seeds +0.0422 → +0.0557; X3a +0.0601 → +0.0776; 2/2 inside "tiny-to-small" band | | CAL SUMMARY region (fresh) |
| K21 | AD6 **rho(yE, Neff)** *(label corrected in place 2026-09-26, G3c: was "AD6 depth × interaction_D pooled" — wrong statistic; yE = position-mean \|delta_ESM\|, DEEP L2701/L2731/L2743)* | — | signed | 586/62 *(the "/62" is uncorroborated — flagged at [X], left in place)* | +0.1714 [+0.0918, +0.2471] | **fresh-verified** — CI [+0.091832, +0.247059] matches the logged CI to 4 dp (closing the old "not re-read this session"); AD6's actual depth × interaction_D statistic is yT3 = mean\|interaction_D\|: rho **−0.0211 [−0.1034, +0.0584]**, null — do NOT quote K21's number as "interaction tracks depth" | (VFT row 65; DEEP L2701/L2731/L2743) |

**Block L — write-up-layer tables** (source = the write-up line itself, freshly read this session; producing scripts NOT re-read — Tier 2, disclosed)

`MTHFR_RESULTS_LOG.md` (on disk = Parts 1–8; see the flag below):
- L27 §1.1: tercile ESM-2 correlations **0.53 / 0.35 / 0.17** — explicitly marked "SUPERSEDED, do not cite as-is" (stratifier mostly artifact + Model B/C comparison rank-degenerate).
- L59–60 §2.1: the Block-G rows (same numbers as RESULTS L24–25).
- L88 §3.1: after controlling region, ρ range −0.1937 … +0.1063 (as quoted; script-26 source not re-read).
- L132 §4.3: region-2 diagnostic ρ +0.090 → **+0.191** under full MSA (as quoted; the producing script for task_region2_diagnostic.csv is MISSING per OV F2a — provenance caveat already logged there).
- L173 §5.2: **"signed delta_ESM vs signed e.b: ρ = −0.088 (published e.b) and −0.088 (own e.b)"** — the published-side label is WRONG: actual published = −0.07070516222228716 (task32 L5). Already flagged as contradiction #1 by OV's §5.2 correction (OV L1878–1881, fresh) and in VFT row 1; not edited here (user-owned file).
- L174–176 §5.2: |Δ_ESM| vs |e.b| ρ = −0.105 to −0.122 (✓ matches task32 L7–L8); Δ_ESM vs e.r ρ = −0.035 (✓ matches task32 L9).
- L178–180 §5.3: the Block-H null rows; L183 §5.4: −0.298, near-222 +0.067 (n=844, p 0.17), beyond −0.075 (n=9,913, p<0.001) (✓ matches task32 L10–L12).
- L246 §6: additive-null MAE results (not correlations — see S2b-iii); L272 §7.2: rank-vs-MAE disagreement ρ +0.278 (E[MD] vs relative severity); L278 §7.3: concordance +0.515 / +0.393 / +0.257 (Δ purity vs e.b sign / |e.b| / shrunken e.b); L294 §8: r(v,A) exceeds r(v,WT) in 27/28 condition arm–region pairs (sign test, not a correlation).

`RESULTS.md` (fresh full read; do-not-touch):
- L9/L12 (X3 section): −0.088118 own / −0.070705 published, n=10,757/654; −0.1455 residual; Thermo −0.0733; seeds −0.0156 (3.45 SD); SaProt −0.0502 [−0.1179, +0.0200] (smoke n=74 — not in Blocks A–C because different n).
- L19–25: Block G rows.
- L50–53: multivariable coefficients (regression coefficients, NOT correlations — excluded from this table by scope).
- L60–63: matched arms (8-way mean ESM-2 fitness prediction): A +0.3766 [0.3480, 0.4047]; B +0.3367 [0.3077, 0.3660]; C +0.3597 [0.3315, 0.3874]; D +0.3278 [0.2995, 0.3555], n=11,901.
- L65: within/beyond CI-exclusion claim for the C2a comparators proximity test — **flagged**: its direction (within excludes 0, beyond includes 0) is the OPPOSITE of task32's locality split (K4: within-25 CI includes 0, beyond excludes 0). These are different analyses; C2a's own numbers were not re-read this session — do not conflate the two.
- L71–73: phase-5 strata, model C: +0.5283 [+0.5064, +0.5507] / +0.3486 [+0.3223, +0.3753] / +0.1713 [+0.1446, +0.1972]; model B same strata: +0.4973 / +0.3428 / +0.1677 (low/mid/high by |e.b|).
- L83–92: per-region ESM-2 vs fitness table (10 observed/null rows — includes region-2's ρ=+0.0901 / +0.1911, F2a's CONFIRMED-WITHIN-REGION pair).
- L106–110: range restriction (10–90th, kept 9,120/10,757): absolute delta −0.094 → −0.037; signed −0.087 → −0.037; Thermo −0.075 → −0.057 (all inside original CIs).
- L116–122: exogenous-anchor excess (S_A222V − S_BLOSUM62): low stratum +0.1969 [0.1763, 0.2190] vs +0.0187 [−0.0017, +0.0404], Δ −0.1782; high stratum +0.1817 [0.1556, 0.2076] vs +0.0081 [−0.0214, +0.0368], Δ −0.1736; follow-up gaps (n=10,757): signed Δ −0.168 [−0.195, −0.139]; mean-within-arm Δ −0.170 [−0.204, −0.132]; ThermoMPNN-specific Δ −0.249 [−0.332, −0.177].
- L143: mechanical baseline ρ = 0.658 / R² = 43.3% (null mean 0.7559, sd 0.0033); region-2 strict-minus-other null −0.0005 (sd 0.0201), p 0.47; Δ vs E1b +0.000533 [+0.000288, +0.000768].
- L150: "rho ≈ 0.975 / 0.983" for own↔published e_b / e_r agreement — **0.983 has NO located source** (OV L19 has Spearman 0.975227810760996 / Pearson 0.9808443000750426 for e_b; no e_r agreement figure found anywhere in `docs/` or `scripts/` by grep). Flagged: do not quote 0.983 until sourced.
- L161–164: confirmation-split permutation results (+0.001663 p 0.0006; +0.002882 p<0.0003; +0.001971 p 0.00109) — permutation differences, not correlations (out of scope for this table; noted for completeness).

### S1b — the apparent sign/target contradiction, resolved

**Direct answer: the task doc's characterization is CONFIRMED. They are two different statistics sharing one target vector — not a contradiction.**

Evidence, all read fresh today:
1. **The computation code.** `scripts/71_proteingym_model_comparison.py` is the severity-baseline's producer. Its pre-registered statistic block states: *"Statistic = Spearman rho with position-cluster bootstrap (cluster_col = position, stratified, N_BOOT = 10000 from env, seed 0). SIGNED ONLY: the task says 'correlate each model's scores against measured e.b'…"* Its `model_cols` are the **95 score columns shipped by ProteinGym** (`data/external/ProteinGym/MTHR_HUMAN_Weile_2021_scores.csv`, raw per-model scores), correlated as `obs[j] = _spearman(A[mi], A[ti])` against `TARGETS` = `own_e_b` and `GI_folinate_independent`. I.e. **each model's RAW score** (WT-background severity/likelihood as shipped) vs e.b.
2. **The one shift row in that same table** is `REF_delta_ESM_our_run` — script 71 reads `delta_esm` from script 32's analysis table as this project's own reference row.
3. **The statistic's definition**: script 12 L29 and script 45 L97 both define `delta_esm = esm2_score_a222v_bg − esm2_score` — a background-induced **SHIFT** between two scores of the same model, not a score.
4. **Same model, same target, same n, opposite signs** — the single crispest proof: ESM2_650M's RAW score × own_e_b = **+0.0853911031053886** (AB2 CSV L67) vs ESM-2's SHIFT × own_e_b = **−0.08811806424891734** (AB2 CSV L2). The sign difference is entirely the statistic.

So: the severity-baseline table (Site_Independent, GEMME, ESM2_650M, … all positive) correlates **raw WT-background scores** against e.b; the headline −0.088 correlates the **delta/shift** against the same e.b vector. Conventions pinned for the rest of this session: "ρ = −0.088 vs e.b" is always `delta_esm, signed, × own_e_b, n=10,757/654`; the table's positive values are always `raw score, signed, × target`; their signs are never compared without naming the statistic.

**Discrepancies found while building the ledger** (flagged, never edited — per AGENTS §5 and rule 6):
1. `MTHFR_RESULTS_LOG.md` §5.2 L173: *"signed delta_ESM vs signed e.b: ρ = −0.088 (published e.b) and −0.088 (own e.b)"* — the published-side label is **wrong**: published = −0.07070516222228716 (task32 CSV L5). Pre-existing, already flagged by OV's §5.2 correction and VFT row 1; file is on the do-not-touch list — flagged again here, not edited.
2. `RESULTS.md` L150 quotes *"rho ≈ 0.975 / 0.983"* for own↔published e_b / e_r agreement — **0.983 has no located source** (grep across `docs/` + `scripts/`: only OV L19's e_b figures, Spearman 0.975227810760996 / Pearson 0.9808443000750426). Do not quote 0.983 until sourced.
3. `RESULTS.md` L65 claims a within/beyond CI-exclusion pattern **opposite** to task32's locality split (K4: within-25 CI includes 0, p=0.1666; beyond excludes 0). Different analyses (C2a comparators proximity test vs task32's |delta|-vs-e.b split); C2a's own numbers were not re-read this session — flagged so the two are never conflated.
4. OV's SUMMARY renders C1d as *"S(v|A222V) vs S(v|WT) not 0.99+"* while the entry (L455–465, fresh) says *"PASS — 0.999636 ≥ 0.99, exactly the threshold the task specified"* with ρ = 0.999636 (n=10,757), agreeing with RESULTS L132's 0.9996. The number is consistent everywhere; only the SUMMARY's compressed phrasing is misleading — phrasing flagged, number stands.
5. S2a says *"the original results log's Parts 1 through 14"* — on disk `MTHFR_RESULTS_LOG.md` holds **Parts 1–8**, and `MTHFR_RESULTS_LOG_PART2.md` does not exist anywhere (S1c searches). Pre-flagged for [S2].

### S1c — BLOCKED: "v3" is not present in this workspace

What was searched (this session):
- `find . -iname "*v3*" -not -path "./venv/*" -not -path "./data/*" -not -path "./.git/*"` → **empty output, exit 0** (run fresh 23:50).
- `find . -name "*PART2*"` + `git log --all --name-only | grep PART2` → **empty**: `MTHFR_RESULTS_LOG_PART2.md` was never committed either.
- `\bv3\b` across all repo `*.md` (earlier this session, 23:24–23:31): only the task doc's own "v3" mentions and `esm1v_v33`-style model-name noise under `data/external`.
- Sentence search ("set out to answer", "analytical questions") across all `*.md`: **one** repo hit, read fresh at 23:51 — `docs/tasks/reliability-and-decompositions/FINAL_CLOSEOUT.md` L3–4: *"All open analytical questions this project set out to answer are resolved as of `RELIABILITY_LOG.md`'s SUMMARY."* — a near-verbatim match for the sentence S2c quotes, but FINAL_CLOSEOUT.md is a task doc created today, not a document called "v3"; identity unproven.
- Desktop-level search for pitch/write-up/draft files (earlier this session): nothing relevant.

Decision (troubleshooting rule 3 + rule 4): the referenced file cannot be located, so no substitution on a guess — especially since two of the likeliest candidates (`MTHFR_RESULTS_LOG_PART2.md`, `RESULTS.md`) are on the do-not-touch list, where editing is forbidden regardless of identity. **S1c BLOCKED**; replacement sentences supplied here for the user to apply wherever v3 actually lives:

> **Replacement for S1c's target sentences (statistic naming):**
> - "ESM-2's background-induced shift (delta_esm = score[A222V background] − score[WT background]), signed, vs own e_b: ρ = −0.088 (n = 10,757; 654 positions); vs published e.b: ρ = −0.0707."
> - "ProteinGym's severity-baseline table correlates each model's **raw WT-background score** (not a shift) against the same e.b vectors — all positive (Site_Independent +0.064 … GEMME +0.076 … ESM2_650M +0.085). Positive raw-score and negative shift for the same model is a statistic difference, not a sign contradiction."
> - Rule for every correlation sentence: name (1) predictor statistic, (2) target (own_e_b vs published), (3) signed vs absolute, (4) n. Never write "ρ = −0.088 vs e.b" bare.

Verdict: **S1a PASS** (ledger built; every Tier-1 row read fresh from its source CSV/log this session, Tier-2 rows cited to freshly read write-up lines with producing scripts disclosed as not re-read; VFT used as index only, not trusted blindly), **S1b PASS** (resolved against code + column names, with five discrepancies flagged), **S1c BLOCKED** (file absent — searches quoted above, replacement text supplied).
Files created/modified: `docs/tasks/disattenuation-and-ledger/DISATTENUATION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- `FINAL_CLOSEOUT.md` L3–4 is a near-verbatim match of the sentence S2c calls "the v3 sentence". I did **not** edit it — identity of v3 is unproven and rule 3 forbids substitution — but the user should know a same-shaped sentence exists in-repo, in a file that is NOT on the do-not-touch list.
- Commit `7df1941` (23:29:15) swept this log into git *while this session was working* — a parallel session is committing concurrently; HEAD may move during this run.
- The full 96-row AB2 CSV was not transcribed; only the 12 rows the write-up quotes (B0–B10) are in this ledger. Read the CSV directly if a later task needs another model's row.
---

## [S2] — Cross-history claims ledger (S2a), three dropped findings verified (S2b), v3 sentence BLOCKED (S2c)
Status: PARTIAL — S2a PASS (with one BLOCKED portion: Parts 9–14 of the original log are not on disk), S2b PASS, S2c BLOCKED (same missing "v3" as S1c; replacement sentence supplied)
Time started / finished: 2026-09-25 23:51 / 2026-09-25 24:02
What I did:
- S2a: rebuilt the claims ledger across the four rounds from source: full re-read of `MTHFR_RESULTS_LOG.md` (Parts 1–8, including its own 12-row status table at L318–334 and its "What's next" at L337–362), full read of `VERIFIED_FINDINGS_TABLE.md` (index only), fresh re-reads of this session's SUMMARY/entry reads from S1 plus `RESULTS.md` L124–134 (corrected conclusion). Status vocabulary used exactly as the task doc specifies: verified / superseded / weakened / never re-examined / contradicted.
- S2b: located and re-read the actual sources of the three dropped findings: (i) the H1a-reversal chain — task doc's paraphrase, FOLLOWUP M1d/M1e entries, SESSION W3 entry; (ii) `GROUPS_C_TO_H_DIGEST.md` Group C in full; (iii) `MTHFR_RESULTS_LOG.md` §6.2/6.3 plus its later re-verifications (OV D1b/C2c, corrected conclusion).
- S2c: same "v3" search evidence as S1c; replacement sentence drafted below.

### S2a — claims ledger across the full history

**Format:** claim (source) → status → current number + pointer. "Fresh" = re-read from source this session; "VFT-indexed" = status cross-referenced to VERIFIED_FINDINGS_TABLE's row (which itself was built from source in the prior closeout session) plus this session's SUMMARY re-reads.

**Original results log, Parts 1–8 (on disk):**

| # | Claim (source line) | Status | Current number + pointer |
|---|---|---|---|
| 1.1 | Tercile ESM-2 correlations 0.53 / 0.35 / 0.17 (L27) | **superseded** (log's own label: "SUPERSEDED, do not cite as-is") | Not re-derivable as a finding — stratifier mostly measurement artifact + Model B/C comparison rank-degenerate (AGENTS §8); later confirmed by the exogenous-anchor collapse: every excess CI crosses 0 (RESULTS L124, fresh) |
| 1.3 | folinate_response / e.r predict error → DROPPED (L41–46) | **superseded by its own re-test**: e.r is "almost entirely a mathematical artifact" per corrected conclusion; never resurrected in rounds 2–4 as far as the summaries read this session show | e.r artifact: sign-flip null (RESULTS L128–131, fresh); delta-vs-e.r itself is −0.03491612890928576 [−0.0591, −0.0104] (task32 L9, fresh) — a different claim than "e.r predicts error" |
| 2.1 | e.b predicts error, raw +0.1199/+0.1297 (L59–60) | **verified as stated** (weakly For, 78–81% artifact) | Block G rows, fresh: +0.1199 (null +0.0977, 81% artifact, p 0.0003); −0.1297 (null −0.1015, 78% artifact, p<0.0001) |
| 3.1 | e.b survives multivariable controls (L86–97) | **verified at write-up layer only** (Tier-2: coefficients not re-derived this session) | RESULTS L50–53 (fresh as quoted) |
| 3.2 | Non-uniformity: region 4 ≈ 0 (L131–132) | **verified** | task32 CSV L13–16 fresh: r1 −0.15634825083466392, r2 +0.022240476124091704, r3 −0.05730595183541588, r4 +0.010345002632234737 |
| 4.4/4.5 | ESM-2 beats matched placebo on rank (L157–163) | **weakened** (two later tests demote it): retention is not background-specific — gap(S_A222V) − gap(S_WT) = +0.0124 [−0.0375, +0.0370], p=0.9630 (DIGEST C1b, fresh); and no predictor's excess survives without `w.fitness` in the anchor (every CI crosses 0, RESULTS L124, fresh) | Surviving fragment: MAE-side comparisons (C2c MSE HOLD) and the descriptively real degradation pattern (see corrected conclusion) |
| 5.2/5.3 | Signed delta vs e.b real, ~0% artifact (L173–180) | **verified** — with the published-side label error re-flagged (S1b #1: published = −0.07070516222228716, not −0.088) | A1/A2 fresh: position-block null −0.0001, p<0.0001, frac_artifact 0.0005687; task32 L5/L6 |
| 5.4 | Proximity confound on delta (L183) | **verified (partial)** | task32 L10–12 fresh: −0.298082610698246 [−0.3495, −0.2450], n=11,344; within-25 +0.0668 (p=0.1666, n=844); beyond −0.0754 (p=0.0, n=9,913) |
| 6.2/6.3 | ESM-2 **worse** than additive null on MAE, esp. high stratum (L246–249) | **verified as a descriptive statistic; weakened as a claim specific to ESM-2** — see S2b-iii | Re-verified: D1b UNCHANGED-HOLD, arm3 +0.001851 [+0.000987, +0.002706] (OV SUMMARY fresh); C2c MSE HOLD (fresh); but corrected conclusion subordinates it (RESULTS L126–128, fresh) |
| 7.2 | Two-latent-trait gate cleared → MoCHI refit recommended (L268–284) | **never re-examined** — the refit was never run | grep: only "runs BEFORE any MoCHI refit" (OV L788, fresh) and planning mentions in REVIEW_TRIAGE; no MoCHI script exists in `scripts/` |
| 8.2 | SE-threshold epistatic set is badly calibrated (×3.76 SE error) (L296–298) | **verified (fail stands)**; its recommended fix was never applied, but the sensitivity test showed E1a thresholds robust to uniform ×3.76 SE inflation | DEEP SUMMARY L3191 (fresh); the epistatic-set flag was not used downstream (as far as the logs read this session show) |
| — | "What's next" #1: reconcile rank-vs-MAE | **done** — by the comparators digest (Group C) and the later tests; see S2b-ii | |
| — | "What's next" #2: fix SE calibration | partially addressed via the L4a sensitivity; core fix never applied | |
| Parts 9–14 | `MTHFR_RESULTS_LOG_PART2.md` | **BLOCKED** — file absent from workspace and git history (S1c searches, re-confirmed fresh 23:50: `find . -name "*PART2*"` empty, `git log --all` grep empty) | No substitute used |

**Deep-dive round (`DEEPDIVE_LOG`), headline claims** (all fresh this session via its SUMMARY + entries):
- **Detection floor ρ_floor = 0.5400, power 35.3% at n=10,757/654** — verified (K17); the anchor −0.088 sits far below it (the V1 question).
- **Resolution ladder (AE6): the fast-only design is wrong** — verified (150M-vs-650M agreement +0.0978, CI [−0.0444, +0.2275], p=0.154; G2's design prediction contradicted).
- **AA1/AA7 positive-control gates** — verified as gated: AA1's power gate FAILS (p=0.3849 at n=57), AA7 PASS (p=0.0019); both presences confirmed, both absences underpowered (19–54%).
- **Site-54 (Z2c): fails its own gate** — verified: Δ = −0.001107 [−0.0998, +0.0980]; genome-wide inference permanently OUT OF SCOPE.
- **AD5 "exceeds floor" claims downgraded** — verified: estimate 0.4143 [0.2714, 0.5571] below bootstrap floor 0.8514 (VFT row 66; SESS SUMMARY fresh).
- **AE3 clade +0.1078** — verified at that round, then **weakened by the reliability round's B3**: MIXED (exceeds size-matched nulls p=0.0010; NOT established vs placebos p=0.2467) — REL SUMMARY fresh.

**Calibration round (`CALIBRATION_LOG`, no `## SUMMARY` of its own — N1–N4 entries read fresh):**
- **N1 published implementation: FAIL** — verified: raw −0.1369 → calibrated −0.3413.
- **N2 custom negative control: FAIL** — verified: raw +0.1135 → calibrated +0.1332.
- **N3 held-out replication: raw −0.0902 → cal +0.0339** — verified (J-block).
- **N4 five seeds "IMPROVED": CONTRADICTED later** — REL A4c (fresh) showed the 0.656 cal agreement is the shared severity term (SHIFT-exact component median 0.089806 vs required 0.168730 → MECHANICAL verdict). This is the round-1 mechanical-inflation pattern; both verdicts stand side by side in their own logs (CAL L465 "IMPROVED", REL L610 "MECHANICAL") — contradiction flagged, neither log edited.
- **M-series: NOT publication-ready** — stands (fresh).

**Reliability round (`RELIABILITY_LOG`), headline claims** (fresh this session):
- **AC4d: the association does NOT survive seed change** — verified: five-seed mean −0.015588, sd 0.021052, 1/5 CIs exclude 0, all |ρ| ≤ 0.041 (CLOSE L2174–2190).
- **A1 ensemble −0.028508 ≈ Spearman-Brown −0.0301** — pre-confirmed in the task doc header; NOT re-run (per instruction).
- **A2 disattenuation −0.303378 / −0.380323** — verified with proxy-assumption banner required.
- **A4c calibration-agreement = MECHANICAL** — verified (contradicts N4 above).
- **B1 Mundlak: association survives within-position** — verified: ddg p=0.5675, delta_esm p=0.8501 (coefficients do not differ; position FE don't kill the delta association).
- **B2 depth: high-Neff threshold effect, not smooth** — verified: pooled +0.1714 vs in-range +0.0125; feeds Group X's shape requirement.
- **B3 clade: MIXED**; **B4 distance: confirmed-but-expected** (residual +0.0097, p=0.5382); **Holm 5/5 (m=8: 8/8)** — all verified fresh.
- **Z3g-h SaProt: BLOCKED** (population-definition decision reserved for the user) — open; smoke run ρ = −0.0502 [−0.1179, +0.0200] is not a verdict (RESULTS L9).

**Reconciliation in one paragraph:** the original log's net read ("a real, if modest, negative finding … with one unresolved rank-vs-MAE contradiction") has been overtaken twice: the comparators/corrected-conclusion round demoted the *rank* half (excess collapses without `w.fitness` in the anchor — near-tautological, RESULTS L124–128 fresh) while the *MAE* half survived its re-tests (D1b, C2c), and the reliability round then weakened the *headline itself* (seed-instability: −0.088 not reproducible across ESM-1v seeds, five-seed mean −0.015588). Nothing in the four rounds retracted the delta-vs-e.b association's *existence*; what changed is (a) how much of it is artifact-free, (b) whether it is seed-stable (no), and (c) whether any of it licenses a claim specific to ESM-2 versus PLMs generally (the write-up now says no).

### S2b — the three dropped findings, verified

**(i) The "H1a reversal" — A222V produces a LARGER representational shift than its own severity predicts.**
- The original claim's text exists only in `MTHFR_RESULTS_LOG_PART2.md`, which is absent (S1c searches) — so the original wording is unverifiable; the task doc's paraphrase is currently the only in-repo statement of it. Logged, not worked around.
- Current status of the *substance*, verified fresh: the generic severity→shift relation holds (M1e Spearman −0.466667 [−0.583333, −0.066667], FOLLOW L565; denser W3 −0.519 [−0.635, −0.388], SESS L2747). The A222V-specific residual was **NOT SUPPORTED** at 9 backgrounds (+0.00954 [−0.00573, +0.02640], contains 0, FOLLOW L348/L575) and **became supported** at 31 backgrounds: **+0.02121 [+0.00465, +0.03934], CI excludes 0 from above** (SESS L2746) — verdict CHANGED to CONTRARY-TO-H1A, i.e. the direction of the original reversal claim (larger shift than severity predicts). The two designs' CIs overlap [0.0047, 0.0264] — "resolution, not reversal" (SESS L3010).
- **Does the reliability framing supersede / contradict / sit alongside?** It **sits alongside, unaddressed**: no entry read this session (REL A1/A2/A4c/B1–B4/C3/AC4d) re-tested A222V's residual across seeds or checkpoints. The reliability result (cross-seed delta agreement median 0.084365; five-seed mean |ρ| ≤ 0.041) does not test the across-background mean-shift fit, but it does imply any single-checkpoint shift *pattern* is weakly seed-reproducible — so the W3 residual should be reported with that caveat. Not contradicted; not superseded.

**(ii) The rank-vs-MAE digest (`GROUPS_C_TO_H_DIGEST.md` Group C, read in full, fresh).**
- Content verified: C1b — retention is **not background-specific** (gap +0.2042 vs +0.1919, difference +0.0124 [−0.0375, +0.0370], p=0.9630) — "the review's suspected answer confirmed"; C1c — BLOSUM62 matched gap +0.0691 [+0.0142, +0.1146] (Grantham UNMATCHED, not interpretable); C1d — S_A222V vs S_WT ρ = 0.999636 → "the MAE story rests on a small number of rank swaps" (OV entry L455–465 fresh; the log's own phrasing flagged in S1b #4); C2a/C2b — proximity concentration seed-robust; **C2c — MSE verdict HOLDS**; C3a — disattenuation r_dis −0.110413 [−0.147534, −0.072340], ratio 1.2530 "MATERIALLY LARGER".
- Current status: the digest was never carried into any write-up (it sat unreviewed — that is why it was "dropped"). Its findings are **verified and now consistent with the write-up**: the rank half was demoted by C1b + the exogenous-anchor collapse (RESULTS L124 fresh), the MAE half stood (C2c), and the disattenuation number is independently re-confirmed by the reliability round's A2 (−0.30/−0.38, same proxy caveats). The original log's open question ("unqualified vs qualified final claim") is answered: **qualified** — RESULTS's corrected conclusion (L126–128) is the qualified version.

**(iii) The additive-null MAE result (original §6.2/6.3).**
- Original claim verified from source (MTHFR_RESULTS_LOG L246–249, fresh): ESM-2's MAE higher than the no-interaction baseline in **every** stratum; high stratum +0.00241 with CI excluding 0; own-side +0.00446–+0.00866; the log's own caveat: the floor-vs-baseline difference also excludes 0 (−0.000767), so magnitude ≠ general inaccuracy.
- Current status: **verified as a descriptive statistic** — re-verified twice after the original log: D1b UNCHANGED-HOLD (shrunken stratifier arm3 +0.001851 [+0.000987, +0.002706], mean SE 0.1166 → 0.0788) and C2c (the verdict matches under squared loss as well as MAE), both fresh from OV's SUMMARY. **Weakened as a claim about ESM-2 specifically**: the corrected conclusion (RESULTS L126–128, fresh) subordinates all accuracy-degradation findings to "a property of how well any WT-arm-informed signal predicts an A222V-arm-derived target, which is close to tautological once seen clearly."
- **Does the reliability framing supersede / contradict / sit alongside?** **Sits alongside, unaddressed**: no reliability-round entry re-ran any MAE or additive-null analysis (the entries read this session are correlation- and agreement-based). The two framings have never been reconciled head-on — stated plainly rather than papered over.

### S2c — BLOCKED: the "v3 sentence"
Same missing file as S1c (search evidence quoted in [S1]'s S1c entry; re-confirmed fresh at 23:50). The closest in-repo match — `FINAL_CLOSEOUT.md` L3–4 — was NOT edited (identity unproven; rule 3 forbids substitution; and if "v3" is `MTHFR_RESULTS_LOG_PART2.md` or `RESULTS.md`, the do-not-touch list forbids it independently). Replacement sentence supplied for the user to apply wherever v3 lives:

> **Replacement for S2c's target sentence:** "As of `RELIABILITY_LOG.md`'s SUMMARY, the project's core analytical questions are answered: the headline anchor and its nulls, its five-seed instability (mean ρ −0.0156, all |ρ| ≤ 0.041), its ensemble value (−0.028508, matching the Spearman-Brown prediction), its disattenuation (−0.30 to −0.38, under stated proxy assumptions), and the positive-control gates. Genuinely open: SaProt epistasis (Z3g-h) awaits the structure-vs-reference population-definition decision reserved for the user; B3's clade specificity is MIXED (size-matched p=0.0010, placebo p=0.2467); calibration is still NOT publication-ready (M-series); the two-trait MoCHI refit was never run; and site-54 genome-wide inference plus detection-floor EXCEEDS claims remain permanently out of scope. 'Resolved' must never be read as 'nothing is open.'"

Verdict: **S2a PASS** with one BLOCKED portion (Parts 9–14 not on disk — flagged, not substituted); **S2b PASS** — all three dropped findings verified from source with current status stated; **S2c BLOCKED** (v3 absent; replacement supplied).
Files created/modified: `docs/tasks/disattenuation-and-ledger/DISATTENUATION_LOG.md` (this entry only).
Anything unexpected or worth flagging:
- The original log's own status table calls 6.2/6.3 "Fails" (ESM-2 loses to the additive null) — the same direction as S2b-iii; anyone skimming "Fails" could misread it as "the claim was falsified." Direction of the claim matters: the claim "ESM-2 beats the null" fails; ESM-2 *loses*.
- CAL L465 "IMPROVED" (N4c) vs REL L610 "MECHANICAL" (A4c) is a live contradiction between two prior logs, both do-not-touch. Neither was edited; both are recorded above exactly as each log states them.
- `RESULTS.md`'s corrected conclusion (L126–128) is currently the strongest statement anywhere in the write-up layer and it *subordinates* the MAE finding — S2b-iii's status statement follows it rather than the original log.
---

## [T] — Group T: is the disattenuation valid? (T1 outlier-vs-distribution, T2 CTT evidence, T3 bootstrap CI, T4 pooled-vs-within reliability, T5 WT-vs-delta money figure, T6 Nambiar comparability)
Status: PASS — T1a/T1b/T1c, T2a, T3a, T4a, T5a, T6a/T6b/T6c all executed; nothing blocked, nothing skipped
Time started / finished: 2026-09-26 00:00 (T1a/T1b/T6a first executed before 00:27) / 2026-09-26 00:47. Script 98 smoke 00:30:03–00:30:35 (N_BOOT=300), full run 00:33:13–00:40:29 (N_BOOT=10000, 436.4 s, EXIT=0). T1a/T1b re-verified fresh and T6b/T6c completed 00:43–00:47.
What I did: Read task text L78–151 fresh (T1–T6 verbatim). T1a recomputed the five member rhos from CSVs this session and cross-checked against published AC4 values; T1b fetched Meta's model README live; T2a retrieved A1's result from RELIABILITY_LOG without re-running it (forbidden by the header); T3/T4/T5 implemented as one new pre-registered script (98) — smoke at N_BOOT=300 first, then the full N_BOOT=10000 run in the foreground; T4's pooled-vs-within question answered by reading AC2/AC4's own code for how the statistic was formed, then recomputing both versions side by side; T6a searched the Nambiar full text, T6c cloned their repo and searched its code, T6b pinned their exact reported values including Supplementary Table S2.

### T1a — where −0.088118 sits in the five-member empirical distribution (recomputed fresh)

Method (this session): `_spearman(member delta, own_e_b)` per member on script 32's exact base (`task32_analysis_table.csv` dropna own_e_b/GI_folinate_independent/delta_esm → 10,757 rows / 654 positions), members joined on [position, mut_aa] validate="1:1" — script 86's R4/R6 convention.

- Five ESM-1v member rhos: **−0.020573, −0.040820, +0.013434, −0.026572, −0.003409** — identical to 6 dp to AC4's published R6 (CLOSEOUT_LOG L2174–2177) and to CALIBRATION_LOG L452's RAW row, so the recomputation is a reproduction, not a new number.
- mean **−0.015588**; sd **0.021052** (ddof=1) / 0.018829 (ddof=0); range **[−0.040820, +0.013434]**.
- ESM-2's −0.088118 lies **0.047298 below the smallest member**; rank **6/6** (the most extreme of the six values).
- Exact two-sided rank-based p with 6 exchangeable values = 2/6 = **0.333** — with n=5 the empirical distribution alone cannot flag the headline as an outlier (0.333 is the largest p a minimum can have); this is why the raw rank/percentile, not z, is the primary report (AGENTS §3).
- z = **−3.45** (ddof=1) / −3.85 (ddof=0) — printed as illustrative scale context only; a Gaussian tail at n=5 is unverifiable, and the exact p above supersedes it.
- |−0.088118| = **2.16×** the largest member |rho|.

### T1b — the documented training relationship (fetched fresh this session: raw.githubusercontent.com/facebookresearch/esm/main/README.md)

Checkable model-card facts, quoted:
- ESM-1v row: ``esm1v_t33_650M_UR90S_[1-5]`` | 33 layers | 650M | Dataset **UR90/S 2020_03** — "Same architecture as ESM-1b, but trained on UniRef90. Released with Meier et al. 2021." What's New: "July 2021: New pre-trained model ESM-1v released, trained on UniRef90."
- ESM-2 row: ``esm2_t33_650M_UR50D`` | 33 layers | 650M | Dataset **UR50/D 2021_04** — released August 2022 with Lin et al. 2022 (Science 2023, doi 10.1126/science.ade2574).
- The five ESM-1v checkpoints are five seeds of one configuration (same corpus snapshot UR90/S 2020_03); ESM-2 is a **different corpus snapshot** (UniRef**50** vs UniRef**90**, 2021_04 vs 2020_03 — different database release *and* different clustering level), a different training run, and a separate release/paper.
- Conclusion on the documented facts: the README documents **different corpora, different runs, separate releases**. Shared architecture/parameter count (t33/650M) is not shared training distribution. Treating ESM-2 as a draw from the ESM-1v seed distribution is not supported by anything in either model's documentation; borrowing r_delta = 0.084365 across the family boundary is an assumption, not a licensed inference.

### T1c — the one-sentence answer the review asked for

**ESM-2's −0.088118 is not an unusually large draw from the ESM-1v seed distribution — it is a different distribution entirely: Meta's own model card documents ESM-2 (UR50/D 2021_04, Lin et al. 2022) and the ESM-1v seeds (UR90/S 2020_03, Meier et al. 2021) as different corpora, different runs, and separate releases, so the outlier question is moot and cross-family reliability borrowing is not a licensed move.** (If forced to the dichotomy the review posed: not "an unusually large draw from the same distribution" — "not the same distribution at all." The n=5 rank test could not have distinguished these by itself: exact two-sided p = 0.333.)

### T2a — does the attenuation model itself hold up? (A1 retrieved from RELIABILITY_LOG, NOT re-run)

- A1's result, quoted from RELIABILITY_LOG L337–339: "rho = −0.028508 (CI [−0.056495, −0.000239], p_boot = 0.0484; sign-flip p = 0.0442, null centered) against the Spearman-Brown-predicted ~−0.030 — **the prediction holds**"; the prediction itself, L310: "−0.015588096 * sqrt(5/(1+4*0.084365)) = −0.0301"; verdict gate L331: "prediction inside CI: True".
- Statement required by the task: this **is** real evidence that the classical-test-theory attenuation model describes the ESM-1v seed family's own internal behavior correctly — averaging the five seeds moved the correlation exactly as Spearman-Brown predicts from the measured r_delta = 0.084365, with a centered sign-flip null.
- And explicitly: it does **not** license applying that model's correction factor to ESM-2 — that is T1's separate question, answered "no" in T1b/T1c. The disattenuated −0.303/−0.380 is therefore a **conditional estimate**: what the anchor would be *if* ESM-2 shared the ESM-1v family's reliability — a counterfactual whose premise T1b fails. Both halves (T2 holds, T1 fails) are reported as the task demands, neither one used to argue the other's case.

### T3a — empirical CI on the disattenuated estimate (script 98, new; pre-registered docstring)

Design (pre-registered before running): 654 positions resampled with replacement per draw (the same unit `scripts/lib/stats.py` position_cluster_bootstrap uses, L51–52); inside **every** draw, recompute from scratch the numerator rho, the 10-pair median r_delta, and r_own (1 − var(syn)/var(ana) with synonymous rows travelling with their positions); form the disattenuated statistic fresh per draw; percentile 2.5/97.5 CIs; seed 0. Smoke N_BOOT=300 first (gates green), then full N_BOOT=10000 foreground, 436.4 s, EXIT=0.

All gates OK (failure would have been STOP/FAIL): G1 frame (10757, 654); G2 rho = −0.08811806424891734 (tol 1e-9); G3 r_delta = 0.0843648 (tol 1e-6); G4 WT = 0.8826369 (tol 1e-6); G5 r_own = 0.6363276 vs 0.6363 (tol 5e-4; syn n=570, var 0.02111 / ana var 0.05804); G6 points −0.3033781 and −0.3803154 (tol 1e-5); G7 AC2 (1900, 100) rho = 0.0977638 vs 0.0978 (tol 5e-4).

Results (10,000 draws, percentile 2.5 / 50 / 97.5):

| quantity | point | in-draw 95% CI |
|---|---|---|
| disattenuated, delta-only = rho/sqrt(r_delta) | −0.303378 | **[−0.440395, −0.301911, −0.192728]** |
| disattenuated, fully = rho/sqrt(r_delta·r_own) | −0.380315 | **[−0.555203, −0.378283, −0.242329]** |
| headline rho | −0.088118 | [−0.117556, −0.088319, −0.058828] |
| r_delta pooled | +0.084365 | [+0.052159, +0.086318, +0.122589] |
| r_own | +0.636328 | [+0.563575, +0.638064, +0.699159] |

- Non-positive denominators: **0/10,000** for both variants (reported, not hidden; no warning threshold triggered).
- Verdict: the interval is **wide, exactly as the task predicted** — the delta-only CI spans −0.44 to −0.19, a factor ~2.3 in magnitude. Direction is stable (every draw < 0), but the point estimate's precision is not ±0.12-scale. Any future write-up must quote the CI, not −0.30 as a number. This CI does not license transferring either reliability to ESM-2 (disclosure printed by script 98).

### T4a — pooled vs position-controlled reliability, side by side

**How AC2/AC4 were actually computed (read from code, not assumed):** both were **pooled**. AC4: `scripts/86_ac4_esm1v_five_members.py` L549–561 — `_spearman(colfn(k), colfn(l))` on the joined 10,757-row column vectors, median over 10 pairs; position clustering enters only the bootstrap CI, never the statistic. AC2: `scripts/58_j2a_proposal_checklist.py` L271 — `position_cluster_bootstrap(d, "position", "delta150", "delta650", ...)` whose statistic is the pooled row-level rho; clustering again only in the CI. So the review's concern (shared positional structure inflating a pooled agreement number) applies in principle to both.

**Recomputed on the same frames (script 98), same median-of-10 convention:**

| reliability, ESM-1v deltas (AC4) | point | 95% CI |
|---|---|---|
| POOLED (A2's quantity) | +0.084365 | [+0.052159, +0.122589] |
| WITHIN-position (position demeaned) | **+0.050813** | [+0.030455, +0.065259] |
| BETWEEN-position (position means) | +0.099947 | [+0.053991, +0.148743] |

| reliability, 150M-vs-650M (AC2, 1,900 rows / 100 positions) | point | 95% CI |
|---|---|---|
| POOLED | +0.097764 | [−0.039090, +0.226736] (published CI [−0.0444, +0.2275] — reproduced) |
| WITHIN-position | **+0.057487** | [−0.027372, +0.144184] |

- Verdict: **positional structure does contribute.** The pooled 0.084 sits between within-position 0.051 and between-position 0.100; isolating within-residue agreement lowers AC4's reliability by ~40% and AC2's by ~41%. Illustrative arithmetic only (not adopted as a new estimate): using within-position as the denominator would enlarge the correction factor sqrt(1/0.0508) ≈ 4.4 instead of sqrt(1/0.0844) ≈ 3.4.
- Both versions are reported side by side as instructed; **neither is chosen post-hoc** — A2's pooled denominator was pre-registered, and the within-position number is the isolated quantity the review asked for, not a replacement for it. Disclosure (printed by script 98): within-position removes ALL between-position structure including the real distance-to-222 gradient, so it isolates within-residue agreement specifically; it is not "the correct number."

### T5a — the money figure: base-score reliability vs delta reliability, same five checkpoints

Same frame (10,757 / 654), same convention (median of 10 pairwise member Spearmans, script 86 R7's exact procedure), same run:

| agreement across the 5 ESM-1v checkpoints | point | 95% CI |
|---|---|---|
| RAW wild-type-background scores (wt_logodds) | **+0.882637** | [+0.869559, +0.881465, +0.891790] |
| background-induced DELTAS | **+0.084365** | [+0.052159, +0.086318, +0.122589] |

- Ratio **10.46×**; the CIs are nowhere near each other. Standalone result, no disattenuation involved (as the task states).
- Reading: the five seeds agree almost perfectly on what a WT-background score *is* and barely at all on the background-induced delta — the disagreement is introduced almost entirely by the subtraction across backgrounds. This is the strongest single figure available, exactly as the review flagged: it is gate-verified (G4/G3 both green to 1e-6) and needs no model of measurement error at all.

### T6 — is the comparison to Nambiar's reported numbers valid?

**T6a (their paper text).** Local full-text extraction of `2025.09.14.676130v1.full-2.pdf` (20 pages, 64,354 chars): **zero** occurrences of *disatten*, *reliab\**, *measurement error*, *noise correct\**, *spearman-brown*, *correction for attenuation*, *true/corrected correlation*; the single `atten` hit is the incidental word "flatten" (their assay-bias discussion). All 12 *calibrat\** hits denote their monotone nonlinear transform ϕ1/ϕ2 (Methods: "fit the parameters (b,c) by nonlinear least squares… a 20% uniform random sample of the double-mutant entries") — a score-to-fitness mapping, **not** a measurement-error correction.

**Their exact reported values (verbatim from the paper).** Headline: "Pearson r = 0.37 for TEM1, r = 0.34 for YAP1, and r = 0.26 for RRM" (model-size sweep: "r = 0.38 for TEM1, 0.34 for YAP1, and 0.26 for RRM" at 650M). Supplementary Table S2 gives all three stages per protein — untransformed / shared-params / separate-params: TEM-1 **0.0918 / 0.1169 / 0.3748**, YAP1 **0.1770 / 0.2364 / 0.3444**, RRM **0.1333 / 0.1508 / 0.2633**.

**T6c (their code).** `github.com/maslov-group/Epistasis` cloned shallow → `data/external/Epistasis` (6.0 MB; 32 text files scanned): **zero** files hit for *disatten*, *spearman-brown* (either spelling), *correction for attenuation*, *measurement error*, *reliab\**, *attenuation*. No reliability correction exists anywhere in their released code either.

**T6b verdict.** Their ~0.26–0.38 are **raw observed Pearson correlations after a score transformation**, with no disattenuation of any kind in paper or code. Comparing our disattenuated −0.303/−0.38 to their 0.26–0.38 is therefore **not a like-for-like comparison**, and the "lands inside their range" claim is **DROPPED from any future write-up** (that claim currently exists only in the read-only CALIBRATION task-doc layer — CALIBRATION_AND_PUBLICATION_READINESS.md L93 and CALIBRATION_LOG L344; `RESULTS.md` does not carry it — flagged here, not edited). The sanctioned reframe, grounded in the Table S2 numbers above: *"our raw anchor (|ρ| = 0.088) sits in a similar range to their raw, pre-calibration numbers (Pearson 0.09–0.18); we have no comparably-corrected number of theirs to compare our corrected estimate against."* — with two caveats the reframe needs: (i) theirs is Pearson vs double-mutant epistasis, ours is Spearman vs own e.b, so this is a magnitude-level statement only; (ii) their values are positive-signed against a different target, so the comparison is on |ρ|, not sign. Consistency check: script 88 (N3) already applied their ϕ1/ϕ2 to our scores and found the move "NOT MATERIAL" (CALIBRATION_LOG L344) — the 0.088-vs-0.26 gap is not explained by calibration on our data either.

Files created/modified: NEW `scripts/98_t3_t4_t5_reliability_audit.py` (next free number 98; pre-registered docstring with G1–G7, smoke+full run instructions); NEW `data/processed/task_T3T4T5_reliability_audit.csv`; NEW `data/external/Epistasis/` (shallow clone); this log entry. No do-not-touch file modified; no existing script or lib modified; the ensemble-mean run and the Nambiar severity-baseline search were NOT re-run.

Anything unexpected or worth flagging:
- **A mislabel inside the task doc itself (flagged, not smoothed):** T6b instructs the reframe "…their raw, **pre-calibration** numbers" while T6a calls the same ~0.26–0.38 "their reported **calibrated** correlations." Both cannot be the raw set: 0.26–0.38 is their POST-calibration range; their raw pre-calibration values are 0.0918/0.1770/0.1333 (Table S2). The reframe sentence is only true against the latter — the entry above states it with the correct numbers.
- The 0.333 exact rank p means T1's conclusion rests on the **documented training facts**, not on the empirical distribution — n=5 could never have settled it statistically. Anyone quoting "3.45 SDs below" (as `RESULTS.md` L9 does) should pair it with this.
- AC2's pooled CI reproduced the published CI to ±0.005 under a different rng stream (same bootstrap design) — consistent, not gated.
- `/tmp/nambiar.txt` was used (ephemeral system tmp); it is reproducible on demand from the local PDF path cited above.
---

## [U] — Group U: positive-control estimator audit (U1a — do the GB1/GRB2 controls test the headline estimator?)
Status: PASS — U1a answered from fresh code reads with direct citations
Time started / finished: 2026-09-26 00:54 / 2026-09-26 00:57 (evidence first located before 00:27; every line below re-read verbatim in this window)
What I did: Read `scripts/73_gb1_estimator_transplant.py` (AA1/GB1) docstring and null sections, `scripts/74_second_double_mutant_control.py` (AA7/GRB2) null sections, and the contrast case — I1's permutation gate in `FOLLOWUP_LOG.md` [L1c] — directly from source. No prior characterization taken on trust.

Actual output (verbatim quotes):

- **Script 73 (AA1, GB1) docstring L82–96:** "STATISTICS (**script 33's code path, transplanted not rewritten**; N_PERM from env, default 10000; SEED 0; +0 correction identical to script 33) … **NULL 1 sign-flip re-derivation**: independent +/-1 per variant cell, re-derive e_b, recompute rho; p = mean(|null| >= |obs|); null centring checked with script 33's exact expression … **IDENTITY GATES (script 33's, kept)**: all-+1 flips reproduce the stored e_b column exactly (max|diff| < 1e-6); all--1 give its exact negation; failure -> sys.exit(1)."
- **Script 74 (AA7, GRB2) L616:** `# ------------- script 33's sign-flip path (as in script 73) -----------` followed at L623 by "SANITY CHECKS (script 33's, transplanted: test the test first)" with the same all-±1 identity checks.
- **Both entries' runs passed those gates exactly:** AA1 identity "max|diff|=0.000e+00" (DEEPDIVE L643–644); AA7 same (L1176–1177 area). AA7's own design-summary line prints the adaptation explicitly: "flip units (cells)=689 (one +/-1 per variant, A5) | … | MTHFR contrast: 10,757 variants x 4 conc cells = 43,028 cells, 654 positions."
- **The contrast — a different statistic:** I1's gate (FOLLOWUP_LOG L122/L167) is an association/excess-over-null threshold test: "null_mean=0.3880021 σ0=0.0532 … floor ρ = 0.5400419 … comparator ρ = 0.4466626 < 0.5400419 → COMPARATOR-UNDERPOWERED, p_one observed 0.1398, power 35.3%." That tests whether GB1's pooled ρ clears an association-null threshold — NOT script 33's signed sign-flip re-derivation.

Verdict (direct answer to U1a): **YES — both positive controls run the same signed sign-flip re-derivation null (script 33's exact code path) that produces the headline −0.088, as their PRIMARY test** — code citation: script 73 L82–96 (docstring, "transplanted not rewritten" + script 33's identity gates) and script 74 L616/L623–636 (same path, "as in script 73"). They do not validate only the earlier excess-over-null association statistic; that older style of test is what I1's permutation gate used, and it is a different (secondary) construction. The one adaptation is the flip unit (one ±1 cell per variant, A5, vs MTHFR's 4 cells × 10,757 = 43,028), disclosed in their own printed design summaries; the identity gates still pass at 0.000e+00. Results under that shared null, for context: AA1/GB1 at n=57 does NOT survive (observed +0.1222, null mean −0.0004, sd 0.1408, p=0.3849 — DEEPDIVE L651, underpowered by its own verdict line), AA7/GRB2 at n=689 SURVIVES (observed +0.1153, null mean −0.0003, sd 0.0371, **p=0.0019**, excess +0.1156, ~0% structural artifact — L1179; Null-2 site-block association p=0.0108 — L1190).

Files created/modified: none (read-only audit; this log entry only).
Anything unexpected or worth flagging:
- AA7's verdict line (L1209) calls p=0.0019 a "(permutation p, primary)" while the output block labels it "NULL 1 — SIGN-FLIP RE-DERIVATION" — same number, wording difference only (the sign-flip IS run as N_PERM=10,000 sign permutations); no contradiction, noted so a future reader doesn't think there are two p-values.
- AA1's absolute-value sign-flip variant is degenerate under the single-cell transplant (|flip × r| = |r| invariant → p=1 by construction), disclosed post-hoc in AA1's own entry (L655–660). MTHFR's 4-cell design keeps it non-degenerate (script 33). Not re-derived here; flagged as already-disclosed.
---

## [V] — Group V: clustering/effective-n resolved (V1a resampling unit read from code, V1b both-framing floors, V1c verdict)
Status: PASS — V1a/V1b/V1c all executed; the answer resolves a three-round-old question without any re-run
Time started / finished: 2026-09-26 00:47 / 2026-09-26 00:55
What I did: Re-read `scripts/lib/stats.py` L34–56 (the bootstrap's own resampling logic) and `scripts/72_mthfr_detection_floor.py`'s docstring plus AA4's full logged output (DEEPDIVE L328–397) fresh. Computed both floors with a formula stated before computing (reproduced verbatim below). No existing run re-executed.

Actual output:

### V1a — the resampling/clustering unit, read from the bootstrap's own code

`scripts/lib/stats.py`:
- L34–36: `_cluster_indices` → `clusters = d[cluster_col].unique()` (the unique values of the position column).
- L51: `drawn = rng.choice(clusters, size=len(clusters), replace=True)` — each replicate draws **654 unique positions with replacement**.
- L52: `i = np.concatenate([pos[c] for c in drawn])` — all rows of each drawn position travel together; **rows are never drawn independently**.
- L55: the function itself returns `n_rows` and `n_clusters` side by side — the resampling frame is the cluster set.

**Unambiguous statement:** the unit the position-cluster bootstrap actually resamples is the **position**, and the effective sample size implied directly by that logic (without any CI-width back-calculation) is **654 independent units per replicate** — that is what `size=len(clusters)` draws. For completeness: script 33's companion sign-flip test resamples nothing — it flips ±1 per *cell* (4 conc cells × 10,757 variants = 43,028 cells; AA4's design-summary print says exactly this), a re-derivation null, not a resampler. AA4's floor used both tests (script-33 sign-flip primary, this cluster bootstrap secondary).

### V1b — the 80%-power detection floor under BOTH framings, side by side

Pre-stated formula (written before computing): Fisher-z test power, two-sided α=0.05, power=0.80 → `ρ_min(n) = tanh((z₀.₉₇₅ + z₀.₈₀)/√(n−3))`, z₀.₉₇₅ = 1.959964, z₀.₈₀ = 0.841621.

| framing | n | 80%-power floor |
|---|---|---|
| rows | 10,757 | **0.027009** |
| positions | 654 | **0.109364** |

Context computed in the same run (all pre-stated formulas, all from numbers already on disk):
- What each framing *predicts* for power at ρ=0.05: row-framing **0.9994**, position-framing **0.2475** — against AA4's *measured* power **1.00** (50/50 detections at 0.05, same position-cluster test, DEEPDIVE L374).
- Design-effect reconciliation using AA4's printed structure (k̄=16.45, ICC=0.0973): de = 1+(k̄−1)·ICC = 2.5033 → n_eff = 10,757/2.5033 ≈ **4,297** → floor = **0.042727**.
- Floors from empirical null SDs already logged: script 33's sign-flip null sd 0.009364 → **0.026234**; AA4's mean null sd 0.0101 → **0.028296**; AA4's mean CI half-width 0.0225/1.96 → **0.032161**.
- Anchor vs the two required framings: |−0.088118| is **ABOVE** row-Fisher (0.027) and **BELOW** position-Fisher (0.109).

### V1c — which framing is correct, and where the anchor actually sits

1. **Correct framing for inference = positions.** The bootstrap resamples 654 positions and never rows (V1a, code-quoted); AGENTS §3 forbids row-level resampling for exactly this reason. The row-Fisher floor (0.027) must therefore **not** be quoted as the project's floor — it assumes 10,757 independent observations the data do not have (pseudoreplication).
2. **But the position-Fisher number (0.109) is also not this pipeline's floor** — it is the floor for a *different statistic* (a correlation of one summary point per position). Our statistic pools all 10,757 rows inside those 654 clusters, and AA4's own power table empirically falsifies the 654-point plug-in for this pipeline: it predicts power **0.2475** at ρ=0.05 where the same position-cluster test *measured* **1.00** (50/50, type-I 0/50 at ρ=0). The measured ICC (0.0973, k̄=16.45 — script 72's own print) explains the gap: positions share only ~10% of variance, so the design-effect n_eff ≈ 4,297, giving floor ≈ **0.043** — consistent with the empirical-null floors (0.026–0.032) and with AA4's pre-registered grid result "**we could have detected ρ ≥ 0.05; we observed −0.088**" (power saturated at the smallest grid point; floor below 0.05, resolution 0.05 as pre-registered).
3. **Where the anchor sits:** under the floor that actually describes this pipeline (AA4's measured injection through the exact two-test position-cluster pipeline: floor ≤0.05, corroborated by design-effect 0.043 and null-SD 0.026–0.032), |−0.088118| sits **above** it by ~2×. The "we had the power to detect this" framing therefore **survives — in its empirical AA4 form only**: it must be cited to AA4's injection and the measured ICC, never to the row count (0.027 would be pseudoreplication), and never to the 654-point Fisher plug-in (0.109), whose power prediction is contradicted ~4-fold by AA4's measured table. If any write-up justified the power claim by "n = 10,757", that justification needs retraction; the claim itself, on AA4's evidence, does not.
4. **Note the three-round pattern:** this question was asked three times because the two naive plug-ins disagree (0.027 vs 0.109) and each side of the debate quoted the one that suited it. The resolution is that **both plug-ins are the wrong formula for a clustered pooled correlation**, and the project already owns the right number: AA4's empirical floor, pre-registered, gates passed, type-I calibrated.

Files created/modified: none (read-only audit + inline computation recorded above; this log entry only).
Anything unexpected or worth flagging:
- The position-Fisher floor (0.109) exceeding the anchor is a real arithmetic fact, not an error — it is reported above precisely so nobody later "discovers" it as a gotcha; its inapplicability rests on AA4's measured power table, not on preference.
- V1b's inline computation used scipy's `norm.ppf` in a quoted heredoc (not a numbered script) — the formula and full output are reproduced above so the log is the record, per the launch prompt's format.
- FOLLOWUP [L1c]'s ρ_floor = 0.5400 / power 35.3% (quoted above for the I1 contrast) is **GB1's association-gate floor**, not MTHFR's — the two floors live in different tests and must never be conflated; MTHFR's own floor is AA4's (this entry).
---
## [W] — Group W: distance stratification (W1 premise reversed) + stability-model identity confirmed (W2)

Status: PASS — W1a/W1b executed as a new pre-registered script (script 99, full run); W2a answered against actual code. W1's hypothesized decay did NOT materialize — the measured direction is the opposite — stated plainly below.
Time started / finished: 2026-09-26 01:10 / 2026-09-26 01:24
What I did: Wrote `scripts/99_w1_distance_decay_vs_syn_floor.py` with pre-registered bands and verdict rule in its docstring (written before any run), smoked at N_BOOT=300, full run at N_BOOT=10000 (37 s, gates G1–G4 green). For W2, read the actual definition/computation in scripts 77 and 96 fresh (code-quoted below), not any summary.

### W1a — |own_e_b| vs distance from 222, analysis vs syn noise floor

Gates (all pass): G1 base frame 10,757/654; G2 pooled rho(delta_esm, own_e_b) = −0.08811806424891734 (exact); G3 task32's `dist_222` == |position−222| on all 11,344 rows (max|diff|=0); G4 syn frame 570 rows/570 positions, var 0.02111 (matches script 98's G5 exactly).

**PREMISE REVERSED — |e.b| does not decay with distance from 222; it grows:**

| statistic | rho | 95% CI (position bootstrap, N_BOOT=10,000, seed 0) | p_boot | n/positions |
|---|---|---|---|---|
| rho(\|own_e_b\|, dist) analysis | **+0.177935** | [+0.141675, +0.212828] | <1e-4 | 10,757/654 |
| rho(\|own_e_b\|, dist) syn (floor) | **+0.081816** | [+0.000373, +0.161996] | 0.0492 | 570/570 |

Distance curve (mean |own_e_b| per pre-registered band):

| band | analysis n/pos | ana mean (sd) | syn n/pos | syn mean (sd) |
|---|---|---|---|---|
| dist ≤ 25 | 844/50 | 0.0967 (0.0950) | 43/43 | 0.0540 (0.0604) |
| 26–100 | 2,449/150 | 0.1166 (0.1316) | 138/138 | 0.0876 (0.0850) |
| > 100 | 7,464/454 | 0.1956 (0.1829) | 389/389 | 0.1159 (0.1104) |

Verdict by the pre-registered rule (both CIs exclude 0): **the gradient is not analysis-specific — the synonymous noise floor carries the same-direction distance structure** (rule output: "BOTH sides show a distance gradient"). The analysis side is ~2.2× the floor in rho and 1.3–1.8× in band means (signal stays above floor at every distance: ana/syn = 1.79, 1.33, 1.69), but the *shape* — growing with distance — is shared with noise, so distance-growth of |e.b| is not by itself evidence of interaction structure. And the task's hypothesized decay (concentration of |e.b| near contact) is **absent**: the sign is the opposite. Reported as a falsified premise, not reinterpreted; no alternative distance metric or band was tried after seeing this.

### W1b — distance-stratified primary correlation (pre-registered bands)

| band | rho(delta_esm, own_e_b) | 95% CI | p_boot | n/positions |
|---|---|---|---|---|
| B1 dist ≤ 25 | +0.069061 | [−0.033307, +0.157836] | 0.1716 | 844/50 |
| B2 26–100 | −0.014756 | [−0.073471, +0.044926] | 0.6032 | 2,449/150 |
| B3 > 100 | −0.051139 | [−0.085157, −0.017061] | 0.0042 | 7,464/454 |

→ **No evidence that contact-range concentration drives the pooled correlation.** The within-25 band is positive and not significant (CI spans 0); B2 is null; the pooled −0.088 lives in the large far band (B3, CI excludes 0). The interaction the task flagged is reproduced fresh in W1c: rho(|delta_esm|, dist) = −0.298214 [−0.349260, −0.245352] p<1e-4 on the 10,757 analysis frame — consistent with S1's K3 (−0.298083 on the full 11,344; same value to 3 dp on different frames).

### W2a — one unambiguous sentence, checked against actual code

**Yes: the interaction term that survived Cα-distance de-biasing and was confirmed as a genuine null is ThermoMPNN-D's native, non-degenerate double-mutant interaction score** — `interaction_D = ddG_epi(222 A→V, X wt→a) − ddG_single(X wt→a) − ddG_single(222 A→V)`, with `ddG_epi` from their epistatic Siamese model (ThermoMPNN-D-ens1.ckpt via `run_double`) and both singles from their single model (ThermoMPNN-ens1.ckpt via `run_single_ssm`), each of the three terms an independent model evaluation — **not** the rank-degenerate additive ddG(v)+ddG(A222V) construction.

Code evidence (read this session):
- `scripts/77_thermompnnD_double_mutant_interaction.py` L47–60, "THE QUANTITY (frozen)": the formula above, plus verbatim — *"No additive-term degeneracy: each of the three terms is an independent model evaluation (task L276-278)."*
- Same file L420–421: `v2["interaction_D"] = (v2["ddg_epi_D"] - v2["ddg_single_D"] - ddg_222_s)`.
- `scripts/96_b4_debias_interaction.py` (B4b) operates on exactly that column: G1 frame = `task77_thermompnnD_doubles.csv` rows with own_e_b (9,595/586); G2 reproduces AD4's rho(interaction_D, own_e_b) = +0.0154 and mean −1.31853 within 4 dp before de-biasing. De-biased residual **+0.0097 [−0.0221, +0.0410], p_boot=0.5382** vs original **+0.0154 [−0.0166, +0.0465], p_boot=0.3406** → CI still includes 0 → RELIABILITY_LOG L1073 verbatim verdict: *"AD4's NULL IS CONFIRMED AS REAL, not an artifact of the offset."*
- The degenerate additive construction exists in script 77 only as a separate control — "(c) additive baseline rho(ddG_vendored, own_e_b)" (L493) — never as the quantity B4b tested.
- → **No walk-back needed** for the "confirmed genuine absence of stability-mediated signal" claim; the task's conditional ("if it was the degenerate version…") does not trigger.

Files created/modified: `scripts/99_w1_distance_decay_vs_syn_floor.py` (new); `data/processed/task_W1_distance_stratified.csv` (new, 10 rows). No existing file modified.
Anything unexpected or worth flagging:
- **W1's premise was backwards in the data:** the task's wording presumes |e.b| decays with distance from 222; measured direction is growth (+0.178), and the syn floor grows too (+0.082, CI excluding 0 only marginally at p=0.0492 — it was 0.0333 at smoke N=300, so the floor gradient sits at the edge; the pre-registered verdict text does not depend on which side of 0.05 it lands).
- **S1 ledger row K12 contained a transcription error (originally flagged, not edited — corrected in the ledger row on 2026-09-26 by true-final-closeout G3c):** its "original +0.0154 [+0.0039, +0.0271]" appears nowhere else in the project's records; every source — DEEPDIVE L2327–2336, RELIABILITY L1036 and L1069, script 96's docstring, and script 96's G2 fresh reproduction — says the original CI is **[−0.0166, +0.0465]**. K12's residual numbers (+0.0097 [−0.0221, +0.0410], p=0.5382) are correct. Cite [−0.0166, +0.0465].
---
## [X] — Group X: continuous depth regression (X1) + region-vs-domain break test (X2)

Status: PASS — X1a/X2a executed as script 100 (pre-registered docstring; smoke exposed one CI bug, fixed before any quotable run; full run N_BOOT=10000, run twice — the second run added the systematic between-boundary segmentation disclosed in-code). Result: the direction claim (ESM tracks depth, ThermoMPNN doesn't) HOLDS; the smooth monotone dose-response reading does NOT survive the leverage check; the break sits at region 4's edge, not the domain edge.
Time started / finished: 2026-09-26 01:19 / 2026-09-26 01:27
What I did: Wrote `scripts/100_x1_x2_depth_regression_domains.py` on `data/processed/task79_depth_positions.csv` exactly as on disk (586 positions; one row = one position, so the position-cluster bootstrap degenerates to a row bootstrap over 586 units — stated in the docstring). Bands, the leverage cut, the coincidence tolerance and the break-test boundaries were all fixed in the docstring before running. Gates: G1 586 unique positions, neff ∈ [111.9, 1215.4] (within script 79's measured bounds [1, 4783]); G2 pooled rho(yE, neff) = +0.171422 reproduces AD6's +0.1714 within 5e-4.

### X1 — continuous regression of per-position shift vs Neff

| model | raw OLS slope per Neff unit | 95% CI (position boot) | Spearman rho | 95% CI | p_boot |
|---|---|---|---|---|---|
| yE (ESM-2 shift magnitude) | +3.402852e-05 | [+1.749427e-05, +5.217293e-05] | **+0.171422** | [+0.091832, +0.247059] | <1e-4 |
| yT1 (ThermoMPNN residual) | +3.292785e-04 | [+1.113656e-04, +5.433597e-04] | +0.006928 | [−0.071569, +0.087827] | 0.8708 |

Decile-binned shape (frozen Neff-decile edges; mean yE per decile with bootstrap CI): deciles 1–5 (Neff 111.9→1198.0): **0.0613, 0.0641, 0.0559, 0.0589, 0.0523 — flat**; deciles 6–10 (→1215.4): **0.1024, 0.0815, 0.0756, 0.0848, 0.1150 — elevated, with a top-decile upturn**. yT1 deciles: 0.9061, 1.0790, 1.1383, 1.1073, 1.1439, 0.9819, 1.3022, 1.0247, 0.9376, 1.0528 — **no trend** (low first decile, then wobble).

Leverage check (pre-registered cut: neff > region-4 max 1213.1 — drops exactly the **124 highest-Neff positions, keeps 462**, matching B2c's expectation exactly, printed by the script):

| set | yE rho [CI] | p | yT1 rho [CI] | p | yE slope [CI] |
|---|---|---|---|---|---|
| all 586 | +0.171422 [+0.091832, +0.247059] | <1e-4 | +0.006928 [−0.071569, +0.087827] | 0.8708 | +3.40e-05 [+1.75e-05, +5.22e-05] |
| without top-124 (n=462) | **+0.012518 [−0.082236, +0.106433]** | 0.7890 | +0.065434 [−0.027181, +0.158539] | 0.1670 | +2.03e-05 [+2.02e-06, +4.10e-05] |

- yE's rank association **vanishes** without the top-124 (+0.1714 → +0.0125, CI spans 0). This exactly reproduces B2c's published in-range number (+0.0125 [−0.0822, +0.1064], p=0.7890 — RELIABILITY_LOG L836): independent confirmation of B2c via a different code path, not a new finding.
- yE's raw-scale slope keeps only a *marginal* positive CI without the cut (lower bound +2.02e-06 ≈ 0) — reported beside, never instead of, the rank result.
- **Slope-vs-rank disagreement on yT1, flagged not resolved:** OLS slope CI excludes 0 in both sets while Spearman is null in both; the decile shape shows why (a step out of decile 1, not a dose-response). Under the house rank statistic yT1 is flat — identical to AD6's logged +0.0069 [−0.0716, +0.0878].

X1 verdict (from the numbers; no threshold chosen post hoc): the transferable claim **"ESM-2's background shift tracks alignment depth; ThermoMPNN's residual does not"** holds under the house statistic on both full and trimmed frames. The stronger reading — a monotone dose-response across the whole protein — **does not**: yE is flat through the bottom five deciles with the association concentrated in the top ~21% of Neff, and yT1 shows no monotone relationship at any scope. The positive raw-scale slopes are reported for completeness with the yT1 slope explicitly flagged as non-monotone-inconsistent.

### X2 — region edges vs domain edges

Boundaries (fixed in the docstring before running):
- Atlas region edges: **147|148, 294|295, 474|475** (`scripts/lib/regions.py` REGION_BOUNDS; provenance: primer file via the 2nd author, Sept 2026).
- MTHFR domains: **PF02219 catalytic 48–337** and **PF21895 eukaryotic SAM-binding regulatory 344–644** → domain edge **337|344** (linker 338–343). Source: InterPro API v110.0 entries pfam/PF02219 and pfam/PF21895 on P42898, fetched live 2026-09-26 (UniProt P42898's flat file carries no FT DOMAIN ranges — noted, hence Pfam/InterPro).
- Domain edge to nearest region edge: **43 residues → do NOT coincide** (pre-stated coincidence tolerance: 5).

Break test — all four pre-registered boundaries, both sides, position-bootstrap CIs:

| split | left rho [CI] | right rho [CI] |
|---|---|---|
| b=147 | +0.167211 [−0.020288, +0.349700] (includes 0) | +0.213730 [+0.130886, +0.294561] (positive) |
| b=294 | +0.343562 [+0.221830, +0.456561] (positive) | +0.014457 [−0.091726, +0.117740] (includes 0) |
| b=337 (domain) | +0.241461 [+0.124610, +0.351079] (positive) | −0.135349 [−0.248382, −0.019487] (negative) |
| b=474 | +0.195771 [+0.106484, +0.286168] (positive) | −0.237283 [−0.379471, −0.085289] (negative) |

Segment decomposition — one systematic set: every segment between consecutive pre-registered boundaries, computed regardless of outcome (13 intervals total across splits+segments, all descriptive and unadjusted, disclosed as such):

| segment | rho [CI] | p | n |
|---|---|---|---|
| 2–147 (region 1) | +0.167211 [−0.020288, +0.349700] | 0.0800 | 108 |
| 148–294 (region 2) | +0.084324 [−0.081814, +0.249863] | 0.3318 | 135 |
| 295–337 (catalytic tail) | +0.120001 [−0.196664, +0.423956] | 0.4710 | 43 |
| 344–474 (regulatory head) | −0.001945 [−0.179525, +0.169462] | 0.9844 | 125 |
| 475–656 (region 4) | **−0.237283 [−0.379471, −0.085289]** | 0.0042 | 169 |

X2 verdict (pre-registered rule: report where the sign/CI pattern changes):
1. Region and domain boundaries **diverge** (43 residues apart at the nearest point; the atlas's other two region edges at 147 and 294 have no domain feature near them at all).
2. The **only segment whose CI excludes zero is region 4 (475–656), negative** — the reversal is a region-4 phenomenon. Every segment in 2–474 is positive-or-null with none individually excluding 0; they reach significance only pooled (2–337 = +0.241, 2–294 = +0.344).
3. **The domain edge marks no transition of its own:** immediately to its right, 344–474 is exactly flat (−0.002, p=0.98) and indistinguishable from 295–337 on its left (+0.120; CIs overlap heavily). b=337's "negative right side" is region-4 mass pooling into the right half — the same negative segment that flips b=474. **The depth-tracking effect breaks at the region-4 edge (474|475), not at the catalytic→regulatory domain edge** — the sharper region-specific form of the finding, with the domain hypothesis tested and not supported.
4. Disclosure: the segmentation was added after the four-boundary test showed flips at two boundaries — it is the adjudication X2's "domain edges or region edges specifically" question requires, computed as one complete set (all five segments), not a search over cuts.

Files created/modified: `scripts/100_x1_x2_depth_regression_domains.py` (new); `data/processed/task100_x1_depth_regression.csv` (28 rows); `data/processed/task100_x2_boundary_break.csv` (13 rows). Existing files unmodified.
Anything unexpected or worth flagging:
- **Smoke-run bug caught before any quotable run:** the first smoke's slope CIs were computed on `df.to_numpy()[:, :2]` (= position/region columns, not the named x/y) because `boot_stat` didn't receive column names — CIs came out identical across yE/yT1 and inconsistent with the slopes (CI ~6e-03 vs slope 3.4e-05). Fixed pre-full-run; no number from the buggy version is quoted anywhere.
- **S1 ledger K21 was mislabeled (flagged here; label corrected in the ledger row on 2026-09-26 by true-final-closeout G3c):** K21's value/CI/n (+0.1714 [+0.0918, +0.2471], 586) is AD6's **rho(yE, Neff)** where yE = position-mean |delta_ESM| (DEEPDIVE L2701, L2731, L2743) — not "depth × interaction_D". AD6's actual interaction_D-vs-depth statistic is yT3 = mean|interaction_D|: rho = **−0.0211 [−0.1034, +0.0584]**, null (same AD6 table). Quoting K21's number as "stability interaction tracks depth" would be wrong; the number itself is now fresh-verified correct **for yE** (fresh CI [+0.091832, +0.247059] matches the logged [+0.0918, +0.2471] to 4 dp — closing K21's "not re-read this session" status). K21's unexplained "62" in its n-column is not corroborated by anything read this session — flagged as unverified.
- Three-way consistency where records overlap: script 100's segments reproduce AD6's per-region table exactly (2–147: +0.167211 vs +0.1672; 148–294: +0.084324 vs +0.0843, CIs matching too) and B2c's in-range number exactly (+0.0125) — three independent code paths, same values.
---
## [Y] — Group Y: severity baseline under its own scrutiny (Y1), mechanism simulation (Y2), Nambiar code check (Y3)

Status: PASS — Y1a and Y2a executed as script 101 (pre-registered docstring, smoked at N_BOOT=N_PERM=300, full run at 10,000/10,000); Y3a executed as a fresh code-repo search with the task's "already cloned" premise corrected on record.
Time started / finished: 2026-09-26 01:20 / 2026-09-26 01:35
What I did: Wrote `scripts/101_y1_y2_severity_baseline.py` — Y1 replicates script 33's sign-flip re-derivation machinery verbatim (same imports, same `wls_line(Rs * rng.choice([-1,1], size=Rs.shape), Ss, CONCS, Vs)` draw loop, same p/centring/excess prints) with Site_Independent as the predictor, plus script 97's Holm step-down copied verbatim; Y2 is a simulation whose design was frozen in the docstring before any number existed.

### Y1 — does Site_Independent's own correlation survive its sign-flip null and the project's Holm?

Gates (all pass): G1 script-33 frame = 10,757/654, ProteinGym join keeps all 10,757/654 (its scores cover all 12,464 single substitutions); G2 rho(Site_Independent, own_e_b) = **0.06396596794067251** — exact reproduction of the S1-verified/AB2 value (tol 1e-6); G3 script 33's identity gates: all-+1 max|diff| = 2.220e-16, all−1 max|diff| = 2.220e-16. The position-bootstrap CI reproduces AB2's published **[+0.037646, +0.090564]** exactly at N_BOOT=10,000.

Sign-flip re-derivation null (signed variant only — AB2a's claim is the signed positive correlation; pre-stated):
- observed **+0.0640**; null mean −0.0001, sd +0.0096; **p < 0.0001** (0 of 10,000 draws); null-centring check: mean consistent with zero; excess over null = +0.0641 → **0% of the raw value is structural artifact** — the entire correlation exceeds the re-derivation null.
- → **SURVIVES script 33's null.**

Multiplicity (Holm step-down, script 97's algorithm verbatim, α=0.05; both families pre-registered in the docstring before the run):
- **F7** — the seven severity baselines, with Site_Independent's entry replaced by this sign-flip p (the stronger null) and the other six keeping AB2's own_p_boot = 0.0 as on disk: **7/7 survive.**
- **F5** — script 97's core m=5 with p4 (the conservative severity-gate entry, "largest own_p_boot among the seven") replaced by this sign-flip p; other four frozen at 9.41e-38 / 0.0 / 0.0 / 0.0: **5/5 survive.** Disclosed: the p4 substitution is this script's operationalization, chosen before the p was known.

**Y1 direct answer: YES — the baseline's own correlation is not mostly structural artifact.** It survives its own sign-flip re-derivation null (p<1e-4, 0% artifact) and the project's Holm correction under both pre-registered families. The critique's shape does not change via this route — but surviving this null does not make it interaction signal, because the sign-flip null only rules out the flip-derivation artifact; it cannot rule out the mechanism Y2 tests.

### Y2 — can the effect be derived? Which route: **SIMULATION** (stated explicitly, as the task requires)

Mechanism under test: scale mismatch — the monotone nonlinearity between severity and fitness that exists whenever fitness composes multiplicatively (additive in log space) while epistasis is measured on the additive scale.
- Real data: task32's `f_bar`, n = 11,344 real values, range [0.0000, 1.9354]; f_wt = median(f_bar_wt) = 0.8177. Ratio-scale assumption (needed for multiplicative composition) disclosed in the script's output.
- Pre-registered design: N_PAIRS = 10,000 pairs drawn iid with replacement from the real fitness distribution; **true model has no interaction** (f_ij = f_i·f_j/f_wt); measured epistasis on the additive scale e = f_ij − f_i − f_j + f_wt; severity-only predictor = mean normalized severity of the two singles; statistic = Spearman; identity check on the unpermuted predictor; label-permutation null.
- Results (full run): identity |diff| = 0.000e+00; **rho = +0.589823**, bootstrap 95% CI **[+0.572604, +0.606830]** (N_BOOT=10,000); permutation **p < 0.0001** (null mean −0.000060, sd 0.010071, centred). Comparator printed alongside: the real Site_Independent rho = +0.063966.
- Pre-registered verdict rule met: mechanism-only positive correlation **DEMONSTRATED**. Magnitude: mechanical |rho| is **9.2× the observed value** → the real baseline sits **inside** what mechanism alone produces.
- Rank-invariance note (printed by the script): under Spearman, any monotone transform of the *predictor* is rank-invariant — the mechanical correlation arises entirely from the severity→FITNESS nonlinearity, not from how severity is scaled on the predictor side.

**Y2 direct answer: YES** — a monotone nonlinearity between severity and fitness mechanically generates the positive severity-vs-measured-epistasis correlation on this dataset's own fitness distribution, at ~9× the observed magnitude. Combined Y1+Y2 for any write-up: the severity baseline is simultaneously (a) real — null-surviving and multiplicity-surviving — and (b) derivable from mechanism alone. Both are true; they answer different questions. It must therefore be read as measurement-scale structure, never as evidence of interaction.

### Y3 — Nambiar's released code, not just paper text

- **Premise correction (flagged):** the task says the repo was "already cloned earlier in this project" — as of this session's start it was **not** present under `data/external/`; the project's earlier evidence was raw-file fetches logged at CALIBRATION_LOG L36–48. Cloned fresh this session (2026-09-26) to `data/external/Epistasis` (6.0 MB, 32 text files).
- Fresh whole-corpus, case-insensitive search: **0 hits** for every severity-only-baseline term tried: `severity`, `site_independent`, `additive baseline`, `singleton`, `consensus`, `one-point`. (Also 0 hits for `disattenuation` / measurement-error terms — the T6c answer.)
- **Y3 verdict: no severity-only baseline appears in their released code either.** Safe phrasing for future write-ups: "not present in the paper text nor in the released `maslov-group/Epistasis` code as searched (terms listed)" — never a claim about what was run privately.

Files created/modified: `scripts/101_y1_y2_severity_baseline.py` (new); `data/processed/task101_y_severity_baseline.csv` (new, 10 rows); `data/external/Epistasis/` (fresh clone this session; gitignored with the rest of `data/`). Existing files unmodified.
Anything unexpected or worth flagging:
- Y1's 0%-artifact result is the mirror image of the project's 77–82%-artifact findings (S1b): the sign-flip null centers at ~0 here, so the whole +0.064 is excess. Correct reading — printed in the script itself — is narrow: it rules out the flip-derivation artifact only; Y2 shows the mechanism channel is wide open, which this null cannot touch.
- In F5's printed table, AD1's 9.41e-38 appears at "rank 5": that is stable-argsort tie behavior (four p-values are exactly 0.0), not an error — AD1 still faces α/1 = 0.05 and rejects, exactly as in script 97's own run.
- Y2's f_bar minimum is exactly 0.0; the script pre-registered a hard STOP if any f were negative (multiplicative model undefined) rather than clipping post hoc — no negatives occurred, nothing was clipped.
---
## [Z] — Group Z: AC3 coverage gap (Z1), test-count context (Z2), ClinVar cross-reference (Z3), email draft (Z4); Z5 = the SUMMARY below

Status: PASS — Z1, Z2, Z3, Z4 all executed; Z5 skipped as its own task (this entry's `## SUMMARY` follows immediately).
Time started / finished: 2026-09-26 01:36 / 2026-09-26 01:58
What I did: Z1 by fresh reads (AC3's full entry + the ESM-1v producer script's gates); Z2 by a two-part count whose method was printed before the counts were; Z3 as new script 102 with the threshold pre-registered in its docstring before any variant-level ClinVar data was fetched (only record count + response schema probed first); Z4 by drafting and saving, not sending.

### Z1 — did AC3 cover the five ESM-1v deltas?

**No.** Read fresh:
- AC3's entry is `DEEPDIVE_LOG.md` L1460–1680, "Numerical precision check: fp32/fp64/batch/CPU rescore of delta_ESM". Its AC3a producer facts come from `scripts/10_score_all_variants_esm2.py:49` (WT background) and `scripts/11_score_a222v_background_esm2.py:59` (A222V background) — both **ESM-2** (esm2_t33_650M_UR50D; batch 1; fp32 default; mps device).
- Grep of the entire entry (L1460–1680) for `esm1v` / `esm-1v` case-insensitive: **0 mentions**.
- The five ESM-1v member deltas (`data/processed/task_AC4_esm1v_member{k}_scores.csv`) are produced by `scripts/86_ac4_esm1v_five_members.py`, which was never put through AC3's four-condition rescore. Script 86's only precision-adjacent gate is R5's three-way parity at `max|·| < 1e-3` **on the ESM-2 scoring path** ("fp32 device/op-order tolerance, same 1e-3 as script 70's G3 precedent", script 86 L110–114) — that measures artifact-vs-rescore agreement for ESM-2, not fp32/fp64/batch/device noise on the ESM-1v deltas themselves.
- **Gap, stated plainly:** the numerical margin of the five ESM-1v deltas — the quantities underpinning T3's rel_delta (ρ = −0.303378), the five-seed reliability family (T5's +0.084365), and the disattenuation's input variance — is **unquantified by AC3's standard**. AC3's finding that ESM-2's fp32-vs-fp64 differences were far below signal, plus script 86's identical fp32/mps machinery, make the same conclusion *plausible* for ESM-1v — but that is an analogy, not a measurement, and must not be written as measured.

### Z2 — count of every distinct statistical test across full project history (no correction re-run)

Method, **printed before counting** (the command output in this session is the record): (A) scripts implementing ≥1 formal inferential test = `grep -lE 'position_cluster_bootstrap|N_PERM|holm\(|binomial|sign-?flip' scripts/*.py` (category counts overlap and are explicitly not summed); (B) reported test-instance lines = `grep -rEc '[^a-z_]p(_boot|_perm|_one|_two|_exceeds|_value|_adj)? ?[=<>]' docs/tasks/*/[A-Z]*_LOG.md RESULTS.md` — an **upper bound**: a re-quote of the same test in a later entry counts again, and neither number is a count of distinct hypotheses.

Results:
- **(A) 53 of 95** numbered scripts implement ≥1 formal test. Categories: position-cluster bootstrap **38**, permutation null (`N_PERM`) **28**, sign-flip **26**, `holm(` **2**, binomial **3**.
- **(B) 537** reported test-instance lines total: DEEPDIVE 145, OVERNIGHT 102, CLOSEOUT 72, DISATTENUATION 67, RELIABILITY 67, SESSION 43, CALIBRATION 15, FINAL_CLOSEOUT 9, MIGRATION 7, MTHFR_RESULTS_LOG 3, FOLLOWUP 3, RESULTS.md 4.
- Context, stated plainly: the project's correction covers **m = 5** (m = 8 in the sensitivity family) — 5 to 8 corrected members set against 53 test-implementing scripts and 537 reported test lines across four rounds of work. Holm was applied to one family in one round; the large majority of the 537 were never multiplicity-corrected. Per the task, **no correction was re-run** — a properly corrected family needs its own pre-registration, which this count deliberately does not supply.

### Z3 — ClinVar cross-reference (threshold pre-registered before fetch)

Design in `scripts/102_z3_clinvar_crossref.py`'s docstring, written after only two probe calls (record count 1,078 + one-record schema; no variant-level data, no classifications, no outcomes):
- **Fetch budget:** 4 NCBI E-utilities requests (1 esearch + 3 esummary batches), all 1,078 MTHFR records taken whole — server-side filters deliberately *not* trusted (probe showed ambiguous errorlist behavior; whole-gene fetch is cheap). Actual: **4,215,521 bytes (4.22 MB)**, saved `data/external/clinvar/clinvar_mthfr_esearch.json` + `clinvar_mthfr_esummary.json`; the script is cache-on-rerun (re-runs refetch nothing).
- **Threshold (pre-registered):** "meaningfully differently scored" = |delta_esm| ≥ **0.1182** = one population SD of delta_esm over the 11,344-row manifest — source `task_delta_esm_noise_floor.csv` `sd_delta_esm = 0.11821991945148934`, independently recomputed from the manifest identical to 17 digits, both **before** any variant-level fetch; script re-checks at run time and exits if the value moved. Sensitivity counts at 0.5 SD / 2 SD pre-stated, descriptive only. delta_esm = `esm2_score_a222v_bg − esm2_score` is exactly the background-aware minus background-naive score difference for that variant.
- **Classes (pre-stated):** PRIMARY = VUS ("Uncertain significance") + "Conflicting classifications of pathogenicity" (legacy spelling "Conflicting interpretations of pathogenicity" mapped in advance); CONTEXT = Pathogenic / Likely pathogenic (reported, no decisions attached).
- **Matching (pre-stated):** parse `p.<WT3><pos><MUT3>` (parentheses tolerated) → 1-letter triple; matched iff the triple is a manifest key, so transcript/isoform numbering mismatches fail to match and are counted, never silently dropped.

Filtering accounting (every step's n): 1,078 fetched → classes 315 primary / 205 context / 558 other → 763 without a parseable missense p. change (verified separately: includes exactly **51 nonsense `p.*Ter`**) → 315 parseable missense → **299 match the atlas manifest** (wt+pos+mut exact).

Answer at the pre-registered threshold:
- **VUS + conflicting in our measurement set: 236 → 34 with |delta_esm| ≥ 0.1182 (1 SD)** — plus 97 at ≥0.5 SD, 5 at ≥2 SD.
- Context P/LP in our set: 29 → **7 ≥ 1 SD**.
- Largest primary-class shifts: V194L (VUS, delta_esm **+1.2512** ≈ 10.6 SD), A220V +0.6883, V218L +0.3928, T227K +0.3056.
- Saved: `data/processed/task102_clinvar_atlas_overlap.csv` (299 rows).
- Disclosed limits (printed by the script): classification is submitters' criteria, not our data; non-match ≠ absent from ClinVar (numbering/isoform or non-missense); the threshold says the background choice moves the score by ≥1 SD — it does **not** say which score is right.

### Z4 — email drafted and saved, not sent
`docs/tasks/disattenuation-and-ledger/EMAIL_DRAFT_nambiar_severity_baseline.md` — asks the exact two-way question (run-and-not-reported vs genuinely-not-considered), states we accept either answer, discloses precisely what we searched (preprint PDF zero-hit list + released-repo zero-hit terms). **Not sent** — no mail was transmitted by this session.

### Z5 — skipped as its own task; `## SUMMARY` follows below.

Files created/modified: `scripts/102_z3_clinvar_crossref.py` (new); `data/processed/task102_clinvar_atlas_overlap.csv` (new); `data/external/clinvar/*.json` (raw fetch, gitignored with the rest of `data/`); `docs/tasks/disattenuation-and-ledger/EMAIL_DRAFT_nambiar_severity_baseline.md` (new draft). Existing files unmodified.
Anything unexpected or worth flagging:
- **AGENTS §5 check performed on a suspicious coincidence:** primary-class records and parseable-missense records are both exactly **315** — verified to be different sets (independent recount: primary ∩ valid-missense = 247; 68 primary records have no missense p. change — intronic VUS; 68 missense records are benign/other classes; the 51 excluded tokens are all `Ter`). Not a shared-counter bug; arithmetic recorded here.
- ClinVar is a public, moving database: the 1,078-record count is a 2026-09-26 snapshot; the cached JSON is the frozen evidence for this number (236/34).
- The 4.22 MB fetch is the session's only outbound data pull; nothing else was fetched for Z.
---
## SUMMARY

*Self-contained by design (task Z5): a reader who has read nothing else should be able to understand the state of the project from this section alone. Where this SUMMARY conflicts with the five do-not-touch files, this SUMMARY wins and the conflict is flagged explicitly at the end.*

### READ THIS FIRST — the review's one-sentence question (T1)

**ESM-2's −0.088118 is not an unusually large draw from the ESM-1v seed distribution — it is a different distribution entirely:** Meta's own model card documents ESM-2 (`esm2_t33_650M_UR50D`, UR50/D **2021_04**, Lin et al. 2022) and the five ESM-1v seeds (`esm1v_t33_650M_UR90S_1-5`, UR90/S **2020_03**, Meier et al. 2021) as different corpora (UniRef50 vs UniRef90, different snapshot), different training runs, and separate releases; shared architecture/parameter count is not shared training distribution. The outlier question is therefore moot, cross-family reliability borrowing (using r_delta = 0.084365 from the ESM-1v family for ESM-2) is an assumption, not a licensed inference — and the n=5 rank test could never have distinguished these by itself (exact two-sided p = 0.333; the five member rhos are −0.020573, −0.040820, +0.013434, −0.026572, −0.003409, mean −0.015588, sd 0.021052).

### Task status across the whole task doc

- **Completed:** S1a, S1b; S2a (with one blocked portion below), S2b; T1–T6; U1; V1; W1, W2; X1, X2; Y1, Y2, Y3; Z1, Z2, Z3, Z4.
- **Blocked:** S1c and S2c — the referenced "v3" does not exist anywhere in this workspace (searches quoted in the entries); replacement sentences were supplied for the user to apply wherever v3 actually lives. S2a's "Parts 9–14" — `MTHFR_RESULTS_LOG_PART2.md` does not exist (never committed, per `git log --all`); flagged, not substituted.
- **Skipped by task design:** Z5 (this SUMMARY).
- **Deliberately not re-run:** the ensemble-mean run (RELIABILITY `[A1]`, ρ = −0.028508 — retrieved and quoted instead) and the Nambiar severity-only-baseline search (T6 — existing evidence read instead).

### S1 in one sentence (sign/target resolution)

The apparent sign contradiction is **two different statistics sharing one target vector**: ProteinGym's severity table correlates each model's **raw WT-background score** with e.b (hence all positive, incl. ESM2_650M **+0.085391**), while the headline correlates the **background-shift** `delta_esm = score[A222V bg] − score[WT bg]` with the same e.b (**−0.088118** own / **−0.070705** published) — same model, same target, opposite signs, entirely a statistic difference; every correlation sentence must name (statistic, target, signed/absolute, n) and never quote "ρ = −0.088 vs e.b" bare.

### S2's three dropped findings and their status

1. **H1a reversal (A222V shifts more than severity predicts):** original wording unverifiable (PART2 absent); substance re-verified — at 9 backgrounds the A222V residual is NOT supported (+0.00954, CI includes 0), at 31 backgrounds it IS supported and **opposite in direction** to the reversal claim (+0.02121 [+0.00465, +0.03934]) → verdict CONTRARY-TO-H1A; sits alongside the reliability framing unaddressed (any single-checkpoint shift pattern is weakly seed-reproducible — report with that caveat).
2. **Rank-vs-MAE digest:** verified from source, never carried into any write-up (that is why it was "dropped"); rank half demoted (C1b non-background-specificity + exogenous-anchor collapse), MAE half stood (C2c verdict holds), disattenuation r_dis −0.110413 independently re-confirmed by A2 — the original log's open question ("unqualified vs qualified final claim") is answered: **qualified**, per RESULTS's corrected conclusion.
3. **Additive-null MAE result (original §6.2/6.3):** **verified as a descriptive statistic** (re-verified by D1b UNCHANGED-HOLD and C2c) but **weakened as an ESM-2-specific claim** — the corrected conclusion subordinates it to "a property of how well any WT-arm-informed signal predicts an A222V-arm-derived target, close to tautological once seen clearly"; sits alongside the reliability framing unreconciled — stated plainly, not papered over.

### T5's two numbers, side by side (the money figure)

Same frame (10,757 rows / 654 positions), same convention (median of 10 pairwise member Spearmans, script 86 R7), same run:

| cross-seed agreement across the 5 ESM-1v checkpoints | point | 95% CI |
|---|---|---|
| RAW WT-background scores (wt_logodds) | **+0.882637** | [+0.869559, +0.881465, +0.891790] |
| background-induced DELTAS (deltas) | **+0.084365** | [+0.052159, +0.086318, +0.122589] |

Ratio **10.46×**, CIs nowhere near each other, no measurement-error model involved: the seeds agree almost perfectly on what a score *is* and barely at all on the difference between backgrounds — the instability is introduced by the subtraction itself.

### V1's direct answer (the three-round effective-n question)

The resampling unit is the **position**: `scripts/lib/stats.py` L51–52 draws `size=len(clusters)` = **654 positions** with replacement and rows travel with their positions; rows are never drawn independently (the sign-flip companion is a re-derivation null, ±1 per cell, not a resampler). Consequently **neither naive Fisher floor applies**: the row-level 0.027009 assumes 10,757 independent observations (pseudoreplication), and the 654-point Fisher plug-in 0.109364 is a different statistic *and* is empirically falsified by AA4 (it predicts power 0.2475 at ρ=0.05 where the same position-cluster pipeline measured 1.00). The floor that fits this pipeline is **AA4's empirical ≤0.05** (corroborated by design-effect 0.042727 from ICC 0.0973, k̄=16.45, and null-SD 0.026–0.032), and |−0.088118| sits ~2× above it → **"we had the power to detect this" survives in AA4's empirical form only** — never cite n = 10,757 for it, and never cite 0.109.

### Y1's verdict

Site_Independent's own +0.063966 correlation **survives**: script 33's sign-flip re-derivation null gives p < 0.0001 with a null centered at ~0 (observed +0.0640, null mean −0.0001, sd 0.0096) → **0% of the raw value is structural artifact**, and it survives the project's Holm step-down under both pre-registered families (**7/7** in F7, **5/5** in F5). But Y2's pre-registered simulation on the real f_bar distribution shows mechanism alone — multiplicative truth measured on the additive scale — mechanically produces **ρ = +0.589823 [+0.572604, +0.606830], p < 0.0001**, i.e. **9.2× the observed value**: the severity baseline is simultaneously *real* (null- and multiplicity-surviving) and *derivable from mechanism alone*. Correct write-up phrasing: it is measurement-scale structure, never evidence of interaction — both statements are true and they answer different questions.

### X1's leverage-sensitivity result

Pooled rho(yE, Neff) = **+0.171422 [+0.091832, +0.247059]** on all 586 positions **collapses to +0.012518 [−0.082236, +0.106433], p = 0.789** when the 124 highest-Neff positions (neff > region-4 max 1213.1) are dropped (n = 462 kept — exactly B2c's expectation and, to 4 dp, B2c's published number). The decile shape explains it: flat through deciles 1–5 (~0.052–0.064), elevated with a top-decile upturn (0.1150 in decile 10). yT1 is flat at every scope (rho +0.006928, p = 0.87; its positive OLS slope is non-monotone — a step out of decile 1 — and is flagged, not resolved by picking a side). **Verdict: the direction claim (ESM tracks depth, ThermoMPNN doesn't) holds; the smooth monotone dose-response reading does not.**

### What was refuted, what survived, what stays uncertain

**Refuted / dropped this round:**
- W1's premise: |e.b| does **not** decay with distance from 222 — it **grows** (+0.177935 [+0.141675, +0.212828]), and the synonymous noise floor grows too (+0.081816 [+0.000373, +0.161996]) → distance-growth is not interaction evidence; the contact-range-concentration hypothesis is unsupported (B1 +0.069 ns; the pooled negative lives in the far band: B3 −0.051139 [−0.085157, −0.017061], p = 0.0042).
- X2's domain-edge hypothesis: the depth effect breaks at the **region-4 edge 474|475** (only segment whose CI excludes 0: −0.237283), not at domain edge 337|344 (segment 344–474 is exactly flat: −0.001945, p = 0.98); the two boundaries are 43 residues apart and do **not** coincide (tolerance was 5).
- X1's smooth dose-response (leverage collapse above).
- "The headline lands inside Nambiar's ~0.26–0.38" comparison (T6): those are raw Pearson r values, ours is a rank ρ — the sentence is **dropped**; the sanctioned replacement compares their Table S2 raw values 0.0918/0.1770/0.1333 against |ρ| = 0.088.
- Reading the severity baseline as interaction evidence (Y1 + Y2: derivable from mechanism).
- Treating ESM-2 as an outlier of the ESM-1v family (T1: different distribution).

**Survived:**
- The headline anchor: ΔESM × own_e_b ρ = **−0.088118**, position-cluster CI [−0.117556, −0.058828], above AA4's empirical floor.
- W2: B4b's null was tested on ThermoMPNN-D's **native, non-degenerate** `interaction_D` (code-quoted: script 77 L47–60 / L420–421), residual +0.0097 [−0.0221, +0.0410] p = 0.5382 vs original +0.0154 [−0.0166, +0.0465] → the "confirmed genuine absence of stability-mediated signal" claim needs **no walk-back**.
- T5's 10.46× base-vs-delta reliability gap; T3's disattenuation CI **[−0.440395, −0.192728]** (delta-only point −0.303378) / **[−0.555203, −0.242329]** (fully, −0.380315) — wide, direction stable, quote the interval never −0.30 bare.
- U1: AA1 (script 73) and AA7 (script 74) both use script 33's sign-flip re-derivation as primary — the convention is consistent, with I1's permutation gate as the deliberate contrast.
- V1's power claim, in AA4's empirical form only.

**Uncertain / open:**
- ESM-1v deltas' numerical precision (Z1): never put through AC3's fp32/fp64/batch/device grid — unquantified by that standard; the ESM-2 analogy is plausible but is an analogy.
- T1's cross-family borrowing: unlicensed but also unrefutable by measurement (ESM-2 has no seed family to measure).
- S2b items (i) and (iii) sit alongside the reliability framing **unreconciled head-on** — stated, not resolved.
- Multiple-testing context (Z2): **53/95 scripts implement a formal test; 537 reported test-instance lines vs 5 (8) corrected members** — no correction was re-run, and a corrected family would need its own pre-registration.
- S1c/S2c: the "v3" sentence still needs a home (replacement text supplied).

**Recommended statements for the final write-up:**
1. Name (statistic, target, signed/absolute, n) for every correlation — the S1 convention.
2. Lead with T5's 10.46× and T1's distribution verdict before any disattenuated number; label the disattenuation as ESM-1v-family with the borrowing assumption explicit; quote its CI, never the point bare.
3. Cite power only to AA4's empirical floor; strike any "n = 10,757" justification.
4. Describe the severity baseline as real-but-mechanistic (Y1+Y2), and use the Table S2 comparison instead of "lands inside their range" (T6).
5. Region-4 depth claims must carry both qualifications: leverage (X1) and boundary specificity (X2).

### Conflicts with the five do-not-touch files (K12/K21 corrected in place 2026-09-26 by true-final-closeout G3c; the remaining conflicts still flagged, not edited; this SUMMARY wins per the task doc)

- `DISATTENUATION_LOG.md` **K12 — CORRECTED in place 2026-09-26 (G3c):** the ledger row previously quoted AD4's original CI as [+0.0039, +0.0271] — a figure that exists in no source; every source (DEEPDIVE L2327–2336, RELIABILITY L1036/L1069, script 96, reproduced by script 96's G2) says **[−0.0166, +0.0465]**, which is what the row now reads. Cite [−0.0166, +0.0465].
- `DISATTENUATION_LOG.md` **K21 — label CORRECTED in place 2026-09-26 (G3c):** the row was labeled "AD6 depth × interaction_D" while its number is AD6's **rho(yE, Neff)** (yE = position-mean |delta_ESM|); AD6's actual interaction_D×depth statistic is −0.0211 [−0.1034, +0.0584], null. The number is fresh-verified correct for yE; the row now carries the correct label and statistic name (its unexplained "/62" in the n-column remains flagged as unverified).
- `MTHFR_RESULTS_LOG.md` §5.2's published-side label (−0.088 where the published value is −0.070705) and `RESULTS.md` L150's unsourced "0.983" remain as previously flagged.

### The single most important thing to look at first

**T1, at the very top of this summary:** the flagship disattenuation chain (−0.30 to −0.38) rests on reliability measured in the ESM-1v seed family and then borrowed across a distribution boundary that Meta's own model card puts between two different corpora and releases — requalify that chain before anything else in the write-up, and re-order the narrative around T5's 10.46× gap, which needs no measurement-error model at all.
