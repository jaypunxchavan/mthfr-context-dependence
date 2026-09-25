# Migration Log — Position-54 Verification, I1 Rerun, and Script 50 Migration

Task doc: `docs/tasks/site54-and-script50-migration/SITE54_AND_SCRIPT50_MIGRATION.md`
Binding rules: `AGENTS.md` (repo root), read in full at session start.
Logging protocol: one `## [TASK ID]` entry per task (pass/fail/partial/blocked),
never batched, always with real quoted output, written immediately after each
task executes and before the next task starts.

Hard gate: task doc P1d — if the site-54 numbering-confusion story does not
independently verify from primary sources, Group P and Group Q stop
immediately (Q1/Q2 logged SKIPPED, "P1 did not confirm") and the session
moves to Group R, which does not depend on P/Q.

Files this session is forbidden to modify at any point: `RESULTS.md`,
`docs/tasks/results-log/MTHFR_RESULTS_LOG.md`,
`docs/tasks/review-triage/REVIEW_TRIAGE.md`.
`docs/tasks/i1-mechanism-followup/ADDENDUM_I1_CAVEAT.md`: APPEND-ONLY (Q2a),
never rewritten — word-count/diff check before and after the append.
Stray first-session scripts (32, 33, 34, 36, 37, 38, 39, 40): ignored entirely,
never read, never built on.

Created: 2026-09-22 (first action of this session, before any other file).
---

## P1 — Independently re-derive the 4th-site exclusion reason from primary sources
Status: PASS
Time started / finished: 2026-09-22 21:56 / 2026-09-22 22:04
What I did:
- P1a: ran `ls scripts/*.py | sort` — exact I1 script filename is
  `scripts/49_i1_gb1_positive_control.py` (confirmed via `ls scripts/49_*.py`).
  Grepped and `sed`-extracted every 4th-site exclusion mention verbatim.
