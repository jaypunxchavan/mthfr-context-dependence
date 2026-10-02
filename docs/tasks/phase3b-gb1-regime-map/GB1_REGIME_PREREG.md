# GB1 regime map — pre-registration v1

Frozen 2026-09-28, before any GB1 scoring. Authors: Arnav (PI), Claude (planning).

## 1. Question

Across many fixed single-mutant backgrounds in one protein with a complete double-mutant matrix, how
does the ESM-2 background-shift statistic behave as a function of regime? This maps where the
statistic is and is not well-behaved. It is a characterisation of the statistic, not a test of any
MTHFR result, and its interpretation does not depend on the MTHFR placebo outcome.

## 2. Statistic

For each background b (a GB1 single mutant) and each partner variant v measured in combination with b:
delta_b(v) = S(v | b) − S(v | WT), where S is ESM-2 masked-marginal log-odds vs the wild-type residue,
one unbatched forward pass per (background, position), matching the MTHFR convention.
e_b(v) = the measured genetic-interaction term for the pair (b, v), computed by the same construction
the project's existing GB1 transplant code uses, quoted in the Phase 3a log.
rho_b = Spearman(delta_b, e_b) over b's high-confidence partners, excluding any partner at b's own
position.

## 3. Roster (fixed before scoring)

Every GB1 single mutant with at least **100 high-confidence partners**, capped at **400 backgrounds**.
If more than 400 qualify, take a seed-0 sample: `numpy.random.default_rng(0).choice(sorted_ids, 400,
replace=False)`. The roster is written to disk before any scoring. No fitness-based or
severity-based selection at any point — qualification is by partner count alone.

## 4. Primary analysis

The distribution of rho_b across the roster: n, mean, median, SD, range, and the fraction with
rho_b < 0. Each rho_b carries a position-cluster bootstrap 95% CI (clusters = partner positions,
N_BOOT = 10000, seed 0).

**Pre-registered regime covariates, all fixed now, each tested against rho_b by Spearman with a
position-cluster bootstrap CI and a 10,000-shuffle label-permutation p:**
- (a) mean sequence separation |pos(b) − pos(v)| over b's partners;
- (b) the background's own measured single-mutant fitness;
- (c) n_partners;
- (d) the SD of e_b over b's partners (the dynamic range available to the correlation).

## 5. Decision rules (constants fixed now)

- **Per covariate:** ASSOCIATED iff the bootstrap CI of its Spearman excludes 0; NOT RESOLVED
  otherwise. NOT RESOLVED is reported as "n cannot resolve this," never as "no relationship."
- **Distribution centering:** the rho_b distribution is CENTERED iff the bootstrap CI of its mean
  includes 0; OFF-CENTER otherwise. If OFF-CENTER, that is a property of the statistic in this system
  and must be reported as such, with equal prominence either way.
- **Wording rule:** no result from this map may be described as confirming, supporting, or
  undermining the MTHFR anchor. The systems, backgrounds, and measurement platforms differ. Any
  cross-system statement requires its own pre-registration.

## 6. Gates (a failed gate stops the run; thresholds are never loosened)

- **G-1:** the V54A background's rho_b reproduces the recorded positive-control value (ρ = +0.122)
  to the precision it was recorded at.
- **G-2:** no partner at a background's own position enters any rho_b.
- **G-3:** bootstrap identity — every cluster once reproduces the point estimate to 1e-12.
- **G-4:** each background scores at least 95% of its eligible positions.
- **G-5:** the wild-type GB1 sequence used for scoring matches the sequence the fitness data implies,
  at every position.

## 7. Execution

Detached, resumable, one output file per background, **only after Phase 2's scoring has completed**
(96 complete background files and a 96-row manifest). Smoke run first. Timing measured in the smoke
run, not assumed.

## 8. Disclosure

The MTHFR anchor motivated building this map, but the map's rules and covariates were fixed before any
GB1 score existed and do not reference any MTHFR value. Any deviation must be disclosed in the log and,
if it changes a rule or constant, requires a new versioned pre-registration (v2), never an edit to v1.
