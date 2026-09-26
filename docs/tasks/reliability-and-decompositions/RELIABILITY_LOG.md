# RELIABILITY_LOG — reliability-and-decompositions session

Append-only log for `RELIABILITY_AND_DECOMPOSITIONS.md`. One entry per
task, in the mandated format (## [TASK ID] — title / Status / Time /
What I did / Actual output / Verdict / Files / Unexpected / ---).
Entries are written only after the check has actually been run and its
real output read.

Session start: 2026-09-25 (evening window). No GPU work in this doc;
all tasks run on CSVs already on disk.

## [V1] — Confirm E3 (AB2a-FIX) is actually closed
Status: PASS — all four claimed facts verified against the real entry and the on-disk file
Time started / finished: 2026-09-25 19:04 / 19:06
What I did:
- Located the actual entry (not a summary): `grep -n "AB2a" docs/tasks/
  closeout-u2-u3-u4-v5/CLOSEOUT_LOG.md` -> the entry is
  `## [AB2a-FIX]` at line 1278. Read it in full (L1278-1735).
- Independently verified the deliverable on disk with `wc -l` +
  `head` (not by trusting the log's own quote of it).
Actual output (real numbers and quoted source text, not a paraphrase):

1. **Anchor swap to H354R — CONFIRMED.** Verbatim from the entry
   (L1365-1366, smoke output embedded in the entry):
   "POST-HOC DISCLOSURE (AGENTS 6): R2 identity-gate anchor row swapped
   A222V -> H354R under explicit user authorization 2026-09-25 (A222V
   is structurally absent: zero rows at position 222 in the analysis
   table; gate mechanism unchanged -- identity atol 1e-12 vs an
   independently measured constant; full text in docstring R2)"
   "R2 identity gate H354R ESM2_650M = -4.309727668762207 (expected
   -4.309727668762207) -> PASS"
2. **Gate |diff| = 0.000e+00 — CONFIRMED.** Verbatim (L1392):
   "G-anchor: observed rho(delta_esm, own) =
   np.float64(-0.08811806424891734) vs -0.08811806424891734
   |diff| = 0.000e+00 -> PASS". Also restated in the entry's Verdict
   (L1708-1709): "G-anchor reproduces the frozen -0.08811806424891734
   with |diff| = 0.000e+00". Companion gate G-lib overall
   max|diff| = 1.388e-17 (threshold 1e-9) -> PASS (L1396).
3. **692-second runtime — CONFIRMED.** Verbatim (L1291-1293):
   "Full run 15:47:24 -> 15:58:57, EXIT=0 (692.1s = 11.5 min;
   projection from the smoke engine measurement was ~670s — within the
   no-guessed-runtime rule)." The embedded run output ends
   "total runtime 692.1s" (L1687).
