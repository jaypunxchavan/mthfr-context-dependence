# Position-54 Verification, I1 Rerun, and Script 50 Migration

Source: `ADDENDUM_I1_CAVEAT.md` §3 and `FOLLOWUP_LOG.md` entries L1a/L1b, from
the I1-mechanism-followup run. Two claims from that run are acted on here:

1. **The site-54 claim.** L1a reported that I1's comparator (script 49,
   GB1) was built on only 3 of GB1's 4 known interacting sites (39/40/41,
   excluding 54), that the exclusion was logged as a data inconsistency
   ("file's WT letter V contradicts RCSB 2GB1's T44") but was actually a
   **numbering confusion** (the real site is 54, not 44), and that the
   dropped 41×54 axis carries the comparator paper's headline interaction
   effect (Wu et al. 2016, Fig 3D, ε≈+5). This has NOT yet been
   independently re-derived from the primary source in this project — it
   is one claim, from one run, that the rest of tonight's conclusions
   (L1c's power verdict, the whole I1-underpowered reading) partially rest
   on. Verify it before authorizing anything built on top of it.
2. **Script 50 reads the retired flag.** N1b confirmed script 50 reads
   `data/processed/task35_epistatic_set.csv`, which J4a showed has FDR
   0.91-1.00 even after correction. It needs to migrate to
   `task_N2_nonparametric_epistatic_set.csv` (built in the prior session's
   N2 task), not be footnoted.

---

## Group P — Verify the site-54 claim before building on it

**Task P1 — Independently re-derive the exclusion reason, from scratch**
- P1a. Open `scripts/49_*.py` (whatever the actual I1 script is named — confirm
  the exact filename first, do not assume) and find the exact line that
  excluded the 4th site. Quote it verbatim in the log, not paraphrased.
- P1b. Independently look up RCSB structure 2GB1's residue numbering for
  the relevant region (do not just trust the addendum's claim — check the
  actual PDB file or RCSB's own residue listing if it's on disk, or via
  whatever reference GB1 files already exist under `data/raw/`). Confirm,
  from the primary source, whether the correct site is 54 or 44, and
  whether "VDGV" as a wild-type string is consistent with V39/D40/G41/V54
  as the addendum claims.
- P1c. Locate wherever GB1's raw data file (`GB1_fitness_landscape.txt`,
  per L1b's md5-logged file) actually lives and confirm site 54's column/
  row exists in it and is populated, not just assumed present.
- P1d. State a plain verdict: CONFIRMED (the numbering-confusion story
  holds, site 54 exists and was validly excluded only by a mislabeled
  check) or NOT CONFIRMED (something in the chain doesn't hold — say
  exactly what). **If NOT CONFIRMED, stop this entire task doc and report
  back — do not proceed to P2/P3 or Group Q.**

**Task P2 — Confirm the headline-effect claim, from the actual source**
- P2a. If GB1's source paper (Wu et al. 2016) or a machine-readable
  version of its Figure 3D data is available anywhere on disk, locate the
  reported ε value for the 41×54 interaction directly and quote it. If the
  paper is not available locally, state that plainly rather than
  re-asserting the addendum's "ε≈+5" from memory — this number should be
  independently re-confirmed, not passed through a second time unchecked.
- P2b. Only if P1d is CONFIRMED and P2a either confirms the effect size or
  explicitly can't be checked: proceed to Group Q. Otherwise stop and
  report.

**Task Q1 — Four-site I1 rerun (only if P1/P2 pass)**
- Q1a. Build the four-site version of I1's design (sites 39/40/41/54
  instead of 39/40/41), following the exact same construction the original
  script 49 used for the 3-site version — same seed, same K, same
  pipeline code path (per the original task doc's L2b instruction: reuse
  the exact delta_ESM + sign-flip-null pipeline, do not rewrite it).
- Q1b. Run it. Report the new pooled rho, null mean, p-value, and CI —
  same format as the original I1 output, so it's directly comparable.
- Q1c. State plainly: does the four-site version clear the gate? If yes,
  does it also partially unblock L2a (i.e., does this now count as "an
  alternative comparator found," even though it's a modification of the
  same one rather than a wholly separate dataset)? If no, report that too
  — a four-site rerun that still fails is informative, not a wasted
  effort.
- Q1d. Save results to `data/processed/task_Q1_foursite_i1_rerun.csv`.
  This is a NEW, separate result — do not overwrite anything from the
  original I1 run or from L2's prior (blocked) attempt.

**Task Q2 — Update the addendum, do not touch the results log**
- Q2a. Append a new section to `docs/tasks/i1-mechanism-followup/ADDENDUM_I1_CAVEAT.md`
  (append only — do not rewrite what's already there) summarizing P1/P2's
  verification outcome and Q1's rerun result, with the same "DRAFT, not
  merged" framing as the rest of that file.
- Q2b. Do NOT edit `MTHFR_RESULTS_LOG.md`, `RESULTS.md`, or
  `REVIEW_TRIAGE.md`. Same rule as every prior session.

---

## Group R — Migrate script 50 off the retired SE flag

**Task R1 — Understand what script 50 actually does before changing it**
- R1a. Read `scripts/50_*.py` (confirm exact filename first) in full.
  Identify every place it reads `task35_epistatic_set.csv`, what column(s)
  it uses (`epistatic_N2`, or something else), and what it does with that
  flag downstream — is it a stratifier for a correlation, a filter for a
  subset, something else. Quote the relevant lines in the log.
- R1b. Identify whether script 50's output is cited anywhere in
  `MTHFR_RESULTS_LOG.md` or `REVIEW_TRIAGE.md` already (grep for its output
  filename or any number it's known to produce). If it IS already cited
  as a "settled" result, flag this explicitly — migrating its input will
  change a number that's already been written up as fact, and that needs
  to be visible, not quietly absorbed.

**Task R2 — Migrate**
- R2a. Modify script 50 to read `data/processed/task_N2_nonparametric_epistatic_set.csv`
  instead of the retired file, using whatever the equivalent flag column
  is called in that file (check N2's actual column name — do not assume
  it matches `epistatic_N2`'s name).
- R2b. Add a one-line comment at the read site noting the migration and
  pointing at N1a's deprecation header, so a future reader knows why this
  changed.
- R2c. Rerun script 50 end to end. Report its full output, old-vs-new,
  side by side if the old output is still available anywhere (check
  `data/processed/` for a prior saved output file before it gets
  overwritten — copy it to a `*_PRE_MIGRATION.csv` backup first if found).
- R2d. State plainly: did migrating the stratifier change script 50's
  qualitative conclusion, or just its exact numbers? This is the number
  I actually need from this task.

---

## Suggested execution order

1. **P1, P2** — verification first, always. Everything else in this doc is
   conditional on these passing.
2. **Q1, Q2** — only if P1/P2 pass. If they don't, skip Q entirely and go
   straight to R (R doesn't depend on P/Q at all).
3. **R1, R2** — independent of P/Q, can run before, after, or in parallel.

If P1 or P2 comes back NOT CONFIRMED, do not attempt Q1 "anyway to see what
happens." A rerun built on an unverified premise is exactly the kind of
result that looks like progress and isn't.
