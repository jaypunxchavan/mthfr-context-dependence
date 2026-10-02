# GB1 regime map - pre-registration v2

Frozen 2026-10-01, before any GB1 scoring. Supersedes v1 (frozen block sha256 b170bdfff729a017def585047e503a86151ba1e89d2632ae9bc5e8eb9c137613).
Authors: Arnav (PI), Claude (planning). This file is self-contained. It carries v1's question, statistic, decision rules and disclosure forward
and amends v1's roster, resampling units, gates and execution, and fixes the three items v1 left open (read-depth qualification, the scored
sequence, passes per background). The amendments were fixed after Phase 3a (acquisition) and before any GB1 delta value existed.

## 1. Question

Across many fixed single-mutant backgrounds in one protein with a complete double-mutant matrix, how does the ESM-2 background-shift statistic behave
as a function of regime? This is a characterisation of the statistic, not a test of any MTHFR result, and its interpretation does not depend on any MTHFR outcome.

## 2. Statistic

For each background b (a GB1 single mutant) and each qualifying partner variant v measured in combination with b:
delta_b(v) = S(v | b) - S(v | WT), S = ESM-2 650M masked-marginal log-odds against the wild-type residue, one unbatched forward pass per (background, position).
e_b(v) = the measured genetic-interaction term for the pair (b, v), by the same construction the project's existing GB1 transplant code uses (script 73, as reproduced
in Phase 3a T3). rho_b = Spearman(delta_b, e_b) over b's qualifying partners, excluding any partner at b's own position.

## 3. Amendments and resolved items

A1 Partner qualification ("high-confidence"). The publisher's file has no confidence column; the only confidence signal is the read depth `Input Count`. A double mutant
qualifies iff Input Count >= 25 (PRIMARY). Sensitivities, all reported, none selected: >= 23, >= 28, and unfiltered. Rationale: the integer thresholds 23 through 28 are exactly
those whose retained double-mutant count lies inside the paper's stated 509,693-517,278 range (Phase 3a T2-G1); 25 is the midpoint, fixed without reference to any score.
v1's floor of 100 qualifying partners is retained but is inert (every one of the 1,045 singles clears it under every threshold).

A2 Scored sequence. The sequence actually assayed: the project's 2GB1 constant with position 2 = Q (the documented template change T228Q). The wild-type arm is one masked-marginal pass at each of
the 55 assayed positions 2..56 under this sequence, computed once. Each background receives 54 passes (the 55 positions minus its own). No pass at position 1, which is never a target.

A3 Gate G-1 replaced. v1's G-1 (reproduce the recorded V54A control rho = +0.122 from the whole-domain matrix) cannot be met: that control came from the four-site library. G-1' (hard): rescoring the V54A
background and the wild-type arm at positions 39, 40, 41 on the PROJECT sequence (T at position 2) reproduces script 73's cached delta_esm for all 57 variants to 1e-6, and the control rho
re-derives as +0.12218045112781956 (to 1e-9). This proves the machinery independent of the sequence choice. V54A on the assayed sequence is reported, not gated.

A4 Roster. All 1,045 single mutants qualify under every threshold. 400 are drawn with numpy.random.default_rng(0).choice(sorted_ids, 400, replace=False), sorted_ids = the single-mutant ids sorted
lexicographically by (position, mutant). Scoring order is the draw order, so any completed prefix is a random subsample. The roster is written to disk and hashed before scoring. No fitness-based or
severity-based selection at any point.

A5 Resampling units (corrects v1 section 4, which conflated them). rho_b's own 95% CI: position-cluster bootstrap (clusters = partner positions; every variant at a drawn position comes with it,
with multiplicity), N_BOOT = 2000, SEED = 0, a descriptive interval. Every statistic ACROSS backgrounds (the distribution's mean; each covariate's Spearman): background-level bootstrap (backgrounds
resampled with replacement, each rho_b held fixed), N_BOOT = 10000, SEED = 0; permutation p from 10,000 shuffles of the covariate across backgrounds.

A6 Gate G-3 strengthened. The bootstrap routine must (i) reproduce its point estimate with every cluster once, AND (ii) agree draw by draw to 1e-12 with an obvious slow reference implementation on
three real backgrounds using identical pre-drawn cluster ids, AND (iii) reproduce Phase 1's published MTHFR CI [-0.1173334458953319, -0.0595113844951173] on the MTHFR anchor rows. The identity gate
alone cannot detect a cluster-to-row mapping error.

A7 Sensitivities (reported, none selected): partner thresholds 23 and 28 and unfiltered (recompute every rho_b and the four covariate tests); and the first 20 backgrounds in roster order scored on BOTH
sequences (assayed and project), reporting the Spearman between the two rho_b vectors and max |delta rho_b|.

A8 Coverage and partial completion. G-4 retained: each background scores at least 95% of its eligible positions. The analysis requires at least 200 completed backgrounds in roster order; with fewer, the
distribution is reported but the covariate tests are labelled UNDERPOWERED and not interpreted.

## 4. Primary analysis

The distribution of rho_b across the completed roster: n, mean, median, SD, range, and the fraction with rho_b < 0. Pre-registered regime covariates, each tested against rho_b by Spearman:
(a) mean sequence separation |pos(b) - pos(v)| over b's qualifying partners; (b) the background's own measured single-mutant fitness; (c) n_partners; (d) the SD of e_b over b's partners.

## 5. Decision rules (constants fixed now)

- Per covariate: ASSOCIATED iff the background-level bootstrap CI of its Spearman excludes 0; NOT RESOLVED otherwise. NOT RESOLVED is reported as "n cannot resolve this", never as "no relationship".
- Distribution centering: CENTERED iff the background-level bootstrap CI of the mean rho_b includes 0; OFF-CENTER otherwise. If OFF-CENTER, that is a property of the statistic in this system and is
  reported with equal prominence either way.
- Wording rule: no result from this map may be described as confirming, supporting or undermining any MTHFR result. The systems, backgrounds and measurement platforms differ.

## 6. Gates (a failed gate stops the run; thresholds are never loosened)

G-1' (A3); G-2 no partner at a background's own position enters any rho_b; G-3 (A6); G-4 and A8; G-5 the sequence used for scoring (assayed) matches the sequence the fitness data implies at every
position 2..56; G-SYN the analysis pipeline recovers a planted signal and a planted null on synthetic scores built from the real partner sets and e_b.

## 7. Execution

Detached, resumable, one output file per background, in roster order, under a lock, only after Phase 2's scoring has completed (done). Timing measured in a smoke run, not assumed.

## 8. Disclosure

The MTHFR anchor motivated building this map, but the map's rules and covariates were fixed before any GB1 score existed and do not reference any MTHFR value (the only MTHFR numbers cited are the
bootstrap-gate reproduction targets in A6). Any deviation must be disclosed in the log and, if it changes a rule or constant, requires a new versioned pre-registration, never an edit to v2.
