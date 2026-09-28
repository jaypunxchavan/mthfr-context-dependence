# Dimer-interface proximity check — does the ThermoMPNN comparator hold away from the interface?

**Written:** 2026-09-28 (Claude, planning) · **Executor:** OpenCode
**Doc lives at:** `docs/tasks/dimer-interface-comparator-check/DIMER_INTERFACE_COMPARATOR_CHECK.md`
**Log to write:** `docs/tasks/dimer-interface-comparator-check/INTERFACE_LOG.md`
**Scripts:** next free numbers; Phase 2 session 2a used 123–125, so expect **126, 127** — verify with
`ls scripts/*.py | tail` first.

## 0. Why this session exists

Dr. Kuhlman's reply (email, 2026-09-28) said the frozen-WT-structure assumption (not re-folding for
A222V, a monomer-dissociating variant) would only matter for ThermoMPNN scoring **if the residues in
question are near the oligomer interface, or if there are larger conformational changes tied to the
oligomerization-state change.** His second condition isn't testable here — it's a literature question
about how large that change is. His first condition is: this session tests it directly, cheaply, on
cached structure only.

**This is a distinct axis from L3.** L3 (`PHASE1_LOG.md`) already split `interaction_D` by distance to
**residue 222** (≤8 Å "proximal"). This session splits by distance to the **chain A/chain B interface** —
a different reference point entirely. A residue can be far from 222 and still sit at the dimer interface,
or vice versa.

**No model scoring. CPU-only, structure and cached tables only.** This is independent of any Phase 2
overnight run: do not touch `data/processed/phase2/`, `run.log`, or `run.pid`, and do not import
torch/esm. If Phase 2 is running when this session starts, that's fine — this doesn't compete for the
GPU/MPS device.

---

## 1. Rules (from `AGENTS.md`; restated where they bite)

1. **No new model scoring** of any kind. This session touches only the dimer PDB structure and already-
   cached tables (`task77`/analysis table columns including `interaction_D`, `own_e_b`).
2. **Position-cluster bootstrap** for the comparator CIs (frame positions as clusters). `N_BOOT=300`
   smoke, then `N_BOOT=10000` full, `SEED=0`. Pre-registration (construction, cutoffs, decision rule)
   written in each script's docstring **before** its first run.
3. **A failed gate means STOP that task, log `FAIL`/`BLOCKED`.** Never loosen a threshold or re-run
   until it passes.
