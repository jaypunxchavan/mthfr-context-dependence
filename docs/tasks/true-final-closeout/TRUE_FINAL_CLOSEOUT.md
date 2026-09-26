# True Final Closeout

This closes the project's remaining open items. All major analytical
questions are already resolved as of `DISATTENUATION_LOG.md`'s SUMMARY —
do not re-open, re-run, or re-litigate T1, T5, V1, or any of that
session's other conclusions. This session does five small, mostly
mechanical things.

---

## Task G1 — Surface Z3 and Z4 into plain view (do this first)

- G1a. Read `DISATTENUATION_LOG.md`'s `[Z]` entry (Z1–Z4) in full and
  quote Z3's actual ClinVar result and Z4's actual drafted email content
  verbatim in this session's log. These were marked "Completed" in the
  prior SUMMARY but never surfaced in a way that made it into any later
  document — fix that now, purely by quoting, no new computation needed
  unless the entry shows the task never actually produced a real number
  (in which case say so plainly rather than inventing one).

## Task G2 — Close the one remaining numerical gap

- G2a. Run the exact same precision/hardware grid used for the original
  ESM-2 delta check (dtype, batch size, device — reuse that script's
  exact machinery, do not rewrite it) on the five ESM-1v checkpoints'
  delta scores. Report whether they reproduce to the same tolerance the
  original check used. This closes the one item flagged as "unverified
  by analogy" in the final write-up.

## Task G3 — Reconcile the two still-unaddressed dropped findings, in writing

- G3a. Write one clear paragraph, checked against the actual numbers
  from both sides, reconciling the H1a-reversal finding (A222V produces
  a larger representational shift than its own severity predicts,
  verified at a 31-background design) against this project's later
  reliability findings. State plainly: does the demonstrated
  cross-seed instability of the background-sensitivity signal mean this
  specific finding should now carry a single-checkpoint caveat, does it
  survive untouched, or is there a real tension that can't be resolved
  without a new test? Do not manufacture false certainty either way.
- G3b. Write the equivalent paragraph for the additive-null MAE finding
  (ESM-2 performing reliably worse than a no-interaction baseline in the
  highest-interaction stratum). Same standard: state the real
  relationship to the reliability findings, don't paper over any
  remaining tension.
- G3c. Fix the two internal-to-this-session errors already identified
  and disclosed in `DISATTENUATION_LOG.md`'s own SUMMARY (the K12
  mislabeled CI and the K21 mislabeled statistic) — these are inside a
  file this session created, not a protected file, so correct them
  directly rather than just flagging them again.

## Task G4 — Commit the final write-up permanently

- G4a. The file `PROJECT_SUMMARY_FINAL.md` will be placed at
  `docs/writeups/PROJECT_SUMMARY_FINAL.md` before this session starts
  (see terminal commands). Confirm it exists, confirm it is what gets
  referenced as "the project's final write-up" in any future session,
  and commit it if it is not already committed.
- G4b. This permanently resolves the earlier "v3 does not exist in the
  workspace" block from the prior session — confirm this explicitly in
  the log so no future session wastes time searching for a phantom file
  again.

## Task G5 — Update RESULTS.md's current-state section (the actual front door)

- G5a. You are authorized to hand-edit RESULTS.md's existing "Current
  State" section (the one added in the prior closeout session) — replace
  its content, do not touch anything below it. Update it to reflect this
  round's corrections: T5's 10.5× reliability gap as the lead figure,
  the disattenuation chain's status as a labeled counterfactual (not a
  finding), the resolved detection floor (cite AA4's empirical value,
  never n=10,757 or the naive position-count formula), and a one-line
  pointer to `docs/writeups/PROJECT_SUMMARY_FINAL.md` for the full
  account. Keep it to a similar length as what's there now — a pointer
  and a summary, not a full restatement.
- G5b. State explicitly in your log entry that this is the second and
  final authorized hand-edit to RESULTS.md under the same authority as
  the first one — flag the standing AGENTS §7 conflict once more, do not
  resolve it by editing that rule.

---

## What NOT to do

Do not re-run T1, T5, V1, Y1, Y2, W1, W2, X1, X2, U1, or any other
already-completed analysis from the prior session. Do not attempt to
generate a new ClinVar number if G1a's quote shows Z3 genuinely never
produced one — report that plainly as still open rather than filling the
gap yourself. Do not touch `MTHFR_RESULTS_LOG.md`, `RESULTS.md`'s
pre-existing content below the current-state section, `AGENTS.md`, or
any file this project has treated as do-not-touch throughout its
history, beyond the one explicitly authorized edit in G5.

---

## Suggested order

G1 first (cheap, and resolves what I don't currently know). G2 next
(independent, mechanical). G3 and G4 in either order. G5 last, since it
should reflect everything else in this session, including whatever G1
surfaces.
