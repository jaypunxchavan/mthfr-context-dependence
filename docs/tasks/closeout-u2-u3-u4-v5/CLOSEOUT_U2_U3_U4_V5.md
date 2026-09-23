# Closeout — U3 Diagnosis, V5 Matched-N, Full U2 Run, U4 Execution

Source: this session's SESSION_LOG.md review. Four items are open:

1. **U3 (ESM-1v) was reported BLOCKED but its raw entry was never pulled
   and reviewed** — unlike U4, whose block reason (a genuine judgment call)
   was read in full. U3's reason is unknown here. Do not assume it's the
   same kind of block as U4; read it first.
2. **V5's head-to-head (ESM-2 vs ThermoMPNN) ran on unmatched n** (10,757
   vs 9,595). Cheap to fix, removes the one hedge in an otherwise clean
   comparison.
3. **U2's full run is authorized**, but its own log entry's timing
   breakdown suggests the "~3-4h" estimate for the recommended overnight
   command may be optimistic — Phase 3 (the brute-force phase) was only
   measured at `BRUTE_N=2`; the recommended command uses `BRUTE_N=16` (8x),
   and if that phase scales roughly linearly, the real total is closer to
   5-6 hours than 3-4. Measure before committing, per AGENTS §1's own rule
   about not inheriting a runtime estimate.
4. **U4 (SaProt) is authorized**, with its three blocking decisions now
   settled: chain A (matches the ThermoMPNN/V2 precedent), exclude
   unresolved positions rather than impute (same precedent), and foldseek
   installation is authorized.

---

## Group Z0 — Diagnose U3 before touching it

**Task Z0 — Read U3's actual block reason**
- Z0a. `sed -n '/^## \[U3\]/,/^---$/p' docs/tasks/comparators-and-consolidation/SESSION_LOG.md`
  (or the exact line range from `grep -n "^##"` if that pattern doesn't
  match — confirm the real heading format first, do not assume). Quote
  the full entry in this session's log before doing anything else.
- Z0b. Classify the block, using U4's two outcomes as the reference
  cases: was it (a) a genuine judgment call like U4 turned out to be
  (multiple defensible choices, no project precedent) — if so, STOP and
  report it plainly, do not guess a resolution; or (b) a mechanical
  limit like a budget cap, a missing dependency, or a fetch failure — if
  so, proceed to Z0c.
- Z0c. If mechanical: resolve it using the same discipline already
  established elsewhere in this project (check actual sizes before
  assuming a cap is exceeded, verify a fetch failure is genuinely
  unrecoverable before giving up, etc.), then run ESM-1v's scoring +
  correlation exactly as U3's original task specified (fetch, score
  MTHFR the same way script 10/11 did for ESM-2 650M, compute
  delta_ESM's correlation with e.b the same way as script 32, sign-flip
  null via script 33's code path, region breakdown). If resolving it
  would itself require a judgment call not contemplated in the original
  task, stop there too — do not chain past one unblock into inventing a
  second one.

---

## Group Z1 — V5 matched-n cleanup

