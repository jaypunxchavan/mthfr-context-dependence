# VERIFIED_FINDINGS_TABLE — ground truth for the human-facing write-up

Compiled 2026-09-25 (task X2 of `FINAL_CLOSEOUT.md`). One row per
headline or near-headline numeric result referenced in this project's
own SUMMARY sections (the six logs named in X2a — OVERNIGHT_LOG,
comparators SESSION_LOG, CLOSEOUT_LOG, DEEPDIVE_LOG, CALIBRATION_LOG,
RELIABILITY_LOG — plus FOLLOWUP_LOG and MIGRATION_LOG, which also carry
`## SUMMARY` sections with headline numbers and were included for
completeness; CALIBRATION_LOG has no `## SUMMARY` of its own, its N1–N4
rows are included because other logs' summaries reference them).

**Verification discipline (X2b).** Every number below was re-read from
its actual source file on 2026-09-25 before this table was written —
from the producing entry's verbatim output line, or (for numbers whose
deepest source is a CSV) from the CSV itself read directly. Nothing was
copied from a prior summary, and nothing was taken from this session's
memory of earlier conversation. Where a SUMMARY's shorthand differs
from what the source file says, the source file won and the difference
is flagged in the Status column and in the discrepancy list below.

**Verification outcome.** No undiscovered SUMMARY-vs-source numeric
mismatch was found. Every SUMMARY number checked against its entry or
CSV matched (to the rounding the SUMMARY used). The four known
contradictions in this project's history were re-confirmed in place
(S1's published-rho label, N4's IMPROVED, AD5's title, I1's three-site
gate) — all already flagged in their own logs; none silently resolved
here.

