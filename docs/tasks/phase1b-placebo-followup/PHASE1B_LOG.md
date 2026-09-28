# PHASE1B_LOG — session log for `docs/tasks/phase1b-placebo-followup/PHASE1B_PLACEBO_FOLLOWUP.md`

Session executor: OpenCode · Started: 2026-09-27.

Rules in force (task doc §1, inherited from `AGENTS.md`): cached CSVs only,
no model scoring / forward passes / torch-esm imports / weight downloads;
`venv/bin/python3` only; position-cluster bootstrap, `N_BOOT=300` smoke then
`N_BOOT=10000`, `SEED=0`; pre-registration in each script's docstring before
its first run; a failed gate means STOP that task (FAIL/BLOCKED), never loosen
a threshold; protected files (`RESULTS.md`, `MTHFR_RESULTS_LOG.md`,
`PROJECT_SUMMARY_FINAL.md`, `AGENTS.md`, every prior log incl.
`PHASE1_LOG.md`) are never edited — corrections are flagged here only; no
commits, no pushes; deviations disclosed in the entry where they happen.

Entries are appended immediately after each task finishes, in S1 format.
`## SUMMARY` appended last, in S2's order.

## Template (S1, verbatim)

## [TASK ID] — [title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (verbatim, not paraphrased):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:

---

## [P1] — Inventory, provenance, and reproduction gates (script 120)
Status: PASS
Time started / finished: 2026-09-27 22:24:45 – 22:39:45
What I did:
Verified script numbering first (`ls scripts/` shows 99 as the highest
two-digit name alphabetically but `scripts/119_l1_l2_l3_cheap_checks.py`
exists; `ls scripts/12[0-2]*` → no matches), so 120–122 are free. Wrote
`scripts/120_p1_inventory_gates.py` with the full pre-registration
(construction, all gates G1–G4 + roster + Grantham tolerance, failure
behaviour) in its docstring before the first run. Read-only over the
real files; nothing written by the script. Ran the session-convention
smoke (`N_BOOT=300 SEED=0`, exit 0) then the full run
(`N_BOOT=10000 SEED=0`, exit 0); full output saved verbatim to
`docs/tasks/phase1b-placebo-followup/PHASE1B_P1_FULL_OUTPUT.txt`
(260 lines). P1 computes no bootstrap — there is nothing stochastic in
it — so smoke and full runs are identical apart from the banner label;
both were executed anyway (disclosed in the script docstring).
(a) roster parsed from `task109_placebo_rhos.csv` (frame == 'AE'),
(b) selection rules printed verbatim at runtime from scripts 82/69 with
a mechanical pre-registered keyword scan,
(c) gates G1–G4 re-derived from raw caches,
(d) literal `grep -rn -i grantham scripts/lib` + value checks.

Actual output (verbatim, not paraphrased) — full output in
`PHASE1B_P1_FULL_OUTPUT.txt`; key blocks:

```
  site placebos (A222_X, X not in {A,V}): n=18
  target A222V (__A222V__): n=1
  AE2 (AV_<pos>): n=38
  FASTA cross-check: fasta[p-1] == table wt_aa for 655/655 positions (12445 rows, positions 2..656, FASTA length 656)
  P1(a) PASS: 38/38 AE2 positions have WT residue Ala (esm2_wt_scores.csv; FASTA mapping confirmed
```
(the 57-row roster table with position/wt/FASTA/class per bg_id is in
the full-output file; every AE2 row shows `A  A`.)

Selection rules, verbatim quotes read at runtime (line numbers as
printed):

```
  --- AE selection: AE1/AE2 definitions + subset rule + scoring: scripts/82_ae_position_vs_identity.py lines 24-47 (verbatim) ---
    28:   AE2 (task L324-329): A>V at every OTHER Ala position (WT table rows
    29:      wt_aa==A, position!=222, mut_aa==V = 38 backgrounds; measured
    30:      before writing: 39 Ala positions total, 38 excluding 222). Same
    31:      construction; compared against AE1's sweep.
    34:   * subset rule: scripts/63's draw_subset/check_subset IMPORTED
    35:     (importlib; module guards __main__): pool = WT-table positions
    36:     MINUS ({222} U the 38 other-Ala positions) = 616 positions, draw
    37:     AE_N_SUB=120 with AE_SEED=0 — one subset, identical for all 57
    42:     scripts/lib/sequence.load_sequence, model = ESM-2 t33 650M
    43:     (esm2_t33_650M_UR50D) — the SAME model and code path that
    47:     pass per (background, position), as in M1.
   228:     ae2["bg_id"] = ["AV_" + str(int(p)) for p in ae2["position"]]
  --- W-series selection rule (W1): scripts/69_w_decile_background_rescore.py lines 23-50 (verbatim) ---
    23: W1 selection (deterministic, no randomness anywhere):
    24:   * Distribution for deciles = the `esm2_score` column of
    25:     data/processed/esm2_wt_scores.csv, ALL 12,445 rows (literal reading
    41:   * Within each bin: rows sorted by (esm2_score, position, mut_aa)
    44:     position's most damaging substitution inside the bin), then positions
    45:     already chosen for an earlier bin are dropped.  Take THREE picks from
    46:     the remaining list L: slot A = L[0] (bin's most damaging), slot B =
    47:     L[len(L)//2] (middle), slot C = L[-1] (least damaging).  10 bins x 3
    48:     slots = 30 backgrounds (task: "~20-30").  Gates: every bin yields
  No score/fitness keyword in the quoted rule for the AE grid/AE2 rule (script 82) (mechanical scan of 35 lines over ['esm2_score', 'fitness', 'severity', 'damaging', 'decile', 'own_e']).
  !! FLAG (P1b): selection rule for the W-series rule (script 69) contains score/fitness keywords: {'esm2_score': [24, 41], 'decile': [24, 26], 'severity': [31], 'damaging': [44, 46, 47]}
     Pre-registered reading: the rule is score-based iff its own text says so (above). The W-series rule is chosen by deciles of the MODEL's own severity column (esm2_score, ESM-2's WT-background log-prob severity), NOT by measured fitness (own_e_b) and NOT by rho_b. It bears on how the group may be used as a null: severity-stratified by design.
```

Gates:

```
  [G1] task109_placebo_rhos.csv rows=175 (expect 175), frame==AE rows=57 (expect 57)
  G1 PASS
  [G2] recompute from raw: rows 129960 -> own_e_b non-null 110124 -> after G6 drops (0) 110124; backgrounds=57
  [G2] max|diff| over 57 AE backgrounds = 9.714e-17 (gate < 1e-9)
  G2 PASS
  [G3] A222V AE rho = -0.104321772935 vs doc -0.104322 (diff 2.271e-07)
  [G3] AE1 mean = -0.055208774237 (n=18, doc n=18) vs doc -0.055209 (diff 2.258e-07)
  [G3] AE2 mean = -0.010138067782 (n=38, doc n=38) vs doc -0.010138 (diff 6.778e-08)
  G3 PASS
  [reported, NOT gated -- task G3 lists only the three values above]:
    W  A222V rho = -0.072547470 vs doc -0.072547 (diff 4.696e-07)
    COMMON A222V rho = -0.104044159 vs doc -0.104044 (diff 1.586e-07)
    AE 56-placebo mean = -0.024625081 (n=56) vs doc -0.024625 (diff 8.057e-08)
  [G4] anchor rho = -0.08811806424891734 | doc -0.088118 (diff 6.425e-08) | full precision record -0.08811806424891734 (diff 0.000e+00)
  [G4] rows=10757 (doc table: 10,757), positions=654 (doc table: 654)
  G4 PASS
```

Grantham gate (task P1(d)):

```
scripts/lib/features.py:5:# Grantham (1974) per-amino-acid composition, polarity, molecular volume.
scripts/lib/features.py:9:_GRANTHAM = {
scripts/lib/features.py:21:def grantham(a, b):
  implementation: scripts/lib/features.py::grantham (loaded OK); tolerance |value - published| <= 1.0 (pre-registered; see docstring)
    A-V: computed 64.4303 vs published 64 |diff|=0.4303 -> PASS
    I-V: computed 29.6091 vs published 29 |diff|=0.6091 -> PASS
    L-V: computed 31.7848 vs published 32 |diff|=0.2152 -> PASS
    L-I: computed 4.8551 vs published 5 |diff|=0.1449 -> PASS
    F-Y: computed 21.6097 vs published 22 |diff|=0.3903 -> PASS
    C-W: computed 214.3624 vs published 215 |diff|=0.6376 -> PASS
    symmetry: max|g(a,b)-g(b,a)| over 20x20 = 0.000e+00 (gate < 1e-12) -> PASS
    zero diagonal: max|g(a,a)| over 20 = 0.000e+00 (gate == 0.0) -> PASS
  GRANTHAM GATE PASS: P3's primary metric (Grantham) is usable.
```