4. **Protected files — never edited:** `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `PROJECT_SUMMARY_FINAL.md`,
   `AGENTS.md`, `PHASE2_PREREG.md`, and every earlier log. Do not touch anything under
   `docs/tasks/phase2-full-frame-placebo/` or `data/processed/phase2/`.
5. **Do not commit, do not push.**
6. `venv/bin/python3` always. Missing package (e.g. `biopython` for PDB parsing):
   `venv/bin/python3 -m pip install <pkg> --break-system-packages`, log it; if it fails, `BLOCKED`.
7. Verbatim output in every entry; full run output saved to
   `docs/tasks/dimer-interface-comparator-check/INTERFACE_<TASK>_FULL_OUTPUT.txt`.
8. **Do not send any email.** Task I5 produces a draft file only.
9. If a premise here turns out wrong, say so plainly in the log rather than papering over it.

## S1. Logging instructions

Create `INTERFACE_LOG.md` first with the standard template; append one entry per task immediately
after it finishes:

```
## [TASK ID] — [title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
```

---

## Task I1 — Locate and quote script 107 verbatim (read-only)

`scripts/107_e2_dimer_distance_recompute.py` already computed the dimer-aware min-distance-to-residue-
222 figures quoted in the project state doc (96.22% monomer / 95.13% dimer-aware beyond 10 Å). Read it
in full and report, quoting line numbers:
- (a) the PDB/structure file it loads (exact path), and whether it's a crystal structure, an
  AlphaFold/AlphaFold-Multimer model, or something else;
- (b) the two chain identifiers used for the two copies (e.g. chain A / chain B);
- (c) the exact distance metric (CA–CA? any heavy atom? which atoms specifically?) and units;
- (d) the residue-number-to-structure-position mapping convention it uses (PDB numbering may not equal
  the 1–656 frame numbering — confirm how script 107 handles this, and quote the check if one exists);
- (e) the total residue range covered by the structure for each chain (structures are often incomplete
  at termini or loops — report any gaps).
Do not assume any of (a)–(e); read and quote. This determines everything downstream.

## Task I2 — Interface distance table (script 126)

Pre-register in the docstring before running. Reusing script 107's exact structure file, chain IDs, and
numbering convention (import script 107's loading code if importable; otherwise replicate line-for-line
and gate the replica): for every one of the 654 frame positions with a resolved chain-A structure
position, compute `d_interface` = the minimum distance from **any atom of that chain-A residue** to
**any atom of chain B** (heavy atoms only, no hydrogens — most PDB/model files won't have hydrogens
anyway; state which if biopython reports otherwise). Report:
- **Gate I2-G1:** re-derive script 107's own headline numbers (96.22% / 95.13% beyond 10 Å from residue
  222) from the same loaded structure, as a sanity check that the structure and parsing match. Round to
  2 dp and compare to the recorded values; if they don't match, STOP and report the discrepancy —
  do not proceed to I3 on a structure that doesn't reproduce the known result.
- **Gate I2-G2:** every frame position not resolved in the structure is logged explicitly (position
  number and count), not silently dropped.
- residue 222's own `d_interface` (informational only — 222 is not a target position in the frame and
  this changes nothing about its own treatment).
- write `data/processed/interface_distances.csv` with columns `position, chain_a_resolved (bool),
  d_interface_angstrom`.

## Task I3 — Classify interface-proximal positions (script 126, same run)

Two pre-registered cutoffs: **5 Å** (direct atomic contact, standard interface definition) and **8 Å**
(the same "proximal" cutoff L3 already used for distance-to-222, for consistency with house convention —
note explicitly that this is a *different reference point*, not a repeat of L3). For each cutoff, report
n and % of the 654-position frame classified as interface-proximal, and the position list. Any position
unresolved in the structure (I2-G2) is excluded from both the interface set and the non-interface set,
and reported separately as "structure-unresolved, not classified either way."

## Task I4 — Recompute the ThermoMPNN comparator, full vs non-interface (script 127)

**Reproduce first, decide never on a threshold change.** Locate the exact script/column that produced
L3's headline number (`Spearman(interaction_D, own_e_b)` = 0.015350499380143039, rounds to +0.0154) —
quote the file and line. Pre-register in the docstring before running:
- **Gate I4-G1:** recompute Spearman(interaction_D, own_e_b) on the full frame; must reproduce
  0.015350499380143039 to 1e-9. If it doesn't, STOP — the comparator table isn't being read correctly;
  do not proceed.
- Recompute the same statistic on **(a)** the non-interface subset at the 5 Å cutoff and **(b)** the
  non-interface subset at the 8 Å cutoff (from I3), each with a position-cluster bootstrap 95% CI
  (10,000 draws, `SEED=0`, clusters = the positions in that subset).
- Report all three (full, non-interface@5Å, non-interface@8Å) side by side with their CIs, n, and the
  % of the frame each subset retains.
- **Decision rule (pre-registered, purely descriptive — nothing here changes any earlier result):**
  `CONSISTENT` if the full-frame point estimate falls inside both subset CIs; `DIFFERS` if it falls
  outside either. Either outcome is reported factually; `DIFFERS` does not retroactively invalidate L3
  or the anchor, and `CONSISTENT` does not prove the frozen-structure assumption is safe for Kuhlman's
  second condition (the conformational-change question), which this session cannot test.
- Also report, purely descriptively: whether A222V's own position (222) is itself interface-proximal at
  either cutoff (informational; 222 is excluded from the frame as a target position regardless).

## Task I5 — Draft-only reply to Dr. Kuhlman (no send)

Write a plain-text draft to `docs/tasks/dimer-interface-comparator-check/KUHLMAN_REPLY_DRAFT.txt`:
short, thanks him for the two conditions, reports the concrete numbers from I3/I4 (% interface-proximal
at 5 Å and 8 Å, and whether the comparator was CONSISTENT or DIFFERS), and does **not** claim to have
resolved his second condition (conformational-change magnitude) — name that as still open. **Do not send
this. It is a draft for Arnav to review and send by hand.**

## S2. Mandated SUMMARY contents

`## SUMMARY` in this order: (1) **READ THIS FIRST** — I4's three-way comparison (full / non-interface@5Å
/ non-interface@8Å) with CIs and the CONSISTENT/DIFFERS verdict at each cutoff; (2) I1's structure
provenance (file, chains, metric, numbering check); (3) I2-G1's reproduction of script 107's known
96.22%/95.13% figures; (4) I3's counts and %; (5) whether 222 itself is interface-proximal; (6) every
gate, PASS/FAIL, value; (7) confirmation nothing under `phase2-full-frame-placebo/` or
`data/processed/phase2/` was touched; (8) confirmation no email was sent; (9) the single most important
entry to read first, with its line number.

---

## What this session is NOT

- Not a change to any Phase 1/1b/2 result, gate, or the frozen `PHASE2_PREREG.md`.
- Not a resolution of Dr. Kuhlman's second condition (conformational-change magnitude) — that's a
  literature question, not something this structure-only check can answer.
- Not permission to send email on Arnav's behalf.
