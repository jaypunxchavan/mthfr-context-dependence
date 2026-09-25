# FOLLOWUP_LOG — I1 Diagnosis, Mechanism Follow-Up, and Script 35 Retirement

Session start: 2026-09-22. Tasks executed in the "Suggested execution order"
of `docs/tasks/i1-mechanism-followup/I1_MECHANISM_FOLLOWUP.md`.
One entry per task, exact format, real numbers only. No entry is written
before the task's script has actually been run and its output read.

## [L1a] — Identify I1's script + comparator dataset, and the source paper's own epistasis effect size
Status: PASS
Time started / finished: 2026-09-22 15:24 – 16:45 EDT
What I did:
1. Identified I1's script as `scripts/49_i1_gb1_positive_control.py` (output: `data/processed/task49_i1_gb1.csv`; full run stdout is pasted in `docs/tasks/review-triage/OVERNIGHT_LOG.md` entry "I1", which I re-read for this task).
2. Comparator dataset: `data/external/GB1_fitness_landscape.txt` — provenance chain from script 49's docstring: Zenodo record 5014984 (Reia & Campos, `Empirical_Landscapes.zip`) attributed there to the dataset's OWN source paper **Wu NC, Dai L, Olson CA, Lloyd-Smith JO, Sun R, eLife 2016;5:e16965** ("Adaptation in protein fitness landscapes is facilitated by indirect paths").
3. Fetched that source paper in full (elifesciences.org/articles/16965) plus Figure 1, Figure 3, Figure 1—figure supplement 3 images from eLife's IIIF endpoint, and read the ε formula/methods from the paper's own Materials and methods — effect sizes below are QUOTED FROM THE PAPER, not assumed.
4. Ran dataset characterization + a reconciliation of the file's genotype counts against the paper's reported counts (output below).
Actual output (real numbers, not a paraphrase):
```
FILE : data/external/GB1_fitness_landscape.txt
md5  : 89e8d0f088466a1e29714721ed7967e8
cols : ['sequence', 'fitness']
n    : 160000 | unique genotypes: 160000
WT (VDGV) fitness: 1.0
sub-landscape (site54=WT): 8000
fitness: min 0.0000 max 9.9131 mean 0.0794 sd 0.3852
fraction f>1 (beneficial): 0.0231
fraction f==0 (lethal): 0.18423125
missing/NaN: 0
zeros(f==0) : 29477
positive    : 130523
paper: measured 149,361 = non-lethal 119,884 + lethal 29477
zeros == paper lethal count: True
positive == 119,884 + 10,639 imputed: 130523 == 130523 -> True
149,361 + 10,639 = 160000 (file n = 160000)
beneficial % of measured: 2.478% (paper: 2.4%)
```
Effect size of the epistasis the dataset is KNOWN to contain — from Wu et al. 2016 itself (each number with its location in the paper):
- **Concrete ε magnitudes (Figure 3D): ε = +5** for the G41L×V54H cycle on background (39=I,40=L) — printed fitnesses ILGV 0.55, ILLV 0.02, ILGH 0.01, ILLH 0.82 — and **ε = −4.5** on background (39=W,40=L) — printed fitnesses WLGV 0.02, WLGH 0.031, WLLH 0.025, WLLV 1.64. ε is log-space (Methods, eq. 2, Khan et al. 2011): ε = ln(w_ab) − ln(w_a) − ln(w_b) + ln(w_BG), i.e. ε=+5 means the double mutant's fitness is e^5 ≈ 148× the multiplicative-independence expectation. Three adjustment rules for w < 0.01 (system detection limit, Olson et al. 2014).
- **Heat-map range (Figure 3C): ε spans −7.5 to +7.5** (color bar) across all 400 (site39×site40) backgrounds for that one substitution pair.
- **Prevalence (Figure 1C + caption):** of the 2166 possible pairwise epistasis values around WT (C(4,2)×19²), 2091 were determinable; bar read-off ≈ magnitude 0.70 / sign 0.28 / reciprocal-sign 0.035 → **~31% of around-WT pairwise interactions are sign or reciprocal-sign (direction-changing, not merely magnitude) epistasis**. (Fractions read off the bar chart — no numeric labels printed; read-off, ±0.02.)
- **Concentration (Results §1):** these four sites contain **12 of the top 20 positively epistatic pairwise interactions in all of GB1** (Olson et al. 2014 as cited by Wu et al. 2016, Figure 1—figure supplement 2).
- **Ruggedness effect size (Figure 1—figure supplement 6):** Pearson **r = 0.66, p = 1.0×10⁻⁴** between epistatic ruggedness (f_sign + 2·f_reciprocal) and number of inaccessible direct paths across the 29 subgraphs.
- **Fourier decomposition (Figure 3A, read off, ±0.02):** 1st-order (additive) expansion explains median ≈ 0.83 of fitness variance, 2nd order ≈ 0.96, 4th order = 1.0 by construction → pairwise + higher-order epistasis account for the residual ~0.17 / ~0.04 median, with the red top-0.1% subgraphs far lower at 2nd order.
- Assay precision as the paper reports it (Methods + Figure 1—figure supplement 3B): 149,361/160,000 (93.4%) measured (count_input ≥ 10), 10,639 imputed by lasso (model-vs-actual Pearson 0.93); cross-study fitness correlation vs Olson et al. 2014 **R = 0.97**; detection limit w ≈ 0.01. No per-variant SE or replicate count is reported anywhere in the paper or the file (used by L1b).
Verdict: PASS — the comparator is a dataset with **strong, well-established, quantitatively large epistasis** (published ε up to |5|–|7.5| in ln-fitness; ~31% of pairwise interactions direction-changing; 60% of GB1's top-20 positive interactions sit in its four sites). Per L1a's framing: a gate failure here is the "strong, well-established epistasis" case, not the weak-benchmark case — so I1's FAIL cannot be dismissed as benchmark weakness.
Files created/modified: `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry) only. All other access read-only (paper fetched read-only; figures saved to the session temp dir `/private/var/folders/tv/.../T/opencode/i1follow/`, not the repo).
Anything unexpected or worth flagging:
- **Site-4 numbering is now RESOLVED (script 49's disclosed contradiction):** the paper states the four sites are **V39, D40, G41 and V54**, and that WT genotype = **"VDGV"** — exactly our file's WT key. Genotype column 4 therefore maps to **position 54 (WT letter V, matching 2GB1 V54)**, NOT position 44 (T44) that script 49's docstring worried about. Script 49's site-4 drop was based on an unresolvable-numbering concern that the paper itself resolves; the dropped axis (41×54, also 39×54/40×54) is precisely where the paper's headline ε=+5/−4.5 lives ("side chains of sites 39, 41, and 54 can physically interact at the core"; "site 40 was mostly excluded from higher-order epistasis"). I did NOT rerun or modify the frozen I1 gate (AGENTS §0/§10 — no post-hoc re-run of a pre-registered gate without authorization); flagged here for L3's addendum as the single biggest design caveat.
- File-count arithmetic reconciles EXACTLY with the paper (lethals 29,477 = 149,361−119,884; positives 130,523 = 119,884+10,639; total 160,000 = measured+imputed) → the file = paper's measured values PLUS lasso-imputed values for the 10,639 missing genotypes, one processing step removed (Pósar/Zenodo). Imputed rows carry model error, not measurement precision — relevant to L1b.
- Minor unexplained rounding gap: beneficial = 2.478% of measured (2.313% of all 160,000) vs paper's "2.4%" — logged both numbers, ~0.1pp, immaterial, not investigated further.
---

## [L1b] — GB1's per-variant measurement precision vs MTHFR's own SE distribution
Status: PASS (task executed end-to-end; verdict is the script's pre-registered NOISIER-BUT-SENSITIVE, i.e. both readings reported)
Time started / finished: 2026-09-22 16:45 – 16:58 EDT
What I did:
1. Established what the comparator actually reports as precision (the file has no SE column; the paper has no error column and no replicate count): cross-study fitness correlation **R = 0.97** vs Olson et al. 2014 (Wu et al. 2016, Figure 1—figure supplement 3B, read from the figure: scatter Fitness(this study) vs Fitness(Olson 2014), R = 0.97, single- + double-substitution points, no error bars), system **detection limit w ≈ 0.01** (Methods, citing Olson 2014), count_input ≥ 10 filter → 149,361 measured / 10,639 imputed.
2. Wrote `scripts/61_l1b_precision_comparison.py` (next free script number — stated explicitly per convention; `ls scripts/*.py` showed 60 as the highest). It (a) derives GB1's implied per-genotype SE from R (bridge assumptions + bias directions in the docstring), (b) reads MTHFR's SE distributions from `data/processed/task35_epistatic_set.csv` (columns confirmed against script 35: `se_e_b` = analytic WLS intercept SE of e_b; `mean_m_se` = mean per-condition measurement SE), (c) rebuilds I1's exact design (seed 0, sites 39/40/41, K=10 — mirror of script 49, no ESM needed) and censuses every fitness lookup entering I1's e values against the detection limit, (d) applies a pre-registered verdict rule written in the docstring before the first run.
3. Ran it: first execution exited 1 at the script's own lookup-count gate because the EXPECTED constant in that new gate was miscounted (+3 double-counting the b0 fitnesses; correct = 3×11×39 = 1287, verified by hand against script 49's loop structure). The gate fired before any verdict statistic existed; fixed only the constant/message, disclosed in the script's docstring, reran in full. This was an arithmetic error in my new check's expectation, not a failed data sanity check (the design-count itself verified), so it is a pre-verdict fix per AGENTS §7, not a test modification to force a pass.
4. Saved results to `data/processed/task61_l1b_precision.csv`.
Actual output (real numbers, not a paraphrase) — final full run:
```
=== GB1 comparator: what it reports (Wu et al. 2016) ===
file=GB1_fitness_landscape.txt md5=89e8d0f088466a1e29714721ed7967e8 n=160000 unique=160000
reported per-variant precision: cross-study R = 0.97 (Fig 1--figsupp3B vs Olson 2014); NO SE column, NO replicate count anywhere; detection limit w ~ 0.01; measured 149,361 (93.4%), imputed 10,639
fitness distribution: mean=0.079442 sd=0.385156 median=0.003718 IQR=[0.001543,0.011420] zeros=29477 max=9.9131

=== derived GB1 precision (bridge assumptions in docstring) ===
primary : sigma_e(per genotype) = sd*sqrt(1-R)      = 0.385156*sqrt(0.03) = 0.066711
          SE(e) for a 4-fitness cycle = 2*sigma_e    = 0.133422
S1 error-free external (sd*sqrt(1-R^2)): per-genotype = 0.093633  cycle = 0.187267
S2 robust sigma (IQR/1.349=0.007322): per-genotype = 0.001268  cycle = 0.002536

=== MTHFR SE distribution (data/processed/task35_epistatic_set.csv) ===
rows=13134  se_e_b valid n=11865  synonymous n=570
se_e_b   : median=0.062230 mean=0.086942 IQR=[0.044065,0.090736] (analytic WLS SE of e_b, script 35)
se_e_b among synonymous: median=0.038652
mean_m_se: median=0.087745 mean=0.124027 IQR=[0.061983,0.133496] (mean per-condition measurement SE)

=== precision in the population I1 actually sampled (rebuild of script 49's design, seed 0, no ESM) ===
fitness lookups building I1's e values: n=1287 (expected 3 sites * 11 backgrounds * (1 f(WT,b) + 19 f(v,b) + 19 f(v,b0)) = 1287; b0 fitness 1.0 is one of the 11 f(WT,b) terms, not extra)
  fraction < 0.01: 0.4149  (534/1287)
  fraction < 0.02: 0.5307  (683/1287)
  fraction < 0.05: 0.6348  (817/1287)
  fraction < 0.10: 0.6923  (891/1287)
  median lookup fitness = 0.015989 (detection limit 0.01)
  lookups within 2x of the detection limit: 683 (0.5307) -> these dominate cycles like the paper's own Fig 3D inputs (0.01, 0.02)

=== comparison (epistasis level: GB1 cycle SE vs MTHFR se_e_b) ===
primary : GB1 SE(e)=0.133422 vs MTHFR median se_e_b=0.062230  ratio=2.144  -> NOISIER
S1      : cycle=0.187267  ratio=3.009  -> NOISIER
S2      : cycle=0.002536  ratio=0.041  -> NOT noisier
=== per-variant level (GB1 per-genotype sigma_e vs MTHFR mean_m_se) ===
primary : 0.066711 vs median mean_m_se=0.087745 ratio=0.760
S1      : 0.093633  ratio=1.067
S2      : 0.001268  ratio=0.014

L1b VERDICT (pre-registered rule): NOISIER-BUT-SENSITIVE: primary rule fires NOISIER, but at least one precision-bridge sensitivity disagrees -> both readings stand; the verdict must not be quoted without the sensitivity (see printed ratios)
```
Verdict:
- **NOISIER-BUT-SENSITIVE** (pre-registered rule fired exactly as written; not renegotiated): at the epistasis level — the level that matters for I1's gate — GB1's implied cycle SE = 0.133422 vs MTHFR's median SE(e_b) = 0.062230, ratio **2.144×** (S1: 3.009×). Under the task's own interpretation, a gate failure on a comparator noisier than MTHFR "says little about the MTHFR pipeline specifically." The robust-σ sensitivity S2 (0.041×) disagrees because the file's fitness distribution is zero-inflated (median 0.0037, IQR [0.0015, 0.0114]) — a single global σ is not a real description of GB1's heteroscedastic precision; both readings stand and the verdict must be quoted with its sensitivity.
- The population-specific census is the load-bearing number regardless of which σ bridge one picks: **41.5% (534/1287) of the fitness lookups that build I1's e values are AT OR BELOW GB1's own detection limit (0.01), median lookup fitness = 0.015989 vs limit 0.01, 63.5% below 0.05.** In the regime I1 sampled, R = 0.97 does not describe precision at all — the paper itself forbids trusting unsigned epistasis there (its three ε-adjustment rules exist precisely for these inputs; its own Fig 3D showcase cycles use fitnesses of 0.01/0.02).
- Per-variant (non-epistasis) level reported as printed: primary 0.066711 vs mean_m_se median 0.087745 = ratio 0.760 (NOT noisier at that level), S1 1.067, S2 0.014 — i.e., GB1's headline precision is fine for ordinary single-variant fitness in the mid/high range; it is the near-detection-limit cycles I1 actually used where it is not.
Files created/modified: `scripts/61_l1b_precision_comparison.py` (new, next free number 61), `data/processed/task61_l1b_precision.csv` (new), `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry). `task35_epistatic_set.csv` read-only; nothing else touched.
Anything unexpected or worth flagging:
- The first run's exit-1 was my own miscounted EXPECTED constant in the new gate (disclosed in the script docstring and above): fixed pre-verdict, constant only.
- MTHFR's synonymous-only median SE(e_b) = 0.038652 (from script 35's file) is even smaller than the all-variant median — noted for N2a later (the synonymous ECDF is tight).
- The S2 flip is not noise to be swept aside: it exists because GB1's fitness distribution is heavily skewed; the honest statement is that GB1's precision is regime-dependent, and I1 sampled its bad regime. This reading is consistent across all three bridges: none of them puts I1's near-detection-limit lookups in a good-precision class.
---

## [L1c] — Detectable-effect-size floor of I1's null test as actually constructed (power 0.8)
Status: PASS — **the task doc's most important number: ρ_floor = 0.5400419 vs known effect ρ_obs = 0.4466626 → comparator UNDERPOWERED → L2 is attempted (condition met)**
Time started / finished: 2026-09-22 17:02 – 17:11 EDT
What I did:
1. Pre-registered the entire calculation **in the script's docstring before the first run** (AGENTS §6): inputs, formulas, sanity gates, and the verdict rule — `ρ_obs < floor` → COMPARATOR-UNDERPOWERED → attempt L2; else PIPELINE-SIDE → skip L2. Fixed before any number was seen by the script.
2. Wrote `scripts/62_l1c_detectable_effect_floor.py` (**next free script number 62**, stated explicitly; 61 was L1b). It reads every quantity from disk — `ρ_obs`, CI, `p_one`, `null_mean`, n, clusters, gate flag from `data/processed/task49_i1_gb1.csv` (script 49's own frozen output); only `σ0 = 0.0532` is a cited constant (script 49's full stdout, pasted in `docs/tasks/review-triage/OVERNIGHT_LOG.md` "I1" entry — the CSV never stored the null sd, so the script cross-checks it against the empirical p before trusting it).
3. Ran it once; **all four sanity gates passed on the first run** (no fix, no retry). No resampling is performed (this reads a frozen run), so N_BOOT/N_PERM do not apply — stated in the docstring.
4. Saved results to `data/processed/task62_l1c_floor.csv`.
Actual output (real numbers, full calculation as printed — this is the show-your-work requirement):
```
=== inputs (sources cited in docstring) ===
rho_obs=0.4466626  ci=[0.2787477, 0.5793188]  p_one_emp=0.139786
null_mean=0.3880021  sigma0=0.0532  (script 49 stdout via OVERNIGHT_LOG I1 entry)
n=570 pairs, 57 (site,variant) position-like clusters, gate: one-sided positive alpha=0.05, gate_pass=0

sanity gates: (a) crit round-trip OK (1e-9), (b) power round-trip OK (p=0.800000000000), (c) Gaussian p=0.135092 vs empirical p=0.139786 |diff|=0.004694 < 0.01, (d) rho<crit=True matches gate_pass=0 -- ALL PASS

=== step 1: critical value (Gaussian null) ===
crit = null_mean + z(1-0.05) * sigma0
     = 0.3880021 + 1.6448536 * 0.0532
     = 0.3880021 + 0.0875062 = 0.4755084
     (empirical-p-calibrated sigma0=0.0542509 -> crit=0.4772369)

=== step 2: sampling sd of rho_hat (position-cluster) ===
se = (ci_hi - ci_lo) / (2*z_0.975) = (0.5793188 - 0.2787477) / 3.9199280 = 0.0766777   [PRIMARY, cluster-based]
row-level Fisher 1/sqrt(n-3) = 1/sqrt(567) = 0.0419961   [sensitivity, ignores clustering -> anti-conservative]

=== step 3: detectable-effect floor at power 0.8 ===
floor = crit + z(0.80) * se
      = 0.4755084 + 0.8416212 * 0.0766777
      = 0.4755084 + 0.0645336 = 0.5400419
sensitivities: row-level se -> floor=0.5108531; sigma0 from empirical p -> floor=0.5417705
same floor as excess-over-null: 0.1520398 (z95*sigma0 0.0875062 + z80*se 0.0645336); observed excess = rho - null_mean = 0.0586605

=== step 4: power of this test AT the observed effect ===
power(rho_obs) = 1 - Phi((crit - rho_obs)/se) = 1 - Phi(0.3761947) = 0.3533861

=== comparator's known effect size vs floor ===
test-scale (rho): known/realized effect rho_obs = 0.4466626 CI [0.2787477, 0.5793188]  vs  floor = 0.5400419  -> BELOW floor  (CI STRADDLES floor)
L1a scale (ln-fitness, from Wu 2016 Fig 3D): epsilon = +5.0 / -4.5, heat-map range [-7.5, +7.5] -- NOT convertible to rho (no published delta-epsilon association exists); printed as context only

L1c VERDICT (pre-registered rule): COMPARATOR-UNDERPOWERED for this test: the comparator's known effect in test units (rho 0.4467) sits BELOW the detectable floor (0.5400); this gate had only 35.3% power at that effect -> ATTEMPT L2 (per task doc). CI upper bound 0.5793 exceeds the floor, so the straddle is disclosed alongside.

LIMITATIONS (printed by the script, AGENTS 6):
  - crit uses a Gaussian null; empirical null sample not stored.
    Gate (c) bounds the error at |dp| < 0.01 vs the real p.
  - se(rho_hat) from the frozen run's percentile CI width is a
    local-power approximation (se treated as constant).
  - Unit bridge: the comparator's 'known effect size' is taken as
    its realized rho because the source paper's epsilon scale has
    no mapping to rho; assumption logged in the log entry.
  - This calibrates power for the GB1 design (570 pairs, 57
    clusters, null mean +0.388). It says nothing direct about
    power on MTHFR's own effect scale.

Saved to /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task62_l1c_floor.csv
```
Verdict (the number, in one line): **the smallest true effect this test can detect with power ≈0.8 is ρ = 0.5400419** (sensitivities: 0.5108531 row-level, 0.5417705 empirically-calibrated σ0 — the floor is ~0.51–0.54 under every bridge). The comparator's known/realized effect in test units is **ρ = 0.4466626 < 0.5400419 → below the floor**, so the pre-registered rule fires **COMPARATOR-UNDERPOWERED** and **L2 is attempted** per the task doc. Power of the gate at that effect: **35.3%** (p_one observed 0.1398 ≈ Gaussian-implied 0.1351 — gates (c)). Framing in excess-over-null units: the gate needs an excess ≥ 0.0875 to reject at all and a true excess ≥ **0.15204** for 80% power, while the observed excess is only **0.05866**. Disclosed: the CI [0.2787, 0.5793] **straddles** the floor (upper bound above it) — the straddle is printed by the script, not hidden.
Files created/modified: `scripts/62_l1c_detectable_effect_floor.py` (new, next free number 62), `data/processed/task62_l1c_floor.csv` (new), `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry). Script 49's CSV read-only; nothing else touched.
Anything unexpected or worth flagging:
- **All four sanity gates passed first try** — including the load-bearing gate (c): the Gaussian-null approximation reproduces the empirical permutation p to |Δp| = 0.0047 < 0.01, which is what licenses using the Gaussian crit at all (the raw 10,000-draw null sample is not on disk).
- Unit-bridge assumption (logged, rule #6): "the comparator's known effect size" is instantiated as its **realized ρ with CI**, because Wu et al. publish ε in ln-fitness and no δ-vs-ε association exists to convert with. The ε = +5/−4.5 magnitudes from L1a are printed as non-convertible context. If someone insists the effect must be compared on ε's scale, this verdict's bridge is the first thing to challenge — but no published number lets them.
- σ0 (0.0532) lives only in script 49's stdout, not its CSV — a reproducibility gap in the frozen artifact worth fixing eventually (not authorized here; flagged for L3).
- The row-level Fisher se (0.0419961) would put the floor at 0.5109 — still above 0.4467, so the UNDERPOWERED verdict does not depend on the cluster-vs-row choice (all three sensitivities agree on the direction).
---

## [L2a] — Disk search for an alternative double-mutant comparator with larger established epistasis
Status: **BLOCKED** — nothing suitable exists on disk; stopped per the task rule ("If nothing suitable exists on disk, stop this subtask and report exactly what's missing rather than downloading a large new dataset unsupervised"). L1c's condition (comparator underpowered) WAS met, so this subtask was correctly attempted first.
Time started / finished: 2026-09-22 17:11 – 17:16 EDT
What I did (executed searches, real commands, no downloads):
1. Enumerated every file under `data/` (excluding the read-only `mthfrModel/` reference copy): the only external landscape is `data/external/GB1_fitness_landscape.txt` (3,343,308 bytes, the dataset I1 already uses). `data/raw/` contains only `6FCX.pdb`, `P42898.fasta`, and the MTHFR reference copy.
2. Filename grep across `data/` for `gb1|double|landscape|epistas|dms|fitness|external` → hits were only `GB1_fitness_landscape.txt`, `task49_i1_gb1.csv` (I1's own output), and `task51_f1a_nonlinear_fitness.csv` (MTHFR-derived, not a comparator).
3. Repo-wide grep (`scripts/`, `docs/`) for other DMS datasets / comparator references → every hit traces back to GB1 or to REVIEW_TRIAGE item 31's wording. `scripts/lib/` has no comparator loader at all (`io.py` loads only MTHFR atlas/reference tables; no file in `scripts/lib/` mentions GB1 or any external landscape).
4. Repo-wide search for the one alternative ever named: `grep -rniE "proteingym|protein gym"` across all .py/.md/.csv/.txt → **exactly one hit**, `docs/tasks/review-triage/REVIEW_TRIAGE.md:238` — "(a ProteinGym double-mutant set, or GB1)". The ProteinGym set was contemplated as an alternative to GB1 and never downloaded; GB1 was chosen instead.
5. Searched for any non-GB1 tabular data file anywhere in the repo (excluding .git/venv/mthfrModel/data/processed/data/raw) → only `requirements.txt`.
6. Listed `docs/tasks/` → only `i1-mechanism-followup`, `results-log`, `review-triage` — no other task doc references a comparator dataset.
Actual output (the search results that decide this, real output excerpts):
```
=== grep data filenames for candidate comparator datasets ===
data/external/GB1_fitness_landscape.txt
data/processed/task49_i1_gb1.csv
data/processed/task51_f1a_nonlinear_fitness.csv

=== any ProteinGym references anywhere in repo ===
./docs/tasks/review-triage/REVIEW_TRIAGE.md:238:  (a ProteinGym double-mutant set, or GB1). Without this, a negative

=== any non-GB1 tab/csv data files outside data/ (repo-wide, excluding git/venv/mthfrModel) ===
./requirements.txt

=== docs/tasks listing ===
i1-mechanism-followup
results-log
review-triage
```
Verdict: **BLOCKED — exactly what is missing:** a second double-mutant (or higher-order) fitness landscape with a *larger, better-established reported epistasis term* than GB1's I1-sampled regime. Concretely, the only candidate ever named in this repo is a **ProteinGym double-mutant substitution set** (REVIEW_TRIAGE item 31), which is not on disk. `scripts/lib/` contains no reference to GB1 or any alternative (the task doc's suggested "may already be referenced in scripts/lib/ or prior task docs" checked — it isn't), and `data/raw/` holds only the MTHFR atlas + two small files. Downloading a ProteinGym set unsupervised is explicitly forbidden by this subtask → not attempted.
Files created/modified: none (read-only search). `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry).
Anything unexpected or worth flagging:
- The "GB1 is the standard reference in this literature and may already be referenced" hint resolved negatively — GB1 exists only as the file I1 itself downloaded; there is no second comparator anywhere.
- This BLOCKED is *not* a dead end for the group: L1c already did its interpretive work (the gate had 35.3% power at the comparator's own realized effect), so L2a's failure to find a better comparator means the "did I1 fail because the comparator was underpowered for ANY method" question cannot be resolved by rerunning on a stronger comparator tonight → that stays an OPEN LIMITATION for L3's caveat text.
---

## [L2b] — Rerun the exact delta_ESM + sign-flip-null pipeline on the better comparator
Status: **SKIPPED** — precondition not met: L2a found no suitable comparator on disk (BLOCKED), and the subtask's own wording is conditional ("*If a suitable comparator is found*, rerun the EXACT SAME pipeline"). Nothing to rerun; the frozen pipeline was not touched or re-executed (AGENTS §10 — no rerun of a frozen run).
Time started / finished: 2026-09-22 17:16 – 17:16 EDT
What I did: verified L2a's BLOCKED outcome, re-read the L2b wording in the task file (lines 57-59) to confirm the conditional, and did not run anything. No commands beyond the read.
Actual output: n/a — no run was performed (an entry with fabricated output would violate the log rules; this is a logged skip, not an execution).
Verdict: SKIPPED (blocked upstream at L2a). The exact same code path as script 33 remains unused for any comparator other than GB1.
Files created/modified: `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry) only.
Anything unexpected or worth flagging: none beyond L2a's block.
---

## [L2c] — Interpret the rerun's outcome (clears gate vs still fails)
Status: **SKIPPED** — conditional on L2b, which did not run (L2a BLOCKED).
Time started / finished: 2026-09-22 17:16 – 17:17 EDT
What I did: confirmed the conditional wording (task file lines 60-63: "If it clears the gate… If it STILL fails…"); neither branch is reachable without L2b's rerun. Recorded the consequence instead of forcing a run.
Actual output: n/a — no run performed (logged skip).
Verdict: SKIPPED. **Both L2c branches remain empirically unresolved tonight**: we cannot say the pipeline clears a gate on a stronger comparator (would vindicate the pipeline), nor that it fails on any comparator (would indict the pipeline). What L1c alone establishes stands regardless: *this* test, on *this* comparator, had ≈35.3% power at the comparator's own realized effect (floor 0.5400 > ρ 0.4467). This open status is the single most important thing for L3's caveat to state honestly — it must NOT be written up as "pipeline has power" or "pipeline has no power."
Files created/modified: `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry) only.
Anything unexpected or worth flagging: none beyond the upstream block; feeding forward to L3.
---

## [M1a] — Select 6–10 alternate background mutations spanning ESM-2's own severity rating
Status: PASS on second execution; **first execution FAILED the script's own gate (g1) because I mis-encoded the expected constant** — caught, investigated, corrected with dual independent verification, disclosed in the script docstring (details below). No scoring had run at that point (M1a stage only), and no selection/verdict rule changed.
Time started / finished: 2026-09-22 17:31 – 17:44 EDT
What I did:
1. Wrote `scripts/63_m1_context_shift_vs_severity.py` (**next free script number 63**, stated explicitly; 62 was L1c) with M1a–M1e's rules pre-registered in the docstring, including a `M1_STAGE=select` stage so M1a gets its own actual run before any model scoring (task: "This step uses data already on disk — no new scoring needed yet").
2. Selection rule (fixed before running): candidates = `esm2_wt_scores.csv` rows (script 10's 12,445-row WT table), position ≠ 222, region from `scripts/lib/regions.py`; per region pick min and max `esm2_score` (most damaging / least damaging) with deterministic tie-break `(esm2_score, position, mut_aa)` and a different-position guard → 8 backgrounds, 2 per region. No atlas-measurability filter (disclosed assumption: any substitution is constructible as a background).
3. **Run 1: `EXIT_CODE=1`, `GATE FAILED: (g1) S(A222V|WT)=-5.200276032090187 != known 1.840757`.** Investigation (real commands, output below): `grep 1.8407567739486694 esm2_wt_scores.csv` → row `2,V,A,p.Val2Ala,1.8407567739486694` — **1.840757 is position 2 Val>Ala, the table's first data row, not A222V.** Its companion `1.851107` lives in `esm2_a222v_bg_scores.csv` row 2 and `merged_wt_a222v_scores.csv` row 2 (`…,1.8407567739486697,2,V,A,1.8511073589324951,0.010350584983825462`) — i.e. the prior session's `1.851107−1.840757=0.010351` was the **delta-sign-convention check on the merged file's first row (position 2)**, which my docstring had misattributed to A222V's severity. The correct value is independently confirmed **twice** in `docs/tasks/review-triage/OVERNIGHT_LOG.md`'s H1a entry: "NEAR-NEUTRAL per the pre-registered rule: S(A222V|WT) = −5.200276 sits inside (p10=−12.80, p90=−1.19); 68.0% of all 12,445 substitutions are at least as deleterious; z = +0.50" and the run summary "H1a NEAR-NEUTRAL (S(A222V|WT)=−5.200276, z=+0.502, rank 16/19 at position 222)". My own percentile recompute from the table reproduces **68.0%** exactly.
4. Fix (disclosed per AGENTS §6/§7): changed ONLY the gate constant `S_A222V_KNOWN` 1.840757 → −5.200276 and rewrote g1's docstring with the corrected provenance + the first-run failure note. Selection rule, subset rule, M1d/M1e verdict rules untouched; no data touched; no scoring had begun. This is the same class as L1b's miscounted EXPECTED constant — a defect in my own new check's reference value, caught by the check itself, corrected against two independent artifacts — not a data sanity check being weakened to force a pass.
5. **Run 2 (final, this entry's output): `EXIT_CODE=0`.**
Actual output (real numbers, run 2):
```
=== M1a: selected backgrounds (rule: min/max esm2_score per region, pos!=222, deterministic ties) ===
  R1 most_damaging  pos  45 L>D  p.Leu45Asp       S(b|WT)=-17.750033
  R1 least_damaging pos 134 R>S  p.Arg134Ser      S(b|WT)=+6.351555
  R2 most_damaging  pos 179 V>W  p.Val179Trp      S(b|WT)=-18.007029
  R2 least_damaging pos 237 F>L  p.Phe237Leu      S(b|WT)=+5.470481
  R3 most_damaging  pos 322 T>W  p.Thr322Trp      S(b|WT)=-16.377231
  R3 least_damaging pos 327 M>V  p.Met327Val      S(b|WT)=+6.235535
  R4 most_damaging  pos 480 L>D  p.Leu480Asp      S(b|WT)=-16.122699
  R4 least_damaging pos 594 R>Q  p.Arg594Gln      S(b|WT)=+7.807393
  (reference)   pos 222 A>V   p.Ala222Val        S(b|WT)=-5.200276  <- A222V arm uses existing script-12 data
severity span of the 8: [-18.007029, +7.807393] ; A222V -5.200276 sits INSIDE that span
(g1) S(A222V|WT) matches prior verified value -5.200276 -- OK
selection saved -> /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task63_m1_selection.csv

M1_STAGE=select -> M1a done, exiting before any scoring.
```
(Run 1's identical selection block printed before the gate fired — the 8 picks depend only on the WT table and are unaffected by the constant.)
Verdict: **8 backgrounds selected** (task asked 6–10), spanning ESM-2's full severity range [−18.007029, +7.807393]: four strongly damaging (−16.12 to −18.01) and four favorable/near-neutral (+5.47 to +7.81), two per region (R1:45/134, R2:179/237, R3:322/327, R4:480/594), all positions distinct and ≠ 222. A222V's S = −5.200276 sits **inside** the span (H1a's NEAR-NEUTRAL band reading: between p10 −12.80 and p90 −1.19, 68.0th-percentile-mild).
Files created/modified: `scripts/63_m1_context_shift_vs_severity.py` (new, next free number 63), `data/processed/task63_m1_selection.csv` (new), `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry).
Anything unexpected or worth flagging:
- **g1 failure on run 1** was my constant misattribution (full trail above + in the script's g1 docstring). The gate earned its keep: without it I would have carried a wrong S(A222V|WT) into M1d's outlier test.
- Design note carried into M1d: the min/max-per-region rule makes the 8's S distribution **bimodal** (four ≈ −17, four ≈ +6.5); A222V at −5.20 lies in the sparse gap between the two clusters. Its M1d residual is therefore an *interpolation between two clusters*, not an edge extrapolation — disclosed now so the residual isn't over-read; n=9 with two clusters also means the M1e correlation is effectively driven by the two cluster means (limitation already in the script's printed limitations).
- H1a's "near-neutral" is a *band* reading (p10–p90), not ≈0: the raw score is −5.20, milder than 68% of substitutions but clearly negative. Worth keeping straight in L3's wording — "ESM-2 does not flag A222V as deleterious," not "ESM-2 scores A222V ≈ 0."
- The prior session's "1.840757/1.851107" pair is a position-2 delta-sign check; if any future doc cites those numbers as A222V's severity, it is repeating this same misattribution.
---

## [M1b] — Rescore a fixed ~100–150-position subset in each of the 8 backgrounds (timed)
Status: PASS — timing rule evaluated on real data: **t1 = 61.3 s ≤ 180 s → NO reduction**; n_sub stayed at 120 (inside the task's ~100–150 band) for all 8 backgrounds.
Time started / finished: 2026-09-22 17:46 – 17:55 EDT (scoring wall time 503.5 s; run continued into M1c–M1e)
What I did:
1. Subset (pre-registered): seed 0, `default_rng(0).choice` of 120 positions without replacement from the 655 table positions minus {222} ∪ {the 8 background positions} → disjoint, identical for every background including A222V's arm (gate (g2) printed OK).
2. Built each substituted sequence exactly as script 11 did (`wt_seq[:pos-1] + mut + wt_seq[pos:]`), verified every background's WT letter in `data/raw/P42898.fasta` matches the table's `wt_aa` and position 222 is Ala (gate (g2)) before any scoring.
3. Scored with `scripts/lib/esm_scoring.get_position_logprobs` unchanged (one forward pass per background×position), device **mps**, after timing the first background per the runtime note. Smoke run at N_BOOT=300 did the scoring; final N_BOOT=2000 run reused the cache (`task63_m1_bg_raw.csv`, spec-matched 8×120×19 = 18,240 rows) so the smoke→full protocol was exact (scoring deterministic in eval mode).
Actual output (real timing numbers, smoke run — the only run that scored; final run printed `CACHE REUSED … 8 bgs x 120 x 19 = 18240 -- model not loaded`):
```
Using device: mps
Loading ESM-2 650M...
M1b timed: background 1/8 R1_L45D -> 61.3 s for 120 positions (511 ms/pass); projected total for 8 = 490.6 s
(g6) timing rule: t1=61.3s <= 180.0s -> NO reduction (n_sub stays 120)
M1b timed: background 2/8 R1_R134S -> 62.3 s for 120 positions (519 ms/pass); projected total for 8 = 498.7 s
M1b timed: background 3/8 R2_V179W -> 62.2 s for 120 positions (519 ms/pass); projected total for 8 = 497.8 s
M1b timed: background 4/8 R2_F237L -> 62.0 s for 120 positions (517 ms/pass); projected total for 8 = 496.0 s
M1b timed: background 5/8 R3_T322W -> 62.7 s for 120 positions (522 ms/pass); projected total for 8 = 501.4 s
M1b timed: background 6/8 R3_M327V -> 63.1 s for 120 positions (526 ms/pass); projected total for 8 = 504.9 s
M1b timed: background 7/8 R4_L480D -> 64.5 s for 120 positions (537 ms/pass); projected total for 8 = 515.7 s
M1b timed: background 8/8 R4_R594Q -> 65.4 s for 120 positions (545 ms/pass); projected total for 8 = 522.9 s
scoring wall time: 503.5 s total
scoring cache saved -> /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task63_m1_bg_raw.csv
(g2) subset OK: n_sub=120, seed=0, disjoint from {222} U {8 bg positions} -- OK
(g2) fasta letters match table at all 8 background positions, 222==A -- OK
```
Verdict: PASS. 8 backgrounds × 120 positions = 960 forward passes in 503.5 s (511–545 ms/pass, stable ±3% across backgrounds) — **well inside the 30–40 min M1 budget; no reduction needed, nothing reduced.** Same 120-position subset in every background (comparability requirement met); A222V not rescored (its full 655-position arm already exists from script 11).
Files created/modified: `data/processed/task63_m1_bg_raw.csv` (new, scoring cache 18,240 rows), `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry). Script 63 run only; no other script touched.
Anything unexpected or worth flagging:
- Per-pass cost (~0.52 s) is ~1.6× script 49's ESM timing (33 passes in 10.8 s ≈ 0.33 s/pass) — plausible (longer 656-aa sequence vs GB1 sub-landscape + MPS variance), logged as observed rather than "timing guessed from another script" (AGENTS §1): these numbers were measured on THIS run.
- The reduction rule's one-attempt floor (60) and the projection line both exist in the script but never fired — the pre-registered branch is documented as unexercised.
---

## [M1c] — mean |delta_ESM_b| per background, script 12's delta definition
Status: PASS — all 9 backgrounds summarized over identical 120×19 = 2,280-value sets; A222V's arm read from script 12's existing file (not rescored), gates (g3)/(g4) passed (row counts exact, every hgvs_pro resolved).
Time started / finished: 2026-09-22 17:55 – 17:57 EDT (same final run as M1b's cache reuse; delta summaries computed in-run)
What I did: computed `delta_ESM_b(v) = S(v|b) − S(v|WT)` merged on `hgvs_pro` (identical semantics to script 12; WT letters taken from the table, valid because target positions are never background positions), took `mean |delta_ESM_b|` per background over subset×19; A222V's arm = `merged_wt_a222v_scores.csv`'s own `delta_esm` column restricted to the same 120 positions (join column `position_wt`), 2,280 rows exactly (gate (g4)).
Actual output (real numbers, final N_BOOT=2000 run; identical to the smoke run — deterministic):
```
M1c R1_L45D          mean|delta_ESM_b| = 0.09529767 over 2280 values (120 pos x 19)
M1c R1_R134S         mean|delta_ESM_b| = 0.03064338 over 2280 values (120 pos x 19)
M1c R2_F237L         mean|delta_ESM_b| = 0.03895129 over 2280 values (120 pos x 19)
M1c R2_V179W         mean|delta_ESM_b| = 0.04111294 over 2280 values (120 pos x 19)
M1c R3_M327V         mean|delta_ESM_b| = 0.05539158 over 2280 values (120 pos x 19)
M1c R3_T322W         mean|delta_ESM_b| = 0.10838513 over 2280 values (120 pos x 19)
M1c R4_L480D         mean|delta_ESM_b| = 0.08254693 over 2280 values (120 pos x 19)
M1c R4_R594Q         mean|delta_ESM_b| = 0.06647830 over 2280 values (120 pos x 19)
M1c A222V            mean|delta_ESM_b| = 0.07425389 over 2280 values (120 pos x 19) [existing script-12 data, not rescored]
(g5) bootstrap OK: 2000 position-cluster draws, all finite, point estimates inside own CIs
```
Verdict: PASS (numbers delivered; interpretation deferred to M1d/M1e entries per the task's split). Descriptive facts to carry: context-shift magnitudes range **0.0306 (R1_R134S) to 0.1084 (R3_T322W)**, a 3.5× spread across backgrounds; **A222V = 0.07425389 is 6th of 9** — higher than all four favorable backgrounds (max of those = R4_R594Q 0.0665) and below three of the four strongly damaging ones.
Files created/modified: values written into `data/processed/task63_m1_backgrounds.csv` by the run; `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry).
Anything unexpected or worth flagging:
- The most damaging background (R2_V179W, S=−18.01) has near-LOWEST shift (0.0411) — the severity→shift relation is NOT monotone within the damaging cluster (flagged here, quantified in M1e).
- A222V producing MORE shift than every favorable background is already visible at M1c level — it points away from "A222V triggers unusually little context-shift" before any modeling; the formal test is M1d's residual (below).
---

## [M1d] — Does A222V sit outlier-LOW on mean|delta_ESM_b| vs S(b|WT)?
Status: PASS (test executed to its pre-registered verdict) — **verdict: NOT SUPPORTED.** A222V does NOT sit outlier-LOW; per the task's own wording, the H1a mechanism is not supported by this test and the weak delta_ESM signal needs a different explanation.
Time started / finished: 2026-09-22 17:57 – 17:58 EDT
What I did: fitted OLS `mean|delta| ~ S(b|WT)` on the **8 new backgrounds only** (A222V held out of the fit — pre-registered), predicted A222V's value at its S = −5.200276, computed residual r = observed − predicted, and put a 95% **position-cluster bootstrap** CI on r (cluster = the 120 subset positions; same resampled indices across all 9 backgrounds so the pairing survives; N_BOOT=2000). Smoke (N_BOOT=300) and final (N_BOOT=2000) runs gave the same verdict — CI endpoints moved by <0.001.
Actual output (real numbers, final N_BOOT=2000 run):
```
=== M1d: mean|delta_ESM_b| vs S(b|WT), sorted by severity ===
   bg_id  position  S_b_given_WT  mean_abs_delta
R2_V179W       179  -18.00702947      0.04111294
 R1_L45D        45  -17.75003335      0.09529767
R3_T322W       322  -16.37723128      0.10838513
R4_L480D       480  -16.12269900      0.08254693
   A222V       222   -5.20027603      0.07425389
R2_F237L       237    5.47048113      0.03895129
R3_M327V       327    6.23553514      0.05539158
R1_R134S       134    6.35155475      0.03064338
R4_R594Q       594    7.80739264      0.06647830

OLS on the 8 new backgrounds: mean|delta| = 0.057630 + (-0.001363) * S(b|WT)   [resid RMS on the 8 = 0.02111155]
A222V: observed 0.07425389, predicted 0.06471638, residual r = +0.00953752
residual 95% position-cluster CI = [-0.00573276, +0.02640051]  (N_BOOT=2000, cluster=subset position)
A222V absolute rank of mean|delta| among the 9: 6 (1 = lowest); lowest-of-nine = False
M1d VERDICT (pre-registered): NOT SUPPORTED: A222V sits within the trend (residual CI contains 0) -> per the task's wording the weak signal needs a different explanation; if it is nevertheless lowest in absolute terms (printed above) that is severity-EXPLAINED, not outlier-LOW
```
Verdict (task's question, answered plainly): **NOT SUPPORTED — A222V sits within the trend, not outlier-LOW.** Both the pre-registered residual test (r = +0.00954, CI [−0.00573, +0.02640] **contains 0**; if anything the point residual is slightly HIGH, not low) and the absolute rank (6/9, `lowest-of-nine = False` — A222V's 0.0743 is *higher* than all four favorable backgrounds) fail the "outlier-LOW" criterion. The H1a mechanism as the task defines it ("A222V triggers unusually little context-shift because the model doesn't see it as damaging") is **not supported**; the task's instructed reading follows: *the weak delta_ESM signal needs a different explanation.* Descriptively, A222V's context-shift is unremarkable for its severity — it behaves like a middling-damaging background, exactly what the generic severity→shift trend (M1e) would grant it.
Files created/modified: verdict scalars written into `data/processed/task63_m1_backgrounds.csv` (verdict_m1d, residual_a222v, resid_ci_lo/hi) and `task63_m1_bootstrap.csv` (`a222v_residual` row) by the run; `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry).
Anything unexpected or worth flagging:
- The residual's CI is wide relative to r (≈2.8× r on each side) because n=9 and the 8 fit-points are two tight clusters (bimodal S, flagged in M1a). The verdict is "CI contains 0" — this is an **absence of evidence for outlier-LOW**, and the point estimate being positive means the effect, if any, leans the OPPOSITE way from H1a's prediction; do not upgrade "NOT SUPPORTED" into "H1a disproven" (n too small, design range-restricted — both printed as script limitations).
- The task's wording resolved an ambiguity logged per session rule 6: "outlier-LOW" = below the trend fitted on the others (residual test), with absolute-rank printed alongside for the alternative reading; both readings agree here (not low by either).
- Fit slope on the 8 is −0.001363 per unit S with resid RMS 0.0211 — i.e. across the extreme clusters, more damaging backgrounds do shift the model more (four damaging mean 0.0818 vs four favorable mean 0.0479 — computed from the printed values: (0.0953+0.1084+0.0825+0.0411)/4 vs (0.0390+0.0554+0.0306+0.0665)/4), but with large within-cluster scatter (V179W vs T322W differ 2.6× at near-identical severity).
---

## [M1e] — Position-cluster bootstrap CI on the M1d relationship (the 9-point correlation)
Status: PASS (executed at N_BOOT=2000 after a 300-draw smoke; both runs same verdict) — **Spearman ρ = −0.466667, 95% cluster CI [−0.583333, −0.066667] — excludes 0; direction matches the severity→shift expectation.**
Time started / finished: 2026-09-22 17:58 – 17:59 EDT
What I did: primary = Spearman ρ across the 9 backgrounds of (S(b|WT), mean|delta|); Pearson alongside (project convention). 95% percentile CIs from a position-cluster bootstrap: resample the 120 subset positions with replacement (cluster = position, AGENTS §3), **same indices for all 9 backgrounds**, recompute each background's mean|delta| from its per-position mean-|delta| vector, recompute the correlation; 2,000 draws. Gates: all draws finite, count == N_BOOT, each point estimate inside its own CI (all passed; `(g5) bootstrap OK …` printed).
Actual output (real numbers, final N_BOOT=2000 run; smoke values in brackets):
```
=== M1e: correlation across the 9 backgrounds ===
Spearman rho = -0.466667  95% cluster CI [-0.583333, -0.066667]  [PRIMARY]
Pearson  r   = -0.601211  95% cluster CI [-0.711076, -0.283792]
H1a expected direction: NEGATIVE (more damaging = lower S = larger shift); observed sign = negative -> consistent with the severity->shift story in sign (CI excludes 0)
```
(Smoke N_BOOT=300: Spearman CI [−0.566667, −0.050000], Pearson CI [−0.713802, −0.254505] — same conclusion, CI tightened as expected at 2,000 draws.)
Verdict: **the severity→shift relationship is real in this designed set**: more damaging backgrounds shift ESM-2's other-position scores more (Spearman −0.467, CI excludes 0; Pearson −0.601, CI excludes 0) — the generic mechanism the task's hypothesis rests on *does* hold across these 8 extremes + A222V. But read together with M1d: A222V is **not** an outlier on that relationship, so what holds is "context-shift scales with rated severity in general," not the specific H1a claim "A222V shifts unusually little." Effect-size context (AGENTS §3): ρ=−0.467 on 9 deliberately separated points is driven mostly by the two cluster means (damaging-mean 0.0818 vs favorable-mean 0.0479, a ~1.7× separation); within-cluster ordering is weak (V179W the MOST damaging has 2nd-lowest shift), so treat ρ as a summary of the cluster separation, not a calibrated dose-response slope.
Files created/modified: `data/processed/task63_m1_bootstrap.csv` (spearman/pearson rows), `task63_m1_backgrounds.csv` (correlation scalars) by the run; `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry).
Anything unexpected or worth flagging:
- **Do not conflate with I1's gate failure.** M1e's CI excludes 0 while I1's analogous positive-direction test failed (p=0.1398): different statistics and different nulls — I1 is a 570-pair pooled Spearman against a permutation null that centers at +0.388 (L1c: 35.3% power at ρ=0.447), whereas M1e is a 9-point correlation whose CI comes from resampling positions over a design built from severity extremes. The bootstrap CI covering position-sampling error ONLY (not background-sampling — n=9 fixed) is the reason it can exclude 0 where I1 could not. Both statements stand; neither validates the other. Flagged for L3.
- The CI here is on a *designed* correlation (extremes chosen on the x-axis, range-restricted), so it must not be quoted as "ESM-2's context-shift correlates with severity in the population of possible backgrounds" — the script prints this limitation in its own output.
- With n=9 and a bimodal x-axis, Spearman takes only coarse values (ρ=−0.4667 = tied rank structure of two clusters + interior A222V); the CI's lower end (−0.583) reflects position-resampling noise in the means, not rank changes across backgrounds (ranks changed little across draws — implied by the narrow band).
---

## [N1a] — Formal retirement: DEPRECATED header on script 35
Status: PASS — header added, nothing deleted, file compiles (`py_compile` OK).
Time started / finished: 2026-09-22 18:05 – 18:10 EDT
What I did: prepended a DEPRECATED block to `scripts/35_se_threshold_epistasis.py`'s existing docstring (edit tool, single insertion above the original text) pointing at the J4a/J4b findings with their exact on-disk numbers, the replacement's location, and a pointer that readership was audited in N1b. Original docstring and all code below unchanged (verified by reading head + compile).
Actual output (the numbers cited in the header, all real, from disk):
```
PY_COMPILE OK  (scripts/35_se_threshold_epistasis.py after edit)
Header cites:
- J4a NO-SUSTAINED-C-IN-GRID: FDR_hat 0.91-1.00 at every z cutoff 2-10 even
  after 3.76x SE inflation; at flat 3.76: FDR = 0.9312 (syn 116/570 pass,
  missense 2,351/10,757 pass)   [task59_j4a_fdr.csv: fdr_at_3.76 =
  0.9311543426835912, pooled_ratio 3.7586477828302316, verdict
  NO-SUSTAINED-C-IN-GRID; 0.91-1.00 range from OVERNIGHT_LOG J4 summary]
- J4b NEEDS-TO-VARY: region ratios 5.1621/2.5374/4.0361/2.5926 (R1-R4),
  max/min = 2.03 > 2 pre-registered gate; fitness terciles 3.6799/3.4410/
  3.5502 stable, low tercile n_syn=11 underpowered
  [task59_j4b_ratios.csv]
- Script 35's own raw behavior: N=2 flag passes 44.7% of SYNONYMOUS
  (255/570) vs 44.8% of missense (4,822/10,757)
  [task35_summary.csv threshold row N=2]
- Replacement: scripts/64_n2_nonparametric_epistatic_set.py (task N2),
  output data/processed/task_N2_nonparametric_epistatic_set.csv
```
Verdict: PASS — script 35 is formally retired in-place; flags marked unusable; WHY-chain (J4a/J4b numbers) and replacement both named; nothing deleted per task instruction.
Files created/modified: `scripts/35_se_threshold_epistasis.py` (DEPRECATED header only — the ONE sanctioned edit to an existing script this session), `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry).
Anything unexpected or worth flagging:
- **Number reconciliation (task doc vs on disk, both logged, nothing edited):** the task doc says "FDR 0.91-1.00 ... correction factor varies 2.5x by region". On disk: FDR range 0.91–1.00 ✓ matches; "2.5x" matches neither the ratios' span (2.54–5.16, i.e. max/min **2.03**, which is what J4b's pre-registered gate used) — the "2.5" appears to be a rounding of the LOWEST ratio (2.54). Header cites the exact per-region values and max/min so no ambiguous "2.5x" propagates.
- The starkest retirement fact wasn't even in the task doc's brief: script 35's N=2 flag calls **44.7% of synonymous variants epistatic** — the flag is not subtly miscalibrated, it is ~coin-flip at the raw threshold level.
- The header references script 64's exact filename (next-free-number reserved for N2) — that file WILL be created in N2 this session; if it ever goes missing, this header's replacement pointer is stale (dependency noted here).
---

## [N1b] — Downstream-reader audit: who reads task35_epistatic_set.csv?
Status: PASS (command executed as specified) — audit complete; **one unexpected reader found: `scripts/50_d1_stratifier_quality.py` (line 222)** — flagged, NOT changed (per task: "flag it — do not silently change what it reads").
Time started / finished: 2026-09-22 18:10 – 18:13 EDT
What I did: ran the task's exact command `grep -rn "task35_epistatic_set" scripts/`, classified each hit (writer / expected reader / unexpected reader / this session's own script), and additionally grepped `docs/` for completeness (informational only — task scope is `scripts/`).
Actual output (real, untruncated for scripts/):
```
=== N1b: grep -rn task35_epistatic_set scripts/ ===
scripts/35_se_threshold_epistasis.py:166:    tab.to_csv(PROC / "task35_epistatic_set.csv", index=False)
scripts/35_se_threshold_epistasis.py:168:    print(f"\nSaved per-variant flags to {PROC / 'task35_epistatic_set.csv'}")
scripts/59_j4_fdr_threshold.py:108:    f_path = PROC / "task35_epistatic_set.csv"
Binary file scripts/__pycache__/50_d1_stratifier_quality.cpython-314.pyc matches
Binary file scripts/__pycache__/35_se_threshold_epistasis.cpython-314.pyc matches
scripts/50_d1_stratifier_quality.py:222:    t35 = pd.read_csv(PROC / "task35_epistatic_set.csv")
scripts/61_l1b_precision_comparison.py:65:task35_epistatic_set.csv. Sensitivities S1/S2 and the per-variant-level
scripts/61_l1b_precision_comparison.py:94:MTHFR_SE = ROOT / "data" / "processed" / "task35_epistatic_set.csv"
scripts/61_l1b_precision_comparison.py:152:    print("\n=== MTHFR SE distribution (data/processed/task35_epistatic_set.csv) ===")
EXIT=0

=== also check docs/readers (informational) ===
docs/tasks/review-triage/OVERNIGHT_LOG.md
docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md
docs/tasks/i1-mechanism-followup/I1_MECHANISM_FOLLOWUP.md
```
Verdict / classification of each hit:
- `scripts/35:166,168` — **writer** (the deprecated script itself) ✓.
- `scripts/59_j4_fdr_threshold.py:108` — **expected reader**: J4 is the very analysis that PROVED the flag dead (reads it to compute FDR) ✓ benign.
- `scripts/50_d1_stratifier_quality.py:222` — **UNEXPECTED downstream reader, FLAGGED**. Script 50 is D1 (stratifier-quality / winner's-curse checks from the overnight run). It reads the retired file — most likely for the `epistatic_N*` flags or the SE columns; **not investigated beyond this line and NOT modified** (task forbids silent changes; scope is to flag). Consequence to carry into L3: any D1-family number that stratified on `epistatic_N2` inherits a flag whose FDR is 0.91–1.00 — if the writeup cites D1a's enrichment, it needs the same retirement footnote.
- `scripts/61:65,94,152` — **this session's own L1b script** (read-only user of the `se_e_b` / `mean_m_se` columns, disclosed in its log entry; it does NOT use the epistatic flags) ✓.
- `__pycache__/*.pyc` matches — stale compiled caches of 35 and 50, not source readers.
- `docs/` mentions are task/log documents (including this follow-up's own docs), not code readers.
Files created/modified: none (read-only audit); `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry).
Anything unexpected or worth flagging:
- **The expected clean result was "only writer + script 59". It wasn't: script 50 reads it too.** Do not delete or repoint script 50's read (task rule). Recommended follow-up for the user's review (not executed): decide whether D1's stratified results get a footnote or a rerun under N2's replacement — recorded as an open item for L3's caveat.
- N2's new file is deliberately named per the task (`task_N2_nonparametric_epistatic_set.csv`) so no reader of the old file is silently switched; N2 adds no new reader of `task35_epistatic_set.csv` (checked: my N2 design reads `task35_summary.csv` for the region-table comparison only, plus the raw model fit — not the retired per-variant file).
---

## [N2a] — Nonparametric stratifier: rank |e_b| against the synonymous ECDF
Status: PASS on second execution; **first execution crashed on a plain bug in my new script** (`KeyError: 'epistatic_ecdf'` — stale pandas slices taken before the flag columns existed; fixed by moving the two slice lines after flag construction, disclosed in the script's inline note). No gate or verdict had run at crash time; no rule, cutoff, or data changed.
Time started / finished: 2026-09-22 18:15 – 18:24 EDT
What I did:
1. Wrote `scripts/64_n2_nonparametric_epistatic_set.py` (**next free script number 64**, stated explicitly — the same name pre-committed in N1a's header). Design pre-registered in the docstring: analysis set = script 35's row-validity mask (own_e_b & SE *notna* — notna as validity only, **SE values never used for flagging**); null = synonymous |e_b|; statistic = ECDF percentile `syn_ecdf_pct = mean(|e_syn| ≤ |e_own|)`; primary flag `> 0.95` (5% nominal FPR), sensitivity `> 0.99`; method choice (ECDF over EB local-FDR) disclosed as an assumption-avoidance choice; gates (g1)–(g6) fixed before running.
2. Run 1: counts gate (g1/g2) PASSED (13,134 total; own_e_b-notna 11,865 == analysis-set mask; syn 570, sub 10,757, nonsense 538 — all exact) then crashed at line 177 with `KeyError: 'epistatic_ecdf'`: I had built `syn`/`mis` as slices *before* assigning the flag columns to `tab`, and pandas copy-on-write never propagates columns added later into stale copies. Fix: moved the two slice assignments to after the flags (plus an inline note in the script); nothing else touched — this was a coding error, not a failed sanity check (gates g3–g6 had not executed), disclosed per AGENTS §7.
3. Run 2 (final): all gates passed first try after the fix.
Actual output (real numbers, final run):
```
=== N2a: row accounting (AGENTS 5) ===
total rows in folate_response_model5.csv: 13134
own_e_b notna (no SE involvement)        : 11865
analysis set (own_e_b & SE notna mask)   : 11865  [mask inherited from script 35 for count comparability; SE VALUES unused for flagging]
  synonymous    :    570  (expected 570)
  substitution  :  10757  (expected 10757)
  nonsense      :    538  (expected 538)
(g1)(g2) counts match J4a / task35_summary exactly -- OK
(g3) empirical FPR among synonymous at 0.95: 0.0509 (29/570) -> inside [0.03, 0.08] -- OK (by-construction check)
(g4) all 10757 missense rows map to a region -- OK
(g6) REPRODUCTION: recomputed retired N=2 region fractions match task35_summary.csv to 5.6e-17 (4/4 regions, n's match) -- rebuild == script 35 -- OK

==========================================================================
N2a: EPISTATIC SET BY SYNONYMOUS ECDF (SE values not used)
==========================================================================
  cutoff pct > 0.95    missense:  1785/10757 (16.6%)  syn (FPR):    29/570   ( 5.1%)  nonsense:    48/538   ( 8.9%)
  cutoff pct > 0.99    missense:   839/10757 ( 7.8%)  syn (FPR):     6/570   ( 1.1%)  nonsense:    22/538   ( 4.1%)
```
Verdict: **the nonparametric stratifier works and calibrates where the SE one couldn't.** Primary (pct > 0.95): 1,785/10,757 missense (16.6%) flagged with a synonymous FPR of 5.1% (29/570 — matches the by-construction 5%, gate (g3)); nonsense 8.9% as the second reference (higher than missense, as a real noise/impact floor should look: nonsense variants perturb e_b more often than missense). Sensitivity (pct > 0.99): 7.8% missense at 1.1% FPR. Contrast that the retired flag could not get below 28.4% syn FPR at any cutoff on disk (N=2: 44.7%). Gate (g6) proves the rebuild reproduces script 35's own numbers to **5.6e-17** before any comparison is trusted. Row accounting fully reconciled: 13,134 total → 11,865 analysis set (own_e_b-only count equals the mask count exactly — no rows dropped by the SE-validity component), types 570 + 10,757 + 538 = 11,865 ✓.
Files created/modified: `scripts/64_n2_nonparametric_epistatic_set.py` (new, next free number 64), `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry). Output file written by N2c (separate entry).
Anything unexpected or worth flagging:
- The first-run KeyError (stale slices) is disclosed above and in the script; it delayed nothing and touched no rule.
- **The ECDF FPR at the cutoff is ~5% by construction** — printed as such in the script's own output. The substantive result is that missense at the same cutoff is 16.6%, i.e. ~3.3× the noise floor (1785 observed vs ~541 expected-from-null at 5%: 16.6%/5.1% = 3.26× enriched) — THAT ratio is the nonparametric analogue of "epistasis beyond noise," and it is immune to the SE-scale problem entirely.
- Method choice: ECDF percentile, not EB local-FDR (assumption-avoidance, disclosed). This file must not be described as FDR-controlled.
---

## [N2b] — Region table under the new stratifier vs script 35's (does the pattern change?)
Status: PASS (executed to its pre-registered rule) — **verdict: CHANGED** (primary ordering rule fired), with the task-relevant nuance fully printed: the change is a near-tie flip between R1 and R3, while the coarse structure (R1/R3 high ≫ R4 mid ≫ R2 low) survives at every cutoff.
Time started / finished: 2026-09-22 18:24 – 18:26 EDT (same run as N2a)
What I did: mirrored script 35's region table (missense, regions 1–4, n's identical — verified against `task35_summary.csv` in gate (g6)) with old N=2 fraction (recomputed, not read from the retired file) vs new ECDF fractions at 0.95 (primary) and 0.99 (sensitivity), plus median |e_b| as the stand-in for the retired median-SE column. Pre-registered rule: pattern CHANGED iff the rank ordering of the four region fractions differs old vs new-at-0.95; levels explicitly not compared (44.7% vs ~5% syn FPR by construction).
Actual output (real numbers, final run):
```
==========================================================================
N2b: REGION TABLE (missense) -- retired N=2 vs new ECDF flags
==========================================================================
  region 1 (2-147) n= 2577  old_N2= 60.3%  new_0.95= 23.0%  new_0.99= 11.7%  delta_0.95= -37.3 pp  median|e_b|=0.1479
  region 2 (148-294) n= 2421  old_N2= 28.4%  new_0.95=  3.2%  new_0.99=  0.8%  delta_0.95= -25.2 pp  median|e_b|=0.0657
  region 3 (295-474) n= 2713  old_N2= 49.7%  new_0.95= 24.2%  new_0.99= 11.1%  delta_0.95= -25.5 pp  median|e_b|=0.1589
  region 4 (475-656) n= 3046  old_N2= 40.4%  new_0.95= 15.0%  new_0.99=  7.1%  delta_0.95= -25.4 pp  median|e_b|=0.1136

  ordering by fraction (high->low):
    retired N=2  : [1, 3, 4, 2]
    new pct>0.95 : [3, 1, 4, 2]
    new pct>0.99 : [1, 3, 4, 2]  (sensitivity)

  PRE-REGISTERED N2b VERDICT (ordering rule): CHANGED: old [1, 3, 4, 2] vs new [3, 1, 4, 2] -- the qualitative regional pattern does NOT survive the nonparametric replacement; note the 0.99 ordering [1, 3, 4, 2] also differs from 0.95's, so the new pattern is itself cutoff-sensitive
  (LEVELS are not comparable by construction: old syn FPR 44.7% vs new ~5%;
   ordering is the pre-registered comparison.)
```
Verdict: **CHANGED as the rule defines it** — old orders regions [1, 3, 4, 2]; new-at-0.95 orders [3, 1, 4, 2] (R1 and R3 swap the top slot). Reported with the full nuance the numbers support: (i) the top-two gap at 0.95 is 1.2 pp (24.2% vs 23.0%) and it *swaps back* at 0.99 (11.7% vs 11.1%, 0.6 pp the other way) — **the R1/R3 "change" is a near-tie flip, cutoff-sensitive, not a robust reordering** (the script's own verdict string says this too); (ii) what does NOT change at any cutoff: R2 stays lowest, R4 stays third, and R1/R3 stay far above R4/R2 — the coarse regional structure (R1≈R3 high, R4 mid, R2 low) survives the replacement; (iii) level drops are large and uniform-ish: −25 to −37 pp everywhere (R1 drops most, −37.3 pp), consistent with the old flag's 44.7% FPR inflating every region. Honest one-liner for the writeup: *the specific "R1 > R3" claim does not survive, the coarse "R1/R3 > R4 > R2" structure does.*
Files created/modified: `data/processed/task_N2_region_comparison.csv` (new — N2b's "report", a results table under `data/processed/` implied by the task's "recompute … and compare — report"; declared here explicitly), `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry).
Anything unexpected or worth flagging:
- My pre-registered rule fired CHANGED — reported as fired, not softened. The post-hoc-adjacent observation that it's a near-tie flip is ALSO reported (both directions), and the sensitivity ordering was pre-registered, so its flip-back is in-plan, not after-the-fact rescue.
- The task doc's expectation ("report whether the qualitative regional pattern changes") is answered: partially — top-pair order yes (fragile), everything else no.
- median|e_b| ranks [R3 0.1589, R1 0.1479, R4 0.1136, R2 0.0657] — matching the NEW 0.95 ordering's R3≈R1 top; the nonparametric magnitude view agrees with the ECDF flags, which makes the old R1>R3 order the outlier (plausibly an artifact of R1's region-specific SE factor 5.16 vs R3's 4.04 from J4b — noted as interpretation, not tested here).
---

## [N2c] — Save the replacement epistatic set to its own file
Status: PASS — written, row count exact, distinct filename, no reader of the retired file added.
Time started / finished: 2026-09-22 18:26 – 18:27 EDT
What I did: wrote the analysis-set rows to `data/processed/task_N2_nonparametric_epistatic_set.csv` (exact path named in the task doc) with columns `hgvs_pro, type, position, own_e_b, region, syn_ecdf_pct, epistatic_ecdf, epistatic_ecdf_99, epistatic_N2_old_RECOMPUTED`; wrote N2b's comparison table alongside (declared in N2b); printed the N1b-constraint confirmation from the script's own output.
Actual output (real, final run):
```
N2c: saved 11865 rows -> /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task_N2_nonparametric_epistatic_set.csv
N2c: region comparison -> /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task_N2_region_comparison.csv
     (distinct file from the retired task35_epistatic_set.csv; no reader of the
      retired file was added or changed -- N1b constraint respected)
```
Verdict: PASS — 11,865 rows (= full analysis set, zero dropped: 570 + 10,757 + 538), file distinct from the retired `task35_epistatic_set.csv` as required, old flag carried only as a clearly-labeled `…_RECOMPUTED` column (never read from the retired file), and the script printed the no-new-reader confirmation itself.
Files created/modified: `data/processed/task_N2_nonparametric_epistatic_set.csv` (new — the task's named deliverable), `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry); nothing else.
Anything unexpected or worth flagging:
- The `_RECOMPUTED` suffix on the old-flag column exists so nobody mistakes it for a join to the retired file (and so gate (g6)'s provenance — recomputed in-script, verified 5.6e-17 — travels with the data).
- Downstream guidance printed by the script: stratify on `epistatic_ecdf` (or `_99`), never on `epistatic_N2*`; the old column is retained only for old-vs-new auditing. Existing readers of the retired file (50, 59, 61) remain untouched per N1b — repointing script 50 to this new file is a user decision, flagged in N1b and again for L3.
---

## [L3a] — Draft the I1 epistemic-caveat addendum (do not merge)
Status: PASS — draft written **last**, after all L1/L2/M/N outcomes were known, exactly as the task's execution order requires; forbidden files untouched (MTHFR_RESULTS_LOG/RESULTS.md/REVIEW_TRIAGE were read-only sources here, never edited).
Time started / finished: 2026-09-22 18:30 – 18:45 EDT
What I did:
1. Read `docs/tasks/results-log/MTHFR_RESULTS_LOG.md` **verbatim** for Parts 5 and 6 (lines 161–255) plus its summary table (317–338) so every conditional claim is quoted from the real text — no claim names or numbers reconstructed from memory.
2. Wrote `docs/tasks/i1-mechanism-followup/ADDENDUM_I1_CAVEAT.md` with: (a) the six load-bearing follow-up outcomes (I1 gate numbers, L1c's floor, L1b's precision+detection-limit census, L2 BLOCKED→open question with the explicit "must not be written as either 'has power' or 'has no power'" instruction, M1's NOT SUPPORTED verdict, N-group retirement+replacement), (b) **claim-by-claim conditionality for Part 5/6** with a drop-in one-sentence caveat for each conditional claim (§5.2/5.3 conditional in interpretation not arithmetic; §5.4 and §5.5 NOT conditional; §6.2 conditional in never-calibrated form; §6.3/6.4 conditional as general claim, unchanged as within-dataset statement), (c) the **site-54 design caveat** (exclusion reason resolved as a numbering confusion — dropped 41×54 axis carries the paper's headline ε ≈ +5; frozen gate not rerun; four-site rerun flagged as a user-authorization decision item and the cheapest way to partially unblock L2), (d) adjacent unresolved items (script 50's retired-file read, N2b's ordering nuance, M1 cutting both ways), (e) provenance footer pointing at this log.
3. Verified no forbidden file was written: only `ADDENDUM_I1_CAVEAT.md` created in this step.
Actual output (the draft's load-bearing content, quoted from the file as written):
```
§5.2/5.3 caveat: "The signed −0.088 result is internally calibrated and holds
for this dataset, but the positive control built to show the same pipeline
can detect a known interaction was underpowered (35.3% power at the
comparator's own realized effect; floor ρ 0.540 > observed 0.447) and did
not clear, so 'AGAINST ESM-2's usefulness' should be read as a statement
about these measurements, not yet as a demonstrated property of the
pipeline's detection ability."
§5.4 / §5.5: NOT conditional (internal nulls; §5.5's p-values 0.001/0.006/
0.156/0.768 do not use the retired SE flag).
§6.2 caveat: "...no positive control exists for the MAE endpoint, and the
correlation endpoint's control (I1) failed its gate while underpowered."
§6.3/6.4 caveat: "...cannot distinguish 'ESM-2 fails on strong interaction'
from 'this evaluation could not certify success anywhere'..."
Net: "the numbers in Parts 5/6 are not overturned ... what I1's outcome
removes is the inference from those numbers to pipeline-level or
model-class-level conclusions."
Site-54: "the dropped 41×54 axis carries the source paper's headline ε ≈ +5
... frozen gate was not rerun with four sites ... Decision item for review."
```
Verdict: PASS — the addendum answers the task's question ("exactly which claims are conditional, and the honest one-sentence caveat") for every Part 5/6 claim, distinguishes conditional-interpretation from conditional-arithmetic (so §5.3's clean null isn't unfairly retracted), carries the L1a site-54 design caveat, and obeys the draft-only constraint.
Files created/modified: `docs/tasks/i1-mechanism-followup/ADDENDUM_I1_CAVEAT.md` (new — the task's named deliverable), `docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md` (this entry). `MTHFR_RESULTS_LOG.md` read-only; `RESULTS.md` / `REVIEW_TRIAGE.md` untouched entirely.
Anything unexpected or worth flagging:
- The draft deliberately reports BOTH directions on two items where a one-sided summary would mislead: N2b (rule fired CHANGED, but it's a cutoff-sensitive near-tie flip) and M1 (H1a unsupported, yet severity-insensitivity is also unsupported). Both are in the addendum's §4.
- The four-site rerun recommendation is presented as a *decision item requiring authorization*, not performed — per AGENTS §0/§10 (frozen gate executed once; post-hoc change needs the user).
- The addendum names script 50's D1 numbers as needing "a footnote or a rerun" — I did not determine WHICH D1 outputs the writeup uses; that's left for review rather than guessed.
---

## SUMMARY

**Tasks completed / blocked / skipped** (every subtask in `I1_MECHANISM_FOLLOWUP.md`, one `## [ID]` entry each in this log, every entry backed by an executed run):

| Group | Completed | Blocked | Skipped |
|---|---|---|---|
| L | L1a, L1b, L1c, L3a | L2a (no stronger comparator on disk; ProteinGym set never downloaded) | L2b, L2c (conditional on L2a) |
| M | M1a, M1b, M1c, M1d, M1e | — | — |
| N | N1a, N1b, N2a, N2b, N2c | — | — |

**L1c's number and implication (the task doc's single most important number):** the smallest true effect I1's null test could detect at power ≈0.8 is **ρ_floor = 0.5400** (crit 0.4755 + 0.8416 × se 0.0767; all sensitivities 0.5109–0.5418 agree in direction), while the comparator's known/realized effect in test units is **ρ = 0.4467 — below the floor**, i.e. this gate had only **35.3% power** at the effect it was looking for. Pre-registered verdict **COMPARATOR-UNDERPOWERED**: I1's gate failure is substantially a power failure of *this test on this design*, not proof the pipeline can't see epistasis — which triggered L2 (attempted; BLOCKED for lack of any second comparator on disk), leaving the pipeline-power question genuinely **open in both directions**.

**M1d's verdict:** **NOT SUPPORTED** — A222V does not sit outlier-LOW: residual +0.00954 with 95% position-cluster CI [−0.00573, +0.02640] (contains 0; point estimate leans *opposite* to H1a), rank 6/9, higher shift than all four favorable backgrounds. Per the task's own wording, the H1a mechanism is not supported and the weak δ_ESM signal needs a different explanation. Read alongside M1e: the generic severity→shift relation *does* hold (Spearman −0.4667, CI [−0.5833, −0.0667]), so neither "A222V is special to the model" nor "the model ignores background severity" survives.

**Single most important thing to look at first:** the **L1c entry in this log** (and its script `scripts/62_l1c_detectable_effect_floor.py` / `data/processed/task62_l1c_floor.csv`) — the floor-vs-effect calculation (0.5400 vs 0.4467, 35.3% power) is what rewrites how every Part 5/6 negative claim may be stated; then review the **draft `ADDENDUM_I1_CAVEAT.md`** (L3a), which applies exactly that reframing claim-by-claim. Two decisions await your call, both flagged and NOT taken: authorizing a four-site (54-included) I1 rerun to strengthen the comparator in-house, and what to do about `scripts/50_d1_stratifier_quality.py`'s read of the retired flag file.

Housekeeping: no commits made or requested; `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `REVIEW_TRIAGE.md` untouched; prior-session stray scripts (32–40) untouched; new files this session = `FOLLOWUP_LOG.md`, `ADDENDUM_I1_CAVEAT.md`, scripts `61`/`62`/`63`/`64`, script 35's DEPRECATED header (one sanctioned edit), and results in `data/processed/` (`task61_*`, `task62_*`, `task63_*`, `task_N2_*`).
---