```
  G1 PASS  G2 PASS (max|diff| 9.714e-17)  G3 PASS  G4 PASS  GRANTHAM GATE PASS
  AE roster: 18 site placebos + A222V + 38 AE2 = 57
  fitness-relatedness: AE rule keyword hits=none; W rule keyword hits={'esm2_score': [24, 41], 'decile': [24, 26], 'severity': [31], 'damaging': [44, 46, 47]} -> FLAG: W selection is score-based (see above)
Elapsed 0.7s
```

Verdict: PASS. All four reproduction gates pass at their pre-registered
thresholds; the roster is exactly 18 + A222V + 38 with every AE2
position confirmed Ala from two sources; the Grantham implementation is
present and matches the published table at the table's precision, so
**P3's primary metric is NOT blocked**.
Files created/modified: `scripts/120_p1_inventory_gates.py` (new);
`docs/tasks/phase1b-placebo-followup/PHASE1B_P1_FULL_OUTPUT.txt` (new);
`PHASE1B_LOG.md` (this entry). Nothing else; no cached input touched.
Anything unexpected or worth flagging:
1. **FLAG (P1(b), prominently): the W-series selection rule is
   score-based.** `scripts/69` lines 24/41/44–47 (quoted verbatim
   above) choose the 30 W backgrounds as deciles of `esm2_score` — the
   MODEL's own severity column — and take "most damaging / middle /
   least damaging" per decile. It is *not* measured fitness
   (`own_e_b`) and not ρ_b, but W is severity-stratified by design;
   W may not be treated as a fitness-blind null. The AE rules
   (enumeration of all 38 non-222 Ala positions + a seed-0 uniform
   draw of 120 grid positions from a 616-position pool) contain no
   score/fitness term at all.
2. Grantham tolerance `|value − published| ≤ 1.0` is a pre-registration
   choice I made (the task doc gives no tolerance): set from
   `features.py`'s own docstring ("max deviation 0.87 (the published
   table is integer-rounded)") before running, and disclosed in the
   script docstring, including that I hand-checked the six pairs
   against the published formula while writing that docstring. Two
   pairs (I–V 0.6091, C–W 0.6376) exceed 0.5, so a strict
   round-to-integer check would have failed them; the pre-registered
   ≤1.0 (table precision) passes all six. Nothing was tuned after a
   result was seen.
3. The task's G3 gates only three recorded values; I reported (did not
   gate) the other three table values (W/COMMON A222V, AE mean), all
   within 6.4e-7 of the doc's 6-dp values.
4. P1 has no bootstrap statistic, so the mandated smoke/full pair is
   identical apart from the banner label — both runs executed,
   disclosed above (deviation from "smoke then full" in spirit, kept
   in letter).
5. `grep -rn -i grantham scripts/lib` also prints two `__pycache__`
   "Binary file ... matches" lines; the verbatim grep output is in the
   full-output file.

---

## [P2] — Same-site vs same-substitution contrast (script 121; EXPLORATORY)
Status: PASS (ran to completion under its pre-registered rule; result
is NOT DISTINGUISHABLE)
Time started / finished: 2026-09-27 22:40:00 – 22:47:27 (P2/P3/P4 are
one script, one run, by the task doc's design — all three finished
together; entries written immediately after)
What I did:
Wrote `scripts/121_ae_placebo_probe.py` with the full pre-registration
(construction, groups S/V, gates G-121.1..4, both inference schemes,
the decision rule, the interpretation guard, RNG streams, NaN policy)
in its docstring before its first run. The AE frame is built
line-for-line from script 109's construction (which P1/G2 gated at
max|diff| 9.714e-17 against the raw caches). Smoke run
`N_BOOT=300 N_PERM=300 SEED=0` ran twice: the first two attempts
crashed on code bugs (see below) and were fixed *before* any full run —
no gate, threshold, or decision rule was touched. The third smoke run
exited 0 in 5.96 s; extrapolating (AGENTS §1) the full run at 10,000
draws to ≈170 s, the full run `N_BOOT=10000 N_PERM=10000 SEED=0`
exited 0 in 150.54 s (22:44:57–22:47:27). Full output saved verbatim to
`docs/tasks/phase1b-placebo-followup/PHASE1B_P2_FULL_OUTPUT.txt`
(115 lines; `PHASE1B_P3_FULL_OUTPUT.txt` and `PHASE1B_P4_FULL_OUTPUT.txt`
are byte-identical copies of the same single run — one script serves
P2+P3+P4 per the task doc).

Actual output (verbatim, not paraphrased):

```
[G-121.1] input shapes
  task109 CSV rows = 175 (expect 175); AE frame rows = 57 (expect 57)
  S (A222_X, X not in {A,V}) = 18 (expect 18); V (AV_*) = 38 (expect 38); disjoint=True; union = 56 (expect 56)
  G6 rows dropped (target pos == bg pos) = 0
  rows per background: min=1932 max=1932 (Phase 1 recorded 1932); identical (position, hgvs_pro) sets across all 57 backgrounds: True
  G-121.1 PASS
[G-121.2] point rhos vs task109_placebo_rhos.csv
  max|diff| over 57 backgrounds = 9.714e-17 (gate < 1e-9)
  G-121.2 PASS
[G-121.3] bootstrap identity: every cluster exactly once -> max|diff| vs point rhos = 0.000e+00 (gate < 1e-12)
  G-121.3 PASS
  position-cluster draws: 10000 x 57 rho recomputed on resampled rows (stream SEED+0); draws with any NaN = 0

--------------------------------------------------------------------------
P2 -- SAME-SITE (S, n=18) vs SAME-SUBSTITUTION (V, n=38) CONTRAST  [EXPLORATORY]
--------------------------------------------------------------------------
  mean rho_b(S) = -0.055208774 (n=18)
  mean rho_b(V) = -0.010138068 (n=38)
  D = mean(S) - mean(V) = -0.045070706
  bootstrap (position-cluster, 10000 draws, SEED+0): D CI 95% = [-0.107025598, +0.017286053] (valid draws 10000/10000, NaN dropped 0)
  bootstrap sd(D) = 0.032070135
  label permutation (10000 shuffles of S/V labels over the 56, two-sided, SEED+1): p = (1 + 13) / (1 + 10000) = 0.001400
  label check: each shuffle keeps n(S)=18, n(V)=38 (mechanical: lab.sum()==18 by construction)
  A222V rho (AE frame) = -0.104321773; signed rank within S u {A222V} (n=19) = 1; within V u {A222V} (n=39) = 1 (rank 1 = most negative; reported, NOT tested)
  P2 RULE (pre-registered): CI excludes 0 -> NOT DISTINGUISHABLE
  P2 IS EXPLORATORY either way.
  INTERPRETATION GUARD (verbatim from the task doc): "A222V shares the site with S and the substitution with V. D < 0 means shared site tracks A222V's e.b more than a shared substitution does. That is compatible with a real site-specific effect; it is NOT evidence of a generic artifact and NOT evidence of A222V-specificity."
```

Verdict: **NOT DISTINGUISHABLE** under the pre-registered rule (the
position-cluster bootstrap CI of D, [−0.107025598, +0.017286053],
includes 0). The rule keys on the bootstrap CI; the label-permutation
p (0.001400) is reported alongside it without changing the verdict.
EXPLORATORY either way; the interpretation guard is printed by the
script with the result.
Files created/modified: `scripts/121_ae_placebo_probe.py` (new);
`PHASE1B_P2_FULL_OUTPUT.txt`, `PHASE1B_P3_FULL_OUTPUT.txt`,
`PHASE1B_P4_FULL_OUTPUT.txt` (new, copies of this run);
`PHASE1B_LOG.md` (this entry). No cached input touched.
Anything unexpected or worth flagging:
1. **The two inference schemes disagree in appearance and must not be
   conflated:** the label-permutation p is small (0.0014) — the
   observed D is unusual under label exchange *conditioning on the
   observed ρ_b* — while the position-cluster bootstrap CI (which
   recomputes all 56 ρ_b from raw scores on resampled positions, i.e.
   propagates their sampling error) spans 0. The pre-registered rule
   uses the CI → NOT DISTINGUISHABLE. Reporting the permutation p
   alone as a "site effect" would be exactly the kind of
   metric-picking AGENTS §0 forbids; both numbers are logged.