**Task Z1 — Rerun the ESM-2 vs ThermoMPNN head-to-head on a strictly matched row set**
- Z1a. Build the exact intersection of the two predictors' analysis sets
  (the `hgvs_pro`s present in both `task32_delta_esm_primary.csv`'s
  own-e.b rows and `task_V2_thermompnn_ddg.csv`'s matched rows). Report
  the intersection's n.
- Z1b. Recompute both correlations (ESM-2 delta_ESM vs own e.b;
  ThermoMPNN pred_eb vs own e.b) on that identical row set, same
  position-cluster bootstrap convention (N_BOOT=10000, seed 0, matching
  the rest of the project).
- Z1c. Report side by side with the original, unmatched-n V5 result.
  State plainly whether "ESM-2 nominally larger" still holds once n is
  controlled for, or whether it was partly an artifact of the two
  predictors covering different variant sets.
- Z1d. Save to `data/processed/task_Z1_matched_n_headtohead.csv`.

---

## Group Z2 — U2's full run, with a measured (not assumed) timing budget

**Task Z2a — Measure BRUTE_N=16's real per-unit cost before committing to the full run**
- Run Phase 3 (the brute-force phase) alone, at `BRUTE_N=16`, on a small
  slice (50-100 rows — reuse whatever slicing mechanism the smoke run
  already used, do not build a new one). Measure wall-clock time,
  compute per-row cost, and extrapolate to the full row count used in
  the original `BRUTE_N=2` measurement (2,620 rows). Compare this
  MEASURED extrapolation against the naive 8x-scaling assumption
  (1,643s × 8 ≈ 13,144s ≈ 219 min) from the prior session's own
  breakdown. Report both numbers.

**Task Z2b — Decide the full run's actual scope from Z2a's real measurement**
- Sum Z2a's measured Phase-3 cost with the OTHER phases' already-measured
  costs, rescaled from `PHASE2_MAX=300` smoke to the full row count
  (11,344) the same way Phase 2's own smoke-to-full ratio was computed in
  the original entry (7,033s for the phase-2-at-full-n figure already
  given — reuse it directly, do not remeasure Phase 2). Produce one
  total projected runtime for `PHASE2_MAX=0 BRUTE_N=16 N_BOOT=10000
  N_PERM=10000`.
  - **If the projected total is ≤ 5 hours:** proceed to Z2c, run at full
    `BRUTE_N=16` as originally planned.
  - **If the projected total exceeds 5 hours:** do NOT run at
    `BRUTE_N=16`. Instead compute the largest `BRUTE_N` value that keeps
    the projected total under 5 hours (using Z2a's measured per-unit
    cost), and run at THAT value instead. Log this explicitly as a
    reduced-resolution run relative to the originally suggested command,
    with the exact `BRUTE_N` used and why.

**Task Z2c — Run it, with a mechanically enforced wall-clock cap**
- Wrap the actual invocation in a shell-level timeout so the cap is
  enforced mechanically rather than relying on the script to notice its
  own runtime: `timeout 5h venv/bin/python3 scripts/67_u2_pll_delta.py`
  (adjust the duration to match whatever Z2b decided, plus a small
  margin — do not set the timeout below the projected total). Run in the
  foreground. If `timeout` kills the process, that is not a script
  failure — log it as a BUDGET STOP, report whatever partial
  progress/output exists (the script's own smoke output showed it prints
  incremental phase completion; capture whatever got logged before the
  kill), and do not treat a partial/no result as a negative finding.

**Task Z2d — Report and compare**
- Full results: rho, CI, p for signed delta_PLL vs signed e_b (both own
  and published), same format as the smoke output. Compare directly
  against the original delta_ESM's -0.088118. State plainly: does the
  whole-sequence pseudo-log-likelihood construction change the
  direction, magnitude, or statistical significance of the finding
  relative to the single-position masked-marginal version.

---

## Group Z3 — U4's execution, now unblocked

**Task Z3a — Install foldseek**
- Check the standard installation path (conda-forge package, or a
  precompiled binary from the foldseek GitHub releases) before
  attempting anything. Verify a checksum if one is published. Log the
  exact method and version installed.

**Task Z3b — Fetch SaProt weights**
- Fetch `SaProt_650M_PDB.pt` (already confirmed at 2,606,464,143 B,
  within the 3GB cap). Do not also fetch the redundant `.bin` format —
  the prior session's own entry noted these are the same model in two
  formats.

**Task Z3c — Generate 3Di tokens for chain A of 6FCX**
- Use ONLY chain A (decision 1, settled: matches the ThermoMPNN/V2
  precedent). Confirm the resulting token count matches chain A's 596
  resolved residues exactly — this is a gate, not a formality; if it
  doesn't match, stop and diagnose before proceeding, the same
  discipline V2 used for its own offset-mapping gate.

**Task Z3d — Score using SaProt's own inference path, not a hand-rolled one**
- Look for SaProt's bundled scoring/inference example (the same
  "reuse their own CLI, don't reimplement" discipline V2 used for
  ThermoMPNN) before writing any new scoring logic. Adapt only as much
  as necessary to fit this project's WT-background and
  A222V-background scoring convention.

**Task Z3e — Document and apply the frozen-structure convention explicitly**
- Standard SaProt DMS practice — noted as "first contact" in this repo
  by U4a's own entry — reuses the SAME 3Di structure tokens for both the
  WT-background and A222V-background scoring passes (only the amino-acid
  channel changes; the backbone/fold is assumed effectively unchanged by
  a single substitution). State this assumption explicitly in the new
  script's docstring before running, exactly as every other convention
  in this project has been pre-registered rather than assumed silently.

**Task Z3f — Score all resolvable positions, WT and A222V background**
- Same exclusion policy as decision 2 (settled): exclude the 59
  unresolved chain-A positions rather than impute. Report the exact
  excluded row count and compare it against V2's own exclusion count
  (1,046 rows at those same 59 positions) — if SaProt's resolved set
  doesn't match ThermoMPNN's exactly, say so and explain why (e.g. a
  tokenizer-level difference), do not assume it will match without
  checking.

**Task Z3g — Build SaProt's own delta_ESM-style statistic and test it**
- `delta_SaProt(v) = S_SaProt(v | A222V bg) - S_SaProt(v | WT bg)`, same
  construction as script 12/32. Correlate against own e.b and published
  e.b, position-cluster bootstrap, same convention as script 32. Run it
  through script 33's sign-flip null code path (reuse, do not rewrite).

**Task Z3h — Region breakdown**
- Same four-region check as every other finding in this project.

**Task Z3i — Update, don't overwrite, the model-robustness summary**
- Append SaProt's results as a new row to whatever U5 already produced
  (`data/processed/task_U5_model_robustness_summary.csv`) rather than
  regenerating that file from scratch — preserve the ESM-2 650M/150M and
  any U3 (ESM-1v) results already in it.

---

## Suggested execution order

1. **Z0** first — cheap, and its outcome (mechanical vs judgment-call)
   decides whether U3 closes tonight or just gets clearly flagged.
2. **Z1** — quick, independent of everything else, do it early.
3. **Z2a/Z2b** — the timing measurement, before anything else in Z2.
   This is the step that prevents an 8-hour surprise.
4. **Z2c/Z2d** — the actual full run, once Z2b has set a real budget.
5. **Z3** — independent of Z0/Z1/Z2, can run in parallel with the U2
   full run if the environment supports it, or sequentially otherwise.

If Z2's full run is still going when everything else is done, that's
fine — it's wrapped in `timeout` and will stop itself. Don't let it block
writing up Z0/Z1/Z3's results in the log.