4. **CSV exists with 96 model rows — CONFIRMED on disk, independently
   of the log.** My own check: `wc -l data/processed/
   task_AB2_proteingym_model_comparison.csv` = **97 lines**, first line
   `model,own_rho,own_ci_lo,own_ci_hi,own_p_boot,own_n,own_n_positions,
   pub_rho,pub_ci_lo,pub_ci_hi,pub_p_boot,pub_n,pub_n_positions` ->
   96 data rows = 95 ProteinGym model columns + the REF_delta_ESM_our_run
   row, exactly as the entry states ("97 lines = header + 96 model rows
   incl. the REF row", L1284-1285). File mtime Sep 25 15:58 (matches
   the entry's 15:58:57 finish), size 15,759 B.
   First data row (verbatim from disk):
   `REF_delta_ESM_our_run,-0.08811806424891734,-0.11733344589533189,
   -0.059511384495117385,0.0,10757,654,-0.07070516222228716,...`
5. Entry's own Verdict (L1703-1704), quoted: "PASS — AB2a's
   deliverable exists with every pre-registered gate green at full N."

Verdict: PASS — the external analysis's summary of E3/AB2a-FIX holds
on every checked fact (anchor swap, |diff| = 0.000e+00, 692.1 s,
96-row CSV). E3 is genuinely closed. Note for downstream: the entry's
own caution stands — REF is a two-background delta while the 95 model
rows are raw severity scores, so their sign difference is descriptive
(L1718-1721).
Files created/modified:
- docs/tasks/reliability-and-decompositions/RELIABILITY_LOG.md (this
  entry; file created earlier this session per FIRST ACTION). Read-only
  everywhere else: CLOSEOUT_LOG.md, data/processed/task_AB2_proteingym_
  model_comparison.csv.
Anything unexpected or worth flagging:
- Nothing contradicted. One nuance worth carrying forward: the entry
  documents TWO disclosed post-hoc fixes (anchor swap under explicit
  user authorization; orientation fix `A = d[cols].to_numpy().T` after
  smoke 1's crash) — both are already disclosed per AGENTS §6 in the
  script and entry, and neither changed a threshold/seed/set/rule.
---

## [V2] — Confirm the severity-baseline numbers in the AB2 comparison table
Status: PASS — all seven claimed values confirmed at the claimed rounding
Time started / finished: 2026-09-25 19:06 / 19:07
What I did:
- Pulled the `own_rho` column directly from data/processed/
  task_AB2_proteingym_model_comparison.csv for the seven named models
  (awk on the CSV, exact-name match — not read from any log's table),
  and compared each against the task doc's claimed value.
Actual output (real numbers and quoted source text, not a paraphrase):

| model (as in CSV) | own_rho (full precision, from CSV) | claimed | 3-dp round | match |
|---|---|---|---|---|
| Site_Independent | 0.06396596794067251 | +0.064 | 0.064 | yes |
| ESM1v_single | 0.06780795371221343 | +0.068 | 0.068 | yes |
| GEMME | 0.07576993585430188 | +0.076 | 0.076 | yes |
| DeepSequence_ensemble | 0.07613611980841997 | +0.076 | 0.076 | yes |
| EVmutation | 0.0765388135872782 | +0.077 | 0.077 (0.07654) | yes |
| ESM2_650M | 0.0853911031053886 | +0.085 | 0.085 | yes |
| ESM2_150M | 0.16223117588303074 | +0.162 | 0.162 | yes |

Header row read for identity (AGENTS §5): `model,own_rho,own_ci_lo,
own_ci_hi,own_p_boot,own_n,own_n_positions,pub_rho,...` — own_rho is
the correlation against own_e_b on n=10,757 / 654 positions (per the
REF row's own_n/own_n_positions columns).

Verdict: PASS — the external analysis's severity-baseline numbers are
correct as stated (all seven to 3 decimals). ESM2_150M's +0.162 being
~2x every other model's ~+0.06..0.08 is confirmed in the source data,
not just in the log.
Files created/modified:
- RELIABILITY_LOG.md (this entry). Nothing else; the CSV was read only.
Anything unexpected or worth flagging:
- No discrepancies. Reminder carried from V1: these are correlations
  of RAW single-mutation severity scores with own_e_b, while the REF
  row is a two-background delta — the comparison the table licenses is
  severity-vs-severity, per script 71's own orientation caution.
---

## [V3] — Confirm script 53 exists, is a global-vs-specific epistasis control, and says what it's claimed to say
Status: PASS — file, purpose, and logged result all confirmed; one framing nuance flagged
Time started / finished: 2026-09-25 19:07 / 19:09
What I did:
- `ls scripts/53*.py` -> scripts/53_g1_global_specific_epistasis.py
  (293 lines), read in full.
- Found its actual logged run: `grep -n "^## G1"` in OVERNIGHT_LOG.md
  -> entry at line 1168; read L1168-1218 (the entry's own verbatim
  output and Verdict, not the SUMMARY).
- Cross-checked the script's saved output on disk:
  `cat data/processed/task53_g1_global_specific.csv`.
Actual output (real numbers and quoted source text, not a paraphrase):

Script identity — docstring L2-11, verbatim: "Task G1 (review-triage):
global vs. specific epistasis decomposition. ... G1a: How much of e.b's
variance is explained by a monotone nonlinear function of w.fitness
alone? If most of it, the atlas's 'interaction' is substantially
global/threshold epistasis ... the fair test as: does ESM-2 predict the
SPECIFIC residual left after removing global epistasis, not the raw
e.b?" -> CONFIRMED: it is a global-vs-specific epistasis control.

Pre-registration present (L13-68): analysis set, cross-fitted isotonic
(house crossfit_isotonic_by_position, n_folds=5, seed=0, held-out
POSITIONS), variance-share bands fixed before running
("R^2_cf >= 0.50 -> MOST-GLOBAL / >= 0.25 -> SUBSTANTIAL-GLOBAL /
else LIMITED-GLOBAL"), Part 2 verdict rule
("SURVIVES iff sign-flip p < 0.05 AND the cluster-bootstrap 95% CI ...
excludes 0. Otherwise NOT-DETECTED ... No retuning after results"),
null type labeled ASSOCIATION (not re-derivation).

Its own logged result (OVERNIGHT_LOG L1169, L1184-1203, verbatim):
- Status line: "PASS (PART 1 verdict: LIMITED-GLOBAL — the 'if most of
  it' premise is NOT met; PART 2 verdict: SURVIVES — ESM-2 predicts the
  specific residual, and the signal STRENGTHENS)"
- "cross-fitted isotonic R^2 (PRIMARY) = 0.1535 (out-of-sample)";
  "cross-fitted R^2 cluster bootstrap (N_BOOT=2000):
  CI=[0.1317,0.1749]"; "pre-registered band: R^2_cf -> LIMITED-GLOBAL"
- "Spearman(delta_ESM, residual) = -0.1455 CI=[-0.1761,-0.1131]
  p_boot=<0.000500 (cluster, N_BOOT=2000)"
- "Spearman(delta_ESM, raw e.b) = -0.0707 ... reconciliation vs
  script 32 on-disk: value=-0.070705 n=10757 |diff|=6.94e-17"
- "paired magnitude difference |resid| - |raw|: +0.0748
  CI=[+0.0585,+0.0912] (both rhos negative in 2000/2000 draws) ->
  removing global epistasis STRENGTHENS the |delta_ESM| signal"
- "identity: all+1 == obs (-0.145545737907), all-1 == -obs
  (+0.145545737907) -> OK"; "observed=-0.1455 null mean=+0.0001
  sd=0.0186 p=<0.000100"; "null-centring: mean IS consistent with zero
  (3 SE)"; "pre-registered verdict: SURVIVES"

Saved CSV on disk agrees exactly (task53_g1_global_specific.csv,
626 B, mtime Sep 22 09:49): r2_crossfit_isotonic 0.1535436240252529
CI [0.13166522618330107, 0.17488062666407062] band LIMITED-GLOBAL;
spearman_delta_resid -0.1455457379073755 CI [-0.17613233561094094,
-0.11308880958514285]; spearman_delta_raw_eb -0.07070516222228716;
paired_magdiff +0.07484057568508833 CI [0.05851390500660684,
0.09124374228171987]; signflip_p 0.0 (n_perm 10000 -> p<1/10000);
n_variants 10757, n_positions 654.

Verdict: PASS — the claim holds: script 53 exists, IS the global-vs-
specific epistasis control, and its logged result says (a) the atlas's
interaction is only ~15% a monotone function of w.fitness (LIMITED-
GLOBAL; the "if most of it" premise fails), and (b) ESM-2's association
survives and strengthens on the specific residual (-0.1455 vs -0.0707,
pre-registered SURVIVES rule met). It is a legitimate piece of the
project's existing differentiation work. Framing nuance to carry
forward (not a failure): script 53 decomposes the OUTCOME (e.b) against
atlas w.fitness, whereas Nambiar's phi decomposes/corrects the MODEL's
scores — related questions, different operations, and script 53's text
never mentions Nambiar (it predates that work). Any write-up citing 53
as "our differentiation from Nambiar" should say it establishes our
own global-vs-specific answer on disk, not that it tested their method.
Files created/modified:
- RELIABILITY_LOG.md (this entry). Everything else read-only.
Anything unexpected or worth flagging:
- Three smoke-stage bugs are disclosed inside the G1 entry itself
  (ceiling direction, paired-difference label, reconciliation column),
  all fixed before the full run with no pre-registered rule touched —
  consistent with AGENTS §6/§7 and already on the record.
---

## [V4] — Confirm the AD5 RSA-per-position-constant fact
Status: PASS — confirmed by the entry's own null-space probe AND by an independent data check this session
Time started / finished: 2026-09-25 19:09 / 19:11
What I did:
- Re-read `[AD5]`'s actual entry (grep -> DEEPDIVE_LOG.md L2436,
  read L2436-2565), not a summary of it.
- Independently verified the underlying mechanism twice, on data:
  (1) read `scripts/lib/features.py` `add_structural_features`
  (L54-64) to confirm RSA is merged ON POSITION;
  (2) ran an independent check with venv/bin/python3 loading the raw
  structural table and the atlas substitution variants, merging with
  the same house function, and counting distinct RSA values within
  each position.
Actual output (real numbers and quoted source text, not a paraphrase):

1. **[AD5]'s own evidence for the fact — verbatim (DEEPDIVE_LOG
   L2494-2501):** "Diagnosed numerically BEFORE any code change with an
   explicit null-space probe: rank 588 < k=589; zero-variance columns:
   none except const; exact duplicate columns: none; SVD null space
   spans ONLY {z_rsa + all 585 position dummies + const} — focal and
   f_bar have ZERO null-space weight. Root cause: rsa is a PER-POSITION
   constant (merged by position, scripts/lib/features.py L61-63), so
   with position FE it is an exact linear function of the position
   indicators — collinear BY CONSTRUCTION, not a data anomaly."
   The full-run output prints the same fact as a standing note
   (L2530): "note: rsa is per-position constant -> exactly collinear
   with position FE; FE holds it fixed at every position (strictest
   RSA control), so the explicit rsa column is redundant by
   construction (smoke-run-1 amendment, docstring G2)".
   The consequence in the entry: SPEC A absorbed RSA via position FE
   instead of an explicit column, and the focal estimate was shown
   invariant (smoke 1 vs smoke 2 `coef=-0.1042 CI=[-0.1426,-0.0658]`
   both runs).
2. **Mechanism check — scripts/lib/features.py L54-64, verbatim:**
   "def add_structural_features(df, struct, position_col=\"position\"):
   Merge relative solvent accessibility and domain by residue
   position. ... s = s[[position_col, \"rsa\", \"domain\"]].copy() ...
   return df.merge(s, on=position_col, how=\"left\")" — the merge key
   is position alone, so every variant at a position receives THE SAME
   rsa by construction. Source table per scripts/lib/io.py L59-65:
   `load_structural_features()` reads
   data/raw/mthfrModel/reference_data/MTHFR_structural_features.csv,
   docstring "Per-position structural covariates."
3. **Independent data check (run this session, my own output):**
   ```text
   struct rows: 651 | unique Position: 651
   duplicate positions in struct table: 0
   merged rows: 11902 | rsa non-null: 10842
   max distinct rsa values within any position: 1
   positions with >1 rsa value: 0
   max distinct domain values within any position: 1
   sample: [{'position': 113, 'rsa': 0.0}, {'position': 116, 'rsa': 0.0}, {'position': 145, 'rsa': 0.0}]
   ```
   — across all 11,902 missense-substitution variants, ZERO positions
   carry more than one RSA value (and the structural table itself has
   651 rows for 651 unique positions, no duplicates that could fan out
   the merge).

Verdict: CONFIRMED — RSA is genuinely a per-position constant; every
variant at a given position shares the same RSA value. The [AD5]
entry's claim holds, the mechanism (position-keyed merge) explains it,
and my independent recomputation on the real atlas frame agrees
exactly (max distinct RSA per position = 1). Task B1's predicted
answer can proceed on this basis: in any position-FE specification,
RSA is absorbed by the fixed effects by construction, and B1d's
statement to that effect is warranted. (Bonus fact for downstream: the
same is true of `domain` — one value per position — relevant to
B1c's domain-granularity FE.)
Files created/modified:
- RELIABILITY_LOG.md (this entry). Everything else read-only; the
  check ran on data/raw/.../MTHFR_structural_features.csv and the
  atlas results CSV without writing anything.
Anything unexpected or worth flagging:
- First check attempt failed on a wrong import (`load_atlas` does not
  exist in scripts/lib/io.py; the correct loader is
  `load_derived_maps`) — fixed by grepping io.py's real functions;
  no result was produced or used from the failed attempt.
- The merge leaves rsa non-null on 10,842 of 11,902 rows (positions
  outside the PDB structure's coverage have no RSA); AD5's own frame
  reported "rsa 10141" non-null on its 10,141-row V2 frame, consistent.
---

## [A1] — The five-member ensemble-mean delta run (never computed before)
Status: PASS — run end to end; the Spearman-Brown prediction HOLDS
Time started / finished: 2026-09-25 19:12 / 19:16
What I did:
- Confirmed the five saved member score CSVs exist (data/processed/
  task_AC4_esm1v_member{1..5}_scores.csv, 12,447 lines each incl.
  header; columns position,wt_aa,mut_aa,wt_logodds,av_logodds,delta).
  No model load, no GPU — arithmetic only.
- Wrote scripts/90_a1_ensemble_mean_delta.py (next free number; checked
  `ls scripts/*.py | sort` — 89 was highest). The docstring
  PRE-REGISTERS, before any ensemble result exists: the ensemble
  definition (A1a mean of five deltas per variant), the analysis set
  (script 86's exact 10,757/654 base + R4 join gates), the statistics
  (position-cluster bootstrap CI + position-level sign-flip null with
  all+1/all−1 identity checks <1e-12 else exit 1), and the verdict
  rule for the prediction test — "HOLDS iff observed rho < 0 AND −0.030
  lies inside the 95% cluster CI". The docstring also re-derives the
  ~−0.030 prediction from on-disk components BEFORE running.
- Smoke first (SMOKE=1 N_BOOT=500 N_PERM=500): EXIT=0, all gates
  green. Then full run (N_BOOT=10000 N_PERM=10000): EXIT=0, 24.2 s
  wall.
Actual output (real numbers and quoted source text, not a paraphrase):

Pre-registered prediction re-derivation (printed by the script before
its own result):
- AC4's five primary rhos (task_AC4_esm1v_summary.csv, quoted by the
  script): member 1 −0.020573 CI [−0.048467, +0.006286] p=0.14;
  member 2 −0.040820 CI [−0.069623, −0.011940] p=0.0046; member 3
  +0.013434 CI [−0.014563, +0.041385] p=0.3444; member 4 −0.026572
  CI [−0.053779, +0.000264] p=0.0524; member 5 −0.003409
  CI [−0.031214, +0.024562] p=0.8194.
- "mean single-member rho = −0.015588096"
- "Spearman-Brown recompute: −0.015588096 * sqrt(5/(1+4*0.084365)) =
  −0.0301 (task doc's given prediction: −0.03)"
  — the doc's ~−0.030 is independently reproduced from AC4's on-disk
  components (r_bar = 0.084365 = AC4 R7's "member-pair Spearman on
  delta scores: min=0.003314 median=0.084365 max=0.162631 (10 pairs)",
  CLOSEOUT_LOG L2188).

A1a (ensemble construction): "A1a ensemble built: 10757 rows / 654
positions, delta_ens mean=+0.021034 sd=0.111937"; all five R4 joins
exact ("member k: joined, 10757 rows", zero unmatched; member mean
deltas +0.023080 / +0.041306 / −0.001012 / +0.029790 / +0.012009).

A1b (full run, verbatim):
- "PRIMARY: rho(delta_ens, own_e_b) = −0.028508
  CI=[−0.056495, −0.000239] p_boot=0.0484 (position-cluster,
  N_BOOT=10000, seed=0)"
- "identity: all+1 == obs (−0.028507550626), all-1 == -obs
  (+0.028507550626)  -> OK"
- "observed=−0.028508  null mean=+0.0002  sd=0.0142  p=0.0442"
- "null-centring: mean IS consistent with zero (3 SE)"
- Verdict block: "(a) observed < 0: True; (b) prediction inside CI:
  True -> the Spearman-Brown prediction HOLDS"
- "context: |observed|=0.028508 vs mean |single-member rho|=0.020962
  -> averaging strengthened the association"
- Saved: data/processed/task90_a1_ensemble_mean.csv.

Verdict: PASS. Plainly stated: the real ensemble-mean result is
rho = −0.028508 (CI [−0.056495, −0.000239], p_boot = 0.0484;
sign-flip p = 0.0442, null centered) against the Spearman-Brown-
predicted ~−0.030 — **the prediction holds** (the predicted value sits
inside the 95% CI, and the sign is negative as predicted). Averaging
the five members strengthened |rho| from the single-member mean
0.020962 to 0.028508 — a real but modest gain, consistent with
Spearman-Brown under low inter-member agreement. HONEST-READING
CAVEAT: both p-values sit just under 0.05 (bootstrap CI upper bound
−0.000239), so this is a marginal detection — it supports the
reliability-capped-attenuation framing (an ensemble of five still
lands at only −0.029) but must not be quoted as a strong result.
Scope: ESM-1v seed replicates only (A3); no ESM-2 implication.
Files created/modified:
- scripts/90_a1_ensemble_mean_delta.py (new, pre-registered docstring)
- data/processed/task90_a1_ensemble_mean.csv (new; plus
  task90_a1_ensemble_mean_smoke.csv from the smoke)
- RELIABILITY_LOG.md (this entry). Nothing else touched.
Anything unexpected or worth flagging:
- First smoke attempt died at import (ModuleNotFoundError: scripts) —
  my sys.path insert used scripts/ instead of the repo root; fixed to
  parents[1] (script 86's convention) before any result was produced.
  No number existed from the failed attempt.
- The bootstrap p and sign-flip p differ slightly (0.0484 vs 0.0442) —
  both are reported; neither was chosen post hoc, both are
  pre-registered in the docstring.
---

## [A2] — Formalize the reliability/attenuation framing as a gated result
Status: PASS — all three gates green; all three computed values match the doc's expected values
Time started / finished: 2026-09-25 19:17 / 19:20
What I did:
- Cited both reliability inputs by their EXACT source entries first:
  (1) AC4's cross-member delta agreement 0.084365 — CLOSEOUT_LOG.md
  entry `## [AC4] — ESM-1v across all five pretrained members ...` at
  L2038, value at L2188: "[AC4] R7 member-pair Spearman on delta
  scores: min=0.003314 median=0.084365 max=0.162631 (10 pairs)";
  (2) own_e_b reliability 0.6363 — OVERNIGHT_LOG.md entry
  `## C3a — Oracle ceiling + correlation disattenuation` at L575,
  value at L594: "reliability, own e.b     : 1 - var(syn 0.02111,
  n=570) / var(analysis 0.05804) = 0.6363".
- Wrote scripts/91_a2_disattenuation.py (next free number). Its
  docstring PRE-REGISTERS the formula r_dis = r_obs/sqrt(rel_delta ×
  rel_own_eb), every input with its source line, the three numbers to
  compute with the doc's expected values printed alongside, the A2c
  context computation, three gates, and the proxy-assumption
  limitation. No bootstrap/permutation exists in this script (point
  identities only), so there is no N to reduce — gates are the sanity
  check.
- Ran once, foreground: EXIT=0, 1.2 s wall.
Actual output (real numbers and quoted source text, not a paraphrase):

GATES (all green, verbatim from the run):
- "G1 provenance: CLOSEOUT_LOG contains 'median=0.084365': True;
  OVERNIGHT_LOG contains 'var(analysis 0.05804) = 0.6363': True"
- "G3' headline re-derivation: rho(delta_esm, own_e_b) =
  -0.088118064248917 (expected -0.088118064248917, |diff| = 0.000e+00)
  -> OK"
- "G2' delta-agreement re-derivation: median of 10 pairwise rhos =
  0.084365 (expected 0.084365, |diff| = 1.886e-07) -> OK"

A2b (computed | doc's expected), verbatim from the run:
- "1. attenuation ceiling sqrt(rel_delta) = +0.290457 | doc: 0.29"
- "2. delta-only disattenuated anchor = -0.303378 | doc: -0.303"
  followed immediately by the pre-registered limitation: "[PROXY
  ASSUMPTION (state with every quote): rel_delta is ESM-1v's
  cross-SEED agreement borrowed for ESM-2, whose own delta
  reliability is unmeasurable (no seed replicates) -- assumption, not
  measurement.]"
- "3. fully disattenuated anchor (both reliab.) = -0.380323 |
  doc: -0.38" (same proxy-assumption banner printed with it)
- "reconciliation: r_obs/sqrt(rel_own_eb) = -0.110467 (= C3a's
  on-disk -0.110413; own_e_b-only correction, not new)"

A2c (descriptive, n=5), verbatim:
- five member rhos: -0.020573, -0.040820, +0.013434, -0.026572,
  -0.003409
- "mean = -0.015588;  sd(ddof=1) = 0.021052;  sd(ddof=0) = 0.018829"
- "z = (r_obs - mean)/sd : ddof=1 -> -3.45 SD;  ddof=0 -> -3.85 SD"
- "plain statement: ESM-2's -0.088118 sits 3.45 sample-SDs BELOW the
  five-member mean (-0.015588)"
Saved: data/processed/task91_a2_disattenuation.csv (12 rows incl. the
doc's expected values in a comparison column).

Verdict: PASS. All three pre-registered numbers are confirmed:
ceiling √0.084365 = +0.290457 (doc ≈0.29), delta-only −0.303378
(doc ≈−0.303), fully disattenuated −0.380323 (doc ≈−0.380). Every
disattenuated number carries the proxy-assumption limitation in its
own printed output (ESM-1v cross-seed reliability borrowed for ESM-2;
assumption, not measurement — A3 scope). A2c adds the complementary
context: ESM-2's −0.088 is 3.45 sample-SDs below the five-member mean
(a bigger association than any ESM-1v member shows alone), stated as
descriptive scale context from n=5, not a p-value.
Files created/modified:
- scripts/91_a2_disattenuation.py (new)
- data/processed/task91_a2_disattenuation.csv (new)
- RELIABILITY_LOG.md (this entry). Nothing else.
Anything unexpected or worth flagging:
- The reconciliation line computed −0.110467 while C3a's on-disk
  value is −0.110413. INVESTIGATED, not waved through: recomputing
  with rel = 0.6369 (the ddof=0 twin) gives −0.110415, matching C3a.
  The 5.4e-5 difference is exactly the documented ddof convention
  difference recorded at OVERNIGHT_LOG L651 ("rel prints twice as
  0.6363 (pandas var, ddof=1) and 0.6369 (np.var, ddof=0) ... recorded
  rather than patched post-hoc"). Both numbers are right; no
  contradiction, no edit made. Note: the two conventions change the
  full disattenuation only in the 4th decimal (−0.3803 vs −0.3802).
---

## [A3] — Correct scope: this is an ESM-1v-seed finding, not an ESM-2-seed finding
Status: PASS — paragraph written after checking both claims against Meta's own released sources this session
Time started / finished: 2026-09-25 19:20 / 19:24
What I did:
- Checked what is actually knowable about Meta's release process,
  fetching primary sources (2026-09-25):
  (1) official facebookresearch/esm README (raw.githubusercontent) —
  the "Pre-trained Models" table;
  (2) the official examples/variant-prediction/README.md;
  (3) the Meier et al. 2021 bioRxiv FULL TEXT (2021.07.09.450648v1.full;
  first .full fetch hit HTTP 429, retry succeeded — one retry, per the
  fetch rule).
- Grepped the logs for any prior framing that explicitly claims AC4
  tested "ESM-2's" seed stability (to correct, per A3a's last sentence).
Actual output (real numbers and quoted source text, not a paraphrase):

1. **ESM-2 = one checkpoint per parameter size — CONFIRMED.** The
   official README's model table lists exactly ONE weight URL per
   ESM-2 size: esm2_t6_8M, t12_35M, t30_150M, t33_650M, t36_3B,
   t48_15B (all "UR50/D 2021_04"), no [1..5] variants and no seed
   replicates anywhere in the table.
2. **ESM-1v = five genuine seed replicates of one architecture —
   CONFIRMED, verbatim from the paper.** Official README:
   "`esm1v_t33_650M_UR90S_1()` ... `esm1v_t33_650M_UR90S_5()` ...
   Same architecture as ESM-1b, but trained on UniRef90" and table row
   "esm1v_t33_650M_UR90S_[1-5] | 33 | 650M | UR90/S 2020_03".
   Meier et al. 2021 §4.1 (full text fetched): "We train ESM-1v, a
   650M parameter transformer language model for prediction of variant
   effects, on 98 million diverse protein sequences... We use Uniref90
   2020-03 [21], employing the ESM-1b architecture... **We train five
   models with different seeds to produce an ensemble.**" Appendix B
   corroborates: "we perform the fine-tuning scheme on five models
   that were pre-trained with different seeds."
   The official variant-prediction README: "predictions can be made
   using an ensemble of five ESM-1v models" (esm1v_..._1 .. _5).
3. **Grep for prior ESM-2-seed framing:** no log explicitly states
   that AC4 tested ESM-2's seed stability. The real exposure is
   CLOSEOUT_LOG L2201's model-UNSCOPED wording: "[AC4d] ... strong
   evidence the 'epistasis signal' reported elsewhere in this project
   is seed noise rather than a stable model property" — since the
   project's headline signal is ESM-2's delta_esm, a reader can take
   that as an ESM-2 claim. Flagged, not edited (rule 6).

**A3a — the corrected scope paragraph (final text for use in write-ups):**

> Scope of the seed-stability finding. ESM-2 was released by Meta as a
> single checkpoint per parameter size — Meta's official ESM model table
> lists exactly one weight file each for the 8M, 35M, 150M, 650M, 3B and
> 15B variants, with no published seed replicates — so ESM-2's own
> seed-to-seed variability cannot be measured from public releases.
> ESM-1v, by contrast, was released as five checkpoints
> (`esm1v_t33_650M_UR90S_1..5`) that Meier et al. 2021 describe verbatim
> as "five models with different seeds" trained with the same ESM-1b
> architecture, the same 650M parameter count, and the same UniRef90
> 2020-03 corpus — genuine seed replicates of one architecture. AC4's
> finding (the five members' delta-vs-e.b correlations scatter across
> zero while WT-score agreement is min-pair-rho = 0.859689) is therefore
> an ESM-1v-seed finding, scoped to ESM-1v specifically: it demonstrates
> training-seed instability of that checkpoint ensemble's
> background-shift association, and it does not directly test ESM-2's
> seed stability, which is unmeasurable. Any use of ESM-1v's cross-seed
> agreement (r = 0.084365) as a stand-in for ESM-2's delta reliability —
> as in A2's disattenuation — is an explicit assumption, not an
> established fact: the two families differ in architecture, pre-training
> corpus (UR90/S 2020-03 vs UR50/D 2021_04), and training code, so the
> direction and size of the proxy's error are unknown. AC4d's own
> verdict wording in CLOSEOUT_LOG ("the 'epistasis signal' reported
> elsewhere in this project is seed noise rather than a stable model
> property") is model-unscoped as written and must be read, and stated
> in any write-up, as: demonstrated for ESM-1v's five seed replicates,
> assumed-not-demonstrated for ESM-2.

Verdict: PASS. Both factual legs of the scope correction check out
against Meta's own released sources (one checkpoint per ESM-2 size;
"five models with different seeds" for ESM-1v). The paragraph states
plainly that AC4's finding is ESM-1v-specific and that A2's proxy use
of it for ESM-2 is an assumption. No prior log made the false claim
outright; the unscoped AC4d wording is flagged for any write-up.
Files created/modified:
- RELIABILITY_LOG.md (this entry). All fetches read-only; no repo
  files touched.
Anything unexpected or worth flagging:
- First .full fetch of the bioRxiv page returned HTTP 429; the single
  retry returned the complete full text (the earlier abstract-page
  fetch had lacked §4.1). Fetch budget respected: one retry, then
  success — no BLOCKED needed.
- Useful corroboration discovered: the two families differ in
  pre-training corpus too (UR90/S 2020-03 vs UR50/D 2021_04, from the
  README table), which strengthens (not weakens) the caution in the
  paragraph — the seed-proxy assumption spans more than seeds alone.
---

## [A4] — N3/N4 state reconciliation, the algebraic-prediction test, and the shift-vs-severity isolation (scripts/92)
Status: A4a PASS — state differs from the doc's premise (N3 AND N4 both exist); logged actual state and adjusted per A4a's own instruction. A4b PASS — the external analysis's prediction is CONFIRMED on both legs against the existing run. A4c PASS — the missing isolation computed; verdict MECHANICAL, resting on the shift-component number
Time started / finished: 2026-09-25 19:24 / 19:32
What I did:

**A4a — state check (grep of actual log headers, not summaries):**
`grep "^## " CALIBRATION_LOG.md` returned real entries at:
[N1] L22, [N2] L136, **[N3] L249** ("## [N3] — Headline recomputed on
calibrated scores, held-out only (script 88): NOT MATERIAL toward
Nambiar's band"), **[N4] L404** ("## [N4] — Does calibration change
AC4's seed-instability finding? (script 89): YES — pre-registered rule
fires IMPROVED"), [O1] L499. The task doc's premise ("N3 does not [have
a real log entry], and N4 was never reached") is STALE. Adjustment per
A4a's own clause ("if the state is different, log what's actually true
and adjust"): N3 and N4 were each executed ONCE under pre-registered
rules earlier today, so nothing was re-run (re-running a completed
analysis adds nothing and would violate the executed-once discipline).
A4b became a test of the prediction against N3's EXISTING logged output;
A4c's genuinely missing quantity (the isolation) was computed fresh in a
new pre-registered script 92.

**A4b — the algebraic prediction vs the existing N3 result.**
Prediction (task doc L112-116, quoted): "because Δφ = φ2 − φ1 is
non-monotone and the severity term dominates the shift term in this
construction, N3 is predicted to show near-zero correlation between
delta_cal and delta_esm and to fail to recover a strong calibrated
correlation." Checked against N3's own logged numbers (CALIBRATION_LOG
L388-393, quoted): "ESM-2 E1 held-out ... calibrated rho = +0.0339
(mechanism diagnostic: Spearman(delta_cal, delta_esm) = −0.0307)" and
"M1 ... NOT MET ... M2 ... NOT MET" with "ESM-2 raw −0.0882 → cal
+0.0339 (smaller, sign flip)". Both premises of the prediction were
also verified directly in script 92 rather than assumed:
- p1 non-monotone: computed Δφ'(x) = φ2'(x) − φ1'(x) on a 1001-point
  grid over [−20, 10]: "min=−0.108320  max=+0.039417  sign changes=1
  -> Delta_phi = phi2 - phi1 is NON-MONOTONE (premise CONFIRMED)".
- p2 severity dominance: already established by N3's run itself
  (delta_cal agrees +0.4139/+0.4186 with the score LEVELS but −0.0307
  with the shift) — quoted from [N3], not recomputed.

**A4c — the mechanical-inflation trap, guarded (scripts/92).**
Script 89 (N4) reported agreement on RAW delta_cal only and its
pre-registered rule (i) fired on that quantity; the isolated shift
component φ2'(x)·d was never computed anywhere. I wrote
scripts/92_a4_shift_vs_severity.py (next free number), docstring
PRE-REGISTERING: the exact decomposition
`delta_cal = [φ2(wt)−φ1(wt)] + [φ2(av)−φ2(wt)] = severity + shift_exact`
(severity = Δφ(wt), the shared term; shift_exact = the task's φ2'(x)·d
term by the mean-value theorem; shift_first = φ2'(wt)·d first-order),
the four gates, the verdict rule ("REAL iff shift median ≥ 2× raw =
0.168730, else MECHANICAL — verdict rests on the shift number"), and
the limitations. Smoke (SMOKE=1 N_BOOT=500): EXIT=0. Full
(N_BOOT=10000): EXIT=0, 71 s.

Actual output (real numbers and quoted source text, not a paraphrase):

Gates (verbatim, full run): "G2 phi' analytic vs central-difference of
script 87's phi: max rel err = 2.572e-10 -> OK"; "G3 exact additive
identity severity + shift_exact == delta_cal: max|diff| < 1e-12 for
all 5 members -> OK"; "G4 machinery identity: recomputed RAW median
0.084365 vs logged 0.084365 (|diff|=1.89e-07); CALIB median 0.655966
vs logged 0.655966 (|diff|=1.91e-07) -> OK" (reproduces script 89's
canonical numbers exactly before computing anything new); base
10,757/654, all R4 joins exact.

The two required numbers, side by side (10 pairs, Spearman):
```text
RAW delta            : min=0.003314 median=0.084365 max=0.162631   (reference)
delta_cal (script 89): min=0.525389 median=0.655966 max=0.734686   <- mechanically inflated?
severity Delta_phi(wt): min=0.546296 median=0.664665 max=0.747319   (the shared additive term)
SHIFT exact           : min=0.003900 median=0.089806 max=0.159392   ** THE VALID TEST **
SHIFT first-order     : min=0.003805 median=0.089675 max=0.159315   (phi2'(wt)*d, same test)
```
Spread context: sd(delta_cal) ≈ 0.0944–0.0967 across members vs
sd(shift_exact) ≈ 0.0122–0.0182 — the calibrated deltas' spread is
~6× the shift's; severity dominates the scale exactly as predicted.

Verdict block (verbatim): "raw median = 0.084365; bar (2x raw) =
0.168730 / delta_cal median = 0.655966 (script 89's rule-(i) quantity)
/ SHIFT exact median = 0.089806 -> NOT MET / SHIFT first-order median =
0.089675 -> NOT MET / -> MECHANICAL: cross-member agreement on the
ISOLATED SHIFT does NOT meet the 2x bar. The delta_cal improvement
(0.655966) is carried by the shared severity term, not by a
seed-stable shift. Per A4c, THE VERDICT RESTS ON THIS SHIFT NUMBER,
not on delta_cal."

Secondary diagnostic (pre-registered, descriptive): per-member
Spearman(shift_exact, own_e_b) with position-cluster CI:
member 1 −0.020618 [−0.048410, +0.006323]; member 2 −0.042673
[−0.071553, −0.013662]; member 3 +0.014238 [−0.013889, +0.042417];
member 4 −0.025906 [−0.052903, +0.001079]; member 5 −0.001091
[−0.029300, +0.026644]; "shift-arm signs: 1 pos / 4 neg (script 89's
delta_cal arm was 5 pos / 0 neg)" — each shift rho is within 0.002 of
its raw rho, i.e. after isolation the members' associations are
essentially back to the raw mixed-sign picture. Script 89's condition
(ii) (5/5 one sign) therefore also fails on the valid quantity.

Verdict, stated plainly (AGENTS §0 — this is a negative result and it
is reported as one):
- **A4a**: the doc's premise is stale; N3 and N4 are real, logged,
  run-once entries. Adjusted as A4a itself instructs; nothing re-run.
- **A4b**: the external analysis's algebraic prediction HOLDS on both
  legs — N3 shows near-zero delta_cal↔delta_esm (−0.0307) and fails to
  recover a strong calibrated correlation (+0.0339, M1/M2 NOT MET) —
  and both stated reasons (Δφ non-monotone; severity dominates) were
  verified directly, not assumed.
- **A4c**: TWO NUMBERS — raw delta_cal cross-member agreement =
  **0.655966**; isolated shift-component (φ2'(x)·d) agreement =
  **0.089806** (first-order form 0.089675; severity-only 0.664665).
  The shift number does NOT meet the 2× bar (0.168730), so the real
  verdict is **MECHANICAL**: calibration did not make the interaction
  shift seed-stable; the near-identical severity-only agreement (0.665
  ≈ 0.656) shows where the inflated agreement lives. Cross-flag for
  the write-up: N4's pre-registered IMPROVED verdict fired correctly on
  its own rule, but the rule's quantity (raw delta_cal agreement + sign
  consistency of delta_cal rhos) was severity-contaminated — on the
  valid quantities neither N4d condition survives.

Files created/modified:
- scripts/92_a4_shift_vs_severity.py (new, pre-registered docstring)
- data/processed/task92_a4c_shift_vs_severity.csv (new; smoke CSV
  task92_a4c_smoke.csv from smoke)
- RELIABILITY_LOG.md (this entry). CALIBRATION_LOG.md read-only — its
  [N4] entry NOT edited (rule 6: contradiction flagged in place, prior
  logs never modified).

Anything unexpected or worth flagging:
- The task doc's premise was wrong (N3/N4 already run) — flagged here
  prominently; anyone reading A4's wording alone would re-run
  completed analyses, which this log explicitly advises against.
- Script 92 emits one harmless SyntaxWarning at import (a `\ ` escape
  inside the pre-registered docstring's ASCII table). Deliberately left
  unedited so the pre-registered script stays byte-identical to what
  ran; the warning touches no number or rule.
- The severity-only median (0.664665) exceeding delta_cal's (0.655966)
  is itself diagnostic: the shared term agrees slightly better than the
  full calibrated delta, confirming the shift adds noise to agreement
  rather than signal.
---

## [B1] — Mundlak decomposition + FE×control-set 2×2 of the sign flip (script 93)
Status: PASS — all three gates green; flip attributed CONTROL-SET-DRIVEN for both focals; the B1d prior NOT borne out as stated
Time started / finished: 2026-09-25 19:33 / 19:39
What I did:
- Located the frame and machinery: the 9,595-row matched frame is
  AD5/script 78's frozen frame (V2 10,141 rows merged to phase5 +
  features, own_e_b non-null → 9,595/586). Read script 78's docstring
  and implementation to reuse its `run_spec` BY IMPORT (importlib of
  scripts/78 — single implementation, no copy drift) for the 2×2.
- Wrote scripts/93_b1_mundlak_and_2x2.py. Docstring PRE-REGISTERS: the
  Mundlak spec exactly as written in B1a/b (unscaled components, both
  controls only as specified — most-literal reading, α=0.05 for the
  direct difference test with SE_diff = sqrt(Vww+Vbb−2Vwb) from the
  cluster-robust covariance), the exact 2×2 cell definitions with the
  rsa-collinearity handling (disclosed as script 78's documented
  amendment, not a new choice), the flip-attribution rule
  (checkerboard across FE levels = FE-driven; across control sets =
  control-driven; else not separable), the G1/G2/G3 gates, and the
  limitations. Ran once, foreground, 3.5 s wall — no stochastic draws
  exist (cluster-robust CI is the specified inference), so no N to
  reduce; gates are the sanity check.
Actual output (real numbers and quoted source text, not a paraphrase):

GATES (verbatim): "G1 frame identity PASS: n=9595 / 586 positions,
rho(ddg, own_e_b) = -0.073299 (AD5 identity, same tol)"; context
"rho(delta_esm, own_e_b) on this frame = -0.077145 (Z1 matched:
-0.0771)". G3 reproduction anchor (all four |diff| < 1e-16):
"G3 T+P focal=ddg: coef -0.1042017081 vs AD5 specA -0.1042017081
(|diff| = 2.78e-17) -> OK" (and same for delta_esm −0.0482707894;
24+D ddg +0.0789764791, delta_esm +0.0353262014) → "G3 reproduction
anchor PASS: T+P == SPEC A, 24+D == SPEC B to < 1e-8 (machinery
identity with AD5)". All eight 2×2 designs passed run_spec's exact
rank==k and finite-inference checks; every cell n=9,595 (identical
rows).

B1a (ddg, Mundlak — verbatim):
- "b_within  = -0.021174 CI [-0.029500, -0.012848]"
- "b_between = -0.017546 CI [-0.026858, -0.008234]"
- "DIRECT TEST (within - between): -0.003628 SE 0.006347
  CI [-0.016067, +0.008811] p = 0.5675 -> do NOT differ at alpha=0.05"

B1b (delta_esm, Mundlak — verbatim):
- "b_within  = -0.085102 CI [-0.160857, -0.009348]"
- "b_between = -0.095648 CI [-0.201175, +0.009879]"
- "DIRECT TEST (within - between): +0.010546 SE 0.055811
  CI [-0.098844, +0.119936] p = 0.8501 -> do NOT differ at alpha=0.05"
(Decomposition sanity: max|within + between − x| = 2.2e-16 / 1.1e-16.)

B1c (2×2, verbatim lines):
```text
T+P      focal=ddg          coef=-0.1042 CI=[-0.1426,-0.0658] p=1.066e-07  -> SURVIVES
T+P      focal=delta_esm    coef=-0.0483 CI=[-0.0900,-0.0066] p=0.02324   -> SURVIVES
T+D      focal=ddg          coef=-0.0796 CI=[-0.1084,-0.0507] p=6.263e-08  -> SURVIVES
T+D      focal=delta_esm    coef=-0.0067 CI=[-0.0392,+0.0259] p=0.6883     -> does NOT survive
24+P     focal=ddg          coef=+0.1382 CI=[+0.1057,+0.1708] p=8.118e-17  -> SURVIVES
24+P     focal=delta_esm    coef=+0.0267 CI=[-0.0040,+0.0573] p=0.08853    -> does NOT survive
24+D     focal=ddg          coef=+0.0790 CI=[+0.0485,+0.1094] p=3.673e-07  -> SURVIVES
24+D     focal=delta_esm    coef=+0.0353 CI=[+0.0123,+0.0584] p=0.002679   -> SURVIVES
```
Flip-attribution verdict (rule fixed before running):
- "ddg signs: T+P - T+D - 24+P + 24+D + -> CONTROL-SET-DRIVEN"
- "delta_esm signs: T+P - T+D - 24+P + 24+D + -> CONTROL-SET-DRIVEN"

Verdict (stated plainly):
- **B1a/B1b**: for BOTH predictors the within-position and
  between-position coefficients do NOT differ (ddg p=0.5675,
  delta_esm p=0.8501) and are both negative — the marginal −0.0733 /
  −0.0771 associations are not concentrated in one side of the
  position-level decomposition. (For delta_esm the between CI barely
  includes zero [−0.2012, +0.0099] — noted, not over-read.)
- **B1c**: the sign flip is **CONTROL-SET-DRIVEN**, not
  FE-granularity-driven, for both focals: switching FE position→domain
  changes magnitude only (ddg −0.1042→−0.0796 and +0.1382→+0.0790;
  delta_esm −0.0483→−0.0067 and +0.0267→+0.0353), while switching
  control set flips the sign at BOTH FE granularities. For ddg all
  four cells exclude zero, so its flip is solid; for delta_esm the
  T+D and 24+P point signs carry the pattern but their CIs span zero —
  disclosed, the rule was sign-based as pre-registered.
- **B1d**: the premise is confirmed (V4: rsa AND domain are
  per-position constants → SPEC B's structural block is
  between-position by construction), BUT the prior it motivates is
  NOT borne out: the flip does not live in the between-position block.
  Decisive cell: **24+P = +0.1382 (within-position identification,
  rsa absorbed by position FE, no domain FE)** — the flip occurs with
  the structural block absorbed/absent, so f_bar_a222v + grantham +
  blosum62 (substitution-scale controls) are what move the sign.
  Further isolation within that set is NOT attempted here (would be a
  new post-hoc analysis beyond the pre-registered 2×2).
- **Contradiction flagged (rule 6, prior logs not edited):** AD5's
  entry title reads "(sign differs by FE granularity)"
  (DEEPDIVE_LOG L2436). That was a description of its two specs
  (which differed in both factors at once); as a causal attribution it
  is contradicted by this 2×2 — the sign does NOT track FE
  granularity. Any write-up must use the corrected attribution.
Files created/modified:
- scripts/93_b1_mundlak_and_2x2.py (new)
- data/processed/task93_b1_mundlak_2x2.csv (new, 16 rows)
- RELIABILITY_LOG.md (this entry). DEEPDIVE_LOG and scripts/78 read
  only.
Anything unexpected or worth flagging:
- The result cuts against B1d's stated prior (the task doc itself
  called it a "strong prior for where the flip lives") — reported
  plainly as a failed prior rather than reconciled away (AGENTS §0).
- Magnitude note: FE granularity still matters for SIZE (24+P +0.1382
  is the largest; domain FE shrinks |coef| in both sets), so the two
  factors are not orthogonal in effect — only the SIGN attribution is
  clean.
---

## [B2] — Region-4 depth reversal: composition or real effect? (script 94)
Status: PASS — gates green; MIXED result reported: composition differs (B2a) but the reversal SURVIVES the conservation control (B2b) and is NOT a range-restriction artifact (B2c)
Time started / finished: 2026-09-25 19:40 / 19:45
What I did:
- Confirmed input task79_depth_positions.csv (587 lines = 586
  positions; columns position, region, neff, cons, n_var, yE, ...) and
  located the raw results already on record (DEEPDIVE_LOG L2705-2731:
  pooled rho(yE, neff) = +0.1714 [+0.0918, +0.2471]; region4
  −0.2373 [−0.3795, −0.0853] p_boot=0.0042 n=169).
- Wrote scripts/94_b2_depth_reversal.py, docstring PRE-REGISTERING: G1
  exact region sizes {108,135,174,169}; G2 raw-recomputation tolerance
  5e-4 vs the record; B2a's "DIFFERS" rule (disjoint CIs between
  region-4 and REST(r1-3) rhos); B2b's "SURVIVES" rule (region-4
  partial negative AND CI upper < 0); B2c's "COULD produce the
  reversal" rule (pooled-in-region-4-range rho < 0), plus the
  distribution/descriptive decile tables; house machinery
  (position_cluster_bootstrap, partial_spearman_cluster_bootstrap,
  seed 0). Smoke N_BOOT=300 (1.4 s) then full N_BOOT=10000 (14.5 s),
  EXIT=0.
Actual output (real numbers and quoted source text, not a paraphrase):

Gates (verbatim): "G1 region sizes PASS: {1: 108, 2: 135, 3: 174,
4: 169}, total 586 (task's 'region 4 = 169 positions' confirmed, not
assumed)"; "G2 raw recomputation: pooled +0.1714 vs record +0.1714
(|diff|=2.17e-05); region4 -0.2373 vs record -0.2373 (|diff|=1.74e-05)
-> OK".

B2a (verbatim):
```text
pooled             n= 586  rho=+0.1093 [+0.0343, +0.1832] p_boot=0.0072
region1            n= 108  rho=+0.0306 [-0.1622, +0.2260] p_boot=0.7810
region2            n= 135  rho=-0.1369 [-0.3032, +0.0353] p_boot=0.1220
region3            n= 174  rho=+0.0835 [-0.0529, +0.2177] p_boot=0.2366
region4            n= 169  rho=+0.2865 [+0.1432, +0.4160] p_boot=0.0002
REST(regions1-3)   n= 417  rho=+0.0599 [-0.0307, +0.1499] p_boot=0.2000
DIFFERS? region4 [+0.1432,+0.4160] vs REST [-0.0307,+0.1499] -> DIFFERS (CIs disjoint) -> composition indicated
```

B2b (verbatim): "pooled partial: rho=+0.1738 [+0.0951, +0.2484]
p_boot=<1/N"; "region4 partial: rho=-0.1763 [-0.3218, -0.0222]
p_boot=0.0244"; "raw record: pooled +0.1714 -> partial +0.1738
(delta +0.0024); region4 -0.2373 -> partial -0.1763
(delta +0.0610)"; "B2b VERDICT ...: region-4 reversal SURVIVES the
conservation control (partial rho -0.1763, CI upper -0.0222)".

B2c (verbatim): "pooled neff: min=111.9 q25=1159.2 median=1198.0
q75=1212.8 max=1215.4 sd=206.7"; "region4 neff: min=111.9 q25=1142.5
median=1168.0 q75=1194.5 max=1213.1 sd=194.2"; "region4 range
[111.9, 1213.1] = 99.8% of pooled [111.9, 1215.4] range";
"78.8% of ALL positions fall inside region 4's Neff range (slice
selectivity); region-4 median Neff = 32.1% percentile of pooled";
"POOLED-in-region4-range: n=462 rho=+0.0125 [-0.0822, +0.1064]
p_boot=0.7890". Decile table (descriptive) shows mean yE by Neff
decile: +0.061, +0.064, +0.056, +0.059, +0.052, +0.102, +0.081,
+0.076, +0.085, +0.115 — flat-to-slightly-rising until a clear
HIGH-END upturn in deciles 6 and 9-10.
"B2c VERDICT ...: NOT explained by the slice alone: pooled rows in
the same Neff range correlate +0.0125 while region 4 alone is
-0.2373 -> region-specific beyond range restriction".

Verdict (plainly stated, mixed as the checks demand):
- **B2a: composition indicator PRESENT.** Region 4's
  Neff-conservation coupling (+0.2865, CI excluding 0) differs from
  the rest of the protein (+0.0599, CI including 0) — disjoint CIs.
  So region 4 IS compositionally different in exactly the Neff-vs-
  conservation relationship that could confound the reversal.
- **B2b: the reversal SURVIVES nonetheless.** Controlling
  conservation attenuates region 4's rho from −0.2373 to −0.1763
  (delta +0.0610, ~26% of the magnitude) but the partial CI
  [−0.3218, −0.0222] still excludes 0 (p_boot = 0.0244). Conservation
  explains part, not the finding.
- **B2c: NOT a range-restriction artifact by the pre-registered
  rule.** Region 4's Neff range is 99.8% of pooled (it contains the
  global minimum; there is essentially NO range restriction), and
  pooled rows within that range correlate +0.0125 (not negative).
  Honest companion observation (the nonlinearity half of B2c's
  question): the pooled +0.1714 itself collapses to +0.0125 when the
  top-124 positions (neff > 1213.1) are excluded, and the decile
  table shows the pooled positive relationship is concentrated in the
  extreme high-Neff deciles — i.e. the pooled relationship is a
  high-end upturn, not a global monotone trend. The pre-registered
  rule still fires NOT-PLAUSIBLE for a negative reversal (in-range
  pooled is ~0, not negative), so the verdict is: region-specific
  beyond range restriction, while carrying the upturn caveat.
- **Net: the region-4 reversal is a real region-specific effect that
  composition partially but not fully explains** — B2a yes differs,
  B2b survives, B2c not slice-explained.
Files created/modified:
- scripts/94_b2_depth_reversal.py (new)
- data/processed/task94_b2_depth_reversal.csv (new; smoke CSV
  task94_b2_smoke.csv from smoke)
- RELIABILITY_LOG.md (this entry). DEEPDIVE_LOG and the input CSV read
  only.
Anything unexpected or worth flagging:
- The pooled-in-range collapse (+0.1714 → +0.0125 on dropping 124
  top-Neff positions) is a stronger nonlinearity caveat about the
  pooled R1 claim ("ESM tracks depth") than B2c's question implied.
  It does not invalidate script 79's pre-registered pooled test (all
  positions, as frozen), but any write-up of R1 should note the
  relationship rides on the top deciles. Reported, not acted on.
- region4's CI [−0.3795, −0.0853] and pooled-in-range's
  [−0.0822, +0.1064] are disjoint by only 0.003 — the separation is
  real at N_BOOT=10000 but narrow; noted so it is not over-quoted.
---

## [B3] — Does AE3's clade signal survive proper controls? Size-matched null + placebo columns (script 95)
Status: PASS — gates green (after three disclosed pre-result defect fixes in the new script); verdict MIXED per the frozen rules: B3a EXCEEDS the null, B3b point-excess NOT established, B3c restate-as-generic conditional does NOT fire
Time started / finished: 2026-09-25 19:46 / 19:57
What I did:
- Verified inputs and located the exact procedures to mirror: AE3 =
  scripts/83 (DEEPDIVE_LOG L2965-3007: primary rho +0.107780
  [0.024259, 0.191756] p=0.0120, 580 eligible positions, V=104 /
  A=4,244 at match col 206, frac 0.021748); script 83's stored
  task83_ae3b_positions.csv (654 rows, 580 eligible) and
  task83_ae3b_results.csv loaded as the reproduction anchor;
  script 29's placebo convention read from its own docstring
  (scripts/29 L26-46: run the identical comparison with placebos;
  "if within the placebos' range -> the pattern belongs to the
  construction"; "the excess ... with a position-bootstrap interval,
  is the finding").
- Wrote scripts/95_b3_clade_controls.py, docstring PRE-REGISTERING:
  B3a's size-matched null (draw 104 of the 4,348 V+A pool vs the
  remaining 4,244 — exact observed group sizes, exact AE3b procedure
  re-derived per draw including the ≥30/group position floors and
  ≥50-eligible floor; N_PERM env default 1,000, seed 0; one-sided
  p = (1+#{null≥obs})/(1+N) as the PRIMARY claim, (obs−mean)/sd
  printed only as "illustrative z scale"); B3b's frozen column
  selection (dominant residue ≥50% of homologs; some other residue in
  the rarity window [0.5×, 2×] of 0.021748 = [0.010874, 0.043496];
  both groups ≥50 carriers; take by |log(frac/222frac)|, K_MAX=10,
  no window widening; fewer than 5 qualifiers = reported shortfall);
  the script-29 reading rule (actual ≤ strongest placebo = WITHIN
  PLACEBO RANGE; actual > strongest AND paired position-bootstrap
  CI of the difference excludes 0 = EXCEEDS ALL PLACEBOS; else
  point-excess only); B3c's frozen conditional (restate-as-generic
  IFF both controls indicate genericness). Machinery imported not
  copied (83's parse_a2m/LUT/scalar jsd via importlib) with a
  vectorized JSD GATED for identity (<1e-12) against the scalar form
  on the actual V/A distributions. Smoke N_PERM=100/N_BOOT=300
  (1.9 s) then full N_PERM=1000/N_BOOT=10000 (18.2 s), EXIT=0.
Actual output (real numbers and quoted source text, not a paraphrase):

Gates (verbatim, full run): "G1 PASS: 4,783 records, 630 match cols
(0 non-conforming <=1%), query[221]='A' -> col 206, query letters ==
esm2_wt_scores at all 655 positions (83's G1/G2 checks)"; "G2 pool
PASS: V=104 + A=4244 = 4348 (the task's 4,348-sequence V+A set
confirmed, not assumed)"; "G2 AE3b reproduction PASS: 580 eligible of
629 candidates (26 degenerate/undefined -> NaN, all floor-excluded);
counts identical (max diff 0), vectorized JSD vs stored max|diff|
=1.11e-16, rho +0.107779587291 == record +0.107779587291
(|diff|=0.00e+00)"; "G4 null-machinery identity PASS: actual V-group
through the per-draw path -> rho +0.107779587291, eligible 580
(== record, tol 1e-09)" (the AGENTS §4 sanity check: the null
machinery reproduces the real statistic before drawing anything).

B3a (verbatim): "draws: 1000 requested, 1000 finite (0 discarded and
counted)"; "NULL rho: mean=-0.073628 sd=0.026905 p2.5=-0.118660
median=-0.075603 p97.5=-0.016907"; "OBSERVED rho = +0.107780";
"PRIMARY (one-sided): p = (1+{null >= obs})/(1+N) = (1+0)/(1+1000)
= 0.0010"; "effect: obs - null mean = +0.181408 (illustrative z
scale only: +6.74 sd — NOT the claim)"; "B3a VERDICT ...: EXCEEDS the
null". Not one of the 1,000 random size-matched groupings produced a
rho anywhere near the real V-group's (null p97.5 = −0.0169; the null
sits on the OPPOSITE side of zero).

B3b (verbatim): "window [0.010874, 0.043496] ... 220 columns qualify;
top 10 taken by |log(frac/222frac)| (K_MAX=10, no widening)" —
placebo rhos: col 207 H +0.032239 (eligible 629); col 268 M
+0.031858; col 281 A +0.073558; col 350 Y +0.071336; col 441 P
+0.015665; col 71 K +0.030597; col 277 E +0.061016; col 362 D
+0.033901; col 513 S +0.077543; col 171 S +0.003342; "placebo rhos:
n=10, max=+0.077543, min=+0.003342; 0/10 >= actual (+0.107780)";
"PAIRED comparison on 576 shared positions (actual rho +0.104834 vs
strongest placebo col 513 rho +0.080373 on shared): diff = +0.024461
CI [-0.046428, +0.093833] p_exceeds = 0.2467 (N_BOOT=10000, seed 0)";
"B3b VERDICT (script-29 reading, frozen): point-excess only,
difference NOT established".

B3c (verbatim): "MIXED: B3a exceeds the size-matched null
(p=0.0010); B3b -> point-excess only, difference NOT established. The
two controls disagree; the restate-the-candidate conditional does NOT
fire (it requires both)."

Verdict (plainly stated, per the frozen rules):
- **B3a: specificity ESTABLISHED against group composition.** The
  real V-group's rho (+0.107780) exceeds all 1,000 size-matched
  random groupings (one-sided p = 0.0010, bounded by 1/N as
  reported). A rho of this size does not arise from drawing any 104
  of the 4,348 sequences.
- **B3b: NOT established against comparable-rarity columns.** The
  actual beats all 10 placebos point-wise (0/10 ≥ actual; max
  placebo +0.077543) — but the paired excess over the strongest
  (+0.024461) carries CI [−0.046428, +0.093833] which includes 0
  (p_exceeds 0.2467), so under script 29's own reading rule this is
  "point-excess only".
- **B3c: MIXED — the restate-as-generic statement does NOT fire** (it
  requires both controls to indicate genericness, and B3a points the
  other way decisively). Equally, B3c's full-specificity branch does
  not fire either. Honest state: AE3's candidate explanation is NOT
  refuted by these controls and NOT confirmed beyond them — it beats
  the size-matched null, its excess over rare-residue placebos is
  suggestive but unproven. Effect size unchanged and small: rho²
  ~1.2% of rank variance (stated, not buried).
- Observation for the write-up: the two null constructions sit at
  different levels (B3a's random-group null mean −0.0736 vs all-positive
  placebo rhos +0.003..+0.078) because they control different things —
  group composition at 222's column shape vs the choice of grouping
  column. Both printed; neither hidden.
Files created/modified:
- scripts/95_b3_clade_controls.py (new, pre-registered docstring)
- data/processed/task95_b3_clade_controls.csv (new; smoke CSV
  task95_b3_smoke.csv from smoke)
- RELIABILITY_LOG.md (this entry). scripts/83/79/29 and all task83
  CSVs read only; no existing result modified.
Anything unexpected or worth flagging:
- THREE defects in the new script were hit and fixed BEFORE any
  result existed (all disclosed per AGENTS §6; none changed a
  pre-registered rule, none involved raising an N to pass a check):
  (1) a syntax error (apostrophe in a single-quoted string);
  (2) the G2-range gate caught 0/0 garbage in my vectorized JSD —
  the 26 degenerate candidates (0 canonical residues in a group)
  produced NaN-poisoned negative values (min −1.358); fixed by
  marking undefined rows NaN (the original scalar jsd never saw such
  rows because 83 only calls it after its ≥30/group floors — the
  floors themselves unchanged); the gate firing here is the
  sanity-check working as designed;
  (3) an IndexError in the paired-comparison indexing (placebo JSD
  stored in eligible-space, indexed with candidate-space positions) —
  fixed by storing candidate-space with NaN off-eligible.
- Descriptive post-run addition (disclosed as post-run, touches no
  rule): several placebo minorities had exactly 104 carriers, so I
  checked whether they are the SAME sequences as the V-group —
  overlap is 0–2% per column (col 207 0/104, col 513 0/105, col 171
  2/103, etc.), i.e. the placebos are genuinely different groupings,
  not the V-group re-observed. This strengthens B3b's reading as a
  real comparison rather than weakening it.
---

## [B4] — De-biased AD4's interaction term and re-tested: null CONFIRMED as real; 96.22% of the frame is beyond 10 Å (script 96)
Status: PASS — all three gates green; B4b verdict fires the CONFIRMED branch; B4c claim verified exactly (9,232/9,595)
Time started / finished: 2026-09-25 19:58 / 20:03
What I did:
- Verified inputs directly before writing anything: task77_thermompnnD_
  doubles.csv has 10,141 rows (586 positions); analysis frame
  (own_e_b non-null) = 9,595/586 with interaction_D and ca_dist_222
  finite everywhere; mean(interaction_D) = −1.3185327539880969;
  >10 Å count = 9,232, ≤10 Å = 363 (B4c's claim confirmed at input
  stage, then re-gated in-script).
- Read AD4's original test conventions from script 77 itself
  (position_cluster_bootstrap seed 0; position_shuffle_test seed 1;
  analysis set t = v2[own_e_b.notna()]) and its logged results
  (DEEPDIVE_LOG L2327-2336: primary +0.0154 [−0.0166, +0.0465]
  p_boot=0.3406; (b) rho(interaction, dist) = +0.0246; offset mean
  −1.31853 sd 0.37904).
- Wrote scripts/96_b4_debias_interaction.py, docstring PRE-REGISTERING:
  the literal linear OLS (interaction_D ~ ca_dist_222 with intercept,
  residuals computed ONCE — the same given-variable convention AD4
  uses for interaction_D itself, disclosed), G1/G2/G3 gates (frame;
  AD4 reproduction to 5e-4; the 9,232/363 counts EXACT or STOP since
  B4c's claim would then be false as stated), AD4's exact test
  conventions for the re-test (cluster bootstrap seed 0 + position
  shuffle seed 1), B4b's frozen CI rule (excludes 0 → restate as
  calibration failure; includes 0 → null confirmed), B4c's required
  standalone-fact + Nambiar §2.4 connection printed as interpretation
  with no new test claimed, and the limitations. Smoke SMOKE=1
  (1.9 s) then full (14.4 s), EXIT=0.
Actual output (real numbers and quoted source text, not a paraphrase):

Gates (verbatim, full run): "G1 frame PASS: n=9595 / 586 positions,
interaction_D and ca_dist_222 finite everywhere"; "G2 AD4
reproduction: rho(interaction_D, own_e_b) +0.015350 vs record +0.0154
(|diff|=4.95e-05); mean -1.318533 vs record -1.31853
(|diff|=2.75e-06) -> OK"; "G3 B4c claim check PASS: >10 A =
9232/9595 (96.22%), <=10 A = 363 — matches both AD4's logged (b)
counts and the task's claimed 9,232/9,595 (~96%)".

B4a (verbatim): "de-biasing regression: interaction_D ~ ca_dist_222,
slope b = +0.000819 A^-1, R^2 = 0.001359 (distance explains 0.1359%
of the offset term's variance)"; "residuals: mean = -6.58e-16 (OLS),
sd = 0.378760 (original sd 0.379018)"; "context (AD4's (b)
recomputed): rho(interaction_D, ca_dist_222) = +0.0246"; "PRIMARY
rho(resid_D, own_e_b) = +0.0097 [-0.0221, +0.0410] p_boot=0.5382
n=9595 clusters=586"; "POSITION-LEVEL association null:
rho_pos=-0.0064 p=0.8784 (N_PERM=10000, positions=586, identity
check PASS)"; "vs ORIGINAL AD4: rho +0.0154 [-0.0166, +0.0465] ->
de-biased +0.0097 [-0.0221, +0.0410] (delta -0.0057)".

B4b (verbatim): "AD4's NULL IS CONFIRMED AS REAL, not an artifact of
the offset: the de-biased residual rho +0.0097 [-0.0221, +0.0410]
still includes 0 (p_boot=0.5382). Removing the distance-independent
offset (itself 0.1359% distance-explained) changes the association by
-0.0057."

B4c (verbatim): "STANDALONE FACT: 9232 of 9595 analysis-frame
variants (96.22%) sit BEYOND 10 A from position 222's C-alpha; only
363 (3.78%) are within 10 A. MTHFR/A222V is overwhelmingly a
long-range system." Plus the required connection printed in the
output: Nambiar §2.4 quoted as the task doc's verified
characterization ("raw, uncalibrated PLM epistasis tracks structural
contact proximity; only their calibrated epistasis reveals
long-range functional coupling"), and the interpretation labeled as
pre-registered interpretation with no new test claimed: with ~96% of
the frame beyond 10 Å, ESM-2's raw scores and ThermoMPNN's stability
term may be instruments better suited to short-range structural
coupling than the long-range regime MTHFR/A222V sits in — "a
candidate unifying reading of B1/B2/B4/A2, held as a hypothesis."

Verdict (plainly stated):
- **B4a: the de-bias barely moves anything, by measurement.**
  Distance explains 0.1359% of interaction_D's variance (R²=0.001359,
  slope +0.000819/Å); residual rho +0.0097 vs original +0.0154
  (delta −0.0057). The offset is what AD4 said it was — large
  (−1.319) and essentially distance-independent.
- **B4b: AD4's null is CONFIRMED AS REAL, not an artifact of the
  offset** (the frozen rule's CI-includes-0 branch; position-shuffle
  companion p=0.8784 agrees). Caveat printed by the script itself and
  repeated here honestly: with rank corr(interaction, dist) ≈ +0.025,
  a near-null residual result is the expected outcome — this
  confirmation is real but WEAK by construction (it rules out the
  offset-artifact mechanism specifically, nothing more).
- **B4c: the claim holds exactly** — 9,232/9,595 = 96.22% beyond
  10 Å, verified in-script and at input stage. The long-range framing
  + Nambiar §2.4 connection is printed in the script's output as the
  task requires, labeled as interpretation/hypothesis (no test
  claimed for it, per AGENTS §0).
Files created/modified:
- scripts/96_b4_debias_interaction.py (new)
- data/processed/task96_b4_debias.csv (new; smoke wrote the same path
  at N=300 and was superseded by the full run — smoke and full differ
  only in CI/p digits, disclosed)
- RELIABILITY_LOG.md (this entry). scripts/77, task77 CSV, DEEPDIVE_LOG
  read only.
Anything unexpected or worth flagging:
- Nothing unexpected: all three gates passed first try, no defects,
  no rework. The smoke CSV overwriting the full-run path is noted
  above because the same filename is used at both N (house
  convention); only the full run's numbers are cited here.
---

## [C1] — Finalized the precise-statistic definition with correct attribution: delta_esm defined in scripts 12/45, own_e_b's multiplicative construction confirmed line-by-line in lib/own_context.py
Status: PASS — every attribution claim checked against source and confirmed; the final corrected paragraph is delivered below
Time started / finished: 2026-09-25 20:04 / 20:13
What I did:
- Located every assignment site of `delta_esm` in the repo with a
  global grep for `["delta_esm"] =` across scripts/*.py (AGENTS §5:
  verify identity before reporting attribution). Matches: scripts/12,
  16, 45, 73, 74 — and nothing else. Read the exact lines:
  - scripts/12_validate_a222v_scores.py L29: `merged["delta_esm"] =
    merged["esm2_score_a222v_bg"] - merged["esm2_score"]`
  - scripts/45_c1_reconciliation.py L97: `df["delta_esm"] =
    df["esm2_score_a222v_bg"] - df["esm2_score"]`
  - (scripts/16_phase5_model_abc.py L52 writes the same quantity under
    phase-5 column names: `df["delta_esm"] = df["model_C"] -
    df["model_A"]` — equivalent, not a third definition.)
  - scripts/73/74 are GB1 / second-double-mutant contexts computing a
    local `eb["delta_esm"]` from their own delta tables — different
    datasets, not this column's definition site.
- Confirmed scripts 32/33 CONSUME rather than define, by reading each
  candidate's actual matches (the number collision means four files
  carry the numbers): `32_delta_esm_primary.py` L61-92 uses
  dropna/abs/to_numpy/PAIRS (no assignment anywhere); `
  33_delta_esm_signflip_null.py` L63-169 likewise (merge, dropna,
  groupby blocks); the stray duplicates `32_delta_esm_noise_floor.py`
  and `33_measurement_noise_control.py` also contain no assignment
  (global grep found none).
- Read `scripts/lib/own_context.py` header (L1-25) and
  `fit_interaction()` (L143-166) line-by-line, plus its `wls_line`
  docstring (L48-49) and script 29's corroborating e_b formula
  (scripts/29 L8-13: `e_b = weighted mean_c [ m_score(c) -
  expected(c) ]`).
Actual output (real numbers and quoted source text, not a paraphrase):

Definition sites (verbatim): scripts/12 L29 and scripts/45 L97 both
read `esm2_score_a222v_bg - esm2_score` — matching the task's claim
exactly, including "defined in scripts 12 and 45, not 32/33".

own_e_b construction (verbatim quotes from lib/own_context.py):
- WLS with 1/se²: header L16-18 — "per-variant fit: score(c) = base +
  c*remediation, Gaussian likelihood with known se. That is exactly
  weighted least squares with w=1/se^2, so a closed-form vectorized
  solve replaces the per-variant optimizer"; `wls_line` L48-49 —
  "Vectorized weighted least squares of y ~ 1 + x, weights 1/se^2".
- The multiplicative expectation: `fit_interaction` docstring L145-150
  — "Fit e.b / e.r: the deviation of the A222V-background arm from the
  multiplicative no-interaction expectation. expected(c) =
  single_mutant_term(c) * (b_A222V + c*r_A222V) [+ correction] where
  single_mutant_term is the fitted line when w.post > 0.5, otherwise
  the variant's mean WT-background score (per fitModels.R)."
- Code: L152-165 — `a222v_line = a222v_fitness + concs *
  a222v_remediation`; `sm = where(use_line, w_fitness + concs *
  w_remediation, w_mean_score)`; `expected = sm * a222v_line` [+ the
  fitness-dependent correction L160]; `resid = m_score - expected`;
  `e_b, e_r, df = wls_line(resid, m_se, concs, valid)`.
- Two-pass/expected-machinery also as stated: header L20-24 — "priorProb
  0.01; lod = logl - null.logl + priorLogOdds; post = logistic(lod) ...
  two-pass: fit raw e.b/e.r, fit a fitness-dependent correction via
  interpolate(), then REFIT with that correction inside expected()".
- f_bar_wt's status confirmed: the WT arm's own scores supply BOTH
  factors' inputs — `sm` is either the WT-arm fitted line (from the
  variant's four w.* scores) or literally `w_mean_score` (the WT-arm
  mean) when w.post ≤ 0.5 — so f_bar_wt sits INSIDE expected() and is
  a construction covariate, not an independent predictor, exactly as
  the task says.

FINAL, CORRECTED PRECISE-STATISTIC PARAGRAPH (the C1 deliverable):

"The project's two load-bearing quantities are defined as follows.
`delta_esm` (the ESM-2 background-shift statistic) is
`esm2_score_a222v_bg − esm2_score`: the per-variant change in ESM-2
log-odds when the scoring sequence background is switched from WT to
A222V. It is defined in `scripts/12_validate_a222v_scores.py` (L29)
and re-derived identically in `scripts/45_c1_reconciliation.py`
(L97) — not in scripts 32/33, which consume the already-defined
column (scripts/16_phase5_model_abc.py writes the same quantity as
`model_C − model_A` under phase-5 names). `own_e_b` is the
interaction term reproduced in `scripts/lib/own_context.py` from the
atlas's fitModels.R: a per-variant weighted least-squares fit of
score(c) = base + c·remediation across folinate concentrations
c ∈ {12, 25, 100, 200} with weights 1/se², where `e_b` is the
weighted-least-squares offset of the A222V-background arm's scores
(m_score) from a MULTIPLICATIVE no-interaction expectation
`expected(c) = single_mutant_term(c) × (b_A222V + c·r_A222V) [+ a
fitness-dependent two-pass correction]`, with
`single_mutant_term` = the variant's WT-arm fitted line when w.post >
0.5 and the variant's mean WT-background score otherwise (per
fitModels.R). Because the WT arm supplies `sm` in both branches,
`f_bar_wt` (and the WT-arm line) sits inside the outcome's own
construction: f_bar_wt is a construction covariate, not an
independent predictor, and any comparison or control that treats it
as a predictor must be read as conditioning on the outcome's
ingredients."

Verdict: PASS — the task's three attribution claims are all confirmed
against source: (1) delta_esm's definition sites are 12 and 45, with
32/33 consuming only; (2) own_e_b is a per-variant WLS with 1/se²;
(3) e_b is the A222V arm's deviation from a multiplicative
expectation built from the WT-arm fit, making f_bar_wt a construction
covariate. One precision added beyond the task's one-line summary (not
a contradiction): the expectation also contains the A222V single's
line factor and the two-pass fitness-dependent correction — the
paragraph above states the full formula so nothing downstream can
quote a simplification as if it were the definition.
Files created/modified:
- RELIABILITY_LOG.md (this entry; the final paragraph lives in it).
  scripts/12, 16, 29, 45, 32_*, 33_*, lib/own_context.py all read only.
Anything unexpected or worth flagging:
- The number collision the F1 task exists to fix showed up here: FOUR
  files carry the numbers 32/33 (canonical
  32_delta_esm_primary/33_delta_esm_signflip_null vs stray
  32_delta_esm_noise_floor/33_measurement_noise_control). Checked all
  four for definition sites — none define delta_esm — but any future
  attribution grep must not confuse them (F1 will remove this hazard).
- The C1 task's phrasing "expectation built from the WT-arm fit" is
  correct for the WT factor but the expectation is a PRODUCT of the
  WT term and the A222V line plus a correction; flagged above rather
  than silently paraphrased either way.
---

## [C2] — Holm-Bonferroni over a narrowly pre-registered headline family: 5/5 core members survive; the three boundary results also survive a disclosed m=8 sensitivity (with thin margins) (script 97)
Status: PASS — family pre-registered in the script docstring before any correction was computed; all five gates green; deterministic single run, EXIT=0
Time started / finished: 2026-09-25 20:14 / 20:21
What I did:
- Gathered every family p-value from its PRIMARY source on disk (never
  from memory): task_AB2_proteingym_model_comparison.csv (REF row +
  the seven V2 severity-baseline rows), task79_depth_associations.csv
  (pooled yE, cons yT1/yE, region-3), task83_ae3b_results.csv (AE3b),
  task78_thermompnn_controls.csv (AD5 SPEC A), and DEEPDIVE_LOG's
  [AD1] entry (L509-599) for the sign audit's own statistic.
- Finalized the family IN SCRIPT 97'S DOCSTRING before running, with
  two operationalizations that AD1/AB2a's original entries left open,
  both disclosed there: (1) AD1 registered NO p — its claim-bearing
  printed statistic is 123/123 buried hydrophobic→charged positive
  (L549), so its entry is the exact one-sided sign test 0.5^123 =
  9.403955e-38, with the position-clustering caveat and a
  pre-registered robustness statement (survives for ANY effective
  n ≥ 5, so clustering cannot change the verdict); (2) AB2a's formal
  gates are identity gates with no p — its entry is the conservative
  max own_p_boot over V2's seven severity-baseline rows (= 0.0; all
  seven are 0.0 at N_BOOT=10000), with the explicit note that NO
  "ESM-2 beats the baselines" test exists and none is implied.
  AD6's conservation dissociation takes the claim-bearing significant
  limb (cons/yT1 p=0.0000); the null limb (cons/yE p=0.7760) is
  printed alongside as context and not corrected toward significance.
- Pre-registered the DISCLOSED sensitivity too (core+trio = m=8), so
  the "at real risk" assessment could not be invented after seeing it.
- Wrote scripts/97_holm_family.py (Holm step-down + adjusted p's,
  frozen α=0.05, five gates G1-G5 each asserting a logged value,
  N_BOOT/N_PERM read and reported UNUSED — no draws). Ran ONCE
  (deterministic; gates as the sanity check), EXIT=0.
Actual output (real numbers and quoted source text, not a paraphrase):

Gates (verbatim): "G1 PASS: AD1's 123/123 control literal present in
DEEPDIVE_LOG.md; sign-test p = 0.5^123 = 9.403955e-38 (operationalization
disclosed in docstring)"; "G2 PASS: REF own_rho == -0.08811806424891734
(|diff| 4.2e-17 < 1e-12), own_p_boot = 0.0 (0/10000 draws, bounded below
~1e-4)"; "G3 PASS: all seven severity-baseline rows present; own_p_boot
max = 0.0 (all seven [0.0] at N_BOOT=10000)"; "G4 PASS: task79 rows
match their logged values — pooled yE p=0.0 rho=+0.171422; cons yT1
p=0.0 rho=+0.393717; cons yE p=0.7760 (null limb); region3 yE p=0.0194";
"G5 PASS: trio sources verified — AE3b p=0.012 (task83), AD6 region3
p=0.0194 (task79), AD5 SPEC A delta_esm p=0.02323873 (task78)".

PRIMARY core family (m=5, Holm step-down, α=0.05), verbatim table:
rank 1 AD6 pooled depth raw_p 0.0 thr 0.010000 reject YES adj 0;
rank 2 AD6 conservation dissoc. raw_p 0.0 thr 0.012500 YES adj 0;
rank 3 AB2a severity-baseline gate raw_p 0.0 thr 0.016667 YES adj 0;
rank 4 core −0.088 anchor raw_p 0.0 thr 0.025000 YES adj 0;
rank 5 AD1 sign audit raw_p 9.403955e-38 thr 0.050000 YES
adj 9.403955e-38; "-> 5/5 survive at family-wise alpha 0.05;
non-survivors: none".

DISCLOSED SENSITIVITY (m=8 = core + the three boundary results),
verbatim: AE3b raw_p 0.012 thr 0.016667 YES adj_p 0.036; AD6 region-3
raw_p 0.0194 thr 0.025000 YES adj_p 0.0388; AD5 SPEC A delta_esm
raw_p 0.023239 thr 0.050000 YES adj_p 0.0388; "-> 8/8 survive at
family-wise alpha 0.05".

'At real risk' assessment (verbatim): "AE3b ... adj_p=0.036000 ->
survives at alpha=0.05 (margin +0.014000)"; "AD6 region-3 ... adj_p
=0.038800 -> survives (margin +0.011200)"; "AD5 SPEC A ... adj_p
=0.038800 -> survives (margin +0.011200)"; "Honest read: at m=8 all
three SURVIVE — the 'at real risk' flag is about MARGIN, not failure:
their adjusted p's sit within 0.011-0.014 of alpha, so one or two
additional mid-range members would flip them (e.g. alpha/(m-rank+1)
at rank 6 falls below 0.0120 once m>=10)."

Verdict (plainly stated):
- **The pre-registered core family: 5/5 survive Holm at family-wise
  α = 0.05.** All four bootstrap-zero members pass at any threshold;
  AD1 (the only non-degenerate p) passes at its rank-5 threshold of
  0.05 with a margin of 12 orders of magnitude. Nothing the correction
  could do to THIS family removes a headline result.
- **The task's "at real risk" expectation for AE3b / AD6 region-3 /
  AD5 SPEC A is NOT borne out at m=8** — reported plainly per AGENTS
  §0 (a negative result for the task's expectation, not a failure of
  the analysis): all three survive, with adjusted p's 0.036/0.0388/
  0.0388. The honest flag is about MARGIN: they sit 0.011-0.014 below
  α and would flip in families of ~10+ members or with any additional
  mid-range member. Both numbers (survive; thin margin) belong in any
  write-up — quoting only one would misrepresent.
- Disclosures carried into the output: four of five core p's are
  stored 0/10000 bootstrap zeros (treating them as exact 0 makes Holm
  STRICTER for the fifth member, never permissive); p3/p4 are
  operationalizations made HERE, disclosed, not tests AD1/AB2a ran;
  no "ESM-2 beats the severity baselines" test exists; the family is
  closed now that results exist — nothing may be added to it.
Files created/modified:
- scripts/97_holm_family.py (new, family pre-registered in docstring)
- data/processed/task97_holm_family.csv (new; 13 rows = 5 core + 8
  sensitivity, one per member per family)
- RELIABILITY_LOG.md (this entry). task_AB2/task79/task83/task78 CSVs
  and DEEPDIVE_LOG read only.
Anything unexpected or worth flagging:
- The direction of the trio finding (survive, rather than fail) is the
  main thing worth flagging — the task's wording expected risk, the
  arithmetic says thin-but-clear survival at the specified family.
- Rank ordering in the printed table follows family order with a rank
  column (ties at p=0 broken by pre-registered family order), so the
  table reads 5,1,2,3,4 — cosmetic only, thresholds/verdicts computed
  from sorted ranks correctly.
- DEEPDIVE [AD1] confirms AD1 itself reported NO p-value; if a future
  write-up wants a p for the sign audit, this entry's 0.5^123
  operationalization (and its disclosed caveats) is now the on-disk
  reference rather than an ad-hoc number.
---

## [C3] — Deprecated the four cell-level-null scripts (21/24/26/28) with script 35's header convention; script 26's row-level target shuffle called out specifically
Status: PASS — all four headers written, all four files compile, every cited line reference verified against the actual files before writing
Time started / finished: 2026-09-25 20:22 / 20:25
What I did:
- Read script 35's deprecation header (scripts/35 L1-34) as the
  convention template: `DEPRECATED (date, task-ref) -- DO NOT USE THE
  <what>. Kept intact as a documented, informative dead end; the log
  entries explaining WHY it failed have value, so nothing below is
  deleted or changed.` + `WHY IT IS DEAD (numbers from <sources>)` +
  `REPLACEMENT` + `-- original docstring below, unchanged --`.
- Gathered the deprecation rationale from its primary sources:
  A1a audit (OVERNIGHT_LOG L40-41; digest GROUPS_C_TO_H_DIGEST L13
  verbatim: "resid = (13134, 4) → flips at (variant × condition) cell
  granularity in scripts/21:138, 24:140, 26:135, 28:172, 33:100;
  second violation scripts/26:85 row-level target shuffle. All
  headline CIs position-clustered as claimed"); A1b's position-block
  repair numbers (L91: position null sd 0.0156 = 1.66× cell 0.0094);
  AF3's verdict (DEEPDIVE L3102, verbatim: "the cell-level nulls in
  scripts 21, 24, 26, 28 (and script 26's row-level target shuffle)
  were NEVER re-run at position granularity — only script 33's was
  (by A1b) ... five old non-headline null outputs remain cell-level
  and must not be cited as position-level" + "no current claim rests
  on the unrepaired ones").
- VERIFIED every cited line number against the actual files before
  writing it into a header (AGENTS §5): 21:138 = `signs =
  rng.choice([-1.0, 1.0], size=Rs.shape)`; 24:140 = `eb_p, _, _ =
  wls_line(Rs * rng.choice([-1.0, 1.0], ...))`; 26:135 = same
  sign-flip, 26:85 = `fake = rng.permutation(df["target"].to_numpy())`;
  28:172 = same sign-flip. All five match the audit's citations.
- Wrote four DEPRECATED headers (inserted after each file's opening
  `""", original docstrings untouched below the marker), then
  `venv/bin/python3 -m py_compile` on all four -> "ALL COMPILE OK".
Actual output (real numbers and quoted source text, not a paraphrase):

Header structure (identical skeleton in all four, matching script 35's
convention), e.g. script 21's opening line pair: "DEPRECATED (2026-09-25,
reliability-and-decompositions task C3a) -- DO NOT CITE THIS SCRIPT'S
SIGN-FLIP NULL OUTPUTS (p-values, null distributions, and any '%
structural artifact' percentage derived from them) AS POSITION-LEVEL.
Kept intact as a documented, informative dead end; ... nothing below is
deleted or changed."

Per-script scoping (each header states exactly what is and is not
deprecated):
- scripts/21_signflip_permutation.py — its sign-flip null outputs
  (cell-level flips at verified line 138).
- scripts/24_accuracy_degradation_gauntlet.py — the null drawn at
  verified line 140.
- scripts/26_mechanical_baseline_and_recovery.py — TWO nulls named,
  specifically as the task requires: the cell-level sign-flip at
  verified line 135 AND "the ROW-LEVEL TARGET SHUFFLE at line 85 --
  `fake = rng.permutation(df["target"].to_numpy())` re-labels single
  rows, which destroys position-block structure entirely and is the
  audit's 'second violation'".
- scripts/28_confirmation_run.py — the null at verified line 172,
  plus an explicit scoping paragraph: "ONLY the cell-level null is
  marked. This file is the FROZEN confirmation run (AGENTS §10:
  executed exactly once, by design) — its split-based point estimates
  and position-clustered CIs are NOT deprecated ... NOTHING here calls
  for re-running the frozen pipeline; re-running it would require the
  user decision AGENTS §10 reserves. Do not read this header as an
  instruction to re-execute."
- All four: the shared WHY block quotes A1a's cell-granularity finding,
  A1b's 1.66× sd ratio, and AF3's verbatim "must not be cited as
  position-level" + "no current claim rests on the unrepaired ones";
  the shared REPLACEMENT block points to
  scripts/lib/position_null.py's position_shuffle_test, A1b's
  position-block sign-flip (OVERNIGHT L60: observed −0.0881, position
  null mean −0.0001, sd 0.0156, p<0.0001, ~0.1% artifact), and
  stats.position_cluster_bootstrap.

Verdict: PASS — the AF3 gap ("five old non-headline null outputs
remain cell-level and must not be cited as position-level") is now
closed at the source: the four offending files say so themselves in
their own first lines, with no re-run (as the task requires: "Ten
minutes, closes this permanently — no re-run needed"). Scoping is
deliberate and stated in each header: unlike script 35 (whose entire
output family is dead), these files carry convention-conforming
position-clustered outputs alongside the deprecated nulls, so only the
nulls are marked — whole-file deprecation would have falsely
invalidated the frozen confirmation run's CIs.
Files created/modified:
- scripts/21_signflip_permutation.py, scripts/24_accuracy_degradation_
  gauntlet.py, scripts/26_mechanical_baseline_and_recovery.py,
  scripts/28_confirmation_run.py (each: header prepended; original
  docstrings and code untouched; py_compile OK). No output CSV, log,
  or lib file touched.
Anything unexpected or worth flagging:
- TASK-DOC WORDING DISCREPANCY (flagged, not silently resolved): C3's
  title says "Deprecate the five old cell-level-null scripts" but the
  task lists only four (21, 24, 26, 28). The reconciliation from AF3's
  own text: FIVE nulls were never repaired = the four cell-level nulls
  in those four scripts + script 26's row-level target shuffle
  (script 33's fifth cell-level site was already repaired by A1b).
  Four scripts deprecate them; "five" counts nulls. If the doc's
  "five scripts" meant a different fifth file, no evidence of one
  exists anywhere in the audit trail (grep found only these four +
  33).
- No script body was executed as part of this task (header-only edit,
  per "no re-run needed"); py_compile is the only execution and is
  cited above.
---

## [C4] — Confirmed SaProt's sign audit is still correctly blocked (Z3g-h never resolved; no SaProt audit attempted); doc's "(no SaProt correlation exists yet)" parenthetical contradicted by an on-disk SMOKE rho — flagged
Status: PASS — confirmation task completed: Z3g-h is still BLOCKED per its own entry and CLOSEOUT's SUMMARY, so C4a's conditional never fired and no SaProt audit was attempted (as the task requires)
Time started / finished: 2026-09-25 20:26 / 20:30
What I did:
- Read the exact C4a spec (task doc L258-265): confirm still blocked
  behind Z3g-h/E4; conditional note about AD1's 123-set only if Z3g-h
  has since resolved; do NOT attempt the SaProt audit unless genuinely
  resolved.
- Checked Z3g-h's status at its primary sources: CLOSEOUT_LOG [Z3g-h]
  entry L1870-1879 (verbatim: "BLOCKED — open decision required (§10).
  Z3g (delta_SaProt vs e.b. with position-cluster bootstrap + the
  script-33 sign-flip/position-block nulls) and Z3h (regional split)
  never ran: the stats stage exited at a guard 2 seconds in, before any
  null or rho was computed. **No SaProt epistasis result exists yet —
  this is neither a positive nor a negative finding about the
  hypothesis; it is an unrun analysis.** Both coherent ways forward
  change frozen script 70's decision rules, which §10 reserves for the
  user") and CLOSEOUT's terminal SUMMARY L2323-2327 (verbatim:
  "BLOCKED — genuine, needs a decision from you (priority order): 1.
  **Z3g/Z3h — INSPECT THIS FIRST. Z3i waits behind it.** Script 70's
  stats stage stopped at its wt_aa-vs-structure guard: `wt_aa agrees
  with chain-A ori_aa on all scored rows: False (9595/9740)` →
  sys.exit(1) 2s in, before any null was computed").
- Verified nothing changed since that block (mtime + git evidence):
  scripts/70_saprot_delta_epistasis.py mtime Sep 23 20:32 (untouched);
  data/processed has only task_Z3f_saprot_scores{,_smoke}.csv and
  task_Z3g_saprot_{delta,summary}_smoke.csv — no full Z3g output
  exists; this session (19:03 onward) ran nothing SaProt-related;
  CLOSEOUT's window ended 18:10 with the block open.
- Searched every doc for "E4" (grep `\bE4\b|\[E4\]|E4a|E4b`): the ONLY
  matches are C4a's own sentence and an unrelated `AE4a` (binning
  |delta_ESM| in DETECTION_FLOOR_AND_MECHANISM L348). No task, entry,
  or item labeled E4 exists anywhere in docs/ or OPEN_ITEMS.md.
- Checked the doc's claim "(no SaProt correlation exists yet to
  protect)" against what is actually on disk: read
  task_Z3g_saprot_summary_smoke.csv in full (see Actual output).
Actual output (real numbers and quoted source text, not a paraphrase):

Z3g-h status: STILL BLOCKED — confirmed at both sources above, with
file-system evidence (script 70 untouched since Sep 23; no non-smoke
Z3g output file exists; the guard's own `sys.exit(1)` was "an intended
stop, NOT an infrastructure death", L1883-1884).

"E4" reference: DOES NOT EXIST as a labeled item anywhere (only the
grep matches stated above). The SaProt-blocking items that DO exist are
[Z3g-h] (CLOSEOUT L1870, the guard decision) and [U4] (OPEN_ITEMS L26,
verbatim: "Status: **BLOCKED on U4a's own preprocessing clause (AGENTS
§10 — decisions needed), NOT on budget.**"). Flagged as a probable
mis-citation in the task doc rather than silently mapped to either.

The parenthetical "(no SaProt correlation exists yet to protect)" is
NOT literally true — smoke-scale rhos exist on disk
(data/processed/task_Z3g_saprot_summary_smoke.csv, mtime 15:33 today,
from the 15:33 smoke before the 16:09 full-stage block), verbatim rows:
- primary signed, own e_b: value **−0.110167**, CI [−0.505453,
  +0.472603], p=0.600000, n=74, ci_includes_zero True;
- primary signed, published e.b: −0.116712, CI [−0.493125, +0.436404],
  p=0.553333, n=74;
- primary absolute, own e_b: **+0.191322**, CI [+0.066178, +0.513514],
  p=0.000000, n=74, ci_includes_zero False;
- primary absolute, published e.b: +0.158889, CI [−0.002134,
  +0.467757], p=0.073333, n=74;
- null rows: signflip signed observed −0.110167 null_mean +0.012628
  null_sd 0.129339 p=0.406667 survives False; signflip absolute
  observed +0.191322 null_mean +0.013299 p=0.030000 survives **True**;
  position_block signed p=0.603333 survives False; all n_perm=300.
These are SMOKE ARTIFACTS, not results: n=74 of 10,757 analysis-set
variants (0.7%), scored from task_Z3f_saprot_scores_smoke.csv = 80 rows
(vs the full Z3f deliverable's 11,940 rows), N_BOOT/N_PERM=300. The
blocking entry's own summary of state ("No SaProt epistasis result
exists yet") means no full-analysis-set result, which remains true.
Both facts are recorded here so nobody later cites the smoke's
+0.191322 or its survives=True p=0.03 as a SaProt finding, and so
nobody claims literally that zero SaProt numbers exist on disk.

Verdict: PASS — C4a's confirmation holds: the SaProt sign audit is
still correctly blocked behind Z3g-h (an open §10 user decision), so
the task's conditional ("If Z3g-h has since resolved...") did NOT fire,
the 123-set readiness note is not yet applicable (it stays as the
documented plan: AD1's 123 buried hydrophobic→charged substitutions
remain a ready-made labeled positive-control set for SaProt under the
same four-layer recipe, per C4a's own wording, once unblocked), and NO
SaProt audit was attempted in this session — zero GPU, zero model load,
zero new analysis, as the task requires. Two doc-claim defects flagged
rather than resolved silently: the phantom "E4" reference and the
"no SaProt correlation exists yet" parenthetical contradicted by the
smoke file.
Files created/modified:
- RELIABILITY_LOG.md (this entry). Everything else read only:
  CLOSEOUT_LOG.md, OPEN_ITEMS.md, task doc, scripts/70 (stat only),
  the four task_Z3*.csv files (read).
Anything unexpected or worth flagging:
- The smoke rho discovery above is the substantive unexpected item: the
  external analysis's parenthetical was written as if the disk were
  clean of SaProt correlations, but a 74-row smoke computed four of
  them (including one survives=True). Correction of record: smoke
  artifacts exist; a RESULT does not.
- "E4" resolves to nothing in this repo. If it was meant to be U4
  (the OPEN_ITEMS SaProt item), both point at the same practical
  status (blocked, §10), so the C4a verdict is unaffected either way.
---

## SUMMARY — reliability window 2026-09-25 (19:03 → 20:33): Groups V, A, B, C complete — 16 tasks, 16 entries, all PASS; Group F not attempted and flagged

**RELIABILITY_AND_DECOMPOSITIONS done through Group C: every task has
one logged entry in the mandated format (Status / Time / What I did /
Actual output with verbatim numbers / Verdict / Files / Unexpected),
each written only after its check actually ran. Group V's four
repo-state claims all held, so the external analysis's foundation stood;
Group A formalized the reliability framing (ensemble-mean lands where
Spearman-Brown predicts, but marginal); Group B's four decompositions
returned four different verdicts (control-set-driven, region-specific,
mixed, confirmed-weak) — none of them the easy answer; Group C closed
the bookkeeping (precise-statistic paragraph finalized, Holm family
5/5 survivors, four null scripts deprecated, SaProt confirmed still
blocked). Eight new scripts (90–97), all with pre-registered
docstrings, smoke-then-full at N_BOOT/N_PERM where draws existed;
script 97 deterministic and run once with gates. No GPU, no model load,
zero commits (HEAD abc7319 untouched).**

Span: 2026-09-25 19:03 (RELIABILITY_LOG.md created, FIRST ACTION) →
20:30 ([C4] finished); this SUMMARY 20:33. 16 entries (V1–V4, A1–A4,
B1–B4, C1–C4) in completion order, suggested order honored (V → A → B
→ C). Every number below is copied from its entry's own verbatim
output — nothing reconstructed from memory.

### The required lines

- **Group V verdict: PASS — all four claims confirmed.** [V1] E3/
  AB2a-FIX genuinely closed (anchor swap |diff| = 0.000e+00, 692.1 s,
  96-row CSV); [V2] all seven severity-baseline own_rhos match to 3
  decimals (0.064/0.068/0.076/0.076/0.077/0.085/0.162); [V3] script
  53 exists, IS the global-vs-specific epistasis control (G1, its own
  logged result LIMITED-GLOBAL R²_cf = 0.1535 and Part 2 SURVIVES,
  rho −0.1455 on the specific residual vs −0.0707 raw); [V4]
  CONFIRMED — RSA is a per-position constant (struct table 651 rows /
  651 unique positions / 0 duplicates; max distinct RSA per position
  = 1 across all 11,902 merged variants).
- **A1, ensemble-mean vs Spearman-Brown: the prediction HOLDS.** The
  five-member ensemble-mean delta gives rho = −0.028508 (CI
  [−0.056495, −0.000239], p_boot = 0.0484; sign-flip p = 0.0442, null
  centered) against the Spearman-Brown-predicted ~−0.030 — predicted
  value inside the CI, sign negative as predicted. |rho| rose from the
  single-member mean 0.020962 to 0.028508 (averaging helps, modestly).
  HONEST-READING CAVEAT in the entry: both p-values sit just under
  0.05 — a marginal detection, not a strong result; scope is ESM-1v
  seed replicates only (A3), no ESM-2 implication.
- **A4b: the external analysis's algebraic prediction is CONFIRMED on
  both legs** against N3's existing run — N3 shows near-zero
  delta_cal↔delta_esm (−0.0307) and fails to recover a strong
  calibrated correlation (+0.0339, M1/M2 NOT MET), with both stated
  reasons (Δφ non-monotone; severity dominates) verified directly.
- **A4c's two numbers: raw delta_cal cross-member agreement =
  0.655966; isolated shift-component (φ2'(x)·d) agreement =
  0.089806** (first-order form 0.089675; severity-only 0.664665). The
  shift number does NOT meet the 2× bar 0.168730, so the verdict is
  **MECHANICAL** — calibration did not make the interaction shift
  seed-stable; N4's pre-registered IMPROVED verdict fired correctly on
  its own (severity-contaminated) rule and is cross-flagged for the
  write-up, prior logs left unedited.
- **B1 verdict: CONTROL-SET-DRIVEN.** Mundlak within- vs
  between-position coefficients do NOT differ (ddg p=0.5675, delta_esm
  p=0.8501); the pre-registered 2×2 shows switching control set flips
  the sign at both FE granularities while switching FE position→domain
  changes magnitude only — so the sign flip is driven by the control
  set, not FE granularity. B1d's prior NOT borne out (decisive cell
  24+P = +0.1382 with the structural block absorbed). AD5's entry
  title ("sign differs by FE granularity") contradicted and flagged.
- **B2 verdict: region-specific beyond range restriction (composition
  partially, not fully, explains).** B2a region 4's Neff–conservation
  coupling +0.2865 (CI excl. 0) vs REST +0.0599 (CI incl. 0), disjoint
  CIs → differs; B2b controlling conservation attenuates −0.2373 →
  −0.1763 but the partial CI [−0.3218, −0.0222] still excludes 0
  (p_boot = 0.0244) → survives; B2c NOT slice-explained (region 4's
  Neff range = 99.8% of pooled; in-range pooled +0.0125, not
  negative). Honest companion caveat carried in the entry: pooled
  +0.1714 collapses to +0.0125 when the top-124 Neff positions drop —
  the pooled R1 relationship is a high-end upturn, noted for any
  write-up.
- **B3 verdict: MIXED.** B3a the real V-group's rho +0.107780 EXCEEDS
  all 1,000 size-matched random groupings (one-sided p = 0.0010,
  bounded by 1/N; null mean −0.073628, 0/1000 ≥ observed); B3b NOT
  established vs comparable-rarity placebos — actual beats all 10
  point-wise (0/10 ≥ actual) but the paired excess +0.024461 has CI
  [−0.046428, +0.093833] including 0 (p_exceeds 0.2467) →
  "point-excess only"; B3c restate-as-generic conditional does NOT
  fire (requires both controls) and full-specificity does not fire
  either — AE3's explanation not refuted, not confirmed; effect size
  unchanged and small (rho² ~1.2% of rank variance).
- **B4 verdict: AD4's null CONFIRMED AS REAL, with the weak-
  confirmation caveat printed.** B4a distance explains R² = 0.001359
  of interaction_D (slope +0.000819/Å); residual rho +0.0097 vs
  original +0.0154 (delta −0.0057); B4b CI includes 0 and
  position-shuffle companion p = 0.8784 → confirmed, but "expected by
  construction" at corr ≈ +0.025 — rules out the offset-artifact
  mechanism specifically, nothing more; B4c 9,232/9,595 = **96.22%**
  beyond 10 Å verified, long-range framing + Nambiar §2.4 printed as
  interpretation/hypothesis only.
- **First look (what to inspect first): [A4]'s verdict block, log
  L633–652** — the one place this session contradicts a prior frozen
  verdict (N4's IMPROVED) and issues an explicit write-up cross-flag;
  read it before anyone quotes N4. Runner-up: [B1]'s AD5-title
  contradiction (L764–769). Both are contradictions of prior logs
  flagged in place per rule 6 — prior logs were never edited.

### Group A's other two (context for the required lines)

- **A2 PASS** — the attenuation framing formalized with all three
  numbers confirmed: ceiling √0.084365 = +0.290457, delta-only
  −0.303378, fully disattenuated −0.380323; ESM-2's −0.088 sits 3.45
  sample-SDs below the five-member mean (descriptive scale context
  from n=5, not a p). Proxy-assumption banner printed in its own
  output: ESM-1v cross-seed reliability borrowed for ESM-2.
- **A3 PASS** — scope corrected against Meta's released sources: the
  five replicates are ESM-1v SEEDS; ESM-2 has one checkpoint per
  size. AC4d's unscoped wording flagged for any write-up; A2's proxy
  use is an assumption, stated as such.

### Group C verdict (closure items)

- **C1 PASS** — delta_esm's definition sites confirmed as scripts/12
  (L29) and /45 (L97), with 32/33 consuming only (four numbered files
  checked); own_e_b's WLS-with-1/se², multiplicative-expectation
  construction verified line-by-line in lib/own_context.py, so
  f_bar_wt is a construction covariate. The final corrected
  precise-statistic paragraph is delivered inside [C1].
- **C2 PASS** — Holm-Bonferroni over the pre-registered core family:
  **5/5 survive at family-wise α = 0.05** (script 97, five gates
  green). The task's "at real risk" expectation for AE3b / AD6
  region-3 / AD5 SPEC A is NOT borne out at m=8 — all three survive
  (adj p 0.036 / 0.0388 / 0.0388) — reported plainly as the negative
  result it is, with the real flag being margin (0.011–0.014 below α;
  they flip in families of ~10+ members). Two family members are
  disclosed operationalizations (AD1's 0.5^123 sign test; AB2a's
  max-of-seven baseline p), not tests the original entries ran.
- **C3 PASS** — DEPRECATED headers added to scripts 21/24/26/28 in
  script 35's exact convention (all four compile; every cited line
  verified: 21:138, 24:140, 26:135, 28:172, plus 26:85's row-level
  target shuffle called out specifically), each scoped to its null
  only so the frozen confirmation run is not over-deprecated. Task
  doc's "five scripts" vs four-listed discrepancy reconciled (five
  unrepaired nulls = four cell-level + 26's shuffle; 33's was
  repaired by A1b) and flagged.
- **C4 PASS** — SaProt sign audit still correctly blocked behind
  Z3g-h (CLOSEOUT L1870 and SUMMARY L2323: guard exit before any null
  ran; script 70 untouched; no full Z3g output exists), so the
  conditional never fired and NO audit was attempted. Two doc defects
  flagged: "E4" exists nowhere in the repo, and "(no SaProt
  correlation exists yet)" is literally contradicted by a 74-row
  SMOKE rho on disk (e.g. absolute +0.191322, survives=True p=0.03 at
  N_BOOT=300, 0.7% of the frame) — a smoke artifact, not a result;
  recorded so neither it nor the block's "no result" claim gets
  misquoted.

### Group F flag (F1 — out of scope, NOT silently skipped)

- **F1 was NOT attempted**, deliberately, and this is the flag AGENTS
  §9 requires rather than a silent skip: F1a's spec ends "One commit"
  (task doc L279) and this session's rules forbid commits outright —
  a direct conflict, resolved in favor of the no-commit rule with the
  conflict stated here. The eight file moves were also left undone so
  the repo is not parked in a half-done, uncommittable state; F1
  remains open for a session that may commit (the stray 32/33/34/
  36–40 duplicates it exists to remove were observed again this
  session in [C1], so the hazard is still live and the task still
  worth doing).

### Disclosures index (everything this session fixed, added, or flagged after seeing results — per AGENTS §6)

- A4a: task doc's stale premise caught before any re-run (N3/N4
  already exist; nothing under a frozen pipeline was touched).
- A4/B1: two prior-log contradictions flagged in place, never edited
  (N4's IMPROVED rule; AD5's entry title).
- B3: three pre-result defects fixed in the new script 95 (syntax;
  degenerate-row JSD NaN; paired-index space) — no rule changed, no N
  raised; one post-run descriptive check disclosed as such.
- B4: smoke and full run wrote the same output path (house
  convention), only full-run numbers cited.
- C2: family + both operationalizations + the m=8 sensitivity all
  pre-registered in script 97's docstring before any number existed;
  the trio-survives result reported against the task's expectation.
- C4: the smoke-rho contradiction reported rather than waved through.
- Unrelated pre-existing dirty files (CALIBRATION_LOG.md and others)
  were left exactly as found; this session's own footprint is:
  RELIABILITY_LOG.md (created), scripts 90–97 (new), scripts 21/24/
  26/28 (header-only edits), task90–task97 CSVs (+ smoke variants) —
  all uncommitted, no commits made or attempted.