2. Smoke-run code bugs, fixed before the full run, thresholds
   untouched: (a) `ValueError: Invalid format specifier` in the P4
   f-string `#{b: rho_b <= rho_A222V}` (braces needed escaping);
   (b) `TypeError: unsupported format string passed to method.__format__`
   from `w_rec.median` (pandas Series attribute resolving to the
   `.median` method → `w_rec["median"]`). The 300-draw smoke had
   already produced the same qualitative verdicts (CI spanning 0; T
   negative) before either fix, and the fixes changed no statistic's
   construction.
3. A222V is rank 1 (most negative ρ_b) in *both* S∪{A222V} and
   V∪{A222V} — reported, not tested, per the task.

---

## [P3] — Similarity-to-valine gradient within S (script 121; EXPLORATORY)
Status: PASS (ran to completion under its pre-registered rule; result
is NOT RESOLVED)
Time started / finished: 2026-09-27 22:40:00 – 22:47:27 (same single
run as P2; entry written immediately after)
What I did:
Same pre-registered script 121 (see [P2]). For the 18 A222X
backgrounds: d_b = Grantham(X, V) via `scripts/lib/features.py`
(gated by P1(d) at PASS; `G-121.4` re-checks import + 18 finite d_b),
T = Spearman(ρ_b, d_b); inference = the same position-cluster draws as
P2 (seed+0, 10,000 draws, pre-registered shared stream), 10,000-shuffle
two-sided label permutation (seed+2), 18 leave-one-out fits, bootstrap
SE and the mandated minimum-detectable |T| ≈ 2.8 × SE; decision rule
(SUPPORTED / REVERSED / NOT RESOLVED) fixed in the docstring before
the run; secondary metrics BLOSUM62 and |ΔKD| computed and reported
side by side with their direction conventions, never selected among.

Actual output (verbatim, not paraphrased):

```
  [G-121.4] grantham import OK; 18 finite d_b (range [21.5, 191.2]) -> PASS
  d_b = Grantham(X, V) for X in the 18 A222X (PRIMARY metric, fixed in the pre-registration)
  T = Spearman(rho_b, d_b) over the 18 = -0.182662539 (prediction if the anchor tracks A222V-like structure: more V-like -> more negative rho_b -> T > 0)
  bootstrap T (same SEED+0 draws as P2): 95% CI = [-0.605779154, +0.364293086] (valid 10000/10000, NaN dropped 0)
  bootstrap SE(T) = 0.256865386 -> minimum detectable |T| approx 2.8 x SE = 0.719223081  (n=18 is small; stated as the task requires)
  label permutation (10000 shuffles of d_b across the 18, two-sided, SEED+2): p = (1 + 4627) / (1 + 10000) = 0.462754
  leave-one-out range of T: [-0.284313725, -0.056372549] (n=18 fits; T > 0 in 0/18)
```
(all 18 individual leave-one-out lines — drop C −0.056372549 … drop Y
−0.144607843 — are in `PHASE1B_P3_FULL_OUTPUT.txt`; every one is
negative)

```
  18-row table sorted by d_b (X, d_b, rho_b, this-run bootstrap CI, Phase 1 recorded CI):
    X=M  d_b=  21.5  rho_b=-0.056981636  CI_this=[-0.127311,+0.014029]  CI_phase1=[-0.127430,+0.013553]
    X=I  d_b=  29.6  rho_b=-0.074744224  CI_this=[-0.136474,-0.010560]  CI_phase1=[-0.137712,-0.010153]
    X=L  d_b=  31.8  rho_b=-0.060453465  CI_this=[-0.126583,+0.006378]  CI_phase1=[-0.126869,+0.005987]
    X=F  d_b=  49.9  rho_b=-0.036052443  CI_this=[-0.097241,+0.024523]  CI_phase1=[-0.096778,+0.025109]
    X=Y  d_b=  54.7  rho_b=-0.022036412  CI_this=[-0.083549,+0.038912]  CI_phase1=[-0.083042,+0.039776]
    X=P  d_b=  67.8  rho_b=-0.079329771  CI_this=[-0.136132,-0.020527]  CI_phase1=[-0.135937,-0.019752]
    X=T  d_b=  69.5  rho_b=-0.103143738  CI_this=[-0.163864,-0.039305]  CI_phase1=[-0.162975,-0.040722]
    X=H  d_b=  83.9  rho_b=-0.009998551  CI_this=[-0.076304,+0.055246]  CI_phase1=[-0.077287,+0.055495]
    X=W  d_b=  88.0  rho_b=-0.027606618  CI_this=[-0.088975,+0.035339]  CI_phase1=[-0.090793,+0.035436]
    X=R  d_b=  95.8  rho_b=-0.041544813  CI_this=[-0.108839,+0.025513]  CI_phase1=[-0.108276,+0.026103]
    X=Q  d_b=  96.3  rho_b=-0.055907333  CI_this=[-0.126285,+0.014749]  CI_phase1=[-0.127079,+0.013236]
    X=K  d_b=  97.0  rho_b=-0.033997855  CI_this=[-0.103003,+0.034719]  CI_phase1=[-0.104057,+0.035356]
    X=G  d_b= 108.8  rho_b=-0.013732276  CI_this=[-0.082969,+0.054333]  CI_phase1=[-0.083482,+0.054777]
    X=E  d_b= 121.3  rho_b=-0.070808815  CI_this=[-0.137325,-0.003943]  CI_phase1=[-0.137592,-0.003748]
    X=S  d_b= 123.0  rho_b=-0.067244952  CI_this=[-0.127276,-0.004335]  CI_phase1=[-0.128057,-0.005908]
    X=N  d_b= 132.9  rho_b=-0.060415888  CI_this=[-0.127477,+0.006108]  CI_phase1=[-0.128494,+0.007575]
    X=D  d_b= 152.0  rho_b=-0.081138735  CI_this=[-0.145796,-0.015624]  CI_phase1=[-0.148578,-0.015530]
    X=C  d_b= 191.2  rho_b=-0.098620412  CI_this=[-0.161751,-0.034699]  CI_phase1=[-0.163621,-0.034968]
  P3 RULE (pre-registered): CI lower bound > 0 (False) AND T > 0 in all 18 LOO (False); CI upper bound < 0 (False) -> NOT RESOLVED
  REQUIRED WORDING for NOT RESOLVED: "n=18 cannot resolve this," never "the gradient is flat".
  SECONDARY (descriptive only; no decision rests on these; all reported, never selected among):
    BLOSUM62(V, X): SIMILARITY metric (gradient predicts T < 0); T = -0.388909932, bootstrap CI [-0.727767689, +0.125729786]
    |dKD| (Kyte-Doolittle): DISTANCE metric (gradient predicts T > 0); T = +0.182575070, bootstrap CI [-0.308121364, +0.557087369]
```

Verdict: **NOT RESOLVED** — reported exactly as mandated: "n=18 cannot
resolve this," never "the gradient is flat." The observed primary
T = −0.182662539 is opposite in sign to the pre-stated prediction
(T > 0), but its bootstrap CI [−0.605779154, +0.364293086] spans 0, the
label-permutation p = 0.462754 shows nothing beyond chance, all 18
leave-one-out fits are negative (so SUPPORTED's second condition fails
decisively), and the CI's upper bound is not < 0 (so REVERSED fails).
With SE(T) = 0.256865386 the minimum detectable |T| ≈ 0.719223081, so
n=18 had no realistic chance of resolving a gradient of plausible
size. BLOSUM62 (T = −0.388909932, CI [−0.727767689, +0.125729786]) and
|ΔKD| (T = +0.182575070, CI [−0.308121364, +0.557087369]) both span 0
too; their signs disagree with each other, which is itself consistent
with noise. All three reported; no decision rests on the secondaries;
Grantham (the pre-registered primary) governs.
Files created/modified: none beyond those listed in [P2] (same run;
`PHASE1B_P3_FULL_OUTPUT.txt` is the verbatim full output).
Anything unexpected or worth flagging:
1. The primary point estimate is negative (opposite to the
   pre-stated T > 0 prediction). It is NOT RESOLVED, not REVERSED —
   the CI spans 0 — and it must not be described as "the gradient is
   flat" or as a reversal. Exploratory/post-hoc either way.
2. The three similarity metrics disagree in sign (Grantham −, BLOSUM62
   − on a similarity scale, |ΔKD| + on a distance scale): reported
   side by side exactly so no metric can be cherry-picked; only
   Grantham was pre-registered as primary.
3. Per-background "CI_this" vs "CI_phase1" columns agree closely but
   not exactly (different bootstrap streams; both are valid
   position-cluster CIs) — e.g. S: [−0.127276, −0.004335] vs
   [−0.128057, −0.005908]. Recorded Phase 1 CIs shown unchanged.