**Status legend:** CONFIRMED = stands, not contradicted by any later
run · CONFIRMED (caveat) = stands with a qualifier another log adds ·
SUPERSEDED = a later result took over its role (numbers still stand as
the frozen run's output) · CORRECTED = a later correction changed the
number or framing · FLAGGED = contradiction recorded against another
log · BLOCKED = never completed, open decision · META = log bookkeeping,
not a scientific result.

Log short-names: OV = `docs/tasks/review-triage/OVERNIGHT_LOG.md`,
SESS = `docs/tasks/comparators-and-consolidation/SESSION_LOG.md`,
CLOSE = `docs/tasks/closeout-u2-u3-u4-v5/CLOSEOUT_LOG.md`, DEEP =
`docs/tasks/detection-floor-and-mechanism/DEEPDIVE_LOG.md`, CAL =
`docs/tasks/calibration-and-publication-readiness/CALIBRATION_LOG.md`,
REL = `docs/tasks/reliability-and-decompositions/RELIABILITY_LOG.md`,
FOLLOW = `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md`, MIG =
`docs/tasks/site54-and-script50-migration/MIGRATION_LOG.md`.

| # | Log | Finding (one line) | Exact number(s), verbatim | Exact source (file + line / task ID) | Status |
|---|-----|--------------------|---------------------------|--------------------------------------|--------|
| 1 | OV | Headline anchor: delta_ESM vs e.b on the 10,757-row set (published e.b) | −0.07070516222228716, CI [−0.09797203801943542, −0.0438395299914251], p=0.0, n=10757 | `data/processed/task32_delta_esm_primary.csv` L5 (read directly 2026-09-25); OV L26 | CONFIRMED; OV SUMMARY's shorthand "ρ = −0.088 (published e.b)" is CORRECTED by OV L1880 (own e_b is −0.088) |
| 2 | OV | Headline anchor on own e_b | −0.08811806424891734, CI [−0.1173334458953319, −0.05951138449511738], p=0.0, n=10757 | `data/processed/task32_delta_esm_primary.csv` L6 (read directly); OV L26, L590 | CONFIRMED |
| 3 | OV | A2b n-chain reconciliation | 13,134 → 11,902 → 11,901 → 11,344 → 11,113 → 10,757, "each step attributable" | OV L157 (A2b verdict); per-step rows L149–156 | CONFIRMED |
| 4 | OV | C1c BLOSUM62 matched comparator | α=0.2559; gap = +0.0691, CI [+0.0142, +0.1146] | OV L446 | CONFIRMED (method limitation: Grantham gap UNMATCHED, α pinned at bisection floor — OV L1866) |
| 5 | OV | C2b fold-seed sensitivity of 6.2 | mean +0.0004980, sd 0.0000528, min +0.0003966, max +0.0006214, 0/50 flips; sd = 0.22× published CI half-width; seed-0 = +0.0005335 | OV L532–533, L539 | CONFIRMED |
| 6 | OV | C3a reliability + oracle ceiling | own e.b reliability 0.6363, published 0.6193; oracle pooled +0.0366 CI [+0.0309, +0.0424]; high stratum +0.0521 CI [+0.0436, +0.0613]; disattenuation r_dis −0.110413, ratio 1.2530 vs 1.25 bar | OV L594–595, L645, L627–628 | CONFIRMED (caveat: "meets the bar narrowly"; oracle circular — DEEP L34) |
| 7 | OV | D1a winner's-curse: SE gradient across |e.b| terciles | D = +0.0461 CI [+0.0396, +0.0535] (2000/2000 valid, 654 positions); ratio 1.654 (+65.4%) | OV L879–880 | CONFIRMED |
| 8 | OV | D1b EB-shrunken high-stratum MAE (UNCHANGED-HOLD) | +0.001851 CI [+0.000987, +0.002706]; mean SE 0.1166 → 0.0788 (gradient inverts: EB-low 0.1045) | OV L904, L932 | CONFIRMED |
| 9 | OV | D1c EB strata vs C1 effect-size floor | R = 1.184 CI [1.025, 1.371]; ratio-to-floor 1.064 CI [0.948, 1.207]; cut23 = 0.1830 vs SE-tercile spread 0.1720 | OV L965, L977, L980 | CONFIRMED |
| 10 | OV | E1a disagreement effect sizes DOWNGRADED at 0.10 floor | 4 of 7 CI-passing groups below 0.10 (0.078, 0.097, 0.062, 0.069); bands: 0.05→7/7, 0.10→3/7, 0.25→1/7 | OV L658, L712, L717 | CONFIRMED (0.10 floor itself post-hoc, disclosed at L664) |
| 11 | OV | F1a spline-control reframe of 6.3 | linear −0.0590 CI [−0.0851, −0.0330] p=8.888e-06 r²=0.0315; binned +0.0537 CI [+0.0352, +0.0723] p=1.41e-08 r²=0.5239; quadratic binned +0.0271 | OV L1017–1018, L1027 | CONFIRMED |
| 12 | OV | F1b |e.b| tail exclusion | p10 = 0.000000, p90 = 1.337150; kept = 9120 of 10,757 | OV L1050, L1082 | CONFIRMED |
| 13 | OV | F2a within-region (range-restriction) test | identity 0.000e+00; within-region pooled rho +0.1897 CI [+0.1597, +0.2188] n=10757 pos=654; published +0.1910, \|delta\|=0.0013 | OV L1150, L1157 | CONFIRMED |
| 14 | OV | G1 global-vs-specific control | cross-fitted isotonic R² = 0.1535436240252529 (printed 0.1535); residual rho −0.1455 CI [−0.1761, −0.1131] sign-flip p<0.0001 null mean +0.0001; paired magnitude diff +0.0748 CI [+0.0585, +0.0912]; reconciliation vs script 32 \|diff\|=6.94e-17 | OV L1184, L1193, L1196, L1201; CSV cross-check REL L166, L156 | CONFIRMED |
| 15 | OV | H1a A222V substitution severity | S(A222V\|WT) = −5.200276; z-score vs all = +0.502; rank 16/19; 68.04% at least as deleterious (p10 −12.80 / p90 −1.19) | OV L1230, L1233; rank/68% at L1871, L1881 | CONFIRMED; S2's "strongly deleterious" label FLAGGED, H1a's distributional reading governs (OV L1881) |
| 16 | OV | H1b ortholog conservation at 222 | PRIMARY n=3, V=0.000, A=1.000; SECONDARY n=12, V=0.000, A=0.917 | OV L1262, L1264, L1271 | CONFIRMED (small-n, sampling-bias caveat L1268) |
| 17 | OV | H2a proximity/locality | reproduce published −0.298214 (\|diff\|=5.55e-17); Cα-3D −0.2443 CI [−0.2982, −0.1820]; FAD −0.2625 CI [−0.3172, −0.2016] (n=9633 pos=588); D1 CI [−0.0036, +0.0676]; D2 CI [−0.0187, +0.0449] | OV L1293, L1296, L1297; D1/D2 CIs OV L1871 | CONFIRMED (MIXED-INDETERMINATE) |
| 18 | OV | H2b local-structure union | primary union rho +0.0507 CI [−0.0432, +0.1348] p=0.307000 n=776 pos=48; 3D-only component +0.1191 CI [+0.0066, +0.2166] p=0.042000 n=363 pos=23; FAD component −0.0574 (CI crosses 0) | OV L1326, L1327, L1336 | CONFIRMED (INCONCLUSIVE-POWER; secondary = lead, not finding) |
| 19 | OV | H3a asymmetric agreement + anti-enrichment | agree-rescue +0.6233 CI [+0.5932, +0.6533]; agree-worse +0.3268 CI [+0.2978, +0.3550]; asymmetry +0.2965 CI [+0.2422, +0.3505]; AUC 0.4525 CI [0.4374, 0.4688] | OV L1362–1365 | CONFIRMED |
| 20 | OV | H4a folinate-condition replication of 6.3 | HIGH@12: +0.00227 CI [+0.00144, +0.00308] n=3461 pos=601; grid 25:+0.00160, 100:+0.00303, 200:+0.00510 (all CIs >0) | OV L1413, L1434, L1435 | CONFIRMED |
| 21 | OV | J2a 150M-vs-650M delta replication | rho +0.0978 CI [−0.0444, +0.2275] p=0.1540 n=1900 pos=100; sign agreement 53.11% of 1900 rows | OV L1680, L1682 | CONFIRMED (SIZE-SENSITIVE — conclusions are 650M-checkpoint-scoped, OV L1692) |
| 22 | OV | J2a extrinsic×intrinsic independence | rho −0.0057 CI [−0.0345, +0.0209] p=0.6660 n=10757 pos=654; fitness-partial −0.0964 CI [−0.1197, −0.0716] p=0.0000 | OV L1666, L1668 | CONFIRMED (INDEPENDENCE-NOT-REJECTED) |
| 23 | OV | J4a FDR of the z=3.76 threshold | FDR_hat = 0.91–1.00 at every cutoff 2–10; at 3.76: 0.9312; syn 116/570; missense 2351/10757 | OV L1724, L1736, L1729 | CONFIRMED (NO-SUSTAINED-C-IN-GRID; no usable threshold exists) |
| 24 | OV | J4b SE-miscalibration variation | regions: 2.54 (r2, CI [2.08, 3.00]) to 5.16 (r1, CI [4.34, 6.15]); max/min = 5.162/2.537 = 2.03 > 2; fitness terciles 3.44 CI [3.05, 3.83] vs 3.55 CI [3.11, 3.99]; low tercile n_syn=11 | OV L1777–1778 | CONFIRMED (NEEDS-TO-VARY; margin 2.03 vs 2.00 disclosed; pooled 3.7586 qualification at L1882) |
| 25 | OV | K1a conditional-damaging flag vs background | n=1,462 (522 positions); WT 0.9501 CI [0.9333, 0.9657] vs A222V 0.9487 CI [0.9310, 0.9645]; Δ = −0.0014 CI [−0.0042, +0.0000] p=0.7250; all-missense baseline 95.3% | OV L1804, L1819, L1820 | CONFIRMED (flag near-saturated; background moves nothing) |
| 26 | OV | I1 GB1 three-site gate (frozen run) | pooled rho +0.4467 n=570, 3 sites, K=10; within-site null mean +0.3880 sd 0.0532 (does NOT center on zero); one-sided p = 0.1398; cluster CI [+0.2787, +0.5793]; gate_pass = 0 | OV L817, L819, L820, L821 | SUPERSEDED as the gate verdict by MIG (Q1 four-site PASS, #101) and FOLLOW (L1c power, #98); numbers stand as the frozen 3-site output |
| 27 | OV | OV log tally | 47 entries; 43 executed; 4 SKIPPED (I2a, I3a, G2a, K2a); 0 BLOCKED | OV L1855, L1858–1860 | META |
| 28 | SESS | U5 model-robustness: 150M delta | rho +0.0978 CI [−0.0444, +0.2275] p=0.1540 SIZE-SENSITIVE; summary table `task_U5_model_robustness_summary.csv` (6 rows); only ESM-2 650M produced e.b correlations | SESS L1933, L2194; SUMMARY L2979–2981 | CONFIRMED |
| 29 | SESS | V2 ThermoMPNN table build | deliverable 10,141 rows; dropped 1,203 = 1,046 at 59 unresolved positions + 157 at 9 construct-vs-canonical positions ([429, 594, 645–651]) | SESS L2349, L2307; breakdown quoted DEEP L3062 (SESS L2340) | CONFIRMED |
| 30 | SESS | V3 ddG(A222V) | −0.0439 (model output units; SSM row resi 222) | SESS L2378 | CONFIRMED |
| 31 | SESS | V4 headline ThermoMPNN-vs-e.b | rho −0.0733 CI [−0.1021, −0.0437] p=<0.0001 n=9595 (pred_eb vs own e.b) | SESS L2406 | CONFIRMED (survives AD5 controls/AD7 dimer/AD8 joint; B1 control-set caveat applies to sign interpretation) |
| 32 | SESS | V5 side-by-side ESM-2 vs ThermoMPNN | ESM-2 delta_ESM −0.0881 CI [−0.1173, −0.0595] n=10757; ThermoMPNN additive −0.0733 CI [−0.1021, −0.0437] n=9595 | SESS L2441–2442 | CONFIRMED |
| 33 | SESS | V6 region-4 reversal (Thermo vs ESM) | region 4 (475–656): Thermo rho −0.1237 CI [−0.1751, −0.0716] n=2860 vs ESM-2 +0.0103 CI [−0.0365, +0.0568] | SESS L2473, L2515 | CONFIRMED |
| 34 | SESS | W1/W2 30-background severity scan | 30 backgrounds; severity span [−18.007029, +4.070509] (A222V −5.200276 inside); scoring 2,051.2 s = 34.2 min ≤ 90-min budget; t1 = 61.7 s; drift 61.7 → 75.1 s (+22%) | SESS L2575, L2641, L2645–2646 | CONFIRMED |
| 35 | SESS | W3 denser-design M1d change | new residual +0.02121 CI [+0.00465, +0.03934] (CI excludes 0) vs original +0.00954 CI [−0.00573, +0.02640]; residual CIs overlap [0.0047, 0.0264]; new Pearson −0.422897 CI [−0.551945, −0.230902] vs original −0.601 | SESS L2746, L2742, L2759, L2694, L2771 | CORRECTED (M1d verdict CHANGES: NOT SUPPORTED → CONTRARY-TO-H1A; "resolution, not reversal" per SESS L2756–2759; Pearson weakens — reported, not smoothed, L2779–2781) |
| 36 | SESS | W4 denser-design M1e | new Spearman −0.519 CI [−0.635, −0.388] vs original −0.467 CI [−0.583, −0.067] | SESS L2747, L2744 | CONFIRMED (strengthens; secondary Pearson weakens −0.601 → −0.423, both exclude 0 — SESS L3008) |
| 37 | SESS | Group X index/audit meta | INDEX.md 11 files, 3 with `## SUMMARY`, 6 dirs (L2799); OPEN_ITEMS 38 rows across 5 logs (L2845, L2858); 27/100 processed CSVs orphan (L2945) | SESS L2799, L2845, L2858, L2945 | META |
| 38 | SESS | Session housekeeping | HEAD `f6c2686` (1 file, 328 insertions) verified via `git show --stat` + reflog | SESS L3034 | META |
| 39 | SESS | T2b/T2c FAIL, blocked items | M3 gate: "WT consensus at only 1/4 mapped columns (need >=3)" → EXIT=1; U2: 0.587 s/seq (BATCH=16) ⇒ ~167 min > 2 h; U3: ESM-1v weights 7,828,635,339 B > 3 GB; U4: `SaProt_650M_PDB.pt` = 2,606,464,143 B PASSED size, blocked on preprocessing clause | SESS L1738/L1785, L1990, L2036, L2137, L2168 | STATUS: T2 FAIL (no post-hoc revalidation); U2-full/U3/U4 BLOCKED (U3's size number later re-verified in CLOSE #44) |
| 40 | CLOSE | Z3f SaProt score stage | 585s on MPS (rc=0); `task_Z3f_saprot_scores.csv` = 11,940 rows (596 positions × 20 alts); all gates True (G3 = 0.00e+00); excluded 1,017 of 10,757 at 59 frozen positions; phase5-absolute 1,046 MATCHES V2's figure | CLOSE L1750, L1804, L1839–1841, L1829 | CONFIRMED |
| 41 | CLOSE | AC4 five-member runtimes/sizes | 668 / 850 / 850 / 876 / 861 s (worst = 14.6 min of 90-min budget); size gate 2,609,603,341 B each; 12,446 rows/member; distinct md5 each | CLOSE L2205, L2294, L2148, L2165 | CONFIRMED |
| 42 | CLOSE | AC4 R5 three-way parity | max\|b−a\| = 1.776e-15 at (100, 'H'); max\|c−b\| = 4.482e-05 at (429, 'R'); tol 0.001 | CLOSE L2132–2133 | CONFIRMED |
| 43 | CLOSE | AC4b arithmetic arm (checkpoint = model + 2 Adam moments) | 7,828,635,339 / 2,609,426,136 = 3.0001 ∈ [2.99, 3.01] → PASS | CLOSE L2146, L2215 | CONFIRMED (supersedes DEEP's AC4b BLOCKED state, #61) |
| 44 | CLOSE | AC4 R8 ensemble gate + column-identity | centered rho 0.9999999998 > 0.99 (6dp prints 1.000000); median \|Δ\| 2.97e-06, max 2.81e-05, only 9/10,757 bit-identical; PG ESM1v_single matches our member 1 exactly (rho 1.000000), members 2–5: 0.873 / 0.887 / 0.890 / 0.875 | CLOSE L2112–2120, L2303 | CONFIRMED (two independent pipelines to fp32 precision — not a duplicated column) |
| 45 | CLOSE | AC4d five seed rhos (ESM-1v) | −0.020573 / −0.040820 / +0.013434 / −0.026572 / −0.003409; mean −0.015588 sd 0.021052; CIs excluding zero 1/5 (member 2 p=0.0046); signs 1 pos / 4 neg; all five \|rho\| ≤ 0.041 | CLOSE L2189–2190, L2176, L2228–2234 | CONFIRMED — SEED-NOISE branch; scope is ESM-1v seed replicates only (REL A3, #85) |
| 46 | CLOSE | AC4d cross-member agreement levels | delta pairs: min 0.003314, median 0.084365, max 0.162631 (10 pairs); WT-score agreement median 0.883 (full-precision median 0.882637, min 0.859689, max 0.890106) | CLOSE L2188, L2226; full-precision CAL L438–439 | CONFIRMED |
| 47 | CLOSE | Z3g-h guard block | guard: `wt_aa agrees with chain-A ori_aa on all scored rows: False (9595/9740)`; 145 rows at 9 positions; tag stretch 645–651; `DBREF 6FCX A 37 644 UNP P42898 MTHR_HUMAN 37 644`; 2 engineered variants E429A, R594Q | CLOSE L1904, L1870, L1940, L2332 | BLOCKED (open decision; verified still blocked in REL C4, #95) |
| 48 | CLOSE | Standing fetch cap | ~196.3 / 200 MB used | CLOSE L2346–2347 | META / open (no further fetches without user say-so) |
| 49 | CLOSE | Window meta | window 2026-09-25 15:27 → 18:10; no commits; HEAD `abc7319` dated 2026-09-24 19:42 | CLOSE L2275, L2282–2283 | META |
| 50 | DEEP | AA4 project-own detection floor | "we could have detected rho >= 0.05; we observed -0.088."; identity max\|diff\| = 2.220e-16; type-I 0/50 false positives at rho=0; sign-flip null mean of null means +0.00002 (mean null sd 0.0101); power saturated at 1.00 at the smallest nonzero grid point (real floor below 0.05, grid cannot say where) | DEEP L382, L381, L389, L391, L393–398 | CONFIRMED (grid limitation disclosed; no adaptive points added) |
| 51 | DEEP | AA1 GB1 single-background transplant (57-row) | observed rho +0.1222, null mean −0.0004 sd +0.1408, p=0.3849 (null inside the ±0.00845 band); f(V54A) = 1.372949 | DEEP L651, L696–697, L630 | CONFIRMED — PLAIN NULL, reported untuned |
| 52 | DEEP | AA3 null-centering mechanism (3-site) | null mean +0.3880 = 86.9% of raw 0.4467 (excess 13.1%); four-site +0.2476 = 61.6% of raw 0.4018 (excess 38.4%); exact 3-site CSV values pooled_rho 0.4466626167166524, null_mean 0.3880021459076137 | DEEP L788, L834, L855–857 | CONFIRMED (feeds MIG Q1, #101) |
| 53 | DEEP | AA6 ε discrepancy resolved | eps_raw (eq. 2) = 7.399806; from figure's printed fitnesses = 7.720905; paper Fig 3D prints ε = 5; no adjustment rule triggers; companion ε = −4.5 re-derives correctly | DEEP L1016, L1025, L952; MIG L724–728 | CONFIRMED (RESOLVED as threshold identification; MIG flags it as needing the user's call before anything quotes it) |
| 54 | DEEP | AA7 second positive control GRB2 | signed rho +0.1153, permutation p = 0.0019 (null mean −0.0003 sd +0.0371) | DEEP L1179, L1209 | CONFIRMED (replicates AA1's centering-YES) |
| 55 | DEEP | AB1 ProteinGym assay existence | `MTHR_HUMAN_Weile_2021`: 12,464 singles (= 656×19); curated MSA 4,783 seqs, MSA_N_eff 646.2, category Low; 95 model-score columns (27 families); ≈11 MB fetched | DEEP L86, L103, L124, L315, L3199–3202 | CONFIRMED |
| 56 | DEEP | AB2a pre-registered gate FAIL | chosen row A222V structurally absent: "position 222 has zero rows in task32_analysis_table.csv (consistent with script 70's prior-session G5 finding of 0 variants @222)"; join half matched 10,757/10,757 (coverage 1.0000); R1 reproduced 10,757/654 | DEEP L184–191 | CONFIRMED FAIL (pre-registered; not re-validated; open user decision — in Holm family C2 as a disclosed max-of-seven operationalization, #93) |
| 57 | DEEP | AB2c EVmutation score substitute | A222V = −4.863357093286666; Site_Independent counterpart = −4.303519347442919 | DEEP L202–204, L95 | CONFIRMED (score-level substitute, NOT a J-matrix) |
| 58 | DEEP | AC1 effective-n arithmetic | 150M: w = 0.13595 ⇒ n_eff = 210.9 (n=1,900, pos=100); 650M n_eff ≈ 4,599; design effect 10,757 / 4,599 = 2.34 | DEEP L1335, L1342, L1349 | CONFIRMED |
| 59 | DEEP | AC3 detection-scale context | median \|delta_ESM\| = 0.04660 nats (0.046600006520749, n=11,344 set) | DEEP L1544, L1619 | CONFIRMED |
| 60 | DEEP | AC4b disk check (then) | shortfall = 16,928,180,919 B = 15.76 GiB (need 1.76× what exists) → BLOCKED | DEEP L475–476 | SUPERSEDED — CLOSE #41–44 ran AC4 via staged one-member-at-a-time deletion |
| 61 | DEEP | AC6 ESMFold/SaProt background | `esm2_t36_3B_UR50D.pt` = 5,678,116,398 B (5.29 GiB) > 3 GB cap → BLOCKED (pre-download) | DEEP L1834, L1883 | BLOCKED (open; launch-prompt-forbidden this window — CLOSE L2359–2360) |
| 62 | DEEP | AD1 ThermoMPNN sign audit | sign NOT flipped: "the sign is NOT flipped; -0.0733 keeps its sign"; buried hydrophobic→charged control: ALL 123 score positive (median +2.629); 88.9% of all 10,141 missense destabilizing; ddG(Phe516Asp) = +4.067 | DEEP L562 (quoted at L3109); sign-test operationalization 0.5^123 = 9.4039548065783e-38 (REL L1277, task97 CSV row 1) | CONFIRMED (the p is C2's disclosed operationalization — AD1 registered none) |
| 63 | DEEP | AD4 interaction term (original) | rho(interaction_D, own_e_b) = +0.0154 [−0.0166, +0.0465] (DEEP L2327–2336, quoted verbatim in REL L1036) | DEEP L2327–2336 as quoted REL L1036; DEEP SUMMARY L3231 | CONFIRMED as null-absent; re-tested by REL B4 (#91) → confirmed real (weak by construction) |
| 64 | DEEP | AD5 multivariable controls on −0.0733 | −0.0733 survives task-literal controls; entry title "(sign differs by FE granularity)" | DEEP L2436, L2594 | FLAGGED — title contradicted by REL B1 (control set drives the sign, not FE granularity; REL L764–769); "survives controls" result stands as reported |
| 65 | DEEP | AD6 depth discriminator | pooled rho +0.1714 [+0.0918, +0.2471] p=0.0000 n=586; region 4 −0.2373 [−0.3795, −0.0853] p=0.0042 n=169 | DEEP L2701, L2717, L2743 | CONFIRMED with B2 caveat: pooled +0.1714 collapses to +0.0125 when top-124 Neff positions drop (REL L879) |
| 66 | DEEP | AD7 dimer-scoring control | Δrho_4 = −0.0136 [−0.0302, +0.0009] p=0.0706; pooled Δrho = −0.0076 [−0.0152, −0.0007] p=0.0292 (outside frozen verdict); mono-vs-dimer rho +0.982; region-4 rho −0.1237 → −0.1101 | DEEP L2849, L2855 | CONFIRMED (region-4 anchor HOLDS; pooled weakening disclosed separately) |
| 67 | DEEP | AD8 joint model | unique_T = 0.004455 [0.001407, 0.009140]; unique_E = 0.005034 [0.001544, 0.010412]; both p<1/10000; rho_ET = +0.0883; shared = 8.8%; R²_full = 0.010407 = 1.04% of rank variance; n=9595 | DEEP L2884–2885, L2893, L2896 | CONFIRMED (both signals independent but small in absolute terms) |
| 68 | DEEP | AE1/AE2 position-vs-identity contrasts | D_identity = −0.01451800615600432 [−0.022076997914527594, −0.006934318360944861] p=0.0006; D_position = +0.025600707800268914 [0.013701600902833486, 0.03923618181911529] p=0.0 (i.e. <1/10000); A222V rank 16/19; 1.68× the A>V-elsewhere median (0.068357 vs 0.040635) | DEEP L2933 (CSV verbatim), L2959, L3244–3247 | CONFIRMED (frozen rule fired MIXED DIRECTION, read as-is) |
| 69 | DEEP | AE3 clade/depth candidate | Val fraction = 0.021748222501045588 (104/4,782), Wilson [0.017981811012450326, 0.02628242038208642]; primary rho +0.1077795872908862 [+0.02425933457518202, 0.191755912435612] p=0.012; Neff-adjusted +0.12356489039260235 [+0.039702178302981894, 0.20638009454763187] p=0.0038; rho² ~1.2% | DEEP L2986, L2994, L2992, L3004, L3007 | CONFIRMED (candidate only, region-4 caveat); REL B3 (#90): exceeds size-matched nulls p=0.0010 but point-excess-only vs placebos p=0.2467 → MIXED |
| 70 | DEEP | AE4 accuracy vs shift magnitude | Delta_signed = −0.10053006930576763 [−0.1708131389574773, −0.03200391939506725] p=0.0046; Q4 signed rho −0.110803 [−0.167445, −0.053712] p=0.0002; secondary Delta_abs −0.04362389414946611 [−0.10722072209565554, 0.020251259831809375] p=0.1776 (flat); ~1.2% rank variance, every within-bin \|rho\| ≤ 0.167 | DEEP L3036, L3035, L3047, L3046, L3050 | CONFIRMED (signed worsens, magnitude flat — both reported as-is) |
| 71 | DEEP | AF2 n-cascade audit | 13,134 → 11,902 / 11,344 / 11,113 → 10,757 / 10,141 / 9,740 / 9,595 per predictor; 40/40 gates recomputed from disk; manifest `task_AF2_variant_manifest.csv` | DEEP L3080, L3062, L3257–3260 | CONFIRMED |
| 72 | DEEP | AF3 flagged-items audit | 3 DONE, 2 PARTIAL; five exploratory-era cell-level nulls never repaired: scripts 21:138, 24:140, 26:135, 28:172, 33:100 cell-granularity + 26:85 row-level target shuffle; headline re-verified by A1b/B2 | DEEP L3089, L3102 | CONFIRMED (PARTIAL); later addressed for citation hygiene by REL C3 (#94): DEPRECATED headers added to 21/24/26/28 |
| 73 | DEEP | Deep-dive tally | 32 tasks: 26 PASS, 1 FAIL by own gate, 1 SKIPPED, 3 BLOCKED, 1 audit; evaluator top-3 2 of 3 executed (AC4 then blocked); 15 new scripts (71–85); HEAD edb6017 | DEEP L3155–3160 | META (AC4's blocked state later resolved, #60) |
| 74 | CAL | N1 Nambiar functional form recovered | their code verbatim: `-1.*log(1+exp(-b.*(x+c)))` (φ1(x) = −log(1+exp(−b(x+c)))); DOI 10.1101/2025.09.14.676130; repo maslov-group/Epistasis | CAL L43–46, L32–33 | CONFIRMED (exact equation, not a reconstruction) |
| 75 | CAL | N2 two-stage fit, 20/80 position split | split: calibration 131 positions / 2,279 rows, held-out 523 / 9,065, overlap 0; φ1 b=0.262004 c=11.017485 (held-out R²=0.1102, Spearman +0.3013); φ2 b=0.143945 c=3.953698 (held-out R²=0.1159, +0.3214); sensitivity contrast b=0.020688 c=23.512049 (cal R²=0.0016) | CAL L171–177, L186–196 | CONFIRMED (fit quality moderate; exclusion skew disclosed L224–230) |
| 76 | CAL | N3 headline on calibrated scores, held-out only | raw −0.0902 CI [−0.1229, −0.0575] p=<0.0001; calibrated +0.0339 CI [+0.0044, +0.0634] p_null=0.0033 n=8584; M1 (\|rho_cal\| ≥ 0.26) NOT MET; M2 (≥2× raw) NOT MET; SIGN CHANGE flagged; diagnostic Spearman(delta_cal, delta_esm) = −0.0307; contrast-arm −0.0850 → −0.0749; post-hoc single-curve −0.0878 (rho +0.9548 with delta_esm) | CAL L338–344, L333, L358–363 | CONFIRMED — verdict NOT MATERIAL; both legs independently confirmed by REL A4b (#87) |
| 77 | CAL | N4 seed-instability on calibrated scores | rule fired IMPROVED: delta-pair median raw 0.084365 → cal 0.655966 (bar 0.168730 MET); five delta-vs-own_e_b rhos raw mean −0.015588 (1 pos/4 neg) → calibrated mean +0.038769 (5 pos/0 neg, 4/5 CIs exclude 0); mechanism caveat carried (delta_cal↔delta_esm −0.0307, levels agree at 0.883) | CAL L437–460, L463–474 | CORRECTED/CROSS-FLAGGED — REL A4 (#86) shows the rule is severity-contaminated: the isolated shift-component agreement is 0.089806, NOT MET vs 0.168730 → verdict MECHANICAL; N4's execution was correct on its own registered rule (CAL unedited) |
| 78 | REL | V1 E3/AB2a-FIX closure | anchor swap \|diff\| = 0.000e+00; full run 15:47:24 → 15:58:57 EXIT=0 (692.1s); 96-row CSV | REL L40, L60, L1583 | CONFIRMED |
| 79 | REL | V2 severity-baseline own_rhos (direct CSV read 2026-09-25) | Site_Independent 0.06396596794067251; ESM1v_single 0.06780795371221343; GEMME 0.07576993585430188; DeepSequence_ensemble 0.07613611980841997; EVmutation 0.0765388135872782; ESM2_650M 0.0853911031053886; ESM2_150M 0.16223117588303074 | `data/processed/task_AB2_proteingym_model_comparison.csv` (direct awk read); REL L90–96 | CONFIRMED — all seven match the external analysis's 3-dp claims |
| 80 | REL | V3 G1 external-claim re-derivation | r2_crossfit_isotonic 0.1535436240252529; spearman_delta_raw_eb −0.07070516222228716; \|diff\| = 6.94e-17; residual −0.1455 survives and strengthens (−0.1455 vs −0.0707) | REL L166, L169, L156, L178 (task46 CSV read in-entry) | CONFIRMED |
| 81 | REL | V4 RSA per-position constant | struct rows 651 \| unique Position 651; duplicates 0; "max distinct rsa values within any position: 1"; frame 11,902 variants (rsa non-null on 10,842 of 11,902) | REL L241, L244, L249, L273 | CONFIRMED |
| 82 | REL | A1 Spearman-Brown prediction test | observed rho −0.028508 CI [−0.056495, −0.000239] p_boot=0.0484 (10,000 draws, 654 positions); sign-flip observed −0.028508 null mean +0.0002 sd 0.0142 p=0.0442; SB recompute −0.015588096 × sqrt(5/(1+4×0.084365)) = −0.0301; single-member mean \|rho\| = 0.020962 | REL L324, L328, L310–312, L332 | CONFIRMED — prediction HOLDS; marginal (both p just under 0.05), ESM-1v-only scope (REL L1596–1600) |
| 83 | REL | A2 disattenuation framing | ceiling sqrt(0.084365) = +0.290457; delta-only −0.303378; fully disattenuated −0.380323; z = −3.45 sample-SDs (ddof=1; ddof=0 → −3.85) | REL L398–405, L414–415 | CONFIRMED (descriptive scale context from n=5; proxy banner: ESM-1v reliability borrowed for ESM-2) |
| 84 | REL | A3 ensemble scope correction | five replicates = ESM-1v SEEDS; ESM-2 = one checkpoint per parameter size; AC4d's unscoped wording flagged | REL L461, L514–518, L1667–1669 | CONFIRMED (scope correction for any write-up) |
| 85 | REL | A4c shift-vs-severity decomposition | delta_cal cross-member median 0.655966; SHIFT exact median 0.089806; first-order 0.089675; severity-only Δφ median 0.664665; bar = 0.168730 → NOT MET → MECHANICAL; reproduction gates \|diff\| 1.89e-07 / 1.91e-07 vs script 89 | REL L596–616, L643–652 | CONFIRMED — cross-flags N4's IMPROVED (#77); first-look block REL L633–652 |
| 86 | REL | A4b external prediction on both legs | N3 legs verified: delta_cal↔delta_esm −0.0307; calibrated correlation +0.0339, M1/M2 NOT MET → prediction CONFIRMED | REL L565, L638; source numbers CAL L333, L340–342 | CONFIRMED |
| 87 | REL | B1 Mundlak within/between | ddg: CI [−0.016067, +0.008811] p=0.5675 → do NOT differ; delta_esm: CI [−0.098844, +0.119936] p=0.8501 → do NOT differ | REL L715, L721, L741–742 | CONFIRMED — B1 verdict CONTROL-SET-DRIVEN: 2×2 flips sign on control set (ddg −0.1042→−0.0796, +0.1382→+0.0790 at L748), FE granularity changes magnitude only; decisive cell 24+P = +0.1382 CI [+0.1057, +0.1708] p=8.118e-17 (L730); AD5 title contradicted, flagged L764–769 |
| 88 | REL | B2 depth-reversal decomposition | region4 Neff-cons +0.2865 [+0.1432, +0.4160] p=0.0002 n=169 vs REST +0.0599 [−0.0307, +0.1499] p=0.2000 n=417 (CIs disjoint); conservation partial −0.1763 [−0.3218, −0.0222] p=0.0244 (raw −0.2373 → partial; pooled +0.1714 → +0.1738); in-range pooled +0.0125 [−0.0822, +0.1064] n=462; region4 Neff range = 99.8% of pooled [111.9, 1213.1] vs [111.9, 1215.4]; pooled collapse to +0.0125 on dropping top-124 Neff positions | REL L818–820, L824–826, L836, L833, L879 | CONFIRMED — region-specific beyond range restriction; high-end-upturn caveat required in any write-up |
| 89 | REL | B3 clade-control battery on AE3 | B3a: observed +0.107780 vs size-matched null mean −0.073628 sd 0.026905, one-sided p=0.0010 (0/1000 ≥ observed), excess +0.181408; B3b: paired excess +0.024461 CI [−0.046428, +0.093833] p_exceeds=0.2467 (0/10 ≥ actual); B3c: restate-as-generic conditional does NOT fire; rho² ~1.2% | REL L941–944, L958, L977, L987 | CONFIRMED — verdict MIXED (exceeds null, not established vs placebos) |
| 90 | REL | B4 de-biased AD4 interaction | R² = 0.001359, slope +0.000819 Å⁻¹; residual rho +0.0097 [−0.0221, +0.0410] p_boot=0.5382 vs original +0.0154 [−0.0166, +0.0465] (Δ −0.0057); position-shuffle p=0.8784 (N_PERM=10000, 586 positions, identity PASS); 9,232/9,595 = 96.22% beyond 10 Å (≤10 Å = 363) | REL L1062, L1066, L1068–1070, L1058, L1105 | CONFIRMED — AD4's null CONFIRMED as real, weak by construction (expected at corr ≈ +0.025; rules out offset-artifact only) |
| 91 | REL | C1 delta_esm definition + own_e_b construction | definitions: scripts/12_validate_a222v_scores.py L29 `merged["delta_esm"] = ...` and scripts/45_c1_reconciliation.py L97 `df["delta_esm"] = ...`; 32/33 consume only (four numbered files checked); own_e_b = per-variant WLS with 1/se² on multiplicative expectation (lib/own_context.py) ⇒ f_bar_wt is a construction covariate | REL L1132–1134, L1142, L1157–1159, L1219 | CONFIRMED (corrected precise-statistic paragraph delivered inside [C1]) |
| 92 | REL | C2 Holm family, core | `task97_holm_family.csv` direct read: core5 all rejected — AD1 (0.5^123) raw 9.4039548065783e-38 → adj 9.4039548065783e-38 (rank 5, thr 0.05); AD6 pooled depth raw 0.0 → adj 0.0 (thr 0.01); AD6 conservation raw 0.0 → adj 0.0 (thr 0.0125); AB2a max-of-seven raw 0.0 → adj 0.0 (thr 0.016667); core −0.088 anchor raw 0.0 → adj 0.0 (thr 0.025) — 5/5 survive family-wise α=0.05, five gates green | `data/processed/task97_holm_family.csv` (direct read 2026-09-25); REL L1289–1293 | CONFIRMED (family + both operationalizations pre-registered in script 97's docstring before any number existed) |
| 93 | REL | C2 Holm m=8 sensitivity | 8/8 survive: AE3b raw 0.012 → adj 0.036000000000000004; AD6 region-3 raw 0.0194 → adj 0.0388; AD5 SPEC A raw 0.0232387273643964 → adj 0.0388; margins 0.011–0.014 below α (flip at ~10+ members) | `task97_holm_family.csv` (direct read); REL L1298–1305, L1320–1321 | CONFIRMED — task's "at real risk" expectation NOT borne out at m=8 (reported as the negative result it is) |
| 94 | REL | C3 deprecation headers | scripts 21:138, 24:140, 26:135, 28:172 cell-level nulls + 26:85 row-level target shuffle — DEPRECATED headers added in script 35's convention; all four py_compile OK; five-nulls-vs-four-listed reconciled | REL L1364, L1375, L1689–1696 | CONFIRMED (header-only; scoped to nulls so frozen script 28 run not over-deprecated) |
| 95 | REL | C4 SaProt audit still blocked + smoke-rho contradiction | block: CLOSE L1870 + SUMMARY L2323 (guard before any null; script 70 untouched); smoke CSV rows: signed own −0.110167 CI [−0.505453, +0.472603] p=0.600000 n=74; absolute own +0.191322 CI [+0.066178, +0.513514] p=0.000000 n=74; signflip absolute null +0.013299 p=0.030000 survives True (n_perm=300); n=74 = 0.7% of 10,757 (score smoke CSV 80 rows vs full 11,940) | REL L1508–1522; CLOSE L1870 | CONFIRMED (smoke artifacts, not results; two task-doc defects flagged: "E4" exists nowhere; "(no SaProt correlation exists yet)" literally false at smoke scale) |
| 96 | REL | Reliability-session meta | 16 entries / 16 tasks, all PASS; 8 new scripts 90–97; zero commits (HEAD abc7319 untouched); span 19:03 → 20:33 | REL L1556–1576 | META |
| 97 | REL | F1 flag (not attempted last session) | F1a spec ends "One commit" vs no-commit rule — conflict flagged, moves left undone; strays 32/33/34/36–40 observed live | REL L1710–1719 | SUPERSEDED — executed this session as X1: commit `fbe4243` (see [X1] in FINAL_CLOSEOUT_LOG) |
| 98 | FOLLOW | L1c detection power of the GB1 gate | ρ_floor = 0.5400 (crit 0.4755 + 0.8416 × se 0.0767; sensitivities 0.5109–0.5418 agree in direction); comparator ρ = 0.4467 below floor; power = 35.3% at the effect being tested | FOLLOW L573 | CONFIRMED — COMPARATOR-UNDERPOWERED (gate failure largely a power failure; pipeline-power question open in both directions) |
| 99 | FOLLOW | M1d mechanism (original 9-background run) | residual +0.00954 CI [−0.00573, +0.02640] (contains 0), rank 6/9 | FOLLOW L575 (original value quoted at SESS L2742) | SUPERSEDED by SESS W3 (#35): denser design gives +0.02121 CI [+0.00465, +0.03934], verdict CHANGES to CONTRARY-TO-H1A; CIs overlap [0.0047, 0.0264] |
| 100 | FOLLOW | M1e severity→shift relation (original) | Spearman −0.4667, CI [−0.5833, −0.0667] | FOLLOW L575 (quoted at SESS L2744 as −0.467 CI [−0.583, −0.067]) | SUPERSEDED by SESS W4 (#36): −0.519 CI [−0.635, −0.388] (strengthens) |
| 101 | MIG | Q1 four-site GB1 gate PASSES | pooled ρ = +0.401757 (n = 760 rows, 76 clusters); permutation null mean +0.247570 (does not center on zero); one-sided p = 0.0009999 (N_PERM = 10,000); cluster CI [+0.258070, +0.521658] (N_BOOT = 2,000); identity 0.000e+00; vs frozen 3-site FAIL (p = 0.139786, gate_pass = 0); excess-over-null 2.63× (0.0587 → 0.1542), null 0.3880 → 0.2476 driven, raw ρ 0.4467 → 0.4018 | MIG L699–707 | CONFIRMED — SUPERSEDES I1's three-site gate FAIL (#26) for the gate question ("same comparator corrected," not a separate dataset) |
| 102 | MIG | R2d script-50 migration outcome | zero new numbers (exit 1 at counts gate); old outputs stand; only movement would have been descriptive rows: missense 0.4483 → 0.1659, syn 0.4474 → 0.0509 | MIG L709–715 | CONFIRMED — "unchanged but untested" (flag-independent, se_e_b-dependent numbers not re-confirmed) |
| 103 | MIG | P1d structure/site facts | 2GB1 parses contiguous 1–56, residue 54 = VAL; four sites paper-verbatim "V39, D40, G41 and V54"; script 49's `site4 dropped` rested on residue 44 (THR), which the paper never used; ε discrepancy flagged: Fig 3D prints ε = 5, on-disk re-derives +7.399806 (figure's printed fitnesses give +7.720905) | MIG L693–697, L724–730 | CONFIRMED (P1d CONFIRMED; ε flagged for user call — see #53) |
| 104 | MIG | R1b citation audit | 0 of 126 numeric fingerprints of script 50's outputs hit MTHFR_RESULTS_LOG/REVIEW_TRIAGE except `3586`, traced to §6.3's own pre-existing row | MIG L717–722 | CONFIRMED (nothing written up as fact would change) |

## Discrepancy and status-change register (the flag list, X2 rule: source file wins)

No SUMMARY-vs-source numeric mismatch was found in this verification
pass — every number checked in a SUMMARY matched its producing entry or
CSV at the SUMMARY's stated rounding. The items below are known
contradictions/status changes, each already recorded in its own log and
re-confirmed here from the sources:

1. **S1's published-rho label (CORRECTED).** OV's SUMMARY line quotes
   "ρ = −0.088 (published e.b)" while the actual published-e.b number is
   −0.07070516222228716 (task32 CSV L5, read directly) and −0.088118…
   is own e_b (L6). OV L1880 itself records the correction; both numbers
   above carry both facts.
2. **N4's IMPROVED verdict (CROSS-FLAGGED, not edited).** CAL L460's
   IMPROVED fired correctly on its registered rule; REL A4 (L643–652)
   shows the rule is severity-contaminated — shift-component agreement
   0.089806 misses the same 0.168730 bar → MECHANICAL. Rows #77 and #85
   both stand; quote them together.
3. **AD5's entry title (CONTRADICTED, flagged in place).** DEEP L2436's
   "(sign differs by FE granularity)" is contradicted by REL B1
   (L764–769): the control set drives the sign; FE granularity changes
   magnitude only. The "−0.0733 survives controls" substance is not
   affected. Rows #64 and #87.
4. **I1's three-site GB1 gate (SUPERSEDED).** The frozen FAIL (row #26)
   stands; Q1's four-site PASS (row #101) and L1c's power analysis
   (row #98) supersede it as the project's current answer to the gate
   question. AA3 (row #52) explains why the 3-site null sits high.
5. **AC4b's disk BLOCKED (SUPERSEVED).** DEEP's 15.76-GiB block (row
   #60) was real when logged; CLOSE ran AC4 by staging one member at a
   time (rows #41–46). Cite CLOSE, not DEEP, for AC4.
6. **M1d/M1e (SUPERSEDED by denser design).** FOLLOW's original values
   (rows #99–100) were not wrong — SESS W3/W4 ran a denser 30-
   background design and both verdicts moved (rows #35–36); the two
   residual CIs overlap, described in SESS as resolution, not reversal.
7. **F1 (done at last by this session).** REL's open-F1 flag (row #97)
   is resolved by commit `fbe4243` (X1, this session's log).

## How to use this table

- For every number, the cited line is the place that number was re-read
  from today. Numbers whose deepest source is a CSV say so and were
  read from the CSV, not from any log.
- When two rows qualify each other (e.g. #77/#85, #64/#87, #52/#101),
  quote both with their sources — the qualification is the finding.
- Status words here track what later runs did to each result; they do
  not authorize editing any prior log. No prior log was edited to build
  this table.