- P1b: ran `ls -R data/raw/` + repo-wide `find` for any 2GB1 file in any
  format → **none on disk** (only PDB present is `./data/raw/6FCX.pdb`, the
  MTHFR structure). Because no local file existed, attempted a live fetch of
  the primary source: `webfetch https://files.rcsb.org/download/2GB1.pdb` →
  **SUCCESS** (86,103 bytes, 1,063 lines, ends `MASTER`/`END`). Internet IS
  available in this environment, so the anticipated BLOCKED condition
  ("cannot access RCSB AND no local structure file") did not trigger.
  Parsed the fetched PDB record programmatically with `venv/bin/python3`
  (SEQRES + ATOM columns read by column index; no new repo file created —
  used the harness's own cached fetch text outside the repo).
- P1c: located the raw GB1 file, verified md5, and counted column-4
  population across all rows with `venv/bin/python3`.
- P1d: assembled the chain verdict below.
Actual output (real numbers and quoted source text):
P1a — exact filename: `scripts/49_i1_gb1_positive_control.py`.
Verbatim exclusion quotes (line numbers from grep/sed):
  - Docstring header (line 27): `SITES — AND WHY SITE 4 IS DROPPED (logged contradiction)`
  - Lines 31-34: `Genotype column 4 has WT letter V, but 2GB1 position 44 is` / `T (V39 D40 G41 E42 W43 T44) — the file and the authoritative sequence` / `disagree about the fourth site's WT residue, and the paper's own numbering` / `could not be retrieved tonight to resolve it. Conservative resolution: use` / `only the unambiguous consecutive triplet (sites 39/40/41), hold column 4 at` / `its WT letter "V" (an 8,000-genotype sub-landscape), and disclose the` / `exclusion rather than guess a numbering.`
  - Line 137: `COL4_WT = "V"                  # dropped site held at WT letter`
  - Line 177: `f"site4 dropped (file WT letter V vs 2GB1 T44 — contradiction)")`
  - Line 383: `print("  - Site4 excluded: file WT letter V vs 2GB1 T44 contradiction,")`
  - Line 384: `    unresolved without the paper's numbering (disclosed, not guessed).")`
P1b — RCSB primary source (`https://files.rcsb.org/download/2GB1.pdb`, fetched
live 2026-09-22), parsed output:
  - `HEADER    IMMUNOGLOBULIN BINDING PROTEIN          15-MAY-91   2GB1`
  - `DBREF  2GB1 A    2    56  UNP    P06654   SPG1_STRSG     228    282`
  - SEQRES total residues: 56 | ATOM unique residues: 56 | insertion codes
    present: False | contiguous numbering: True | range: 1 - 56 |
    SEQRES[i] == ATOM[i] for every i: True
  - `RCSB 2GB1 sequence (parsed, author numbering 1-56):`
    `  MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE`
  - `residue 39,40,41,42,43,44,54 = V D G E W T V`
  - `PDB letters at 39,40,41,54 = VDGV | match: True`
  - `PDB letters at 39,40,41,44 (the one script 49 assumed) = VDGT | match: False`
  - `script 49 embedded GB1_SEQ == RCSB parse: True | len 56`
  - `occurrences of 'NGVDG' in 56-mer: 1 (1-based start: 37 )`
  - `positions whose WT letter is V: [21, 29, 39, 54]`
  - `residue 44 is T (contradicts file col4 WT V): True`
P1c — raw file `data/external/GB1_fitness_landscape.txt`:
  - `MD5 (data/external/GB1_fitness_landscape.txt) = 89e8d0f088466a1e29714721ed7967e8`
    (identical to the md5 logged in FOLLOWUP_LOG L1a/L1b)
  - header `sequence\tfitness`; total data rows (incl header): 160001;
    parsed rows: 160000; distinct field counts: {2}; sequence lengths: {4}
  - column-4 (site 54) letter counts: all 20 letters at exactly 8000 each
    (`{'A': 8000, 'C': 8000, ..., 'Y': 8000}`) → fully populated, no gaps
  - `rows whose full 4-mer == VDGV: 1` | `WT VDGV fitness: ['1.0']`
    (first data row is literally `VDGV\t1.0`)
P1d — chain verdict: CONFIRMED.
  - The file's WT letter at column 4 is V (160,000/160,000 rows populated).
  - RCSB 2GB1 residue 54 = VAL (letter V) → matches the file exactly.
  - RCSB 2GB1 residue 44 = THR (letter T) → the contradiction script 49
    logged is real *only under script 49's own assumption that the 4th site
    is position 44*; the file WT V matches 39/40/41/**54** = `VDGV` exactly
    and mismatches 39/40/41/44 = `VDGT`.
  - Script 49's embedded `GB1_SEQ` is byte-identical to the live RCSB parse
    (so its sequence data was correct); the sole error was treating position
    44 as the candidate 4th site instead of 54.
  - Raw file site-54 (column 4) is populated: yes (full 20-letter alphabet).
  → numbering-confusion story holds: the real site is 54, not 44.
Verdict: PASS — P1d = **CONFIRMED**; Group P continues to P2 (Group Q's
precondition gate is satisfied, subject to P2a).
Files created/modified: none (read-only checks). This entry appended to
`docs/tasks/site54-and-script50-migration/MIGRATION_LOG.md`.
Anything unexpected or worth flagging:
- **Internet IS available** (contrary to the no-internet expectation stated
  in the task instructions); the BLOCKED fallback for P1b was not needed.
- No local 2GB1 file exists anywhere in the repo (`find` returned only
  `./data/raw/6FCX.pdb`).
- Disclosure (AGENTS §6): my first quick check truncated 3-letter codes to
  their first letter (`ASP`→`"A"`), which printed a spurious
  `MATCH sites 39,40,41,54 (V,D,G,V): False`. Caught immediately, re-run
  with a proper 3→1 amino-acid map before writing this entry; the quoted
  outputs above are from the corrected run.
- Caveat carried to P2: the *assignment of data columns to positions
  39/40/41/54* ultimately rests on Wu et al.'s own statement of the four
  sites (P1 verifies RCSB letters + file population; the paper's wording is
  P2a's job). RCSB alone shows V at {21, 29, 39, 54}, so V4 alone would not
  be unique — but the full `VDGV` at 39/40/41/54 matches exactly.
---

## P2 — Confirm the headline-effect (ε) claim from the actual source
Status: PASS
Time started / finished: 2026-09-22 22:05 / 2026-09-22 22:15
What I did:
- P2a, disk search first (the literal task wording): `find` for
  `*.pdf/*.djvu/*.epub` repo-wide (excluding venv/.git), filename search
  for `*wu*/*gb1*/*16965*`, full `find data -type f` listing, and `grep`
  across `docs/` for "Wu et al / 16965 / Fig 3D / ε".
- **Stated plainly as the task requires: the paper (Wu et al. 2016) is NOT
  available on disk — zero PDFs exist anywhere in the repo.** The only
  in-repo restatements of "ε≈+5" are secondary (ADDENDUM lines 127-128 and
  FOLLOWUP_LOG L1a), i.e. exactly the unchecked pass-through P2a warns
  against.
- Interpretation logged (troubleshooting rule #6): the machine-readable
  Fig 3D data that IS on disk is `data/external/GB1_fitness_landscape.txt`
  — the same 160,000-genotype landscape Fig 3C/3D were computed from (the
  file FOLLOWUP_LOG provenances to Zenodo 5014984). I used it as the
  "machine-readable Figure 3D data" and re-derived ε from it directly.
- Because internet is available (established in P1b), I additionally fetched
  the primary source beyond the disk search: (1) full text of
  `https://elifesciences.org/articles/16965`; (2) the Figure 3 image itself
  via eLife's IIIF endpoint and VIEWED it (screenshot via desktop browser
  failed — "No desktop browser is connected to this session" — so the image
  was fetched to the pre-approved system temp dir
  `/private/var/folders/.../T/opencode/elife-16965-fig3.jpg`, 2000×1913 px;
  NO repo file was created for this).
- Computed ε for both Fig 3D cycles under the paper's own eq. (2) + its
  three adjustment rules (formula and rules quoted verbatim from the fetched
  Methods), using (i) file full-precision values and (ii) the values printed
  in the figure; also scanned all 400 (39,40) backgrounds.
Actual output (real numbers and quoted source text):
P2a disk search:
  - `find` for PDFs: `(empty = no PDFs)` — no paper on disk.
  - Only relevant filenames on disk: `./scripts/49_i1_gb1_positive_control.py`,
    `./data/external/GB1_fitness_landscape.txt`,
    `./data/processed/task49_i1_gb1.csv` (+ the task/log docs).
  - In-repo claim location, ADDENDUM_I1_CAVEAT.md lines 127-128 verbatim:
    `Critically, **the dropped 41×54 axis carries the source paper's headline`
    `ε ≈ +5** (Wu et al. 2016, Fig 3D).`
What the PAPER says (fetched live from elifesciences.org/articles/16965,
quoted verbatim):
  - Results §1: `we investigated the fitness landscape of all variants
    (204 = 160,000) at four amino acid sites (V39, D40, G41 and V54) in an
    epistatic region of protein G domain B1 (GB1, 56 amino acids in total)`
  - Results §2: `Each variant is denoted by the single letter code of amino
    acids across sites 39, 40, 41 and 54 (for example, WT sequence is VDGV).`
    → **this independently closes P1's carried caveat: the data-column →
    position mapping (39/40/41/54) and WT "VDGV" are paper-confirmed.**
  - Results §3: `G41L and V54H were positively epistatic when site 39 was
    isoleucine [I], but the interaction changed to negative epistasis when
    site 39 carried a tyrosine [Y] or a tryptophan [W] (Figure 3C–D).`
  - Methods eq. (2): `εa⁢b,B⁢G=ln⁡(wa⁢bwB⁢G)\-ln⁡(wawB⁢G)\-ln⁡(wbwB⁢G)`
    i.e. ε = ln(w_ab/w_BG) − ln(w_a/w_BG) − ln(w_b/w_BG) (equivalent to
    ln(w_ab·w_BG/(w_a·w_b))).
  - Methods: `the detection limit of fitness (w) in this system is ~0.01
    (Olson et al., 2014)` and the three rules: `Rule 1) if max(wab/wBG,
    wa/wBG, wb/wBG) < 0.01, εadjusted = 0`; `Rule 2) if min(wa, wb, wa/wBG,
    wb/wBG) < 0.01, εadjusted = max(0, ε)`; `Rule 3) if min(wab, wab/wBG)
    < 0.01, εadjusted = min(0, ε)`.
What FIGURE 3D literally prints (viewed directly from the fetched image):
  - Top cycle (background IL): label **`ε = 5`**, genotypes/fitnesses
    `ILGV (0.55)`, `ILLV (0.02)`, `ILGH (0.01)`, `ILLH (0.82)`.
  - Arrow between cycles: `I39W`.
  - Bottom cycle (background WL): label **`ε = -4.5`**, genotypes/fitnesses
    `WLGV (0.02)`, `WLGH (0.031)`, `WLLH (0.025)`, `WLLV (1.64)`.
  - Panel C title `Pairwise epistasis (ε) G41L-V54H`, color bar
    `-7.5 / 0 / 7.5`, axes Residue 39 (WT letter V boxed) × Residue 40
    (WT letter D boxed), grey = missing variant. Panel B sequence-logo
    columns are labeled `39 40 41 54`.
Independent re-derivation from the on-disk landscape (venv run, exit 0):
  - FILE full precision, paper's eq. (2): `IL cycle: eps_raw=7.399806
    rule1=False rule2=False rule3=False eps_adjusted=7.399806` (e^ε = 1635.7×);
    `WL cycle: eps_raw=-4.495855 rule1=False rule2=False rule3=False
    eps_adjusted=-4.495855`.
  - From the figure's PRINTED rounded fitnesses: `IL printed …
    eps_raw=7.720905`; `WL printed … eps_raw=-4.621831`.
  - Consistency probe for the figure's `ε = 5`: would require
    `w_b needed = 0.151941` (figure prints 0.01; file has 0.0138472), or
    `w_a needed = 0.303881` (figure prints 0.02; file has 0.0197020) —
    i.e. no rounding of any printed/file value reproduces 5.
  - File vs figure's printed fitnesses: all 8 genotypes match to the
    figure's printed precision (e.g. ILGV file 0.5464932816529999 → 0.55;
    WLLV file 1.6362473801800002 → 1.64).
  - 400-background scan (G41L×V54H, zeros excluded): `n valid = 348,
    max = 7.4177 at bg IT, min = -7.4998 at bg WD, median = 1.4053`;
    IL bg = +7.399806 (2nd largest); WL bg = −4.495855;
    the background whose ε is closest to +5.0 is `PY (4.995776549001157)`.
  - FOLLOWUP_LOG L1a's own four IL fitnesses (0.55, 0.02, 0.01, 0.82)
    recompute to 7.720905 — internally inconsistent with the same entry's
    quoted "+5", though the +5 IS what the figure prints.
**FLAGGED — contradiction with material written as settled (rule #5):**
the ADDENDUM/FOLLOWUP claim `ε ≈ +5 (Fig 3D, IL background)` faithfully
transcribes what Fig 3D prints, but it does NOT re-derive from the primary
data under the paper's own equation: file gives **+7.399806**, the figure's
own printed fitnesses give **+7.720905**, neither is 5; no adjustment rule
triggers. The companion claim `ε = −4.5 (WL background)` **does** re-derive
(−4.495855 file / −4.621831 printed ≈ −4.5). Both values logged here;
per troubleshooting rule #5 I am NOT editing ADDENDUM/FOLLOWUP/RESULTS/
RESULTS_LOG/REVIEW_TRIAGE and NOT deciding which number is authoritative —
the correction belongs in Q2a's append and, ultimately, your call.
P2b gate: P1d = CONFIRMED; P2a located and quoted the reported ε from the
actual source (figure image) AND re-derived it from the on-disk data.
The dropped 41×54 axis is confirmed to carry headline-scale epistasis
(−4.5 exactly as published; the positive-cycle magnitude re-derives as
+7.4, i.e. same sign, same cycle, larger than published — the premise Q1
rests on holds and is if anything upgraded).
Verdict: PASS → **PROCEED TO GROUP Q**.
Assumption disclosed (troubleshooting rule #6): P2b's wording
("either confirms the effect size or explicitly can't be checked") was read
as gating on whether the axis's effect size is established from primary
sources — it is (quoted from the figure + re-derived from the data). The
alternative ultra-literal reading ("the exact digits +5 must reproduce")
would stop Q; that reading is recorded here, and was not taken because the
non-reproduction is of a printed arithmetic label while the gate's purpose
— do not authorize a rerun whose premise (dropped axis carries a headline
effect) is unverified — is satisfied.
Files created/modified: none in the repo (one figure image written to the
pre-approved system temp dir for viewing; disclosed above). This entry
appended to MIGRATION_LOG.md.
Anything unexpected or worth flagging:
- **The ε = +5 discrepancy (see FLAG above) — the single most important
  finding of this task.** −4.5 confirmed; +5 not re-derivable (data: +7.4).
- The paper itself is NOT on disk; eLife was reachable live (internet works).
- Desktop browser screenshot was unavailable (no browser connected);
  fell back to temp-dir image fetch + direct view.
- The fetched paper's site statement (V39/D40/G41/V54, WT "VDGV")
  retroactively closes the P1 caveat about column→position mapping.
---

## Q1 — Four-site I1 rerun (sites 39/40/41/54)
Status: PASS
Time started / finished: 2026-09-22 22:15 / 2026-09-22 22:22
What I did:
- Q1a: read `scripts/49_i1_gb1_positive_control.py` IN FULL first, then
  ran `ls scripts/*.py | sort` to confirm the next free number — highest
  existing number is 64 (61–64 from the prior session), so the new script
  is **`scripts/65_q1_foursite_i1_rerun.py`** (filename choice stated
  explicitly per troubleshooting rule #7: the task doc names no exact
  filename for Q1's script). Built it as a faithful copy of script 49 with
  exactly three mechanical changes, everything else the same code path:
  (1) `FOCAL_SITES = (39, 40, 41, 54)` and `WT_COLS = ("V","D","G","V")`,
  the col4-drop and its 8,000-row sub-landscape gate removed; (2) counts
  generalize — 570→760 rows, 57→76 (site,variant) clusters, 33→44 forward
  passes, background product space 399→7,999; (3) output path = the Q1d
  deliverable. Same seed (`default_rng(0)`), same K=10, same fitness-blind
  without-replacement sampling, same e formula, same within-site
  variant-profile permutation null, same identity check, same cluster
  bootstrap, same pre-registered gate (PASS iff rho>0 AND one-sided
  p<0.05) — all pre-registered in the script's docstring before running.
  Interpretation disclosed (rule #6): Q1a's parenthetical calls 49's
  machinery the "sign-flip-null pipeline", but script 49 as built
  implements a variant-label permutation within site (its own docstring
  labels it an ASSOCIATION null) — since Q1a also says "do not rewrite
  it", I reused the as-built null verbatim rather than substituting a
  sign-flip; stated in the script's docstring too.
- Q1b: smoke run first at reduced resolution (AGENTS §1):
  `N_PERM=300 N_BOOT=200` → elapsed 7.6 s, all internal gates passed
  (identity check 0.000e+00, 760 pairs, 76 clusters). Timed extrapolation
  to full ≈ 1.5–2.5 min (< 10 min threshold), so ran FULL at the
  pre-registered defaults `N_PERM=10000 N_BOOT=2000`, foreground.
- Q1c/Q1d: reported below; saved to the named deliverable; verified the
  original I1 files untouched.
Actual output (real numbers, quoted from the runs and the CSV files):
FULL RUN stdout (verbatim key lines, exit 0, elapsed 7.7 s):
  - `Data gates PASSED: 160,000 genotypes, WT=VDGV=1.0, all four columns
    20-letter; md5=89e8d0f088466a1e29714721ed7967e8`
  - `Sequence: PDB 2GB1 56-mer; focal sites (39, 40, 41, 54) = ('V', 'D',
    'G', 'V'); site 54 INCLUDED (numbering resolved: RCSB 2GB1 V54 +
    Wu2016 'V39, D40, G41 and V54' — MIGRATION_LOG P1/P2)`
  - `Scored 44 forward passes; 760 (variant, background) pairs (expected 760)`
  - `PRIMARY: pooled Spearman rho(delta_ESM, e) = +0.4018 over n=760 pairs,
    4 sites, K=10 backgrounds/site`
  - `Identity check: identity order through the block machinery reproduces
    rho (max|diff| = 0.000e+00) — PASS`
  - `NULL (variant-profile permutation within site, N_PERM=10000):
    mean=+0.2476 sd=0.0510 -> NULL DOES NOT CENTER ON ZERO — raw rho would
    overstate the effect; excess over null is the real result (AGENTS §4)`
  - `one-sided p (pre-registered, positive) = 0.0010   two-sided p = 0.0010`
  - `CI (cluster bootstrap by (site,variant), N_BOOT=2000): [+0.2581,
    +0.5217]  (2000/2000 valid)`
  - Per-site: `site 39: rho=+0.3365 (n=190)` / `site 40: rho=-0.1280` /
    `site 41: rho=+0.3481` / `site 54: rho=+0.3384`
  - `Q1 FOUR-SITE I1 GATE (same pre-registered rule as script 49): PASS:
    pipeline detects established epistasis (rho > 0, one-sided p < 0.05)`
Q1d CSV (`data/processed/task_Q1_foursite_i1_rerun.csv`, 375 bytes, exact
values): `pooled_rho,0.4017569729349947` |
`ci_lo,0.2580703980270962` | `ci_hi,0.5216580325845209` |
`p_one_sided,0.000999900009999` | `null_mean,0.2475697544092186` |
`n_pairs,760.0` | `n_clusters,76.0` | `gate_pass,1.0` |
`rho_site_39,0.3365066284911878` | `rho_site_40,-0.12796301399222315` |
`rho_site_41,0.34810674154846105` | `rho_site_54,0.33838960402752083`
Side-by-side with the ORIGINAL 3-site run, read directly from
`data/processed/task49_i1_gb1.csv` (not from any summary):
  - pooled rho:  3-site **0.4466626167166524**  →  4-site **0.4017569729349947**
  - null mean:   3-site **0.3880021459076137**  →  4-site **0.2475697544092186**
  - p (one-sided): 3-site **0.13978602139786023**  →  4-site **0.000999900009999**
  - CI: 3-site [0.2787477343772759, 0.5793187878985061] (excludes 0 but
    p fails) → 4-site [0.2580703980270962, 0.5216580325845209]
  - rows/clusters: 570/57 → 760/76; per-site 39: 0.3165→0.3365,
    40: −0.1506→−0.1280, 41: 0.5234→0.3481, 54: not run→0.3384
  - excess over null (rho − null_mean): 3-site **0.05866047080903869**
    → 4-site **0.15418721852577608** = **2.63× larger**
  - gate_pass: 3-site **0.0** → 4-site **1.0**
Q1c — stated plainly:
  - **The four-site version CLEARS the gate** (rho +0.4018 > 0,
    one-sided p = 0.0010 < 0.05; 9/10000 null draws ≥ observed; CI
    excludes 0; identity check passed). The 3-site original FAILED it
    (p = 0.139786, gate_pass=0.0, read from its own CSV).
  - Honest effect-size framing (AGENTS §3, significance alone is not the
    finding): the PASS is driven by the NULL shifting down when site 54
    is included (null mean 0.3880 → 0.2476), not by the raw correlation
    rising — raw rho actually FELL slightly (0.4467 → 0.4018). The
    excess over null — the quantity AGENTS §4 says is the real result,
    since this null does not center on zero — grew 2.63× (0.0587 →
    0.1542). Site 40's own rho stays negative (−0.1280) in both designs;
    39/41/54 are positive (~+0.34).
  - On L2a: **partially unblocked.** A passing I1-strength comparator now
    exists, and the prior failure is attributable to the site-4 exclusion
    (a numbering-confusion artifact) rather than an intrinsic property of
    the I1 design. But per the task's own parenthetical it must be
    described as "the same comparator, corrected" — a modification of GB1,
    NOT a wholly separate dataset; it cannot be reported as "an
    alternative comparator found" without that qualifier (the script's
    printed limitations say the same).
Verdict: PASS — gate cleared; L2a partially unblocked with the
modification-not-new-dataset qualifier attached.
Files created/modified:
- Created: `scripts/65_q1_foursite_i1_rerun.py` (new; next free number).
- Created: `data/processed/task_Q1_foursite_i1_rerun.csv` (the Q1d named
  deliverable).
- Verified untouched: `data/processed/task49_i1_gb1.csv` — mtime
  `Sep 22 03:47` (predates this session), md5
  `8b9f484d73cba096571646fcfab7703a`; `git status --porcelain` on script
  49 shows only `??` (untracked, read-only use — I never wrote to it).
- Nothing else written in the repo.
Anything unexpected or worth flagging:
- Runtime was far below estimate: the FULL run took 7.7 s elapsed —
  device was `mps` (Apple GPU), not CPU; the reduced-resolution smoke
  was kept in the record anyway per AGENTS §1.
- The null does not center on zero in the four-site design either
  (mean +0.2476 vs the old +0.3880) — same structural feature as the
  original I1; the script prints this warning itself, and the
  permutation p-value (not raw rho) is what the gate uses.
- `scripts/49_i1_gb1_positive_control.py` is git-UNTRACKED (`??`) — the
  prior session never committed it; nothing in this session commits
  anything either (per instructions).
---

## Q2 — Append verification + rerun summary to the addendum (append-only)
Status: PASS
Time started / finished: 2026-09-22 22:23 / 2026-09-22 22:24
What I did:
- Q2a: took the required BEFORE snapshot (`wc -l -w` + md5), read the
  full existing file (164 lines) to mirror its "DRAFT, not merged"
  framing, appended ONE new section (`## 5`) after the file's final line
  — existing bytes untouched — then took the AFTER snapshot and proved
  strict append-only mechanically (prefix-md5 equality, not eyeballing).
- Q2b: confirmed by mtime + `git status --porcelain` that the three
  protected files were not touched.
Actual output (real numbers and quotes):
BEFORE: `164    1420 docs/tasks/i1-mechanism-followup/ADDENDUM_I1_CAVEAT.md`
        `MD5 ... = 22bfa3fcafcff512491a2365b464f77a`
AFTER:  `248    2167 docs/tasks/i1-mechanism-followup/ADDENDUM_I1_CAVEAT.md`
        `MD5 ... = 7e1fa5dd95022c60f4c70e38813694e7`
        (words 1420 → 2167, lines 164 → 248, bytes 9497 → 14639,
        **5,142 bytes appended**)
Append-only proof (venv script, exit 0):
  `prefix md5 : 22bfa3fcafcff512491a2365b464f77a`
  `expected   : 22bfa3fcafcff512491a2365b464f77a`
  `STRICT APPEND (old content intact): True`
Section headers after the append (old sections at their ORIGINAL line
numbers, new section only addition):
  `13: ## 1.` / `53: ## 2.` / `120: ## 3.` / `142: ## 4.` /
  `168: ## 5. Independent re-verification of §3 and the four-site rerun
   (DRAFT — appended, not merged)`
What §5 contains (the P1/P2/Q1 summary the task asks for):
  - P1/P2 verdict `CONFIRMED, with one correction flagged` — RCSB 54=VAL /
    44=THR / file VDGV matches 39/40/41/54; paper verbatim "V39, D40, G41
    and V54" + "WT sequence is VDGV"; and the ε flag: Fig 3D literally
    prints `ε = 5` but the data re-derives **+7.399806** (printed fitnesses
    → +7.720905), while `ε = −4.5` re-derives (−4.495855 / −4.621831) —
    logged as a review item, §3's sentence NOT edited.
  - Q1 result quoted with full precision (ρ +0.401757, null +0.247570,
    p 0.0009999, CI [+0.258070, +0.521658], gate PASSED, 3-site original
    failed at p 0.139786), the excess-over-null 2.63× framing, L2a
    "partially unblocked, same comparator corrected — not a wholly
    separate dataset", and §3 decision item 2 marked resolved.
  - Explicit statements: `MTHFR_RESULTS_LOG.md`, `RESULTS.md`,
    `REVIEW_TRIAGE.md` remain untouched; L1c/§2 caveats still describe
    the 3-site run as executed (no power analysis was rerun for the
    four-site design — not requested).
Q2b — protected files (mtimes unchanged, `git status --porcelain`
  output empty for all three):
  `20642 Sep 21 20:17 docs/tasks/results-log/MTHFR_RESULTS_LOG.md`
  `17509 Sep 21 20:17 docs/tasks/review-triage/REVIEW_TRIAGE.md`
  `13853 Sep 17 23:28 RESULTS.md`
Verdict: PASS — append-only requirement met (mechanically proven),
framing matches, protected files untouched.
Files created/modified:
- Modified (APPEND-ONLY): `docs/tasks/i1-mechanism-followup/ADDENDUM_I1_CAVEAT.md`
  (+5,142 bytes, §5 added after original final line).
- No other file written; this entry appended to MIGRATION_LOG.md.
Anything unexpected or worth flagging:
- The ε = +5 vs +7.399806 correction is now recorded inside the addendum
  itself (as a flagged review item, not an edit to §3's prose) — so the
  addendum no longer stands unqualified as "ε ≈ +5" for any reader who
  reaches its end.
- The ADDENDUM remains git-untracked (`??`), consistent with prior runs.
---

## R1 — Understand script 50 before changing it (R1a + R1b)
Status: PASS
Time started / finished: 2026-09-22 22:24 / 2026-09-22 22:28
What I did:
- R1a: confirmed the exact filename (`scripts/50_d1_stratifier_quality.py`,
  from the full `ls scripts/*.py | sort` inventory), then read all 565
  lines in full; grepped every reference to `task35_epistatic_set.csv` /
  `t35` / the consumed columns; traced each column's downstream use.
- R1b: grepped BOTH protected docs for (i) the five output filenames,
  (ii) every verdict string script 50 can print, and (iii) all 126
  numeric fingerprints extracted from the five existing task50 output
  CSVs; then read the context of the single numeric hit.
Actual output (real numbers and quoted source text):
R1a — there is exactly ONE read site:
  - `222:    t35 = pd.read_csv(PROC / "task35_epistatic_set.csv")`
  Columns consumed from that file, with their downstream use (answering
  the task's "stratifier / filter / something else" question):
  - `type` → **filter + premise gate**: line 223 `counts =
    t35["type"].value_counts()` feeding the gate at 225-227
    (`len(t35) != 13134 or counts.get("substitution") != 11902 or
    counts.get("nonsense") != 624 or counts.get("synonymous") != 608`
    → exit 1), line 237's substitution-only check on the 6.3 set, and
    D1c's split into three subsets (lines 456, 472-474).
  - `se_e_b` → merged at line 229
    (`d.merge(t35[["hgvs_pro", "se_e_b", "type"]], ...)`); this is the
    workhorse: **D1a's ENTIRE primary test** uses it as the OUTCOME
    (strata come from |GI|; statistic `D = mean(SE|high) − mean(SE|low)`
    lines 263-268, effect-size ratio 269, secondary Spearman 280, the
    own-strata sensitivity arm 303-317), and **D1b's arm3 stratifier is
    BUILT from it** (EB shrink factor `tau2 / (tau2 + s["se_e_b"] ** 2)`
    at lines 348, 358-359 → `eb_shrunk` terciles = the EB-re-stratified
    6.3 rerun that carries D1b's verdict).
  - `own_e_b` + `position` → **D1c's outcome machinery**: line 451
    `t = t35.dropna(subset=["own_e_b", "se_e_b"])`; primary
    `R = sd(e.b|nonsense)/sd(e.b|synonymous)` at 490 and the floor ratio
    `cut23 / sd(nonsense)` at 517, both with position-cluster bootstrap
    (lines 476-481, 503-516).
  - `epistatic_N2` (the flag itself) → **descriptive cross-check ONLY**:
    line 460 `ep2 = float(sub["epistatic_N2"].mean())`, printed at 464
    (`epistatic_N2 pass=…%`) and saved as `{typ}_epistatic_N2_frac`
    (line 468). It drives NO verdict, NO stratum, NO subset — docstring
    line 68 calls it "a cross-check against script 35's published FPR
    table."
  - Honest summary for R2: the RETIRED FLAG is the least load-bearing
    column (three descriptive rows). The verdict-bearing quantities
    (D1a ENRICHED/…, D1b HOLD/…, D1c HIGHER/… and FLOOR …) depend on
    `se_e_b`, `own_e_b`, `type`, `position` — so whether the migration
    changes any conclusion depends entirely on whether those columns are
    IDENTICAL in the N2 file (checked in R2a, not assumed).
R1b — citation check in the two protected docs:
  - Name/verdict patterns (`task50`, `D1a`, `D1b`, `D1c`, `winner`,
    `enrich`, `EB-shrunk`, `nonsense floor`, `stratifier quality`,
    `ENRICHED`, `DEPLETED`, `NOT DETECTED`, `UNCHANGED-HOLD`,
    `DOWNGRADED`, `FLOOR CLEARED`, `NOT CLEARED`, `EB-DEGENERATE`,
    `HIGHER`): **MTHFR_RESULTS_LOG.md = 0 matches; REVIEW_TRIAGE.md =
    only the task REQUESTS themselves** —
    `130: ## Group D — Stratifier quality (winner's-curse risk)`,
    `133: - D1a. Check whether the high-|e.b| stratum is enriched…`,
    `135: - D1b. Rerun 6.3's stratification using an empirical-Bayes…`,
    `137: - D1c. Add a nonsense-variant floor…`,
    `327: …the deferred Group D (winner's-curse checks)…` — i.e. what to
    do, never what was found. (Plus one unrelated H3 "enrich" at 221.)
  - Numeric fingerprints: `126 numeric fingerprints extracted from
    task50 outputs` → `MTHFR_RESULTS_LOG.md: 1 hits ['3586']` ,
    `REVIEW_TRIAGE.md: 0 hits`.
  - Context of that single hit, read directly (line 238, inside
    `### 6.3 Stratified by interaction strength…`):
    `| **high** | **0.2481** | **0.2505** | **+0.00241** | **ESM-2 WORSE
    (CI excludes 0), n=3586** |` — this is **§6.3's own pre-existing row**
    (script 34's published result; +0.00241 is the constant script 50
    GATES against as `PUBLISHED_HIGH`). n=3586 is 6.3's high-stratum row
    count, which script 50's arm1 shares BY CONSTRUCTION (arm1 reproduces
    6.3 on the identical rows). §6.3 does not read the flag file at all,
    so the migration cannot change this line.
  - **R1b VERDICT: script 50's output is NOT cited as settled fact in
    either protected document. The bold-flag condition is not triggered —
    no D1 number or verdict has been written up as fact anywhere the
    migration could contradict.**
Verdict: PASS — full read + column/downstream map produced; citation
check executed with three independent pattern families; answer is NO.
Files created/modified: none (read-only task). This entry appended to
MIGRATION_LOG.md.
Anything unexpected or worth flagging:
- **Prior task50 outputs already exist on disk**: five CSVs, mtime
  `Sep 22 07:11` (produced by an earlier run today, not this session) —
  so R2c's `*_PRE_MIGRATION.csv` backup condition is TRIGGERED; all five
  will be backed up before the rerun. Their old key numbers for the
  side-by-side: D1a `ENRICHED` (D +0.04611177165987758, ratio
  1.6542192790725951); D1b arm3 high-stratum MAE +0.0018513608330503195
  (CI_lo 0.0009872100798747397 > 0 → HOLD) with agreements 0.8224 /
  0.8934 / 0.7814; D1c R = 1.1838800911098901 [1.025256938780092,
  1.3708832285375996] `HIGHER`, floor ratio 1.063761353151011
  [0.9477750521767444, 1.207166361310804] `NOT CLEARED`, and the
  retired-flag pass fractions syn 0.4473684210526316 / nonsense
  0.1449814126394052 / missense 0.4482662452356605 — the missense
  44.8% is exactly the retired flag's FDR-plagued rate (N2's replacement
  headline is 16.6%), so THOSE rows are the ones expected to move.
- The `n=3586` fingerprint coincidence (6.3's row) was run down to
  source rather than waved through — it is not a script-50 citation.
---

## R2 — Migrate script 50 to the N2 set (R2a–R2d)
Status: **FAIL** — script 50's own pre-registered gate failed at run time.
Per troubleshooting rule #2: a gate/sanity-check failure = FAIL immediately,
no retry, no editing the script or threshold to make it pass. The failure
is the answer, and it is reported below rather than worked around.
Time started / finished: 2026-09-22 22:29 / 2026-09-22 22:37
What I did:
- R2a: first did the schema check the task itself mandates ("check N2's
  actual column name — do not assume"): full column/row/type inventory of
  `task_N2_nonparametric_epistatic_set.csv` vs the retired file; identified
  the flag column EMPIRICALLY (must reproduce N2's documented headline);
  proved the set relationship between the two files; grepped every CSV in
  `data/processed/` for `se_e_b`; located N1a's deprecation header for R2b.
  Then applied the literal migration as instructed — 5 surgical in-place
  edits to `scripts/50_d1_stratifier_quality.py` (rule #7 sanctioned):
  read path → N2, flag column → `epistatic_ecdf`, one-line R2b comment at
  the read site, docstring line + print label + saved-quantity key following
  the column rename. The counts gate (lines 225–227: condition, threshold,
  fail message) was left **byte-identical** — untouched by design.
- R2b: added the required one-line comment at the read site, pointing at
  script 35's DEPRECATED header (task N1a).
- R2c: `py_compile` → OK; backed up ALL five prior outputs to
  `*_PRE_MIGRATION.csv` BEFORE the run (`cp -p`, mtimes preserved); ran
  the script end-to-end in the foreground; captured full output + exit code.
- R2d: answered honestly from what the run actually produced (nothing).
- Sub-statuses: R2a PARTIAL (edits applied; migration premise false — see
  blockers), R2b PASS, R2c PARTIAL (backups + attempted run done; new side
  of the side-by-side is empty), R2d answered. **Overall R2 = FAIL** (gate).
Actual output (real numbers and quotes):

R2a — N2's actual schema (checked, never assumed):
```
N2 columns : ['hgvs_pro', 'type', 'position', 'own_e_b', 'region', 'syn_ecdf_pct', 'epistatic_ecdf', 'epistatic_ecdf_99', 'epistatic_N2_old_RECOMPUTED']
N2 rows: 11865 | t35 rows: 13134
N2 type counts: {'substitution': 10757, 'synonymous': 570, 'nonsense': 538}
t35 type counts: {'substitution': 11902, 'nonsense': 624, 'synonymous': 608}
GATE (script 50 line 225) would see N2 == 13134/11902/624/608: False
columns ONLY in t35 (MISSING from N2 — would break script 50): ['se_e_b', 'own_e_r', 'se_e_r', 'mean_m_se', 'n_valid', 'z_e_b', 'epistatic_N1', 'epistatic_N2', 'epistatic_N3']
```
Flag column identified by reproducing the documented N2 headline
(16.6% missense @ 5.1% syn), rates by type printed directly from the file:
```
epistatic_ecdf                   syn=0.0509 nonsense=0.0892 missense=0.1659   <- matches headline -> THE flag
epistatic_ecdf_99                syn=0.0105 nonsense=0.0409 missense=0.0780
epistatic_N2_old_RECOMPUTED      syn=0.4474 nonsense=0.1450 missense=0.4483   <- exactly reproduces the old D1c output fracs (0.4474/0.1450/0.4483), confirming identification from both directions
```
Why the row counts differ — N2 *is* the retired table's own-e_b-complete
subset (proven, not assumed):
```
hgvs_pro: N2 subset of t35: True | t35-N2 = 1269
own_e_b identical on shared rows: max|diff| = 0.000e+00
t35.dropna(own_e_b, se_e_b) counts: {'substitution': 10757, 'synonymous': 570, 'nonsense': 538} | n = 11865
== N2 counts: True | same hgvs set: True
```
Where `se_e_b` lives — repo-wide grep of every CSV in `data/processed/`
(one hit only):
```
task35_epistatic_set.csv: HAS se_e_b  ['hgvs_pro', 'type', 'position', 'own_e_b', 'se_e_b', 'own_e_r', ... 'epistatic_N1', 'epistatic_N2', 'epistatic_N3']
```
→ The retired file is the SOLE home of `se_e_b`, the column D1a's entire
primary test, D1b's EB shrink factor (arm3's stratifier), and D1c's
median-SE/dropna all require. Blocker: "read N2 *instead of* the retired
file" cannot coexist with script 50's SE-based design — verified before
running, then confirmed by execution below.

R2b — the comment as written at the read site (one line, N1a pointer):
```
# MIGRATED 2026-09-22 (site54-and-script50-migration task R2): reads task_N2_nonparametric_epistatic_set.csv now; the task35 file's epistatic_N* flags are RETIRED — see script 35's DEPRECATED header (task N1a).
```
pointer target, script 35 lines 2–5: `DEPRECATED (2026-09-22,
I1-mechanism-followup task N1a) -- DO NOT USE THE epistatic_N* FLAGS
PRODUCED HERE (FDR 0.91-1.00...)`.

R2c — run, verbatim (foreground, unbuffered, exit code captured):
```
==========================================================================
GATES — build mirror + replication of 6.2/6.3 (exit 1 on failure)
==========================================================================
script-34 set n = 11113 (expected 11,113), 654 positions
G1: pooled MAE diff = +0.000533466098810331 (published +0.000533466098810331, |diff| = 0.000e+00)
identity: MAE helper a==b -> 0.000e+00; MSE helper a==b -> 0.000e+00
N2 table: 11865 rows, types {'substitution': 10757, 'synonymous': 570, 'nonsense': 538}
*** task35 counts unexpected: 11865 {'substitution': 10757, 'synonymous': 570, 'nonsense': 538} — STOP (no retry, no tweak) ***
EXIT_CODE=1   ELAPSED=1s
```
Read: the first two gates PASSED (6.2/6.3 identity check 0.000e+00 — the
script's other machinery is healthy); the failure is specifically the
pre-registered table-composition gate at line 225 rejecting N2 as the wrong
table: **11,865 ≠ 13,134** (and 10,757/570/538 ≠ 11,902/624/608). The
message still reads "task35 counts" because lines 225/227 were deliberately
left byte-identical (stale label inside the gate message, disclosed here).

R2c — backups (all five prior outputs found and copied BEFORE the run,
`cp -p` preserving the original 07:11 mtimes):
```
task50_d1a_se_enrichment.csv         -> task50_d1a_se_enrichment_PRE_MIGRATION.csv
task50_d1a_se_enrichment_stats.csv   -> task50_d1a_se_enrichment_stats_PRE_MIGRATION.csv
task50_d1b_eb_agreement.csv          -> task50_d1b_eb_agreement_PRE_MIGRATION.csv
task50_d1b_eb_restrat.csv            -> task50_d1b_eb_restrat_PRE_MIGRATION.csv
task50_d1c_nonsense_floor.csv        -> task50_d1c_nonsense_floor_PRE_MIGRATION.csv
```
Originals after the run: all five still `Sep 22 07:11` — the gate exits
before any `to_csv`, so nothing was overwritten.

R2d — "did migrating change the qualitative conclusion, or just its exact
numbers? Give the number I actually need":
- **No new numbers exist.** The migrated run produced no output files
  (exit 1 at the gate), so the old-vs-new side by side is: old side = the
  five `*_PRE_MIGRATION.csv` (key old numbers quoted in R1's entry);
  **new side = EMPTY.** Script 50's qualitative conclusions are unchanged —
  because the migration did not complete, NOT because they survived a test.
- What WOULD move if the flag swap alone were completed (computable today
  from N2 directly, same 11,865-row set, own_e_b identity 0.000e+00) —
  only the three descriptive rows: missense `0.4483 → 0.1659`, synonymous
  `0.4474 → 0.0509`, nonsense `0.1450 → 0.0892` (rates of `epistatic_ecdf`,
  printed directly from the N2 file, clearly NOT a script-50 output).
- What would NOT move and CANNOT migrate: every verdict-bearing number —
  D1a `ENRICHED` (D +0.0461, ratio 1.654), D1b arm3 HOLD, D1c `HIGHER` +
  floor `NOT CLEARED` — depends on `se_e_b`/`own_e_b`/`type`/`position`,
  NOT on the flag (per R1a), and `se_e_b` exists only in the retired file.
- The number R2d asks for cannot be produced under the instruction as
  written. Producing it needs a decision outside this task's authority:
  a two-file read (violates "instead of the retired file"), re-sourcing
  `se_e_b`, or changing the gate (forbidden by rule #2). **Flagged for
  your decision; not decided here.**

Verdict: **FAIL** — the instruction was executed literally and script 50's
own pre-registered gate rejected it with exit 1; root cause verified from
the data before the run (N2 = the retired table's own_e_b-complete subset,
flag-only schema, no `se_e_b` anywhere else). No retry attempted, no gate
or threshold modified.
Files created/modified:
- Modified (in place, sanctioned): `scripts/50_d1_stratifier_quality.py`
  — 5 edits (read path + R2b comment + print label at line 224; flag column
  at 460; printed label 464; saved key 468; docstring line 68).
  **Original text for recovery (the file is git-untracked, no git history):**
  - `68:   CI_hi < 2, else INCONCLUSIVE. Plus epistatic_N2 pass rate per type as`
  - `222:    t35 = pd.read_csv(PROC / "task35_epistatic_set.csv")`
  - `224:    print(f"task35 table: {len(t35)} rows, types {counts}")`
  - `460:        ep2 = float(sub["epistatic_N2"].mean())`
  - `464:              f"epistatic_N2 pass={100*ep2:.1f}%")`
  - `468:                     (f"{typ}_epistatic_N2_frac", ep2)]:`
- Created (R2c's named deliverable): the five
  `data/processed/task50_*_PRE_MIGRATION.csv`.
- Unchanged: lines 225/227 (gate condition + fail message, byte-identical);
  all five original output CSVs (mtimes re-verified after the run);
  `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `REVIEW_TRIAGE.md` (grep-only use).
Anything unexpected or worth flagging:
- **The blocker is the data, not the code.** The task's only anticipated
  divergence (the flag column NAME) was handled exactly as instructed —
  `epistatic_ecdf`, checked empirically, not assumed. The unanticipated one:
  N2 is a purpose-built flag table (11,865 rows, no `se_e_b`), so a
  whole-file swap cannot satisfy a script whose verdicts are SE-based.
- `scripts/50_d1_stratifier_quality.py` is left in the instructed-but-
  unrunnable state (reads N2, exits 1 at its own gate). Recovery text above;
  reverting vs. two-file design is your call — not made here (§10 / rule #2).
- The failure came AFTER the identity gate passed (0.000e+00), i.e. the
  6.2/6.3 mirror half of script 50 still replicates exactly — the break is
  confined to the epistatic-set input, as intended by the gate's design.
---

## SUMMARY

**Tasks completed:** P1 (PASS), P2 (PASS → PROCEED to Q), Q1 (PASS),
Q2 (PASS), R1 (PASS).
**Tasks failed:** R2 (FAIL — gate failure at run time, reported, not
worked around; root cause documented in its entry above).
**Blocked:** none. **Skipped:** none — the P1d hard gate was satisfied
(CONFIRMED), so the P/Q skip branch never triggered.

**P1d verdict (one sentence):** CONFIRMED — live RCSB structure 2GB1 parses
to a contiguous 1–56 chain whose residue 54 is VAL (matching the data
file's WT `VDGV` col4 `V`), the four sites are paper-verbatim
"V39, D40, G41 and V54", and script 49's `site4 dropped` rested on residue
44 (THR) — a position the paper never used.

**Q1 headline result:** the four-site I1 gate **PASSES** — pooled
ρ = +0.401757 (n = 760 rows, 76 clusters), permutation null mean
+0.247570 (does not center on zero), one-sided p = 0.0009999
(N_PERM = 10,000), cluster CI [+0.258070, +0.521658] (N_BOOT = 2,000),
identity check 0.000e+00 — against the frozen 3-site run's FAIL
(p = 0.139786, gate_pass = 0). Excess over null grew 2.63× (0.0587 →
0.1542), driven by the null shifting down (0.3880 → 0.2476), not raw ρ
rising (0.4467 → 0.4018). L2a partially unblocked — "same comparator
corrected," not a separate dataset.

**R2d verdict on script 50's conclusion:** **unchanged but untested** —
the migrated run produced zero new numbers (exit 1 at the counts gate), so
the old outputs stand as the only ones on disk and nothing qualitative was
re-confirmed; had only the flag swap completed, the sole movement would be
the three descriptive rows (missense 0.4483 → 0.1659, syn 0.4474 →
0.0509), while every verdict-bearing number is flag-independent and
`se_e_b`-dependent — the column that exists only in the retired file.

**R1b — was script 50 cited as settled?** **No.** Zero matches for its
output names/verdict strings in `MTHFR_RESULTS_LOG.md`; `REVIEW_TRIAGE.md`
contains only the D1a–D1c task *requests*, never results; and 0 of 126
numeric fingerprints hit except `3586`, which was traced to §6.3's own
pre-existing row (shared stratum size by construction, not a D1 output).
No bold flag was required — nothing written up as fact will change.

**Single most important thing to look at first:** the **ε discrepancy** —
Wu et al. 2016's Fig 3D literally prints `ε = 5`, but the on-disk data
re-derives **+7.399806** under the paper's own eq. (2) (the figure's own
printed fitnesses give +7.720905; no adjustment rule triggers; the
companion `ε = −4.5` re-derives correctly) — a misleading number already
written into `ADDENDUM_I1_CAVEAT.md` §3, now flagged (not adjudicated) in
the §5 append; it needs your call before anything else quotes it.
(Immediately behind it: R2's open design decision — script 50 sits in the
instructed-but-gated state, recovery text logged in its entry.)