---

## [P4] — Non-site placebos only (script 121; DESCRIPTIVE)
Status: PASS
Time started / finished: 2026-09-27 22:40:00 – 22:47:27 (same single
run as P2/P3; entry written immediately after)
What I did:
Same pre-registered script 121. Restricted to non-site placebos: the
38 `AV_*` (V group, AE frame) and the 30 W-series backgrounds (W
frame). For each: n, mean ρ_b, background-bootstrap 95% CI (10,000
draws, stream seed+4, V then W in that fixed order), median, range,
A222V's frame-matched signed rank, and p_spec =
(1 + #{ρ_b ≤ ρ_A222V})/(1 + n). Cross-checked the W group's
deterministic quantities against F1's recorded summary row
(`task109_distribution_summary.csv`). No decision rule (none was
pre-registered).

Actual output (verbatim, not paraphrased):

```
  [V (AE2, AE frame)] n=38 mean=-0.010138068 background-bootstrap 95% CI=[-0.025250004,+0.006068308] (N_BOOT=10000, stream SEED+4) median=-0.022696950 range=[-0.094598010,+0.116091440]
    A222V rho (frame-matched) = -0.104321773; signed rank in group u {A222V} = 1/39 (rank 1 = most negative); # {b : rho_b <= rho_A222V} = 0; p_spec = (1 + 0) / (1 + 38) = 0.025641026
  [W (W frame)] n=30 mean=-0.016421191 background-bootstrap 95% CI=[-0.032881444,-0.000116764] (N_BOOT=10000, stream SEED+4) median=-0.020178655 range=[-0.130455833,+0.086283923]
    A222V rho (frame-matched) = -0.072547470; signed rank in group u {A222V} = 3/31 (rank 1 = most negative); # {b : rho_b <= rho_A222V} = 2; p_spec = (1 + 2) / (1 + 30) = 0.096774194
  F1 recorded (task109_distribution_summary.csv) side by side:
    [W] F1: n=30 mean=-0.016421191 median=-0.020178655 range=[-0.130455833,+0.086283923] rank_signed=3 mean CI=[-0.032867760,+0.000010545]
    [W] deterministic quantities identical to F1 (n/mean/median/range/rank): True (must be True; a False would be a bug -- reported plainly)
    [W] CI comparison: this run [-0.032881444,-0.000116764] vs F1 [-0.032867760,+0.000010545] -- fresh bootstrap stream, small differences expected
    [AE-frame F1 record = ALL 56 placebos, a DIFFERENT set than V's 38, context only]: n=56 mean=-0.024625081 mean CI=[-0.036997660,-0.011453351]
  POST-HOC, DESCRIPTIVE; does not replace F1d; may not be cited as support for background-specificity.
  No decision rule for P4 (none pre-registered; none applied).
```

Verdict: DESCRIPTIVE ONLY — no decision, as pre-registered. The block
is labelled verbatim in the output: `POST-HOC, DESCRIPTIVE; does not
replace F1d; may not be cited as support for background-specificity.`
Its purpose is served: the non-site placebos (V, W) are now reported
on their own so the AE1 same-site contamination can't be silently
carried into a write-up.
Files created/modified: none beyond those listed in [P2] (same run;
`PHASE1B_P4_FULL_OUTPUT.txt` is the verbatim full output).
Anything unexpected or worth flagging:
1. W's deterministic quantities (n/mean/median/range/rank) are
   **bit-identical to F1** (check printed `True`) — reproduction of
   the recorded W numbers confirmed. The W background-bootstrap CI
   from this run [−0.032881444, −0.000116764] barely EXCLUDES 0 while
   F1's recorded CI [−0.032867760, +0.000010545] barely INCLUDES it —
   a fresh-stream difference at a boundary-hugging endpoint; both are
   printed; neither is a decision (P4 has no rule; F1d stands).
2. V group's p_spec = 0.025641026 (0 of 38 placebos ≤ A222V's ρ) —
   this is the same-formula quantity Phase 2 will use on the full
   frame, reported here descriptively on n=38 cached positions; it is
   NOT a confirmatory p-value (positions subset, post-hoc group).
3. F1's AE-frame row covers all 56 placebos, not V's 38; printed
   explicitly labelled "DIFFERENT set … context only" to prevent
   conflation.

---

## [Q1] — Feasibility and cost audit (read-only, inline commands)
Status: PASS
Time started / finished: 2026-09-27 22:48:00 – 22:52:30
What I did:
Read-only audit of scripts 63/69/82 and their library calls (no model
run, no torch/esm import — greps/awk/stat/inline `venv/bin/python3`
over cached CSVs only). Every command and its output is verbatim below.

Actual output (verbatim, not paraphrased):

(a) model size/checkpoint — command:
`grep -n "esm2_t33\|650M\|load_model\|esm.pretrained\|alphabet\|batch_converter" scripts/63_m1_context_shift_vs_severity.py scripts/69_w_decile_background_rescore.py scripts/82_ae_position_vs_identity.py scripts/lib/esm_scoring.py scripts/11_score_a222v_background_esm2.py`

```
scripts/63_m1_context_shift_vs_severity.py:282:    print("Loading ESM-2 650M...")
scripts/63_m1_context_shift_vs_severity.py:283:    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
scripts/69_w_decile_background_rescore.py:58:    model ESM-2 650M, eval mode, deterministic.
scripts/69_w_decile_background_rescore.py:328:    print("Loading ESM-2 650M...")
scripts/69_w_decile_background_rescore.py:330:    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
scripts/82_ae_position_vs_identity.py:42:    scripts/lib/sequence.load_sequence, model = ESM-2 t33 650M
scripts/82_ae_position_vs_identity.py:43:    (esm2_t33_650M_UR50D) — the SAME model and code path that
scripts/82_ae_position_vs_identity.py:283:    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
scripts/11_score_a222v_background_esm2.py:50:    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
```
→ ESM-2 t33 650M, checkpoint `esm2_t33_650M_UR50D`, identical in every
scoring script (10/11/12/63/69/82 lineage).

(b) scoring method — `scripts/lib/esm_scoring.py` verbatim (read via
the Read tool, lines 1–38):

```
1: """ESM-2 masked-marginal scoring -- the core reusable scoring function."""
17: def get_position_logprobs(model, alphabet, batch_converter, sequence, position_1idx, device):
18:     """One forward pass at position_1idx. Returns dict of {amino_acid: score}
19:     for all 19 non-wildtype substitutions (masked-marginal log-odds vs WT)."""
23:     masked_seq = sequence[:idx0] + "<mask>" + sequence[idx0 + 1:]
27:     with torch.no_grad():
28:         out = model(tokens, repr_layers=[], return_contacts=False)
35:     return {
36:         aa: log_probs[alphabet.get_idx(aa)].item() - wt_score
37:         for aa in AA_LIST if aa != wt_aa
38:     }
```
and `scripts/82_ae_position_vs_identity.py` lines 239–243:

```
239: def score_all(bg, wt_seq, subset, part_path=None):
240:     """One forward pass per (background, position); 650M, eval mode;
```
→ Method = **masked-marginal**: mask the target position, one forward
pass, log-softmax at that position, subtract the WT residue's log-prob
(log-odds vs WT). **Forward passes per (background, position) = 1**
(one pass yields all 19 non-WT substitution scores).

(c) device and recorded runtime/timing — command:
`grep -n -i "device" scripts/63_*.py scripts/69_*.py scripts/82_*.py`

```
scripts/63_m1_context_shift_vs_severity.py:280:    device = get_device()
scripts/63_m1_context_shift_vs_severity.py:281:    print(f"Using device: {device}")
scripts/69_w_decile_background_rescore.py:326:    device = get_device()
scripts/69_w_decile_background_rescore.py:327:    print(f"Using device: {device}")
scripts/82_ae_position_vs_identity.py:280:    device = get_device()
scripts/82_ae_position_vs_identity.py:281:    print(f"Using device: {device}")
```
with `scripts/lib/esm_scoring.py` lines 9–14:

```
9:  def get_device():
10:     if torch.cuda.is_available():
11:         return torch.device("cuda")
12:     elif torch.backends.mps.is_available():
13:         return torch.device("mps")
14:     return torch.device("cpu")
```
Device as actually used, from recorded prior-run log lines — command
`grep -rn "Using device\|ms/pass\|projection for 30\|projected total\|backgrounds scored in\|scored in " docs/ --include="*.md"`:

```
docs/tasks/comparators-and-consolidation/SESSION_LOG.md:1929:Using device: mps
docs/tasks/comparators-and-consolidation/SESSION_LOG.md:2630:Using device: mps
docs/tasks/comparators-and-consolidation/SESSION_LOG.md:2633:M1b-timed: background 1/1 D1A_V179W -> 61.7 s for 120 positions (514 ms/pass)
docs/tasks/comparators-and-consolidation/SESSION_LOG.md:2634:(g6) t1=61.7s for the first background; projection for 30 = 1850.9s (budget 5400s)
docs/tasks/comparators-and-consolidation/SESSION_LOG.md:2637:M1b-timed: background 29/29 D10C_I488V -> 75.1 s for 120 positions (626 ms/pass)
docs/tasks/comparators-and-consolidation/SESSION_LOG.md:2642:backgrounds x 120 positions = 3,600 forward passes; 514–626 ms/pass) —
docs/tasks/detection-floor-and-mechanism/DEEPDIVE_LOG.md:1304:Using device: mps
docs/tasks/detection-floor-and-mechanism/DEEPDIVE_LOG.md:1483:and the original runs printed "Using device: mps" => ORIGINAL DEVICE = mps;
docs/tasks/detection-floor-and-mechanism/DEEPDIVE_LOG.md:2916:  attempt 1 evidence (preserved log): "timed: background 1/57 A222_C -> 77.6s for 120 positions (647 ms/pass); projection total = 4423.8s" ... last line before interruption "timed: background 38/57 AV_292 -> 95.5s ... projection total = 5442.5s"
docs/tasks/detection-floor-and-mechanism/DEEPDIVE_LOG.md:2918:  "(G6) timing rule: projection 3593s <= 5400s -> NO reduction (n_sub stays 120)"  (t1 = first background scored in the resuming process, 63.0s; attempt 2's own in-run projections were 4,563-4,592s — both readings of the frozen rule land under 5,400, so no reduction under either; disclosed)
docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md:277:Using device: mps
docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md:279:M1b timed: background 1/8 R1_L45D -> 61.3 s for 120 positions (511 ms/pass); projected total for 8 = 490.6 s
docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md:293:Verdict: PASS. 8 backgrounds × 120 positions = 960 forward passes in 503.5 s (511–545 ms/pass, stable ±3% across backgrounds) — **well inside the 30–40 min M1 budget; no reduction needed, nothing reduced.** Same 120-position subset in every background (comparability requirement met); A222V not rescored (its full 655-position arm already exists from script 11).
```
→ Device recorded: **mps** (all scoring runs). Recorded per-pass cost:
**511–647 ms/pass** (scripts 63/69/82 runs), stable ±3% per run.

File timestamps — command
`stat -f "%Sm  %N" -t "%Y-%m-%d %H:%M:%S" <caches and scripts>`:

```
2026-09-22 18:09:00  data/processed/task63_m1_bg_raw.csv
2026-09-23 05:02:48  data/processed/task69_w2_bg_raw.csv
2026-09-24 17:29:14  data/processed/task82_ae_raw.csv
2026-09-11 02:00:55  data/processed/esm2_wt_scores.csv
2026-09-12 22:02:00  data/processed/merged_wt_a222v_scores.csv
2026-09-22 17:59:31  scripts/63_m1_context_shift_vs_severity.py
2026-09-23 04:26:29  scripts/69_w_decile_background_rescore.py
2026-09-24 15:27:46  scripts/82_ae_position_vs_identity.py
```
(script-write → output-write gaps: 63 ≈ 9.5 min, 69 ≈ 36.3 min,
82 ≈ 121.5 min — coarse upper bounds including analysis time, cited as
supplementary; the ms/pass log lines above are the primary timing.)

(d) passes table — inline command (`venv/bin/python3 -c ...`, verbatim
output; N_V computed here to fill this table, to be independently
re-derived in Q3):

```
passes per background (full 654-position frame) = 654 (1 forward pass per position; all 19 non-WT subs from that pass)
arms 18 (S) + N_V(38) + 40 (G) = 96 backgrounds -> 96 x 654 = 62784 passes
(if N_V > 60 the frozen rule would cap V at 40: 18 + 40 + 40 = 98 -> 98 x 654 = 64092)
at 511 ms/pass (recorded): 32082.6 s = 8.91 h
at 545 ms/pass (recorded): 34217.3 s = 9.50 h
at 626 ms/pass (recorded): 39302.8 s = 10.92 h
at 647 ms/pass (recorded): 40621.2 s = 11.28 h
at script-82 attempt-1 projection rate (5442.5 s / 6840 passes = 0.7957 s/pass): 49956.4 s = 13.88 h
A222V arm new passes = 0 (merged_wt_a222v_scores.csv = 12426 rows = 654 x 19, cached); WT baseline new passes = 0 (esm2_wt_scores.csv = 12445 = 655 x 19, cached)
```
supplementary frame check from the same inline run:
`frame positions: 654 | 222 in frame: False`,
`alanine positions in frame: 38 | ==222: False | N_V (= Ala in frame, !=222): 38`.

(e) **YES — the projected wall time vastly exceeds the ~55–65 min
foreground limit.** 62,784 passes at the recorded 511–647 ms/pass =
**8.91–11.28 h** (13.88 h at script 82's own slowest recorded
projection rate). A full-frame run must be executed detached
(`nohup`), exactly as frozen Appendix A §8 already mandates; one
output file per background, resumable. H-set ρ recomputation adds no
passes (H ⊂ frame; same cached scores). Gate G-B's reproduction check
can be satisfied inside the run by re-scoring 3 cached backgrounds at
their 120 cached grid positions — those positions are already part of
each background's full-frame pass set, so +0 passes if checked during
the frame run (+360 passes ≈ 184 s ≈ 3.1 min at 511 ms/pass if
implemented as a separate re-scoring step).

Verdict: PASS. Feasible on cache-compatible infrastructure; costed at
62,784 forward passes ≈ 9–14 h on the recorded mps per-pass rates →
detached execution required (Appendix A §8 already requires it).
Files created/modified: `PHASE1B_LOG.md` (this entry) only. No script
written for Q1 (inline commands, as the task allows); no cached file
touched; no model run.
Anything unexpected or worth flagging:
1. Timing was NOT "NOT AVAILABLE" — this machine's prior runs recorded
   per-pass timings in three separate logs (citations above), so the
   projection is grounded in measurements, not guesses (AGENTS §1).
2. N_V was computed inside Q1 to complete the mandated table (the task
   says "see Q3 for N_V"); Q3 re-derives it independently and must
   agree (38) — flagged rather than silently deferred.
3. A222V's full-frame arm is already cached (12,426 rows =
   654 × 19), so the anchor arm needs no new scoring; the 38 Arm-V
   backgrounds are the same constructions as AE2's cached `AV_*` arms,
   but only on 120 grid positions — full-frame scoring for them is
   new work (the G-B overlap above).

---

## [Q2] — Held-out positions (script 122; design work only, no scoring)
Status: PASS
Time started / finished: 2026-09-27 22:53:00 – 22:55:50
What I did:
Wrote `scripts/122_q2_q3_frame_and_arms.py` covering Q2 + Q3 (one
script, by design: both are deterministic counts) with the full
pre-registration in its docstring before its first run: construction
(frame = dropna(delta_esm, own_e_b) positions of
`task32_analysis_table.csv`; AE set = unique positions of
`task82_ae_raw.csv`; W set = unique positions of `task69_w2_bg_raw.csv`;
H = frame \ (AE ∪ W)), gates Q2-G1 (654/120/120/10757), Q2-G2
(|AE ∩ W| = 41, the value script 109's G1 recorded from these same
files), Q2-G3 (222 ∉ frame, AE, W, hence ∉ H — with the mandated
citations printed), the row-accounting identity (usable(H) + usable(frame
\ H) = 10,757), and the statement that there is no rng and no selection
anywhere (Q3's rule: "enumerate only, choose nothing"). Smoke run
`N_BOOT=300 SEED=0` → EXIT 0; full run `N_BOOT=10000 SEED=0` → EXIT 0;
`diff` of the two outputs shows exactly one differing line — the banner
label — and nothing else (documented, since with no bootstrap statistic
the two runs are identical apart from that label; disclosed in the
docstring). Full output saved verbatim to
`docs/tasks/phase1b-placebo-followup/PHASE1B_Q2_FULL_OUTPUT.txt`
(`PHASE1B_Q3_FULL_OUTPUT.txt` is a byte-identical copy of the same
single run, since one script serves both tasks).

Actual output (verbatim, not paraphrased):

```
/Users/arnavchavan/Desktop/mthfr-context-dependence/scripts/122_q2_q3_frame_and_arms.py:26: SyntaxWarning: "\ " is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\ "? A raw string is also an option.
  usable(frame \ H) = 10,757.

--------------------------------------------------------------------------
Q2 -- HELD-OUT POSITIONS
--------------------------------------------------------------------------
  |frame|  = 654 (expect 654)
  |AE set| = 120 (expect 120)
  |W set|  = 120 (expect 120)
  |AE n W| = 41 (F1/script-109 recorded 41)
  |AE u W| = 199
  |H| = |frame \ (AE u W)| = 455
  usable variants in H = 7526
  usable variants at held-in frame positions = 3231
  row accounting: 7526 + 3231 = 10757 (frame total = 10757; expect 10757)
  H positions (sorted): [np.int64(2), np.int64(8), … 455 values …, np.int64(656)]
  citations: PHASE1_LOG.md [L1] (line 1517): "rows at position 222: base = 0, task77 all = 0, task77 analysis = 0"; PHASE1_LOG.md [K1] (lines 1462-1463): "independently verified (`222 in AE grid: False | 222 in W grid: False`")
  Q2-G1 PASS  Q2-G2 PASS  Q2-G3 PASS (222 excluded from every set as a target position)
```

(the full sorted H list — all 455 positions, 2…656 — is in the
saved full-output file verbatim; the `np.int64(…)` wrapper is numpy-2
repr noise around plain integer values, see flags below)

Verdict: **PASS. |H| = 455 held-out frame positions, containing 7,526
usable variants; the row accounting closes exactly (7,526 + 3,231 =
10,757).** 222 is excluded from every set as a target position
(citations above: [L1] for the analysis table, [K1] for both grids).
Files created/modified: `scripts/122_q2_q3_frame_and_arms.py` (new);
`PHASE1B_Q2_FULL_OUTPUT.txt`, `PHASE1B_Q3_FULL_OUTPUT.txt` (new,
copies of this run); `PHASE1B_LOG.md` (this entry). Nothing else; no
cached input touched; no scoring launched.
Anything unexpected or worth flagging:
1. The saved output's first lines contain a compile-time
   `SyntaxWarning: "\ " is an invalid escape sequence` from line 26 of
   the script's own docstring (the prose `frame \ H`). It is cosmetic —
   emitted at module compile, before any computation; no gate, value,
   or decision rule is affected. I did **not** edit the script to
   silence it and re-run: the docstring is the pre-registration record
   written before the first run, and silently changing the file after
   its run would break that provenance for a cosmetic gain. Flagged
   here instead (AGENTS §6).
2. Printed lists show `np.int64(...)` wrappers (numpy 2.x scalar
   repr); the underlying values are ordinary integers. Cosmetic only.
3. F1's premise-check: the recorded AE ∩ W = 41 held (P1's F1-style
   precedent where a recorded premise was wrong does not repeat here).

---

## [Q3] — Arm roster counts (script 122; enumerate only, choose nothing)
Status: PASS
Time started / finished: 2026-09-27 22:53:00 – 22:55:50 (same single run
as Q2; entry written immediately after)
What I did:
Same pre-registered script 122 (see [Q2]). From the wild-type sequence
in the repo (`data/raw/P42898.fasta`, residue p = FASTA index p−1,
mapping independently verified 12,445/12,445 against
`esm2_wt_scores.csv` in P1 and re-checked here over all 654 frame
positions): counted Ala positions ≠ 222 lying in the 654-position frame
(= N_V), reported N_V and whether N_V > 60. Gates: Q3-G1 (FASTA vs
`esm2_wt_scores.csv` WT-residue agreement at every frame position,
disagreements printed and failed), Q3-G2 (222 not counted, plus the
pre-registered cross-check that this independent count equals Q1's
inline count of 38). **No selection of any backgrounds: no rng in the
script, no sampling — Appendix A freezes selection for Phase 2.**

Actual output (verbatim, not paraphrased):

```
--------------------------------------------------------------------------
Q3 -- ARM ROSTER COUNTS (enumerate only, choose nothing)
--------------------------------------------------------------------------
  FASTA vs esm2_wt_scores.csv agreement over all 654 frame positions: 654/654
  Q3-G2: 222 in frame = False -> not counted
  alanine positions in frame != 222 (N_V) = 38
  sorted positions: [np.int64(5), np.int64(19), np.int64(70), np.int64(73), np.int64(84), np.int64(85), np.int64(98), np.int64(113), np.int64(116), np.int64(145), np.int64(155), np.int64(175), np.int64(195), np.int64(204), np.int64(209), np.int64(220), np.int64(233), np.int64(242), np.int64(292), np.int64(293), np.int64(302), np.int64(311), np.int64(328), np.int64(350), np.int64(353), np.int64(368), np.int64(396), np.int64(461), np.int64(462), np.int64(511), np.int64(522), np.int64(524), np.int64(551), np.int64(558), np.int64(587), np.int64(589), np.int64(650), np.int64(655)]
  N_V > 60 ? False (reported only; the frozen Appendix A cap rule is decided by this count alone and is NOT executed here)
  cross-check vs Q1's inline count: Q1 = 38, Q3 = 38 -> AGREE
```

```
SUMMARY
  Q2: frame 654, AE 120, W 120, overlap 41, |H| = 455, usable variants in H = 7526; 222 excluded everywhere
  Q3: N_V = 38 (<= 60 -> no cap rule would trigger); enumeration only, no backgrounds selected

LIMITATIONS (AGENTS 6): counts only; no scoring; no inference; no selection (Appendix A freezes selection).
Elapsed 0.1s
```

Verdict: **PASS. N_V = 38; N_V > 60 is False, so Appendix A's frozen
seed-0 cap rule (sample 40 if the count exceeds 60) would NOT trigger —
Arm V would be all 38 Ala positions.** Nothing was selected in this
task (report-only). Q1's early inline count (38) and this independent
re-derivation agree (pre-registered cross-check `AGREE`).
Files created/modified: none beyond those listed in [Q2] (same run;
`PHASE1B_Q3_FULL_OUTPUT.txt` is the verbatim full output).
Anything unexpected or worth flagging:
1. The 38 enumerated positions (5…655) are printed as enumeration for
   the record only — no background was chosen, and the count alone
   decides the cap question (≤ 60 → no cap).
2. Same two cosmetic points as [Q2]: the compile-time SyntaxWarning in
   the saved output's header and the `np.int64(...)` list reprs; both
   disclosed there; no value affected.
3. Roster-overlap facts for Phase 2. **CORRECTION (made minutes after
   first writing this flag, same session, before anything cited it):**
   my first draft claimed some Ala positions were "also in the AE grid
   (e.g. 70, 85, 98, 113 …)" — that is wrong. Verified directly with
   `venv/bin/python3` (set intersection of N_V against task82 positions
   and task69 positions): output `N_V: 38 | N_V in AE grid: [] -> 0`
   (consistent with script 82's pool rule, which excludes all 39 Ala
   positions from the grid); `N_V in W grid: [5, 73, 98, 155, 204, 242,
   302, 311, 396, 462, 655] -> 11`; `N_V in H: 27`; `222 in AE grid:
   False | 222 in W grid: False`. Accurate statement: of the 38 N_V
   positions, none are in the AE grid, 11 are in the W grid, 27 are in
   H; and Arm V's 38 backgrounds are the same constructions as AE2's
   cached `AV_*` arms (cf. Q1's cost note — cached on 120 grid
   positions only). The false first draft is replaced here rather than
   left standing (AGENTS §5: wrong numbers get corrected, plainly
   flagged in this log).

---

## [Q4] — Freeze the pre-registration (exact awk extraction + hash gate)
Status: PASS
Time started / finished: 2026-09-27 23:01:32 – 23:01:40
What I did:
Ran the task doc's extraction command **exactly as written** (line-
anchored FROZEN_BEGIN/FROZEN_END match; no looser pattern), after
`mkdir -p docs/tasks/phase2-full-frame-placebo`. Nothing in the source
document was edited; the frozen text was not touched. No scoring was
launched anywhere this session (Part B is design-only; no script of
mine imports torch/esm). Then applied gate G-Q4 verbatim: line count
86, no `FROZEN` substring, `shasum -a 256` equals
`420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2`.

Actual output (verbatim, not paraphrased):

```
$ mkdir -p docs/tasks/phase2-full-frame-placebo && awk '/^<<<FROZEN_BEGIN>>>$/{f=1;next} /^<<<FROZEN_END>>>$/{f=0} f' \
>   docs/tasks/phase1b-placebo-followup/PHASE1B_PLACEBO_FOLLOWUP.md \
>   > docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md
AWK_EXIT=0
      86 docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md
0
grep_FROZEN_exit=1 (1 = none found)
420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2  docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md
EXPECTED  420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2
# PHASE 2 — Full-frame placebo-background test: pre-registration v1

Frozen 2026-09-27, before any Phase 2 scoring. Authors: Arnav (PI), Claude (planning).
Confirmatory weight therefore rests on this frozen rule and on the held-out set H, not on the
Phase 1 numbers. Any deviation from this document must be disclosed in the log and, if it
changes a rule or constant, requires a new versioned pre-registration (v2), never an edit to v1.
```

Verdict: **PASS. G-Q4 satisfied: 86 lines, zero `FROZEN` strings,
sha256 = `420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2`
— byte-identical to the expected hash of the Appendix A frozen block.**
No re-extraction was needed (and none would have been run had it
failed — the rule is FAIL-and-stop, not retry-until-match). The
extracted file is byte-identical to Appendix A's frozen block by
construction (line-anchored extraction) and by hash equality.
Files created/modified: `docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md`
(new, the deliverable); `PHASE1B_LOG.md` (this entry). The source
`PHASE1B_PLACEBO_FOLLOWUP.md` was **not** edited.
Anything unexpected or worth flagging:
1. Nothing in Q1–Q3 revealed an infeasible design or a wrong premise
   that would trigger the doc's "log that fact plainly and stop" clause:
   N_V = 38 ≤ 60 (no cap rule), H = 455 positions / 7,526 usable
   variants exists for G-E, and the cost audit (Q1) says full-frame
   scoring is feasible but needs detached execution (~9–14 h). Design
   intact; v1 stands.
2. Confirmation: no model scoring, no forward pass, no weight download
   was launched at any point this session (verified by what ran:
   scripts 120/121/122 read cached CSVs only; Q1/Q4 were shell/read-only).

---

## [R1] — Housekeeping (read-only; git status / git diff, no adds)
Status: PASS
Time started / finished: 2026-09-27 23:02:00 – 23:02:30
What I did:
Ran `git status --short` and `git diff --stat` (read-only), plus a
`find -newermt "2026-09-27 22:20"` over `scripts/`, the PHASE1B task
dir, and the new phase2 dir to isolate **this session's** files from
the pre-existing uncommitted state. No `git add`; no commit; no push.

Actual output (verbatim, not paraphrased):

```
$ git status --short
 M .gitignore
 M README.md
 M requirements.txt
?? PROVENANCE.md
?? data/processed/task32_analysis_table.csv
?? data/processed/task54_uniprot_mthfr.tsv
?? data/processed/task_AA5_distance_caveat.txt
?? data/processed/task_AB2_proteingym_model_comparison.csv
?? data/processed/task_AC3_state.json
?? data/processed/task_AC4_esm1v_member1_scores.csv
?? data/processed/task_AC4_esm1v_member2_scores.csv
?? data/processed/task_AC4_esm1v_member3_scores.csv
?? data/processed/task_AC4_esm1v_member4_scores.csv
?? data/processed/task_AC4_esm1v_member5_scores.csv
?? data/processed/task_G2_state.json
?? data/processed/task_V2_thermompnn_ddg.csv
?? data/processed/task_Z3c_6fcx_chainA.pdb
?? docs/tasks/c1-prime-independent-channels/C1_PRIME_LOG.md
?? docs/tasks/disattenuation-and-ledger/EMAIL_DRAFT_nambiar_severity_baseline.md
?? docs/tasks/manuscript-review-response/REVIEW_RESPONSE_LOG.md
?? docs/tasks/phase1b-placebo-followup/PHASE1B_LOG.md
?? docs/tasks/phase1b-placebo-followup/PHASE1B_P1_FULL_OUTPUT.txt
?? docs/tasks/phase1b-placebo-followup/PHASE1B_P2_FULL_OUTPUT.txt
?? docs/tasks/phase1b-placebo-followup/PHASE1B_P3_FULL_OUTPUT.txt
?? docs/tasks/phase1b-placebo-followup/PHASE1B_P4_FULL_OUTPUT.txt
?? docs/tasks/phase1b-placebo-followup/PHASE1B_Q2_FULL_OUTPUT.txt
?? docs/tasks/phase1b-placebo-followup/PHASE1B_Q3_FULL_OUTPUT.txt
?? docs/tasks/phase2-full-frame-placebo/
?? scripts/100_x1_x2_depth_regression_domains.py
?? scripts/101_y1_y2_severity_baseline.py
?? scripts/104_a1_a2_thermompnn_interaction_decomposition.py
?? scripts/105_d1_d2_difference_score_reliability.py
?? scripts/106_c1_mechanism_only_null_shift.py
?? scripts/107_e2_dimer_distance_recompute.py
?? scripts/108_c1prime_channel_independent_null.py
?? scripts/120_p1_inventory_gates.py
?? scripts/121_ae_placebo_probe.py
?? scripts/122_q2_q3_frame_and_arms.py

$ git diff --stat
 .gitignore       | 17 +++++++++++++++++
 README.md        | 55 +++++++++++++++++++++++++++++++++++++++++++++++++++++++
 requirements.txt |  9 ++++++---
 3 files changed, 78 insertions(+), 3 deletions(-)

$ find scripts docs/tasks/phase1b-placebo-followup docs/tasks/phase2-full-frame-placebo -newermt "2026-09-27 22:20" -type f | sort
docs/tasks/phase1b-placebo-followup/PHASE1B_LOG.md
docs/tasks/phase1b-placebo-followup/PHASE1B_P1_FULL_OUTPUT.txt
docs/tasks/phase1b-placebo-followup/PHASE1B_P2_FULL_OUTPUT.txt
docs/tasks/phase1b-placebo-followup/PHASE1B_P3_FULL_OUTPUT.txt
docs/tasks/phase1b-placebo-followup/PHASE1B_P4_FULL_OUTPUT.txt
docs/tasks/phase1b-placebo-followup/PHASE1B_Q2_FULL_OUTPUT.txt
docs/tasks/phase1b-placebo-followup/PHASE1B_Q3_FULL_OUTPUT.txt
docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md
scripts/120_p1_inventory_gates.py
scripts/121_ae_placebo_probe.py
scripts/122_q2_q3_frame_and_arms.py
```

Verdict: **PASS. Files created or changed BY THIS SESSION (11):**
`scripts/120_p1_inventory_gates.py`, `scripts/121_ae_placebo_probe.py`,
`scripts/122_q2_q3_frame_and_arms.py`, `PHASE1B_LOG.md`,
`PHASE1B_P1_FULL_OUTPUT.txt`, `PHASE1B_P2_FULL_OUTPUT.txt`,
`PHASE1B_P3_FULL_OUTPUT.txt`, `PHASE1B_P4_FULL_OUTPUT.txt`,
`PHASE1B_Q2_FULL_OUTPUT.txt`, `PHASE1B_Q3_FULL_OUTPUT.txt`, and
`docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md`. All are new
files; no pre-existing tracked file was modified by this session.

**Protected files: none appear.** `RESULTS.md`,
`MTHFR_RESULTS_LOG.md`, `PROJECT_SUMMARY_FINAL.md`, `AGENTS.md`, and
`PHASE1_LOG.md` are absent from `git status --short` entirely (tracked
and unmodified) — confirmed untouched. The task doc
`PHASE1B_PLACEBO_FOLLOWUP.md` likewise does not appear (unmodified —
Q4's source was only read).

Everything else in `git status` predates this session and was left
alone: ` M .gitignore / README.md / requirements.txt` and the older
`??` entries (PROVENANCE.md, task32 table, scripts 100–108, C1_PRIME /
REVIEW_RESPONSE / EMAIL_DRAFT docs, etc.) are prior sessions'
uncommitted work — listed verbatim above so the boundary is explicit,
not merged with this session's output. No `git add` was run.
Files created/modified: `PHASE1B_LOG.md` (this entry) only beyond what
is listed above.
Anything unexpected or worth flagging:
1. The pre-existing uncommitted state is larger than the prior session
   summary suggested (3 modified + many untracked) — not this
   session's doing; Arnav commits after review, unchanged by R1.
2. `?? docs/tasks/phase2-full-frame-placebo/` shows as a directory
   (new); its only file is the Q4 deliverable.

---

## SUMMARY

### (1) READ THIS FIRST — P3's primary gradient result and outcome (verbatim)

Task P3, primary metric = Grantham distance d_b from V (fixed in
script 121's pre-registration before its first run), T = Spearman(ρ_b,
d_b) over the 18 A222X backgrounds:

```
  T = Spearman(rho_b, d_b) over the 18 = -0.182662539 (prediction if the anchor tracks A222V-like structure: more V-like -> more negative rho_b -> T > 0)
  bootstrap T (same SEED+0 draws as P2): 95% CI = [-0.605779154, +0.364293086] (valid 10000/10000, NaN dropped 0)
  bootstrap SE(T) = 0.256865386 -> minimum detectable |T| approx 2.8 x SE = 0.719223081  (n=18 is small; stated as the task requires)
  label permutation (10000 shuffles of d_b across the 18, two-sided, SEED+2): p = (1 + 4627) / (1 + 10000) = 0.462754
  leave-one-out range of T: [-0.284313725, -0.056372549] (n=18 fits; T > 0 in 0/18)
  P3 RULE (pre-registered): CI lower bound > 0 (False) AND T > 0 in all 18 LOO (False); CI upper bound < 0 (False) -> NOT RESOLVED
  REQUIRED WORDING for NOT RESOLVED: "n=18 cannot resolve this," never "the gradient is flat".
```

**Outcome: NOT RESOLVED — "n=18 cannot resolve this."** The point
estimate is opposite to the pre-stated prediction (T < 0 where T > 0
was predicted) but the CI spans 0, the permutation p = 0.462754 shows
nothing, and with SE(T) = 0.256865386 the minimum detectable |T| ≈
0.719223081. Secondaries (descriptive only): BLOSUM62 T = −0.388909932,
CI [−0.727767689, +0.125729786]; |ΔKD| T = +0.182575070, CI
[−0.308121364, +0.557087369]. All exploratory / post-hoc.

### (2) P2 site-vs-substitution contrast (verbatim)

```
  mean rho_b(S) = -0.055208774 (n=18)
  mean rho_b(V) = -0.010138068 (n=38)
  D = mean(S) - mean(V) = -0.045070706
  bootstrap (position-cluster, 10000 draws, SEED+0): D CI 95% = [-0.107025598, +0.017286053] (valid draws 10000/10000, NaN dropped 0)
  label permutation (10000 shuffles of S/V labels over the 56, two-sided, SEED+1): p = (1 + 13) / (1 + 10000) = 0.001400
  A222V rho (AE frame) = -0.104321773; signed rank within S u {A222V} (n=19) = 1; within V u {A222V} (n=39) = 1 (rank 1 = most negative; reported, NOT tested)
  P2 RULE (pre-registered): CI excludes 0 -> NOT DISTINGUISHABLE
```

**Outcome: NOT DISTINGUISHABLE** (the pre-registered rule keys on the
bootstrap CI, which includes 0; the smaller label-permutation p =
0.001400 is reported alongside but does not change the verdict —
flagged in [P2] so the two can't be conflated). The task's
interpretation guard was printed verbatim with the result.

### (3) P4 descriptive numbers

V group (AE2, AE frame): n=38, mean = −0.010138068, background-
bootstrap 95% CI [−0.025250004, +0.006068308], median −0.022696950,
range [−0.094598010, +0.116091440], A222V signed rank 1/39,
p_spec = (1+0)/(1+38) = 0.025641026.
W group (W frame): n=30, mean = −0.016421191, CI
[−0.032881444, −0.000116764], median −0.020178655, range
[−0.130455833, +0.086283923], A222V signed rank 3/31, p_spec =
(1+2)/(1+30) = 0.096774194. W's n/mean/median/range/rank are
**bit-identical to F1** (check printed `True`); W's fresh CI differs
slightly from F1's recorded [−0.032867760, +0.000010545] (boundary
endpoints, both printed). Label, printed with the block: `POST-HOC,
DESCRIPTIVE; does not replace F1d; may not be cited as support for
background-specificity.` No decision rule exists or was applied.

### (4) Q1 cost table and detached execution

Passes per background for the full 654-position frame = **654** (1
masked-marginal forward pass per position yields all 19 non-WT subs).
Arms: 18 (S) + N_V (38) + 40 (G) = **96 backgrounds → 96 × 654 =
62,784 passes** (the >60 cap alternative, 98 × 654 = 64,092, does not
apply). A222V arm = 0 new passes (cached 12,426 = 654 × 19); WT
baseline = 0 new (cached 12,445 = 655 × 19). At the recorded 511–647
ms/pass (mps): **8.91–11.28 h**, up to 13.88 h at script 82's slowest
recorded rate → **YES: a full-frame run vastly exceeds the ~55–65 min
foreground limit and needs detached (`nohup`) execution**, exactly as
frozen Appendix A §8 already requires.

### (5) Q2 held-out-position counts

frame = 654, AE = 120, W = 120, overlap = 41, union = 199 →
**|H| = 455 positions, 7,526 usable variants** (held-in 3,231;
7,526 + 3,231 = 10,757 closes exactly). 222 excluded from every set as
a target position, citing PHASE1_LOG [L1] (line 1517: "rows at
position 222: base = 0, task77 all = 0, task77 analysis = 0") and [K1]
(lines 1462–1463: "222 in AE grid: False | 222 in W grid: False").

### (6) Q3 arm sizes and subset rule

**N_V = 38** (Ala positions ≠ 222 in the frame; FASTA ↔ table
agreement 654/654; Q1's inline count 38 agrees — cross-check `AGREE`).
**N_V > 60 is False → the frozen seed-0 subset rule did NOT trigger**
(and was not executed: enumeration only, nothing selected).

### (7) Q4 sha256 and byte-identity

`docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md` extracted with
the doc's exact awk command: **86 lines** (expected 86), **no `FROZEN`
string** (grep count 0), **sha256 =**
`420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2`
**= the expected hash → byte-identical to Appendix A's frozen block.**
Source document not edited; no scoring launched; no re-extraction
needed.

### (8) Every gate: name, PASS/FAIL, value

**P1 (script 120):** G1 175 rows / 57 AE → PASS (175, 57); G2 max|diff|
over 57 recomputed ρ_b → PASS (9.714e-17 < 1e-9); G3 → PASS (A222V AE
−0.104321772935, diff 2.271e-07; AE1 mean −0.055208774237 n=18, diff
2.258e-07; AE2 mean −0.010138067782 n=38, diff 6.778e-08; all < 1e-6);
G4 anchor → PASS (−0.08811806424891734, diff 6.425e-08 < 1e-6; rows
10,757, positions 654); roster P1(a) → PASS (18+1+38=57, 38/38 Ala,
FASTA 655/655); Grantham gate → PASS (A-V 64.4303, I-V 29.6091, L-V
31.7848, L-I 4.8551, F-Y 21.6097, C-W 214.3624; max |diff| 0.6376 ≤
1.0; symmetry 0.000e+00 < 1e-12; diagonal 0.000e+00) → P3's primary
metric usable.
**Script 121:** G-121.1 shapes/paired frame (175, 57, S=18, V=38,
disjoint, 56; identical row sets, 1,932 rows/bg) → PASS; G-121.2 point
ρ vs CSV → PASS (9.714e-17 < 1e-9); G-121.3 bootstrap identity → PASS
(0.000e+00 < 1e-12); G-121.4 Grantham import + 18 finite d_b → PASS.
**Script 122:** Q2-G1 (654/120/120/10,757) → PASS; Q2-G2 (|AE∩W| = 41
= 41) → PASS; Q2-G3 (222 ∉ frame/AE/W/H) → PASS; Q3-G1 (FASTA↔table
654/654) → PASS; Q3-G2 (222 not counted; Q1=38 = Q3=38 → AGREE) →
PASS. **Q4:** G-Q4 line count 86 → PASS; `FROZEN` absent → PASS; hash
equals expected → PASS.
**No gate failed; nothing was BLOCKED.** Standing flags (not gates):
the P1(b) W-series selection-is-score-based FLAG (prominent in [P1]),
the P4 post-hoc label, and the two cosmetic items in [Q2]/[Q3]
(SyntaxWarning header line, `np.int64` repr).

### (9) What this session changes about the central claim

**Nothing.** P2 is NOT DISTINGUISHABLE and P3 is NOT RESOLVED on
exploratory, post-hoc-motivated data; P4 is descriptive only. None of
it can upgrade, replace, or weaken F1d, and none of it is confirmatory
— the frozen Phase 2 design (v1, hash-gated) remains the only path to
a confirmatory answer. The Phase 1b session adds: reproduced anchors,
costed feasibility, a defined held-out set H (455 positions / 7,526
usable variants), a frozen pre-registration, and honest null results.

### (10) The single most important entry for Claude to read first

**`## [P3] — Similarity-to-valine gradient within S (script 121;
EXPLORATORY)` at line 277 of `PHASE1B_LOG.md`** — the primary gradient
result, its NOT-RESOLVED outcome with all verbatim numbers, and the
wording constraint ("n=18 cannot resolve this," never "the gradient is
flat").
