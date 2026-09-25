# CLOSEOUT_LOG — U3 Diagnosis, V5 Matched-N, Full U2 Run, U4 Execution

Working log for `CLOSEOUT_U2_U3_U4_V5.md`. One `## [TASK ID]` entry per
task, appended immediately after that task's real execution, in the
exact format required by the session instructions. Final `## SUMMARY`
appended after the last task.

Binding rules: `AGENTS.md` at the repo root, read in full at session
start. Deliverable files limited to what the task doc's subtasks name
or clearly imply, plus this log.

---
 
## [Z0] — Read U3's actual block reason; classify; resolve only if mechanical
Status: **PARTIAL** — Z0a and Z0b executed in full; Z0c executed its
mechanical re-check (size re-verified) and then STOPPED at Z0c's own
stop clause: no mechanical unblock exists, and the only paths forward
are two judgment calls (below). U3 remains BLOCKED; ESM-1v was **not**
fetched and **not** scored.
Time started / finished: 2026-09-23 16:07:38 / 2026-09-23 16:11:41
What I did: (Z0a) Ran the mandated heading-format check FIRST —
`grep -n "^##" docs/tasks/comparators-and-consolidation/SESSION_LOG.md`
— before any extraction (per this session's explicit warning that
heading formats differed between sessions). Format confirmed as
bracketed `## [ID]`; U3 = lines 2067–2107, bounded by `## [U4]` at
2108. Extracted and quoted the full entry below (Z0a's requirement).
(Z0b) Classified the block against U4's two reference outcomes, then
applied this session's stricter key-discipline test. (Z0c) Performed
the mechanical checks the discipline prescribes *before* trusting a cap
block — a fresh HEAD on the real weights URL and a re-read of the
installed `esm` loader — then stopped; **no fetch, no install, no
scoring, no file written under `data/` or `scripts/`**.

Z0a — U3's full entry, quoted verbatim from SESSION_LOG.md lines
2067–2107:
```
## [U3] — ESM-1v, budget-gated (U3a)
Status: **BLOCKED — model size exceeds the 3 GB budget; subtask stopped before any download, per the task's own rule.**
Time started / finished: 2026-09-23 03:47:17 / 2026-09-23 03:48:02
What I did: U3a says to check ESM-1v's model size BEFORE attempting
anything, mark BLOCKED with the size found if a download would exceed
3 GB, and not attempt a partial download. I first resolved the real
loader names from the installed `esm` package (the canonical entry
point is `esm.pretrained.esm1v_t33_650M_UR90S()`, which loads
`esm1v_t33_650M_UR90S_1` — one of a 5-model ensemble; URL template
`https://dl.fbaipublicfiles.com/fair-esm/models/{name}.pt`,
pretrained.py line 53). My first guess at the URL
(`esm1v_t33_650M_UR50D.pt`) returned HTTP 403 (name does not exist —
logged as an unexpected correction below), so I re-HEADed the true
URLs. Only HEAD requests were sent; no bytes were downloaded.
Actual output (verbatim, `curl -sI`):
```
--- weights ---
HTTP/2 200
content-length: 7828635339
--- contact regression ---
HTTP/2 403
```
Size verdict (both readings of "3 GB", conservative first):
- 7,828,635,339 B = 7.829 GB (decimal) vs 3×10^9 B cap → EXCEEDS.
- = 7.292 GiB (binary) vs 3×2^30 = 3,221,225,472 B cap → EXCEEDS.
Either way **> 3 GB ⇒ BLOCKED**. (The regression file HEADed 403 — the
loader's own guard skips contact regression for esm1v, pretrained.py
line 21 — irrelevant to the verdict since weights alone already fail
the gate.)
Verdict: **U3a = BLOCKED (7,828,635,339-byte model > 3 GB); U3's
scoring/correlation body NOT attempted, no partial download made.**
Files created/modified: SESSION_LOG.md (this entry only). No file
written under `~/.cache/torch`, `data/`, or `scripts/`.
Anything unexpected or worth flagging: the wrong-name 403 (corrected
before any fetch); the ensemble structure (ESM-1v = 5 models — even
had the single file fit, "ESM-1v" would have needed an ensemble-choice
decision to be well-defined); model file is 3× larger than the
architecturally identical ESM-2 650M (2,604,537,549 B cached), which
is itself notable but not investigated (out of scope).
---
```

Z0b — classification. Two layers, both stated because they do not
point to the same answer on their own:
- **The block reason as recorded** is a budget cap — 7,828,635,339 B
  against the original task's explicit 3 GB rule, arithmetic only, no
  choice embedded in the diagnosis itself. The task doc literally
  lists "a budget cap" as its example of category (b) *mechanical*.
  On its face: **(b) mechanical**.
- **But this session's key discipline is not satisfied by the face
  classification**: it requires stopping if the block "turns out to
  involve ANY choice with more than one defensible answer and no
  existing precedent in this repo (the same shape U4 turned out to
  have)." Resolution of this block involves **two** such choices:
  1. **The cap waiver.** The only way to unblock is to fetch a 7.83 GB
     model over the original task's own "mark BLOCKED if >3 GB, do not
     attempt a partial download" rule (U3a). The closeout doc's Z0c
     parenthetical says "…then run ESM-1v's scoring + correlation
     exactly as U3's original task specified (fetch, …)" — but its own
     source note says U3's block reason "is unknown here" when that was
     written, so it cannot be read as *informed* authorization to waive
     the cap. Two defensible readings of two planning docs, in direct
     conflict; no precedent anywhere in this project for exceeding a
     budget cap (U3, U4, V1, T all stopped at their gates). Treating
     the waiver as mechanical would be exactly the failure mode the
     discipline names.
  2. **The ensemble choice** (independent, and of literally U4's
     shape): "ESM-1v" is a 5-model ensemble; the original task never
     specified which member or how to combine them, and this project
     has only ever scored with single models (ESM-2 650M/150M). U3's
     own entry flagged this: *"even had the single file fit,
     'ESM-1v' would have needed an ensemble-choice decision to be
     well-defined."* Confirmed below in Z0c from the installed package.
- **Decision: STOP. Z0c's resolution/scoring branch not executed.**
  (The stop lands either way: at Z0b under the key discipline, or
  inside Z0c under its own second clause — "if resolving it would
  itself require a judgment call not contemplated in the original
  task, stop there too — do not chain past one unblock into inventing
  a second one." Recorded as PARTIAL rather than PASS because the
  resolve-and-score half of Z0c did not happen.)

Z0c — the mechanical checks that *were* performed (read-only), then
stop. Fresh HEAD against the real URL, this session, 16:11:40:
```
=== fresh HEAD on the real ESM-1v weights URL (metadata only, no bytes) ===
HTTP/2 200 
content-length: 7828635339
```
Identical to U3's recorded number: **7,828,635,339 B = 7.829 GB /
7.292 GiB — genuinely over 3 GB under both readings**, so the
discipline's "check actual sizes before assuming a cap is exceeded"
step *confirms* the cap rather than dissolving it. Ensemble structure,
from the installed package (`venv/.../site-packages/esm/pretrained.py`):
```
285:def esm1v_t33_650M_UR90S():
291:    return load_model_and_alphabet_hub("esm1v_t33_650M_UR90S_1")
294:def esm1v_t33_650M_UR90S_1():  ...   (and _2, _3, _4, _5 at 303/312/321/330)
21:    return not ("esm1v" in model_name or "esm_if" in model_name)
```
Five loaders `_1`…`_5`; the generic entry point silently loads **only
member 1** — so even the choice "use the default (n=1) vs average the
paper's 5-member ensemble (5× fetch ≈ 39 GB, 5× scoring)" is live and
undocumented in this repo. No mechanical resolution exists; stop here.
Verdict: **Z0 = PARTIAL (diagnosis complete, correctly quoted and
classified); U3 remains BLOCKED with a sharpened reason: not merely
"over budget", but "over budget AND ensemble-undefined — two judgment
calls, neither settled anywhere in this repo." Resolution not
attempted; ESM-1v not fetched or scored; Z0c's scoring body (script
10/11-style scoring, script 32-style correlation, script-33 sign-flip
null — by this repo's established prior-session resolution of those
references, `32_delta_esm_primary.py` / `33_delta_esm_signflip_null.py`,
NOT the ignored strays) left for a session that has user input.**
Files created/modified: `CLOSEOUT_LOG.md` (this entry only). No other
file created or modified; no bytes downloaded (HEAD only).
Anything unexpected or worth flagging: the conflict between Z0c's
"fetch" parenthetical and U3a's explicit cap rule is flagged, not
resolved (this session may not edit either planning doc); the generic
`esm1v_t33_650M_UR90S()` loading member 1 *only* is a silent-default
trap worth knowing for whoever resolves this; the size re-verification
matched U3's number to the byte (no drift, no contradiction between
sources).
---

## [Z1] — V5 matched-n cleanup: head-to-head on a strictly identical row set
Status: PASS
Time started / finished: 2026-09-23 16:23:02 / 2026-09-23 16:29:22
What I did: (Z1a) Extracted [V5]'s original entry verbatim first
(SESSION_LOG.md line 2430) to fix the baseline numbers, plus
`_summarize`'s return keys, before computing anything. Built both
analysis sets: ESM-2 = `task32_analysis_table.csv` rows with
`delta_esm` & `own_e_b` non-null; ThermoMPNN =
`task_V2_thermompnn_ddg.csv` rows with `pred_eb` & `own_e_b` non-null;
intersected on `hgvs_pro`. **Logged assumption (task-doc file-name
slip, per session rule 6):** Z1a names
`task32_delta_esm_primary.csv`'s "own-e.b rows", but that file is a
16-row *summary* (columns `stage,quantity,value,ci_lo,ci_hi,p,n`)
with no `hgvs_pro` column — it cannot supply a variant-level
intersection. The variant-level table is script 32's own dump
`task32_analysis_table.csv` (script 32 line 168, same analysis set);
used it, and *verified the substitution is exact* rather than assumed:
its own-e.b rows reproduce n=10,757 and rho to −4.163e-17 (below).
(Z1b) Identity gates first (AGENTS §4/§5: cross-file column identity
checked before trusting any comparison), then position-cluster
bootstrap via the project's own
`scripts/lib/stats.py:position_cluster_bootstrap`, `N_BOOT=10000`,
`seed=0` (matching script 32/68's `SEED = 0`), smoke at N_BOOT=300
first (AGENTS §1). (Z1c) Mechanical side-by-side vs the original.
(Z1d) Saved the named CSV. **No script file created** — the only
named deliverable is the CSV; computation ran inline (heredoc),
outputs quoted below in full.
Actual output (verbatim, full run at N_BOOT=10000):
```
[set] ESM  n=10757 pos=654 (script 32 summary n=10757)
[set] Thermo n=9595 pos=586 (V5 n=9595)
[Z1a] intersection n=9595 pos=586  (ESM loses 1162, Thermo loses 0)
[gate] position mismatches across files : 0
[gate] max |own_e_b diff across files|  : 0.0
[gate] max |delta_esm diff on 9595 common rows| : 0.0
[gate] all identity checks passed
--- Z1b: N_BOOT=10000 seed=0 ---
MATCHED  ESM-2 delta_ESM  : rho=-0.0771 CI=[-0.1081,-0.0457] p=0 n=9595 pos=586 (n_boot=10000, seed=0, 11.8s)
MATCHED  ThermoMPNN pred_eb: rho=-0.0733 CI=[-0.1021,-0.0437] p=0 n=9595 pos=586 (n_boot=10000, seed=0, 12.1s)
ORIG-n   ESM-2 delta_ESM  : rho=-0.0881 CI=[-0.1173,-0.0595] p=0 n=10757 pos=654 (n_boot=10000, seed=0, 13.6s)
ORIG-n   ThermoMPNN pred_eb: rho=-0.0733 CI=[-0.1021,-0.0437] p=0 n=9595 pos=586 (n_boot=10000, seed=0, 12.3s)
[verify] ESM original vs task32 summary row: d_rho=-4.163e-17 d_ci_lo=+0.000e+00 d_ci_hi=-7.633e-17
[verify] Thermo original vs [V5] logged rho=-0.0733 CI=[-0.1021,-0.0437]: rho AGREES at 4dp, CI AGREES at 4dp (recomputed CI=[-0.1021,-0.0437])
Z1c -- SIDE-BY-SIDE (original unmatched vs strictly matched)
  original n : ESM 10757 vs Thermo 9595  (rho -0.0881 vs -0.0733, |ESM| larger: True)
  matched  n : both 9595  (rho -0.0771 vs -0.0733, |ESM| larger: True)
  matched CI overlap: True | both exclude 0: ESM True, Thermo True
  rho shift from matching: ESM +0.0110, Thermo +0.0000
  |ESM|-|Thermo| gap: original +0.0148 -> matched +0.0038 (26% of original gap remains)
[Z1d] saved data/processed/task_Z1_matched_n_headtohead.csv (4 rows)
```
(`p=0` from the bootstrap helper means p < 1/n_boot, i.e. **p < 1e-4**
for all four — helper's own docstring: "p_boot == 0.0 means no
resample crossed zero".) Saved CSV, verbatim:
```
predictor,analysis_set,n_rows,n_positions,rho,ci_lo,ci_hi,p_boot,n_boot,seed
ESM-2 delta_esm,matched_intersection,9595,586,-0.07714525927574277,-0.10809218873681738,-0.045705555794129264,0.0,10000,0
ThermoMPNN pred_eb,matched_intersection,9595,586,-0.07329934766090093,-0.10211176806696763,-0.04374642098952218,0.0,10000,0
ESM-2 delta_esm,original_unmatched,10757,654,-0.08811806424891734,-0.1173334458953319,-0.05951138449511738,0.0,10000,0
ThermoMPNN pred_eb,original_unmatched,9595,586,-0.07329934766090093,-0.10211176806696763,-0.04374642098952218,0.0,10000,0
```
Verdict: **Z1 = PASS.** Z1a: intersection **n = 9,595 (586
positions)** — and the mismatch had a precise direction: ThermoMPNN's
set is a **strict subset** of ESM-2's (Thermo loses **0** rows;
ESM-2 loses **1,162**), so V5's "9,595 ⊂ 10,757 roughly" is now
verified *exact*. Z1c, plainly: **"ESM-2 nominally larger" still holds
on identical rows (−0.0771 vs −0.0733), but it was PARTLY an artifact
of coverage**: the |rho| gap shrinks from 0.0148 to 0.0038 — **74% of
the original gap disappears** when ESM-2 is restricted to Thermo's
rows, and since the subset relation is one-directional, the artifact
runs exactly the way the hedge suspected (ESM's extra 1,162 rows
carried the larger magnitude). Thermo's numbers are bit-identical
before/after *by set identity* (same 9,595 rows, same seed — its
"shift" of +0.0000 is structural, not evidence of insensitivity).
Both CIs still exclude 0 and still overlap ([−0.1081,−0.0457] vs
[−0.1021,−0.0437]) — V5's qualitative conclusion survives on matched n
with the hedge now removed; the residual point-estimate ordering is
0.0038, far inside the overlap, so no "larger" claim beyond *nominal*
is supported. Effect sizes stated alongside p<1e-4 per AGENTS §3;
statistic/seed/convention were all fixed by the task before running —
nothing chosen after seeing results (AGENTS §0).
Files created/modified: `data/processed/task_Z1_matched_n_headtohead.csv`
(created, 4 rows); `CLOSEOUT_LOG.md` (this entry). No script created;
no other file touched.
Anything unexpected or worth flagging: (1) the task doc's file-name slip
(summary vs variant-level table) — resolved and gate-verified as
documented above, not silently; (2) the exact one-directional subset
structure (0 Thermo rows lost) — makes Z1c's artifact-direction reading
unambiguous; (3) matched-ESM CI shifted slightly narrower on top and
wider on bottom vs original ([−0.1173,−0.0595]→[−0.1081,−0.0457]) —
point estimate moved toward zero and n dropped ~11%, both as expected.
---

## [Z3a] — Install foldseek
Status: PASS
Time started / finished: 2026-09-23 16:39:38 / 2026-09-23 16:56:26
What I did: Checked installation paths BEFORE attempting anything, per
the task: environment probe first (`uname -m` = arm64;
`foldseek`/`conda`/`mamba` not found; `/opt/homebrew/bin/brew` present
as a fallback), then the GitHub releases API for
`steineggerlab/foldseek` (the task's explicitly named alternative to
conda-forge, which is unavailable here — no conda). Latest release =
tag `10-941cd33` (published 2025-01-19); the mac asset is
`foldseek-osx-universal.tar.gz` (universal x86_64+arm64, so correct
for this arm64 Mac). Checksum check per the task's exact wording
("verify a checksum **if one is published**"): the API asset object
has `digest=None` AND the release body contains no sha/md5/checksum
line — **none is published**, so I recorded the local sha256 for
provenance instead and used two independent integrity signals (exact
byte-size match against the API's published `size`, and the binary's
own version string cross-checked against the release tag).
Downloaded to `data/external/foldseek/` — **stated location choice**
(rule 7): the task names the install but not a path; `data/external/`
is this repo's established home for outside-project code (ThermoMPNN,
GB1 precedent) and is gitignored like the rest of `data/`.
Actual output (verbatim):
```
=== foldseek latest release ===
tag: 10-941cd33
published: 2025-01-19T13:29:44Z
asset: foldseek-osx-universal.tar.gz  size=17021264  digest=None  url=https://github.com/steineggerlab/foldseek/releases/download/10-941cd33/foldseek-osx-universal.tar.gz
=== release body: checksum mention? ===
checksum lines: NONE (no checksum published in release body)
=== download ===
-rw-r--r--  1 arnavchavan  staff  17021264 Sep 23 16:56 foldseek-osx-universal.tar.gz
=== local sha256 (recorded for provenance; no published reference) ===
6d8b07e188d443044f0c98db30aa3d4cca6750e97b50679372b54b45a664cae5  data/external/foldseek/foldseek-osx-universal.tar.gz
=== extract + verify ===
data/external/foldseek/foldseek/bin/foldseek
941cd33ff0771cd2e3f144e3293e22a2b87e9fda
```
Downloaded size 17,021,264 B == API-published size exactly;
`foldseek version` prints its build commit
`941cd33ff0771cd2e3f144e3293e22a2b87e9fda`, whose short form
`941cd33` is exactly the release tag `10-941cd33` — binary and release
agree.
Verdict: **Z3a = PASS. Method: precompiled official GitHub-release
binary (task's sanctioned path; conda-forge unavailable — no conda in
env); version 10-941cd33 (build commit 941cd33ff07..., published
2025-01-19); no checksum was published by upstream (both channels
checked), local sha256 recorded above; binary runs and self-reports
the matching commit.** Fallback path (Homebrew formula) existed but
was not needed.
Files created/modified: `data/external/foldseek/foldseek-osx-universal.tar.gz`
+ extracted tree under `data/external/foldseek/foldseek/` (binary at
`data/external/foldseek/foldseek/bin/foldseek`, chmod +x);
`CLOSEOUT_LOG.md` (this entry). Nothing else touched; `data/` is
gitignored per AGENTS §2.
Anything unexpected or worth flagging: upstream publishes NO checksum
in either channel the task named (so "verify a checksum" reduced to
size-match + self-reported-commit cross-check + local sha256 —
disclosed rather than silently skipped); `foldseek version` prints a
bare commit hash rather than a semver (cross-checked above);
the tarball is universal-binary so the same asset would also run on
x86_64 Macs — irrelevant here but noted for provenance.
---

## [Z3b] — Fetch SaProt weights
Status: PASS
Time started / finished: 2026-09-23 16:56:40 / 2026-09-23 17:01:38
What I did: Resolved the exact source from U4a's own entry (it named
the HF repo `westlake-repl/SaProt_650M_PDB` — I re-read that entry in
full this session rather than guessing the URL). HEAD-checked
`https://huggingface.co/westlake-repl/SaProt_650M_PDB/resolve/main/SaProt_650M_PDB.pt`
against U4a's recorded 2,606,464,143 B FIRST, downloaded only on an
exact match (the command contains an explicit size gate that prints
STOP instead of downloading on mismatch). Fetched **only**
`SaProt_650M_PDB.pt` — the redundant `pytorch_model.bin` was NOT
fetched, per the task. **Stated location choice** (rule 7): the task
names the file but not a path; `data/external/SaProt/` matches the
repo's external-asset convention (ThermoMPNN, foldseek) and is
gitignored. After download: exact byte-size check, then local sha256
against HF's published LFS `x-linked-etag` (which IS the file's
sha256) — a genuine checksum verification, unlike Z3a's case.
Actual output (verbatim, trimmed of curl progress-meter noise):
```
=== HEAD check against U4a's recorded 2,606,464,143 B ===
HTTP/2 302
content-length: 1008
x-repo-commit: 6f7468fdd0cdffe7e780bd4f57fa291df6b01867
x-linked-etag: "2f82f3d5aa1df7bb9eee67bf5f5816269a35caff42e520ab593bc05369732346"
HTTP/2 200
etag: "16865d330308fb4665e9728ce2caab16dc7275d992de478cb29832ebb0a50d61"
content-length: 2606464143
parsed content-length: 2606464143
SIZE MATCHES U4a's recorded figure -> downloading
-rw-r--r--  1 arnavchavan  staff  2606464143 Sep 23 17:00 SaProt_650M_PDB.pt
actual size: 2606464143
=== local sha256 of the weights ===
2f82f3d5aa1df7bb9eee67bf5f5816269a35caff42e520ab593bc05369732346  data/external/SaProt/SaProt_650M_PDB.pt
=== dir contents (confirm no .bin) ===
-rw-r--r--  1 arnavchavan  staff  2606464143 Sep 23 17:00 SaProt_650M_PDB.pt
```
Verdict: **Z3b = PASS. Weights fetched at
`data/external/SaProt/SaProt_650M_PDB.pt`; byte size 2,606,464,143 B
== U4a's figure and == HEAD's content-length (both readings within
the 3 GB cap: 2.606 GB / 2.427 GiB); local sha256
`2f82f3d5…732346` matches HF's published LFS etag EXACTLY —
checksum verified; the redundant `.bin` (2,606,517,773 B) was not
downloaded.** Download took 2m52s at ~14.4 MB/s (100% clean, no
retry).
Files created/modified: `data/external/SaProt/SaProt_650M_PDB.pt`
(created); `CLOSEOUT_LOG.md` (this entry). No script, no other file;
the `.bin` absent by design.
Anything unexpected or worth flagging: HF served a 302 → CDN redirect
(the first `content-length: 1008` line is the redirect body — the
real length is on the final 200; parsed with `tail -1` accordingly);
CDN `etag` differs from the LFS sha256 etag (CDN-side hash of the
served object — the authoritative content hash is `x-linked-etag`,
which is what I verified against); `x-repo-commit`
`6f7468fd…` recorded for provenance (HF repos are mutable — pinning
the commit matters if a re-fetch ever differs).
---

## [Z3c] — Generate 3Di tokens for chain A of 6FCX (gate: 596 exact)
Status: PASS (with a first-attempt gate FAIL, diagnosed byte-level
before proceeding — full disclosure below; thresholds never changed)
Time started / finished: 2026-09-23 17:03:06 / 2026-09-23 17:05:48
What I did: (1) Established prerequisites before touching foldseek:
`6FCX.pdb` has 0 MODEL records (single-model X-ray — no ensemble
choice); HETATM content is only CIT/FAD/SAH/HOH (no MSE, so every
polymer residue is an ATOM record); V2's chain-A usage lives in
scripts 18/55/68 (read-only precedent check). (2) Extracted chain A
to `data/processed/task_Z3c_6fcx_chainA.pdb` (ATOM + chain-A TER only;
ligands/waters excluded — mechanical reading of "ONLY chain A"; stated
as a choice since the task doesn't spell out HETATM handling) and
enumerated its residues independently in the same pass (resnum, icode,
3-letter→1-letter). Cross-checked against U4a's recorded figures.
(3) `foldseek createdb` on that file (scratch DB in the session tmp
dir — no scratch files in the repo), dumped the AA DB (`6fcxA`) and
the 3Di DB (`6fcxA_ss`). (4) Ran the task's gate: 3Di token count must
equal chain A's 596 resolved residues EXACTLY, plus my own extra
gates (AA-identity between foldseek's output and my enumeration — the
V2-style offset-mapping discipline — and a 20-state alphabet check).
Actual output, first run (verbatim — **gate FAILED**):
```
chain-A polymer residues: 596  range 40..651  breaks [(160, 172), (391, 397)]
icodes present: none
unknown resnames: none
...
Ignore 0 out of the 1.
Too short: 0, incorrect: 0, not proteins: 0.
=== GATE: counts + AA identity + token alphabet ===
len(foldseek AA)=597  len(expected AA)=596  len(3Di)=597
AA identity vs own enumeration: False
3Di alphabet:  ACDEFGHIKLMNPQRSTVWY  (21 distinct states)
GATE (3Di token count == 596 AND AA == own enumeration): FAIL
head: data/processed/task_Z3c_6fcx_chainA_3di.csv: No such file or directory
```
Stopped at the FAIL (Z3c's own words: "stop and diagnose before
proceeding") and inspected raw bytes rather than touching any
threshold:
```
6fcxA: 598 bytes total; last 6 bytes = b'LYFQ\n\x00'; NULs = 1
6fcxA_ss: 598 bytes total; last 6 bytes = b'PVRD\n\x00'; NULs = 1
```
Diagnosis: both files are exactly `596 letters + \n + \x00` — the
mmseqs/foldseek **record terminator** (a trailing NUL byte). My
text-mode reader kept the NUL in the string; Python's `sorted(set(...))`
placed it first and the terminal rendered it as the phantom "space" of
the 21-state alphabet. The extra 597th "residue" was the terminator,
in both files, identically. This is a **parser artifact, not a token
mismatch** — proven at byte level, with the threshold (596) untouched.
Actual output, corrected re-run (verbatim — terminator stripped via
`b[:-2]` after asserting the terminator is exactly `b"\n\x00"`; gate
criteria unchanged):
```
len(foldseek AA)=596  len(expected)=596  len(3Di)=596
AA identity vs own enumeration: True
3Di alphabet (20 states): ACDEFGHIKLMNPQRSTVWY
resnums: 596 entries, span 40..651
GATE (3Di token count == chain A's 596 resolved residues, AA-identity to own enumeration, 20-state alphabet): PASS
saved data/processed/task_Z3c_6fcx_chainA_3di.csv (596 rows)
```
CSV head/tail:
```
res_num,aa,di3
40,E,D
41,R,D
42,H,L
...
650,F,R
651,Q,D
```
Verdict: **Z3c = PASS. Chain-A-only 3Di tokens generated by foldseek
10-941cd33: 596 tokens for 596 resolved residues (range 40..651,
breaks at 161-171 and 392-396 absent by construction), AA sequence
identical to my independent enumeration, alphabet = the standard
20 3Di states.** My enumeration also reproduced U4a's three recorded
facts exactly (596 / 40..651 / breaks [(160,172),(391,397)]) — two
independent derivations agree before any token was generated.
Files created/modified: `data/processed/task_Z3c_6fcx_chainA.pdb`
(chain-A subset — implied intermediate), 
`data/processed/task_Z3c_6fcx_chainA_3di.csv` (deliverable, 596 rows
+ header), `CLOSEOUT_LOG.md` (this entry). foldseek DB files went to
the session tmp dir (scratch, not repo).
Anything unexpected or worth flagging: (1) the initial 597-vs-596
gate FAIL and its byte-level resolution — recorded verbatim above so
the "it failed once" fact is never lost (had the diagnosis shown a
real extra residue instead of a terminator, this task would have been
FAIL per the stop rule); (2) foldseek wrote no `>` header on a
single-record DB (dumps are bare sequences — affects any future
parser); (3) AA and 3Di share the same visual alphabet style — they
are kept in separate named columns throughout to prevent channel
confusion downstream; (4) FAD/CIT/SAH/HOH excluded from the token
file (not polymer residues — SaProt's paired vocab is AA+3Di only).
---

## [Z3d] — Score using SaProt's own inference path, not a hand-rolled one
Status: PASS
Time started / finished: 2026-09-23 17:06:00 / 2026-09-23 19:04:16
What I did: Located their bundled scoring/inference path BEFORE writing
any logic: README §"Predict mutational effect" (their documented
example: `SaprotFoldseekMutationModel.predict_mut` /
`predict_pos_mut` / `predict_pos_prob` — all three bodies read
verbatim) + their zero-shot eval entry point
`scripts/mutation_zeroshot.py`. **Path decision, disclosed (rule 6):**
their HF-class direction requires (a) `pytorch_model.bin` — the exact
redundant `.bin` Z3b forbade fetching — and (b) the `transformers`
package (absent from the venv); their README explicitly documents the
alternative route ("User could also load SaProt by esm repository...
We provide a function to load the model") = their own
`utils/esm_loader.load_esm_saprot`, which consumes only the `.pt` we
already have. Chose the esm route: it is their bundled loader (not a
reimplementation), needs no forbidden fetch, needs no new pip install.
What I adapted = ONLY a batch loop + the two-background convention;
the scoring arithmetic is transcribed from their `predict_pos_mut`
line-for-line: mask site = `"#"` + site's struc letter (the structure
channel stays VISIBLE at the masked site), read row `pos` (BOS shift:
residue i sits at model row i), score = log(Σ 21-block mut-aa probs /
Σ 21-block ori-aa probs) — AA marginalized over all 21 struc states,
exactly their slice `[st : st+len(foldseek_struc_vocab)]`. Also ran
their own `get_struc_seq` on the ORIGINAL `6FCX.pdb`: it reproduces
my Z3c tokens bit-identically (free independent re-derivation of Z3c).
Smoke-tested the adapted path on CPU — GPU deliberately untouched:
Z2a is mid-phase-3 on MPS and any GPU load now would corrupt its
timing measurement; Z3f's full scoring is scheduled after Z2a ends.
Actual output (verbatim):
```
chains returned: ['A']
len(seq)=596 len(struc)=596 len(combined)=1192
AA identity vs Z3c:  True
3Di identity vs Z3c: True
GATE (their get_struc_seq == my Z3c tokens): PASS
combined[0:6]: EdRdHl | combined[-6:]: YvFrQd
--- load smoke ---
model type: ESM2
alphabet len: 446 | prepend_bos: True | append_eos: True
get_idx('Ed') = 76 | get_idx('E') bare = 3 | unk = 3
n_params: 651572307
encode('EdRdHl...') len = 596 matches per-pair idx: True
encode(spaced) len = 596 matches per-pair idx: True
--- gates + single masked forward (CPU, WT bg, fused pos 1 = residue 40) ---
GATE1 block-order (idx(aa+struc[0])+k == idx(aa+struc[k]) for all 21x21): PASS
GATE2 mask tokens (#+struc) all in vocab: PASS
input tensor shape: (1, 598) (expect (1, 598) = 596+2)
logits shape: (1, 598, 446) | probs row sums to 1: True
pos40 ori=E: self-logodds (ori vs ori) = 0.0 (expect exactly 0.0)
all 20 logodds finite: PASS
sample: [('A', 0.7832), ('C', -1.7233), ('D', -1.0669), ('E', 0.0), ('F', 0.6588)]
Z3d adapted-path smoke: PASS
```
Verdict: **Z3d = PASS. Reuse path confirmed = SaProt's own
`load_esm_saprot` loader + their `predict_pos_mut` arithmetic
(transcribed, not reinvented; only batching + the WT/A222V
two-background framing added — precisely the "adapt only as much as
necessary" the task names). Their published semantics, now on the
record: masked pair token keeping the site's 3Di letter, log-ratio of
21-state AA-block marginal sums, BOS-shifted row index — all three
confirmed against a live forward (self-logodds exactly 0.0, probs sum
to 1, 446-class head = 441 pairs + 5 specials = 21×21+5).**
Files created/modified: `CLOSEOUT_LOG.md` (this entry) only — no new
script yet (Z3e creates it with the pre-registered docstring);
`data/external/SaProt/code/` (their repo clone) was created during
this task as the prerequisite for "use their own path" (same
precedent as ThermoMPNN's clone); all scratch stayed in the session
tmp dir.
Anything unexpected or worth flagging: (1) their HF-class direction is
blocked by Z3b's no-`.bin` rule + missing `transformers` — the esm
route avoids both, disclosed as a choice, not presented as the only
option; (2) `transformers`/`easydict`/`lmdb`/`peft` absent from the
venv but NOT needed on the chosen route (rule 1 deliberately not
triggered — no pip install taken); (3) bare `'E'` resolves to `unk`
(=3): bare AAs are not tokens in the paired vocab, so the 21-state
block sum is the ONLY correct readout — which is exactly what their
code does, confirming transcription fidelity; (4) benign load warning
`contact_head.regression.* not initialized` (contact head unused for
scoring); (5) their `get_struc_seq` uses foldseek
`structureto3didescriptor` while my Z3c used `createdb`+`_ss` dump —
two different foldseek subcommands agreeing token-for-token is a
stronger check than either alone.
---

## [Z3e] — Pre-register the frozen-structure convention in the new script's docstring, before running
Status: PASS
Time started / finished: 2026-09-23 19:58:00 / 2026-09-23 20:34:39
What I did: Verified the next free script number with `ls scripts/*.py |
sort` (highest numbered = 69_w_decile_background_rescore.py -> next free
= 70; check_match_rate.py is unnumbered and left alone). Wrote
`scripts/70_saprot_delta_epistasis.py` whose docstring states — before
any run, per the task's exact wording — the FROZEN-STRUCTURE
CONVENTION: both backgrounds (WT and A222V) reuse the SAME chain-A 3Di
tokens from 6FCX; only the amino-acid channel changes, at residue 222
only (A->V); no re-folding, no 3Di token differs; explicitly labeled an
ASSUMPTION, not a measured fact, with the caveat that nothing in the
script tests it. The same docstring pre-registers every other
convention before first contact: score = SaProt's own predict_pos_mut
arithmetic (Z3d's verified reuse path), delta_SaProt = S(av) - S(wt)
(script 12/32 construction), chain-A-only with the 59 unresolved
positions excluded never imputed, analysis set = script 32's 10,757-row
set, bootstrap N_BOOT=10000 seed=0, sign-flip through script 33's code
path with its +/-1 identity checks, four-region check as script 32d,
gates G1-G7 with fail->sys.exit(1), and the env-var contract
(N_BOOT/N_PERM/STAGE/SMOKE/BATCH). Before the first run I also made
four purely mechanical pre-registration edits (all before any data was
seen: G3 batch-tolerance set to 1e-3 for fp32/MPS — CPU smoke lands
2e-5; removed a dead helper; fixed a pandas index-alignment bug in the
wt_aa check; restricted the stats stage to scored positions under
SMOKE). Then ran the mandated CPU smoke
(SMOKE=1 STAGE=all N_BOOT=300 N_PERM=300). Run 1 FAILED at G1 and
crashed later; both are logged verbatim below with their diagnoses.
Run 1's G1 failure = a case bug in MY gate comparison (their get_struc_seq
struc channel is UPPERCASE, my fused pairs store 3Di lowercased per their
combined_seq convention): diagnosed byte-level before touching anything —
their dump compared case-sensitively against the raw Z3c CSV column was
identical (AA exact == True; 3Di exact == True) — so the pipeline
disagreement the gate appeared to show did not exist. Fixed by folding
case in the comparison only; the criterion stayed exact token-for-token
equality, threshold untouched (same precedent as Z3c's NUL-terminator
reader fix). Run 1 also raised KeyError 'pub_e_b' (alias column never
created — crash bug) and printed a 1,046-vs-0 DIVERGENCE; both fixed
after run 1 as disclosed bug fixes that change no threshold, no metric,
no subset: created the pub_e_b alias, and identified which base
reproduces V2's 1,046 by measuring (phase5 = exactly 1,046). Run 2 =
clean end-to-end pass.
Actual output (verbatim, run 2; run 1's failure lines are quoted above
and also appear in the Unexpected section):
```
script 70 | STAGE=all SMOKE=True N_BOOT=300 N_PERM=300 SEED=0 BATCH=16
device=cpu
[score] chain-A fused length 596 residues 40..651
[G1] their get_struc_seq == Z3c tokens: True
[G2] AA blocks consecutive from aa+struc[0]: True
[bg] A222V swaps fused token Ah -> Vh at index 171; all other 595 tokens identical (frozen structure)
[G3] batched vs single forward, max|diff| = 2.00e-05 (limit 1e-3): True
[G4] self-logodds at fused pos 1 (residue 40, E) = 0.0: True
[score] wt background done (5s elapsed)
[score] av background done (10s elapsed)
[score] saved .../data/processed/task_Z3f_saprot_scores_smoke.csv (80 rows = 4 positions x 20 alts; smoke-limited=True)
[score] stage wall-clock 33s on device=cpu
[G5] variants at position 222 in analysis set: 0 (expect 0): True
[G7] unresolved atlas positions: 59 == 59 and == 2-39/161-171/392-396/652-656: True
[G7] phase5 base (n=11344) rows at those positions: 1046 (V2's own figure: 1,046) -> MATCH
[G7] task_V2 rows present at those positions: 0 (expect 0: V2 dropped them at construction -- structure-based scoring cannot cover unresolved residues)
[SMOKE] stats restricted to the 4 scored positions [40, 41, 42, 43] (smoke scores only the first 4 residues)
[Z3f] analysis set 10757 -> excluded at 59 unresolved positions: 1017 rows; scored set 74 (4 positions)
[Z3f] reconciliation vs V2's 1,046: that figure = phase5 rows at the same 59 positions (measured here: 1046); ours (1017) = the subset of those inside script 32's pre-registered 10,757-row set after delta_esm/own_e_b filtering (29 of the 1,046 are not in it); task_V2 itself holds 0 unresolved rows -- dropped at its construction. Same 59 positions, three bases, all consistent.
[Z3f] scored set vs ThermoMPNN's coverage: ours 9740 vs task_V2 10141 rows (9595 with own_e_b) -- bases differ by design (script 32 = ESM-2+e.b filters; V2 = ddG+structure filters), so an exact match is NOT expected and is not asserted.
[Z3f] wt_aa agrees with chain-A ori_aa on all scored rows: True (74/74)
[Z3g] join miss (mut_aa not among scored alts at that residue): 0
==========================================================================
Z3g  PRIMARY -- delta_SaProt vs e.b  (N_BOOT=300, seed=0)
==========================================================================
  signed, own e_b: rho=-0.1102 CI=[-0.5055,+0.4726] p=0.6000 n=74 pos=4
  signed, published e.b: rho=-0.1167 CI=[-0.4931,+0.4364] p=0.5533 n=74 pos=4
  absolute, own e_b: rho=+0.1913 CI=[+0.0662,+0.5135] p=<0.0033 n=74 pos=4
  absolute, published e.b: rho=+0.1589 CI=[-0.0021,+0.4678] p=0.0733 n=74 pos=4
  [anchor] script 32's single-position delta_ESM signed own e_b = -0.0881 (n=10,757); our n = 74 after unresolved exclusions
==========================================================================
SANITY CHECKS (script 33's +/-1 identity checks -- test the test)
==========================================================================
  [G6] all-+1 flips reproduce own_e_b exactly: max|diff|=9.714e-17
  [G6] all--1 flips give exactly -own_e_b:     max|diff|=9.714e-17
==========================================================================
NULL 1 -- SIGN-FLIP RE-DERIVATION (300 permutations; script 33's path)
==========================================================================
  signed delta_SaProt vs signed e_b
    observed=-0.1102  null mean=+0.0126 sd=0.1293  p=0.4067
    excess over null=-0.1228  (-11% of the raw value is structural artifact)
    -> does NOT survive
    null-centring check: null mean IS consistent with zero -- machinery behaving
  absolute |delta_SaProt| vs |e_b|
    observed=+0.1913  null mean=+0.0133 sd=0.0914  p=0.0300
    excess over null=+0.1780  (7% of the raw value is structural artifact)
    -> SURVIVES
==========================================================================
NULL 2 -- POSITION-BLOCK PERMUTATION (300; weaker; association only)
==========================================================================
  observed=-0.1102  null mean=+0.0367 sd=0.1871  p=0.6033
  This asks whether the pairing beats chance, NOT whether the
  interaction exceeds measurement noise. Null 1 is the real test.
==========================================================================
Z3h  REGION CHECK (script 32d convention)
==========================================================================
  pooled rho=-0.1102 CI=[-0.5055,+0.4726] n=74
    region 1 SKIPPED (4 positions)
    region 2 SKIPPED (0 positions)
    region 3 SKIPPED (0 positions)
    region 4 SKIPPED (0 positions)
[saved] task_Z3g_saprot_delta_smoke.csv + task_Z3g_saprot_summary_smoke.csv (rows: primary=4, nulls, regions)
P-values apply to own_e_b (primary). Transfer to the published e.b only
as far as the two agree (script 17 prints that correlation).
LIMITATIONS (printed here per AGENTS s6): frozen-structure assumption
(Z3e docstring) is untested by this script; chain-A-only tokens exclude
the 59 unresolved positions (never imputed); reproduction of script 33's
path is a unit test of consistency, not independent evidence.
[stats] stage wall-clock 1s
[total] 34s
exit=0
```
Verdict: **Z3e = PASS.** The frozen-structure convention is on the
record in the new script's docstring before any run (the proof line in
the run itself: "A222V swaps fused token Ah -> Vh at index 171; all
other 595 tokens identical"), every pre-registered gate passes, the
reused script-33 sanity checks are at machine precision
(9.714e-17, well under the 1e-6 bar), the 1,046 accounting reconciles
by direct measurement (phase5 = 1,046 MATCH), and the full pipeline
score->delta->nulls->regions executes end-to-end with exit=0. IMPORTANT
READING NOTE: the rho/p numbers above come from the SMOKE subset only
(n=74, 4 positions) and are machinery checks — they are NOT findings and
must never be quoted as results; the real numbers come from the full
9,740-row run (Z3f, scheduled after Z2a so no GPU work corrupts its
timing measurement).
Files created/modified: `scripts/70_saprot_delta_epistasis.py` (the
task-mandated new script, next free number, named here explicitly);
smoke outputs `data/processed/task_Z3f_saprot_scores_smoke.csv`,
`task_Z3g_saprot_delta_smoke.csv`, `task_Z3g_saprot_summary_smoke.csv`
(machinery-check artifacts, kept for the record); `CLOSEOUT_LOG.md`
(this entry). No protected file touched.
Anything unexpected or worth flagging: (1) run 1's G1 FALSE failure —
verbatim: "[G1] their get_struc_seq == Z3c tokens: False / G1 FAILED --
token pipelines disagree. Stop." — diagnosed as a case bug in the gate
comparison itself (their struc channel uppercase vs my lowercased
fused pairs), confirmed by case-sensitive identity against the raw Z3c
column (AA exact == True, 3Di exact == True); criterion unchanged,
construction fixed, disclosed per the Z3c precedent — NOT a modified
test; (2) run 1's KeyError 'pub_e_b' crash (alias column bug, fixed);
(3) the initial "V2 rows at those positions: 0 ... DIVERGENCE" printed
by run 1's G7 — resolved by measuring every candidate base: phase5
(11,344) = exactly 1,046 = V2's published figure, own_context_metrics =
1,079, script-32 set = 1,017, task_V2 = 0 — three different bases, all
consistent, now printed by the script itself as the reconciliation
line; (4) benign RuntimeWarnings "Mean of empty slice" from
own_context.py:84 / stats_ext.py:76 under the 4-position smoke (empty
concentration bins at tiny n; appears in stderr so it interleaves into
the transcript mid-run — stdout is pipe-buffered); (5) run 1 exposed
that pipes masked python's exit code (grep returned 0) — run 2 used
`set -o pipefail`, whose exit=0 is the one quoted; (6) region check
correctly SKIPPED all four regions in smoke (4 positions < the
pre-registered 15-position gate) — no gate was loosened to make
regions print.
---

## [Z2a] — Measure BRUTE_N=16's real per-unit cost before committing to the full run
Status: PASS (executed as a BACKGROUND run by the prior session — disclosed
per rules; completed on notification without polling; phase-3 timing
measured from its own markers and both of Z2a's mandated comparison
numbers reported below; the task doc's "(2,620 rows)" label diagnosed as
a mislabel of 2,620 forward passes — contradiction logged both ways)
Time started / finished: 2026-09-23 16:39:38 (background launch, prior
session, shell sh_0cffed22c001zK90EUzUNolL35) / 2026-09-24 00:09:32
(job completed, exit 0); measurement + this entry 2026-09-24 00:31:29
What I did: (Background run, disclosed: `PHASE2_MAX=75 BRUTE_N=16
N_BOOT=10 N_PERM=10 BATCH=16 venv/bin/python3 scripts/67_u2_pll_delta.py`,
launched 16:39:38 by the prior session with a `date` wrapper; I did NOT
poll — handled when the completion notification arrived, deepdive kept
priority meanwhile, entry written now.) Executed the carry-forward's
"restore z2_backup/ smoke CSVs" first: the job had overwritten the
canonical `task67_u2_*_smoke.csv`, so I preserved the job's own outputs
before restoring — outputs copied to
`z2_backup/z2a_run_outputs/task67_u2_pll_scores_smoke.csv` (6,935 B, 74
lines, md5 a6e440ccc8516fd987e2a97f57ba7031) and
`.../task67_u2_results_smoke.csv` (1,021 B, md5
edbb3c828491bd5281102ba34bd8a5cb); originals copied back to
`data/processed/` (27,770 B / 298 lines, md5 73b8c6dd3a1063b4c928d15b2a31b70a;
results 1,249 B, md5 8033907764c6770f78a513851e923a66 — matches the
PHASE2_MAX=300 original smoke whose command is recorded at SESSION_LOG
L1993: `N_BOOT=300 N_PERM=300 BRUTE_N=2 PHASE2_MAX=300 BATCH=16`, total
runtime 2831 s at L2022). Measured phase-3 from the job's own markers:
phase-2-done t=1598 → phase-3-done t=26991 ⇒ **25,393 s = 423.2 min =
7.05 h** for 16 variants / 20,960 forward passes ⇒ 1,587.0625 s per
variant, 1.211546 s per forward pass. Computed Z2a's two mandated
numbers (measured extrapolation vs the prior session's naive 8×) under
both readings of "(2,620)", with the diagnosis below.
Actual output (verbatim, the job; head + timing markers + key blocks,
elisions marked):
```
Z2A_START 2026-09-23 16:39:38
Using device: mps; BATCH=16 N_BOOT=10 N_PERM=10 BRUTE_N=16 PHASE2_MAX=75 SEED=0
P (PLL sum set): 655 positions incl. 222
Analysis set (delta_esm): 11344 variants, 654 positions

Loading ESM-2 650M (already cached -- no new download)...
  [model-loaded t=     4s]

==========================================================================
PHASE 1 -- raw masked log-probs, both backgrounds (1310 forward passes)
==========================================================================
  G1 odds identity (wt bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
  G1 odds identity (av bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
  G2 raw delta at 222 across backgrounds = 0.000e+00 (must be ~0: masked contexts identical)
  G1/G2 PASS
  global constant K = sum_j delta_bg logP(wt_j) = +1.849228 (sd across positions = 0.03409)
  [phase1-done t=  1553s]

==========================================================================
PHASE 2 -- L222 term, 11344 variants (mask @222, variant substitution in context)
==========================================================================
  PHASE2_MAX=75 (SMOKE ONLY -- 11269 rows keep NaN delta_pll; reduced-n outputs are machinery checks, NOT results)
  L222 (n=75): mean=-5.18161 sd=0.03121 min=-5.25684 max=-5.07137
  delta_pll sd = 0.05921 (delta_esm sd = 0.11823)
Null set (+own_e_b): 73 variants, 4 positions
  [phase2-done t=  1598s]

==========================================================================
PHASE 3 -- direct un-frozen full-sum check on 16 variants (seed 0, 20960 forward passes)
==========================================================================
  direct - (delta_esm+L222): mean=+1.86950 vs K=+1.84923  -> mean algebra residual = +0.02028
  frozen-distal approximation error: sd=0.09794 max|e|=0.19096  (= 165.4% of sd(delta_pll), n=16 disclosed)
  (sample) spearman(direct full-sum, fitted frozen) = +0.5559 n=16
  [phase3-done t= 26991s]

==========================================================================
PHASE 4 -- PRIMARY correlations (position-cluster bootstrap, N_BOOT=10)
==========================================================================
  ORIGINAL delta_ESM (full n, script 32): own e.b rho=-0.088118 | published e.b rho=-0.070705
  *** PHASE2_MAX set: the rows below are reduced-n machinery checks, NOT results (see SESSION_LOG). ***
  PLL, signed, own e_b                         rho=+0.043262 CI=[-0.076753,+0.205802] p=0.6000 n=73  (crosses 0)
  ... (2 more reduced-n rows) ...
  ORIGINAL delta_ESM, own e_b (rerun here)     rho=-0.088118 CI=[-0.119614,-0.070906] p=<0.1000 n=10757

==========================================================================
PHASE 5 (U2b) -- SIGN-FLIP RE-DERIVATION NULL (10 perms), script-33 machinery unchanged
==========================================================================
  all-+1 flips reproduce own_e_b exactly: max|diff|=9.021e-17
  all--1 flips give exactly -own_e_b:     max|diff|=9.021e-17
  signed delta_PLL vs signed e_b
    observed=+0.0433  null mean=+0.0247 sd=0.1276  p=0.8000
    excess over null=+0.0185  (57% of the raw value is structural artifact)
    -> does NOT survive
    null-centring check: null mean IS consistent with zero -- machinery behaving
    ORIGINAL delta_ESM side-by-side: observed=-0.0881 null mean=+0.0001 p=0.0000
  absolute |delta_PLL| vs |e_b|
    observed=-0.1673  null mean=-0.1053 sd=0.0631  p=0.2000
    excess over null=-0.0621  (63% of the raw value is structural artifact)
    -> does NOT survive

  NULL 2 -- POSITION-BLOCK PERMUTATION (weaker; association only)
    observed=+0.0433  null mean=+0.0045 sd=0.0833  p=0.5000

  REGION CHECK (sign-flip null, per region; script-33 parity)
    region 1: SKIPPED (4 positions)
    ... (regions 2-4 SKIPPED) ...

Saved to /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task67_u2_pll_scores_smoke.csv
Saved to /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task67_u2_results_smoke.csv

LIMITATIONS (stated here, not only in a writeup):
  * Distal context is frozen at each background's WT sequence;
    the dropped term has sd=0.09794 max=0.19096
    on the n=16 brute-force sample above.
  * One-directional: the atlas measures v in the A222V background
    only (no symmetrisation) -- same caveat as script 32.
  * P-values apply to own_e_b; transfer to published e.b only as
    far as the two agree (script 17).
  * Total runtime 26992s.
Z2A_END 2026-09-24 00:09:32
```
(harness: `Command exited with code 0.` ⇒ EXIT=0.)
Z2a's mandated numbers ("Report both numbers"):
```
MEASURED extrapolation — per-unit cost x 2,620:
  reading A — 2,620 = FORWARD PASSES (diagnosis: script 67's own print
    formula (BRUTE_N*2*len(positions)) = 2 x 2 x 655 = 2,620 at
    BRUTE_N=2; the prior breakdown line reads "Phase 3 brute BRUTE_N=2
    (2,620): 1,643 s", SESSION_LOG L2033):
      2,620 x 1.211546 s/pass  = 3,174 s = 52.9 min
  reading B — 2,620 = ROWS, the closeout doc's literal label (line 79):
      2,620 x 1,587.0625 s/row = 4,158,104 s = 1,155 h ~= 48 days
      -> PROVABLY not what the original measurement did (its whole
         phase-3 ran in 1,643 s), so the label is wrong; contradiction
         logged both ways (AGENTS sec 5) and treated as passes below.
NAIVE 8x (prior session's own): 1,643 s x 8 = 13,144 s = 219 min = 3.65 h
Apples-to-apples, same workload (BRUTE_N=16, 20,960 passes):
  naive 13,144 s  vs  MEASURED 25,393 s  ->  naive under-estimates by 1.932x
  (the same 1.932x factor appears as 3,174 / 1,643: today's per-pass
   rate is 1.932x the original run's rate — internally consistent.)
Rate diagnosis (both runs at BATCH=16, SESSION_LOG L1991 "BATCH=16 fixed
as the setting"; unexplained, disclosed):
  phase 1 per-pass:  785/1310 = 0.599 s (original) vs 1553/1310 = 1.186 s (Z2a) -> 1.98x
  phase 3 per-pass: 1643/2620 = 0.627 s (original) vs 25393/20960 = 1.212 s (Z2a) -> 1.93x
  phase 2 per-seq:    0.62 s (original)            vs 45/75 = 0.600 s (Z2a)        -> unchanged
```
Verdict: PASS. Phase-3's real cost at BRUTE_N=16 is measured (25,393 s;
7.05 h) — and because Z2a ran at exactly the BRUTE_N the full run was
planned for, this is a DIRECT measurement, so Z2b needs no
extrapolation for its phase-3 input. The naive 8× (13,144 s) is shown
untrustworthy: it under-estimates the same workload by 1.93×, because
the machine's full-length-pass rate is ~1.95× slower than in the
original smoke run (phase-2's rate is unchanged — between-run
difference unexplained, reported as-is, not rationalised).
Files: CLOSEOUT_LOG.md (this entry); `data/processed/task67_u2_*_smoke.csv`
(restored originals, md5s above); `z2_backup/z2a_run_outputs/*` (preserved
job outputs, md5s above); no script modified; the job fetched **0 network
bytes** ("already cached -- no new download" — ESM-2 650M from cache).
Unexpected: (1) background run disclosed (prior session's launch; handled
on notification, not polled). (2) The job had overwritten the canonical
smoke CSVs → preserve-then-restore executed as above (both generations
now retained with md5s). (3) "(2,620 rows)" is a mislabel of 2,620
forward passes — logged both ways, arithmetic shown. (4) Between-run
per-pass rate shift ~1.95× on phases 1/3 but NOT phase-2, same BATCH —
unexplained, disclosed, and it is what makes the naive-8× planning number
unsafe (feeds Z2b's conservatism). (5) Deviations from Z2a's task text,
disclosed: the prior session ran ALL phases at smoke params rather than
"Phase 3 alone", and the slice was the BRUTE_N parameter itself (16
variants, the smoke run's existing mechanism — explicitly what the task
said to reuse) rather than the suggested 50-100 rows; timing stays cleanly
separable via the phase markers, so the measurement Z2a asked for exists.
(6) Job duration 7 h 29 m 54 s, of which 7.05 h is phase 3 — measured
from its own timestamps, never estimated.
---

## [Z2b] — Decide the full run's actual scope from Z2a's real measurement
Status: PASS (decision computed exactly per the pre-registered rule; the
outcome is the REDUCED-SCOPE branch — **BRUTE_N=5**, explicitly disclosed
as reduced-resolution vs the task's suggested BRUTE_N=16; Z2c itself NOT
yet run — deferred under the deepdive-priority rule, exact command
pre-specified below)
Time started / finished: 2026-09-24 00:31 / 2026-09-24 00:33:20
What I did: Read Z2b's exact text (task doc L84-99). Collected only the
inputs it names, each labelled with its source — nothing remeasured:
(1) Z2a's measured phase-3 = **25,393 s at BRUTE_N=16** ([Z2a], direct
measurement at exactly the planned parameter, so NO phase-3
extrapolation is needed for the projection); (2) the other phases'
already-measured costs from the original breakdown (SESSION_LOG
L2031-2034, quoted in [Z2b]'s output below) — phase-1 785 s,
phase-2-at-full-n **7,033 s reused directly as the doc instructs
(L88: "reuse it directly, do not remeasure Phase 2")**, phase-4+5
~600 s (already scaled ×33 to N_BOOT=N_PERM=10000); (3) summed for
`PHASE2_MAX=0 BRUTE_N=16 N_BOOT=10000 N_PERM=10000` → 33,811-34,579 s
(9.39-9.61 h) > 5 h → took the task's second branch: do NOT run at
BRUTE_N=16; largest BRUTE_N under 18,000 s at Z2a's measured
per-unit cost 1,587.0625 s. Hit a genuine input conflict (AGENTS §5
reconcile duty): phase-1 has TWO measurements — 785 s (original entry)
vs 1,553 s (Z2a), same script, same BATCH=16, cause not determinable
from the records (it is the same between-run rate difference Z2a
measured in phase-3) — so both were carried through the arithmetic, and
the decision is required to hold under BOTH (assumption logged, below).
Actual output (the decision arithmetic, each input source-labelled;
input breakdown quoted verbatim from SESSION_LOG L2031-2034):
```
Phase 1 (gates + K, 1310 passes):      785 s  = 13.1 min
Phase 2 (L222, 0.62 s/seq x 11,344):  7,033 s = 117.2 min
Phase 3 brute BRUTE_N=2 (2,620):      1,643 s =  27.4 min
Phase 4+5 (boots+nulls, scaled x33):  ~600 s =  ~10 min
----
Projection for PHASE2_MAX=0 BRUTE_N=16 N_BOOT=10000 N_PERM=10000 BATCH=16:
  phase 3 (Z2a measured) ...... 25,393 s
  phase 1 ...................... 785 s  OR  1,553 s   [two measurements, 1.98x, unexplained]
  phase 2 @ full n (given) ..... 7,033 s              [reused, not remeasured — task L88]
  phase 4+5 @ 10k/10k (given) .. ~600 s               [already-measured, "scaled x33" — task L87]
  TOTAL: 33,811 s = 9.39 h  (phase-1=785)
         34,579 s = 9.61 h  (phase-1=1,553)
  -> BOTH exceed 18,000 s (5 h)  =>  do NOT run at BRUTE_N=16; reduce BRUTE_N
Largest BRUTE_N under 18,000 s (per-unit 1,587.0625 s, from Z2a):
  phase-1=785:   overhead 8,418 -> phase-3 budget 9,582 -> 9,582/1,587.0625 = 6.04
                 -> BRUTE_N=6: total 17,940 s (margin 60 s); cross-checked under
                    the slower phase-1: 17,940 + 768 = 18,708 s > 18,000 -> EXCEEDS
  phase-1=1,553: overhead 9,186 -> phase-3 budget 8,814 -> 8,814/1,587.0625 = 5.55
                 -> BRUTE_N=5: total 17,121 s (margin 879 s); under phase-1=785:
                    16,353 s (margin 1,647 s) -> under 18,000 s under BOTH readings
DECISION: BRUTE_N=5  — projected 16,353-17,121 s = 4.54-4.76 h (under 5 h either way)
ASSUMPTION LOGGED (AGENTS ambiguity rule): "keeps the projected total
  under 5 hours" is read as required to hold under BOTH existing
  measurements of phase-1 — a projection that exceeds the cap under one
  of two real measurements of the same input does not demonstrably keep
  it under. Under the alternative doc-literal reading (phase-1=785 only)
  the answer would be BRUTE_N=6 — that alternative is stated here, and
  its 60 s margin sits inside the "~600 s" tilde's own uncertainty and
  below the 768 s phase-1 disagreement, so it was not chosen.
MANDATED DISCLOSURE (task L97-99): reduced-resolution run relative to the
  originally suggested command — BRUTE_N 16 -> 5; why: projected
  9.39-9.61 h >> the 5-h rule at BRUTE_N=16. BRUTE_N is the phase-3
  brute-force sample size (variants checked), so phase-3's disclosure
  arm shrinks from 16 to 5 variants.
Z2c command (NOT YET RUN — deepdive keeps priority; foreground, no job):
  set -o pipefail
  timeout 5h env PHASE2_MAX=0 BRUTE_N=5 N_BOOT=10000 N_PERM=10000 BATCH=16 \
    venv/bin/python3 scripts/67_u2_pll_delta.py
  timeout 18,000 s > projection 17,121 s (margin 879 s = "small margin",
  task L103-109). Budget-kill during the run = BUDGET STOP (no retry, no
  gate/threshold change).
```
Verdict: PASS — the scope decision Z2b asked for exists, is derived only
from measured/already-given inputs, and lands in the branch the task
itself anticipated (reduced BRUTE_N, explicitly logged with the exact
value and the reason). No gate, threshold, or pre-registered rule was
changed; nothing was tuned toward any result (no result existed at
decision time — this is a timing/scope decision only).
Files: CLOSEOUT_LOG.md (this entry). No script, data, or writeup file
modified.
Unexpected: (1) the phase-1 input conflict (785 vs 1,553 s at identical
settings — unexplained; both carried, conservative rule applied, and the
alternative answer BRUTE_N=6 shown); (2) BRUTE_N=6's 60-s margin would
have sat inside the phase-4+5 "~" uncertainty — the razor-thin case was
avoided precisely because the projection could not have been claimed to
stay under 5 h; (3) phase-4+5's ~600 s is a pre-existing scaled figure
(reused as the task directs, not remeasured — disclosed); (4) Z2c runs
hours later under the deepdive-priority rule, so its phase rates could
differ from both measured runs — if the run's real cost would exceed the
timeout, the mandated handling is BUDGET STOP, not a retry or a
loosened cap.
---
## [Z2c] — Run it, with a mechanically enforced wall-clock cap — EXECUTED (attempt 3 in the user's own terminal, outside the harness; two in-harness attempts lost to infrastructure; no cap ever fired)

Status: EXECUTED — PASS, with one disclosed deviation (Verdict): the successful attempt
ran in the user's own terminal, fully outside my tool-call machinery, specifically because
the two in-harness attempts before it failed for infrastructure reasons unrelated to the
script itself — so no mechanical wall-clock cap could be attached to the run that produced
the results. Both output files exist on disk, written by script 67's end-of-run save block
with the complete expected schema, and the run's scope is verified from the artifacts
below, not assumed.

Time: Attempt 1 launched 2026-09-24 18:39:35 (harness shell, exact [Z2b] argv, `| tee`);
phase-1 done t=729s logged 18:51:46; process verified dead 21:25:12 (harness turn-end /
interrupt cleanup kill during phase 2; best kill-time estimate ~19:40 from the watchdog's
creation). Attempt 2 launched 2026-09-24 23:05:49 (session-detached supervisor, same argv);
phase-1 done t=1705s; child SIGTERMed (rc=-15) 2026-09-25 00:12:51 after 4,022s by the user
during a resource-contention hang. Attempt 3 (user's terminal): start not captured; both
outputs written 2026-09-25 04:27:02; the launch prompt states its output block ended
`EXIT: 0`. This entry appended 2026-09-25 afternoon.

What I did:
- Pre-spec honoured throughout, [Z2b] (this log L945-951): `timeout 5h env PHASE2_MAX=0
  BRUTE_N=5 N_BOOT=10000 N_PERM=10000 BATCH=16 venv/bin/python3 scripts/67_u2_pll_delta.py`;
  budget-kill during the run = BUDGET STOP, no retry, no rule change.
- Attempt 1 (mine): exact argv under the harness shell, output `| tee` to z2c_full.log.
  `timeout`/`gtimeout` do not exist in this environment (no coreutils), so the cap substitute
  was a sleep+pkill watchdog. The harness auto-backgrounded the run; it was killed silently
  mid-phase-2 — no traceback, no outputs (script 67 writes nothing until the final save),
  and the harness's own output file for the shell 404s (record removed, not completed).
  CORRECTION to the previous session record: a watchdog subshell DID start —
  z2c_watchdog.log exists, created 19:40:18, 0 bytes — and was killed during its sleep
  before it could fire. The earlier claim that the watchdog was "interrupted before start"
  is wrong on this evidence. Neither the 18,000s watchdog nor the harness's 18,000,000 ms
  timeout ever fired: both due times postdate the death.
- Attempt 2 (mine): session-detached supervisor (z2c_supervisor.py in session tmp — the
  exact pattern mandated for every compute job from here on), enforcing the 18,000s cap
  itself with SIGTERM-at-cap (= `timeout 5h` semantics, disclosed substitution), writing
  merged stdout+stderr from the detached process so the log survives harness cleanup.
  Phase 1 completed (t=1705s vs attempt 1's 729s = 2.34x slower — consistent with the
  contention incident); phase 2 printed nothing that reached the log because Python
  block-buffers piped stdout (the `model-loaded t=13s` line was flushed 28 minutes late;
  the `phase1-done` line sat in-buffer until process death) — progress was invisible from
  outside, which is exactly the ambiguity the user then had to judge. The user diagnosed a
  resource-contention hang and SIGTERMed the child at 00:12:51; the supervisor recorded
  rc=-15 after 4,022s, capped=False (i.e. the cap did NOT kill it — an external signal did).
  Two supervisor log labels are cosmetic and disclosed as such: `*** Z2c attempt 2 FINISHED
  rc=-15 ***` (its exit path labels any non-cap exit FINISHED; rc=-15 is the external
  SIGTERM) and `[SUPERVISOR ERROR: SystemExit(1)]` (main() returns 1 on a nonzero child
  status, and sys.exit(1) was then caught by the supervisor's own top-level handler).
  Verified: neither attempt produced any result file — only the Sep-24 smoke CSVs existed
  until 04:27:02 on Sep 25.
- Attempt 3 (user): the identical command, run manually in the user's own terminal after
  both in-harness attempts failed for infrastructure reasons unrelated to the script itself.
  The launch prompt's output block was NOT actually pasted — the prompt contains the literal
  unfilled placeholder `[PASTE THE FULL OUTPUT BLOCK FROM YOUR LAST MESSAGE TO CLAUDE HERE —
  THE ONE STARTING "Using device: mps; BATCH=16..." THROUGH "EXIT: 0"]` — and no stdout
  capture of that run exists anywhere (verified this session: no Sep-25 capture file in
  session tmp; the only repo files touched since Sep 25 are the two result CSVs).
  Per AGENTS §5 nothing is reconstructed from memory: this entry quotes the on-disk
  artifacts verbatim, plus the prompt's own statement `EXIT: 0`.
- Artifact-based verification of the run's scope (each checked from the files): full-mode
  output filenames (not `_smoke`) => PHASE2_MAX=0; both null rows carry n_perm=10000 and
  the four region rows carry n_perm=1000 = max(200, N_PERM//10) (script L448) => N_PERM
  =10000; analysis n=10,757 => the pre-registered script-32 set; scores CSV contains the
  `delta_pll_subset` column => the {p,222}-subset branch ran; exactly 11 result rows
  (4 primary + 2 null1 + 1 null2 + 4 regions) => execution reached the region loop, the
  last append site before the save. BRUTE_N=5 is NOT independently verifiable from the
  artifacts (it appears only in the uncaptured LIMITATIONS print) — taken on the user's
  report and disclosed as unverified. Gate passing in attempt 3 is inferred from code
  structure, not quoted: both `sys.exit(1)` gate exits (script L237, L387) precede the only
  writes (L479-484), so the files' existence implies the gates passed.
- Runtime bound for attempt 3 (derived; assumption stated): outputs at 04:27:02, attempt 2
  killed 00:12:51 — if, per the user's account of sequential attempts, attempt 3 started
  after that kill, runtime was < 4h14m11s < the 18,000s cap, i.e. the cap would not have
  fired had it been enforceable. If the attempts overlapped instead, the bound fails and
  attempt 3's duration is simply unknown; either way the cap was unenforceable on it.
- Script 67 has no checkpoint: every attempt restarted from zero; phase 1 ran three times
  total (729s, 1,705s, and once uncaptured in attempt 3).

Actual output (verbatim — logs and CSVs embedded from disk by `cat`, no transcription):

**Attempt 1 — z2c_attempt1_killed.log (872 B; last write 18:51:46; ends after phase1-done; killed during phase 2):**
```text
Using device: mps; BATCH=16 N_BOOT=10000 N_PERM=10000 BRUTE_N=5 PHASE2_MAX=all SEED=0
P (PLL sum set): 655 positions incl. 222
Analysis set (delta_esm): 11344 variants, 654 positions

Loading ESM-2 650M (already cached -- no new download)...
  [model-loaded t=     3s]

==========================================================================
PHASE 1 -- raw masked log-probs, both backgrounds (1310 forward passes)
==========================================================================
  G1 odds identity (wt bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
  G1 odds identity (av bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
  G2 raw delta at 222 across backgrounds = 0.000e+00 (must be ~0: masked contexts identical)
  G1/G2 PASS
  global constant K = sum_j delta_bg logP(wt_j) = +1.849228 (sd across positions = 0.03409)
  [phase1-done t=   729s]
```

**Attempt 2 — z2c_attempt2_killed.log (1,313 B; renamed from z2c_full.log for unambiguous archiving, content unchanged; supervisor header + child output + exit record):**
```text
Z2c ATTEMPT 2 (detached, supervisor-enforced cap) cmd: env PHASE2_MAX=0 BRUTE_N=5 N_BOOT=10000 N_PERM=10000 BATCH=16 venv/bin/python3 scripts/67_u2_pll_delta.py
cap=18000s; attempt-1 log preserved as z2c_attempt1_killed.log
Using device: mps; BATCH=16 N_BOOT=10000 N_PERM=10000 BRUTE_N=5 PHASE2_MAX=all SEED=0
P (PLL sum set): 655 positions incl. 222
Analysis set (delta_esm): 11344 variants, 654 positions

Loading ESM-2 650M (already cached -- no new download)...
  [model-loaded t=    13s]
[2026-09-24 23:34:16] progress: [model-loaded t=    13s]

==========================================================================
PHASE 1 -- raw masked log-probs, both backgrounds (1310 forward passes)
==========================================================================
  G1 odds identity (wt bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
  G1 odds identity (av bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
  G2 raw delta at 222 across backgrounds = 0.000e+00 (must be ~0: masked contexts identical)
  G1/G2 PASS
  global constant K = sum_j delta_bg logP(wt_j) = +1.849228 (sd across positions = 0.03409)
  [phase1-done t=  1705s]
[2026-09-25 00:12:51] progress: [phase1-done t=  1705s]
[2026-09-25 00:12:51] child exited rc=-15 after 4022s
*** Z2c attempt 2 FINISHED rc=-15 after 4022s ***
```

**Attempt 3 — on disk: data/processed/task67_u2_results.csv (12 lines; both output files written 2026-09-25 04:27:02):**
```csv
stage,quantity,rho,ci_lo,ci_hi,p_boot,n,observed,null_mean,null_sd,excess,frac_artifact,p,n_perm,survives
primary,"PLL, signed, own e_b",-0.07776959983837096,-0.10688322888854776,-0.04974711981416686,0.0,10757.0,,,,,,,,
primary,"PLL, signed, published e.b",-0.0600374013755153,-0.0871279033544947,-0.03368731845238712,0.0,10757.0,,,,,,,,
primary,"PLL({p,222}-subset), own e_b",-0.08109550220262333,-0.10851202804213385,-0.05422478024373552,0.0,10757.0,,,,,,,,
primary,"ORIGINAL delta_ESM, own e_b (rerun here)",-0.08811806424891734,-0.1173334458953319,-0.05951138449511738,0.0,10757.0,,,,,,,,
null1_signflip,signed delta_PLL vs signed e_b,,,,,,-0.07776959983837096,7.024193230850521e-05,0.00930718807068743,-0.07783984177067947,-0.0009032055257387483,0.0,10000.0,True
null1_signflip,absolute |delta_PLL| vs |e_b|,,,,,,0.08377842455872947,0.07912517131677745,0.006674706792613659,0.004653253241952024,0.944457618217802,0.2439,10000.0,False
null2_position_block,signed,,,,,,-0.07776959983837096,0.00011453347616062488,0.01379053808466202,,,0.0,10000.0,True
null_signflip_region,region_1,,,,,,-0.138288574347306,-1.776245659478859e-05,0.019085693762900202,-0.1382708118907112,,0.0,1000.0,True
null_signflip_region,region_2,,,,,,0.025507947521752818,-0.0010102797909094863,0.020597422137432413,0.026518227312662304,,0.225,1000.0,False
null_signflip_region,region_3,,,,,,-0.06699228445856907,0.00027789393863091716,0.0188353868373497,-0.06727017839719998,,0.0,1000.0,True
null_signflip_region,region_4,,,,,,0.0028576906282245956,-1.7528263827054745e-05,0.0176906267288677,0.00287521889205165,,0.858,1000.0,False
```

**Attempt 3 — on disk: data/processed/task67_u2_pll_scores.csv (1,015,768 B; 10,758 lines = header + 10,757 rows); header + first two rows:**
```csv
hgvs_pro,position,mut_aa,delta_esm,l222,delta_pll,delta_pll_subset
p.Ala113Arg,113,R,0.1260910613928008,-5.194302558898926,-3.2189837597252318,-5.068227767944334
p.Ala113Asn,113,N,0.0541716201696544,-5.184264749288559,-3.2808653913380112,-5.130109399557114
```

Verdict: PASS — the full run Z2c asked for exists: n=10,757, N_BOOT=N_PERM=10,000, both
backgrounds, every phase and null completed, exit reported 0. The in-run rerun of the
original delta_ESM reproduces the deep-dive anchor BIT-FOR-BIT
(-0.08811806424891734 in both places) — a pipeline-identity unit check per §6, not a
replication claim. No BUDGET STOP occurred at any point: neither in-harness attempt was
killed by a cap (watchdog, harness timeout, and supervisor cap all went untriggered —
infrastructure kills came first), so [Z2b]'s no-retry-on-budget-kill rule was never
engaged; the two retries were infrastructure recoveries under this session's explicit
self-healing authorization, not rule violations. DISCLOSED DEVIATION: the attempt that
produced the results ran with NO mechanically enforced cap, because it ran outside any
tooling at the user's terminal — the task's mechanical-cap requirement (task L101-111)
was implemented in both of my attempts and could not be attached to the user's run; it is
recorded here rather than smoothed over. Direction/magnitude/significance of the numbers
versus delta_ESM is Z2d's task, not this entry's.

Files: CLOSEOUT_LOG.md (this entry). Attempt-3 outputs: data/processed/task67_u2_pll_scores.csv
and data/processed/task67_u2_results.csv (pre-existing names overwritten by this run;
gitignored, regenerable). Ephemeral record, session tmp: z2c_attempt1_killed.log,
z2c_attempt2_killed.log (renamed from z2c_full.log), z2c_status.txt, z2c_supervisor.py,
z2c_watchdog.log (0 B — proof the watchdog started), z2c_probeB.{log,pid} (survival probes
from the launch-method decision). No script, lib, or writeup file modified; no commits.

Unexpected: (1) Three attempts were needed — two infrastructure deaths (harness cleanup
kill; contention hang + manual SIGTERM), both quoted verbatim above, logged with the same
multi-attempt discipline as AE1's two interrupted attempts. (2) The previous record saying
the attempt-1 watchdog never started is CORRECTED here on filesystem evidence (0-byte log
created 19:40:18): it started and was killed in its sleep. (3) The launch prompt's paste
placeholder was left unfilled, so attempt 3's stdout is unavailable; everything quoted comes
from disk or the prompt's own words (AGENTS §5: never reconstruct). (4) Phase-1 wall times
disagree across attempts (729s vs 1,705s) — the same unexplained two-measurement conflict
class [Z2b] already documented (785 vs 1,553s); no decision here depended on it. (5) Block
buffering hid attempt 2's progress for 38 minutes — the observation that looked like a hang
and could not be ruled out from outside the process; recorded because it is why the manual
kill was reasonable. (6) The supervisor's cosmetic FINISHED/ERROR labels on rc=-15 would
mislead a future reader without this note. (7) The successful run's argv is verified from
artifacts only to the extent stated above; BRUTE_N=5 and the exact SEED rest on the user's
report, disclosed as such.
---
## [Z2d] — Report and compare: does whole-sequence delta_PLL change the finding vs delta_ESM? — EXECUTED (writeup from Z2c's on-disk results; no new compute)

Status: EXECUTED — PASS. Report task: every statistic below is a row of
data/processed/task67_u2_results.csv (attempt 3, quoted raw), and every derived
comparison (percent-smaller, CI containment, half-widths) was computed from that
same file in a single venv/bin/python3 pass whose stdout is embedded verbatim —
nothing hand-calculated, nothing recalled (AGENTS §5).

Time: spec read 2026-09-25 ~15:27; entry appended ~15:31. No compute jobs.

What I did:
- Located the exact spec: it is in the task doc CLOSEOUT_U2_U3_U4_V5.md L113-119,
  NOT in CLOSEOUT_LOG.md as the Sep-25 launch prompt claimed (grep for "Z2d" in
  CLOSEOUT_LOG = 0 hits) — the prompt's file pointer was wrong; flagged here per
  §9 rather than silently resolved. Spec verbatim: "Full results: rho, CI, p for
  signed delta_PLL vs signed e_b (both own and published), same format as the
  smoke output. Compare directly against the original delta_ESM's -0.088118.
  State plainly: does the whole-sequence pseudo-log-likelihood construction
  change the direction, magnitude, or statistical significance of the finding
  relative to the single-position masked-marginal version."
- All four primary rows sit on the identical analysis set (n = 10,757 — the same
  script-32 pre-registered set in every row), so the comparison is like-for-like.
- Limitations stated BEFORE the verdict, per §6/§3: (a) no PLL-vs-ESM difference
  test is pre-registered anywhere — the magnitude comparison below is descriptive
  (point estimates, CI containment, CI width); adding a paired delta-rho
  bootstrap post-hoc would be a NEW unregistered test and was NOT done (flagged
  as an open option); (b) script 67's own printed caveat is carried: p-values
  apply to own_e_b, and transfer to published e.b only as far as the two agree
  (script 17); (c) the anchor row's in-run rerun reproducing the original
  bit-for-bit is a pipeline-identity unit check (§6), not independent evidence.

Actual output:

**Primary rows, raw lines of task67_u2_results.csv (attempt 3, written 2026-09-25 04:27:02):**
```csv
stage,quantity,rho,ci_lo,ci_hi,p_boot,n,observed,null_mean,null_sd,excess,frac_artifact,p,n_perm,survives
primary,"PLL, signed, own e_b",-0.07776959983837096,-0.10688322888854776,-0.04974711981416686,0.0,10757.0,,,,,,,,
primary,"PLL, signed, published e.b",-0.0600374013755153,-0.0871279033544947,-0.03368731845238712,0.0,10757.0,,,,,,,,
primary,"PLL({p,222}-subset), own e_b",-0.08109550220262333,-0.10851202804213385,-0.05422478024373552,0.0,10757.0,,,,,,,,
primary,"ORIGINAL delta_ESM, own e_b (rerun here)",-0.08811806424891734,-0.1173334458953319,-0.05951138449511738,0.0,10757.0,,,,,,,,
```

**Null rows, raw lines of the same file:**
```csv
null1_signflip,signed delta_PLL vs signed e_b,,,,,,-0.07776959983837096,7.024193230850521e-05,0.00930718807068743,-0.07783984177067947,-0.0009032055257387483,0.0,10000.0,True
null1_signflip,absolute |delta_PLL| vs |e_b|,,,,,,0.08377842455872947,0.07912517131677745,0.006674706792613659,0.004653253241952024,0.944457618217802,0.2439,10000.0,False
null2_position_block,signed,,,,,,-0.07776959983837096,0.00011453347616062488,0.01379053808466202,,,0.0,10000.0,True
null_signflip_region,region_1,,,,,,-0.138288574347306,-1.776245659478859e-05,0.019085693762900202,-0.1382708118907112,,0.0,1000.0,True
null_signflip_region,region_2,,,,,,0.025507947521752818,-0.0010102797909094863,0.020597422137432413,0.026518227312662304,,0.225,1000.0,False
null_signflip_region,region_3,,,,,,-0.06699228445856907,0.00027789393863091716,0.0188353868373497,-0.06727017839719998,,0.0,1000.0,True
null_signflip_region,region_4,,,,,,0.0028576906282245956,-1.7528263827054745e-05,0.0176906267288677,0.00287521889205165,,0.858,1000.0,False
```

**Derived comparisons — verbatim stdout of the one-pass computation over that file:**
```text
own vs anchor: diff=-0.010348464410546404  ratio=0.8825613737801378  smaller=11.74%
pub vs anchor: diff=-0.028080662873402003  ratio=0.6813290996261641  smaller=31.87%
anchor point inside own CI: True
own point inside anchor CI: True
anchor point inside pub CI: False (pub CI lower=-0.0871279033544947; miss by 0.0009901608944225954)
pub point inside anchor CI: True
CI half-widths: own=0.02856805453719045  pub=0.0267202924510538  anchor=0.0289110307001073
own-anchor |diff|=0.010348464410546404 vs own half-width 0.02856805453719045 -> 36.2% of the half-width
```

Verdict — the plain statement the spec asks for:
- **Direction: UNCHANGED.** All three signed estimates are negative: delta_PLL vs
  own e_b = -0.07776959983837096; delta_PLL vs published e.b = -0.0600374013755153;
  anchor delta_ESM vs own e_b = -0.08811806424891734.
- **Magnitude: modestly attenuated, not transformed.** On own e_b, |rho| is 11.74%
  smaller than the anchor (ratio 0.88256; difference 0.01035 = 36.2% of the
  own-row CI half-width 0.02857); each point estimate lies inside the other's
  95% CI (anchor -0.0881 inside own [-0.10688, -0.04975]; own -0.0778 inside
  anchor [-0.11733, -0.05951]) — descriptively indistinguishable at CI scale.
  On published e.b the attenuation is larger: 31.87% smaller (ratio 0.68133), and
  reported as an observation only: the anchor point -0.08812 falls just OUTSIDE
  the published row's CI lower bound -0.08713, by 0.00099 — a point outside
  another estimate's CI is not a significance test of the difference, and none is
  pre-registered, so no claim is built on it.
- **Statistical significance: UNCHANGED.** Both PLL rows: p_boot < 1/10,000 with
  CIs excluding zero (own [-0.10688, -0.04975], published [-0.08713, -0.03369]);
  the anchor likewise p_boot < 1/10,000, CI [-0.11733, -0.05951]. No threshold,
  seed, or set differs between the rows.
- **Null behavior (reported plainly, §0):** the SIGNED association survives both
  registered nulls — sign-flip null centred at +0.0000702 (frac_artifact -0.09%,
  i.e. effectively zero structural share) p < 1/10,000, and position-block
  centred at +0.0001145, p < 1/10,000. The ABSOLUTE version does NOT survive:
  observed 0.08378 vs null mean 0.07913 -> 94.4% of |delta_PLL|-|e_b| is what
  the null already produces, p = 0.2439 — the magnitude-only story fails again,
  and in the same way AE4's |delta_ESM|-|e_b| failed there (p = 0.1776): two
  different constructions, same negative.
- **Region split (Z3h-style check printed by the run):** region 1 -0.13829
  p < 0.001 survives; region 3 -0.06699 p < 0.001 survives; region 2 +0.02551
  p = 0.225 null; region 4 +0.00286 p = 0.858 null. The pooled negative is
  carried by regions 1 and 3; region 4 shows NO signed PLL association — stated
  as-is.
- **Plain answer to the spec's question:** No — the whole-sequence
  pseudo-log-likelihood construction does not change the direction, does not
  change the statistical significance, and changes the magnitude only modestly
  (|rho| attenuates ~12% on own e_b, ~32% on published e.b). The finding holds
  under the alternative construction; the absolute/magnitude-only variant of it
  fails under both constructions, and the effect is region-heterogeneous (1, 3)
  with region 4 null.

Files: CLOSEOUT_LOG.md (this entry). Read-only inputs: data/processed/
task67_u2_results.csv, task67_u2_pll_scores.csv (attempt 3), task doc spec
L113-119. No new files, no jobs launched, no scripts touched.

Unexpected: (1) The launch prompt pointed at the wrong file for this spec
(CLOSEOUT_LOG vs the task doc) — corrected and flagged above. (2) The
absolute-version null failure (94.4% structural share, p = 0.2439) is a genuine
negative result and is carried in the verdict beside the positive answer, not
buried. (3) The anchor-point-vs-published-CI boundary miss (0.00099) exists in
the numbers; with no pre-registered test for it, it is reported as an
observation only. (4) If a formal paired delta-rho (PLL vs ESM) CI is ever
wanted, it must be added later as a NEW disclosed test — it is deliberately not
computed here.
---
## [AB2a-FIX] — The multi-model comparison table: gate-row fix + first-ever engine execution (deepdive [AB2]'s AB2a, user-authorized 2026-09-25)

Status: EXECUTED — PASS. Smoke 1 crashed (real implementation bug,
diagnosed, fixed to the frozen docstring, disclosed); smoke 2 and the
full run both exited 0 with every gate green at N_BOOT=10000, and the
deliverable exists on disk: data/processed/task_AB2_proteingym_
model_comparison.csv (97 lines = header + 96 model rows incl. the
REF row). Logged in CLOSEOUT_LOG (this session's log) rather than
appended after DEEPDIVE_LOG's terminal `## SUMMARY`, cross-referenced
both ways; the deepdive's [AB2] FAIL entry stands as written.

Time: 2026-09-25. Prep/anchor measurement ~15:41-15:42. Smoke 1
15:43:20 -> 15:43:21, EXIT=1 (crash). Patch + diagnosis 15:44-15:45.
Smoke 2 15:46:10 -> 15:46:33, EXIT=0 (23s). Full run 15:47:24 ->
15:58:57, EXIT=0 (692.1s = 11.5 min; projection from the smoke
engine measurement was ~670s — within the no-guessed-runtime rule).
Entry appended ~16:00.

What I did:
- Authorization: the Sep-25 session prompt explicitly authorized the
  pre-registered gate's row swap ("this is a construction bug ... not a
  weakened test. Swap to any well-measured variant present in both the
  ProteinGym table and script 32's analysis table, re-run the smoke
  and full comparison"). That is the user's call deepdive [AB2] logged
  as open (tree #2 forbade me making it then); it resolves block item 3
  of the deepdive SUMMARY.
- md5 reconciliation FIRST (AGENTS 5 — before the gate ran against the
  file): script 71's docstring recorded md5 7f9ddcc0589f5f93821e8c0a3e5bb539
  for data/external/ProteinGym/MTHR_HUMAN_Weile_2021_scores.csv; today's
  file hashes 6222922d3c4b69d043dc50b802814c7c. Verified: the two copies
  (data/external and AB1's session-tmp extraction) are byte-identical
  (cmp + matching md5 + matching size 29,370,765 B), so every AB1-quoted
  value holds in the file script 71 reads. The recorded 7f9ddcc... is
  the md5 of AB1's MSA artifact MTHR_HUMAN_2023-08-07_b02.a2m (measured
  this session) — a pre-run documentation slip; the docstring line was
  corrected with a bracketed disclosure. No check had ever used that
  md5 (there is no md5 check in the code).
- Anchor selection rule, stated before measuring: argmax |own_e_b|
  over R1's 10,757-row set -> H354R (own_e_b -2.132941112516231,
  region 3; next two for context: T69W -1.5042618515458612,
  A145T +1.3735220963707022). Constant -4.309727668762207 measured via
  a standalone csv.DictReader over AB1's independent session-tmp copy
  (different file, different read path than script 71's pandas merge),
  cross-checked equal in data/external's copy (byte-identical), and
  re-parsed a third time; exactly one ProteinGym row matches H354R.
  AB1 had measured only A222V, so this new independent measurement was
  required; method disclosed in docstring R2 and in the script's
  always-printed gate disclosure.
- Patch 1 (4 edits, atomic replacement with per-edit uniqueness
  assertions): docstring R2 anchor-swap disclosure (mechanism unchanged:
  identity to atol 1e-12 vs an independently measured constant);
  constants ANCHOR_ROW / ANCHOR_ESM2_650M replacing A222V_ESM2_650M;
  gate code swap + a POST-HOC DISCLOSURE line printed on every run;
  docstring md5 correction. R1/R3/R4/R5 rules untouched.
- Smoke 1 (N_BOOT=300): row accounting, join 10757/10757 (coverage
  1.0000), new R2 gate PASS, frame MATCH — then a real Python crash at
  the first bootstrap draw (verbatim traceback below). Not a gate
  failure: a code crash in the shared-draw engine, which had NEVER
  executed before ([AB2] flag 2 predicted exactly this: the original
  smoke exited at the R2 gate, so G-anchor/G-lib never ran).
- Diagnosis (read-only, before editing): pandas .to_numpy() returns
  (n, K) = (10757, 98), while docstring R4 and every engine loop
  (R[k], C = R @ R.T, boot[b] = C[pi, pj]) require (K, n). The same
  wrong orientation silently poisoned the pre-crash `obs` pass — which
  is why G-anchor's frozen identity is the correctness check for the
  fix. Per this session's pre-authorization ("fix if it's a clear
  code-vs-spec bug"), patch 2 (3 edits): A = d[cols].to_numpy().T to
  match the FROZEN docstring, a POST-HOC IMPLEMENTATION FIX print, and
  a bracketed note inside R4. No threshold, seed, set, or rule changed.
- Smoke 2 (N_BOOT=300): ALL gates PASS — G-anchor |diff| = 0.000e+00
  (engine path reproduces -0.08811806424891734 bit-exactly), G-lib
  overall max|diff| = 1.388e-17 < 1e-9. EXIT=0.
- Full run (N_BOOT=10000, script default): EXIT=0, 692.1s, same gates
  green at full N; table written. Ran concurrently with Z3f's SaProt
  scoring (pandas/numpy only, zero model weights loaded — permitted by
  the never-two-heavy-jobs rule, which governs model-loading jobs;
  disclosed for transparency).

Actual output (verbatim; logs embedded from disk by `cat`):

Smoke 1 — the crash (z3f-era session log: ab2a_smoke.log):
```text
Script 71 / AB2a  N_BOOT=300 seed=0 smoke=True  (N_PERM=10000 read but UNUSED -- R3)
*** SMOKE RUN: numbers below are machinery checks only, NOT findings, NOT for quoting. ***
row accounting: task32 table = 11344 rows -> non-null on own_e_b + GI_folinate_independent + delta_esm = 10757 rows / 654 positions (script 32's published set = 10757 / 654)
ProteinGym file: 12464 rows, 95 model score columns, NaNs = 0
join: matched 10757 / 10757 base rows (coverage 1.0000); dropped 0
POST-HOC DISCLOSURE (AGENTS 6): R2 identity-gate anchor row swapped A222V -> H354R under explicit user authorization 2026-09-25 (A222V is structurally absent: zero rows at position 222 in the analysis table; gate mechanism unchanged -- identity atol 1e-12 vs an independently measured constant; full text in docstring R2)
R2 identity gate H354R ESM2_650M = -4.309727668762207 (expected -4.309727668762207) -> PASS
analysis frame: 10757 rows / 654 positions (R1 expectation 10757 / 654: MATCH)
engine: 98 columns x 300 boot draws, 192 pairs (shared-draw, R4)
Traceback (most recent call last):
  File "/Users/arnavchavan/Desktop/mthfr-context-dependence/scripts/71_proteingym_model_comparison.py", line 377, in <module>
    main()
    ~~~~^^
  File "/Users/arnavchavan/Desktop/mthfr-context-dependence/scripts/71_proteingym_model_comparison.py", line 277, in main
    r = rankdata(A[k][i])
                 ~~~~^^^
IndexError: index 9049 is out of bounds for axis 0 with size 98
```

Smoke 2 — all gates green at N_BOOT=300 (ab2a_smoke2.log):
```text
Script 71 / AB2a  N_BOOT=300 seed=0 smoke=True  (N_PERM=10000 read but UNUSED -- R3)
*** SMOKE RUN: numbers below are machinery checks only, NOT findings, NOT for quoting. ***
row accounting: task32 table = 11344 rows -> non-null on own_e_b + GI_folinate_independent + delta_esm = 10757 rows / 654 positions (script 32's published set = 10757 / 654)
ProteinGym file: 12464 rows, 95 model score columns, NaNs = 0
join: matched 10757 / 10757 base rows (coverage 1.0000); dropped 0
POST-HOC DISCLOSURE (AGENTS 6): R2 identity-gate anchor row swapped A222V -> H354R under explicit user authorization 2026-09-25 (A222V is structurally absent: zero rows at position 222 in the analysis table; gate mechanism unchanged -- identity atol 1e-12 vs an independently measured constant; full text in docstring R2)
R2 identity gate H354R ESM2_650M = -4.309727668762207 (expected -4.309727668762207) -> PASS
analysis frame: 10757 rows / 654 positions (R1 expectation 10757 / 654: MATCH)
engine: 98 columns x 300 boot draws, 192 pairs (shared-draw, R4)
POST-HOC IMPLEMENTATION FIX (2026-09-25, disclosed per AGENTS 6): A = d[cols].to_numpy().T -- docstring R4 specifies (K, n) but pandas returns (n, K); the pre-fix code crashed with IndexError at the first bootstrap draw (this engine had NEVER executed before -- [AB2] flag 2, the original smoke died at the R2 gate first). Code changed to match the FROZEN docstring; no threshold, seed, set, or rule changed. The pre-fix 'obs' pass had the same wrong orientation; with the fix, G-anchor's 1e-12 identity check vs -0.08811806424891734 is the independent confirmation of correctness.
engine done: 20.1s
G-anchor: observed rho(delta_esm, own) = np.float64(-0.08811806424891734) vs -0.08811806424891734 |diff| = 0.000e+00 -> PASS
G-lib delta_esm x own_e_b: engine rho=-0.088118064249 CI=[-0.117582890178,-0.060596290776] p=0.000000 | lib rho=-0.088118064249 CI=[-0.117582890178,-0.060596290776] p=0.000000 | max|diff|=1.388e-17
G-lib ESM2_650M x own_e_b: engine rho=+0.085391103105 CI=[+0.060008088637,+0.110617899887] p=0.000000 | lib rho=+0.085391103105 CI=[+0.060008088637,+0.110617899887] p=0.000000 | max|diff|=1.388e-17
G-lib EVmutation x GI_folinate_independent: engine rho=+0.062451801231 CI=[+0.038701424192,+0.086785021143] p=0.000000 | lib rho=+0.062451801231 CI=[+0.038701424192,+0.086785021143] p=0.000000 | max|diff|=1.388e-17
G-lib overall max|diff| = 1.388e-17 (threshold 1e-9) -> PASS

wrote /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task_AB2_proteingym_model_comparison_smoke.csv  (96 model rows, sorted by own_rho ascending)

full table (own block, then pub block):
                     model   own_rho  own_ci_lo  own_ci_hi  own_p_boot   pub_rho  pub_ci_lo  pub_ci_hi  pub_p_boot
     REF_delta_ESM_our_run -0.088118  -0.117583  -0.060596    0.000000 -0.070705  -0.097636  -0.044794    0.000000
         xTrimoPGLM-7B-CLM -0.003085  -0.025413   0.020298    0.773333 -0.008465  -0.030306   0.015144    0.486667
                  ProtGPT2  0.000660  -0.022950   0.028406    0.940000  0.001187  -0.020246   0.024442    0.940000
                    VESPAl  0.016658  -0.013301   0.046083    0.286667  0.016861  -0.011324   0.041494    0.246667
                 CARP_600K  0.020578  -0.007619   0.044826    0.106667  0.016904  -0.008489   0.040628    0.146667
         xTrimoPGLM-3B-CLM  0.023231  -0.004677   0.050856    0.080000  0.022697  -0.002527   0.047942    0.080000
                    RITA_m  0.026164  -0.000804   0.056339    0.060000  0.030092   0.003529   0.055422    0.013333
                    RITA_l  0.026328   0.001855   0.054953    0.040000  0.029838   0.005455   0.057477    0.020000
                     VESPA  0.029222  -0.000633   0.059229    0.060000  0.029421   0.003015   0.054411    0.033333
         xTrimoPGLM-1B-CLM  0.030084   0.001441   0.058566    0.026667  0.027702   0.001501   0.052705    0.040000
                Progen3_1b  0.032046   0.006181   0.057722    0.026667  0.033127   0.008251   0.057419    0.013333
Tranception_L_no_retrieval  0.032382   0.007121   0.059316    0.020000  0.033471   0.010451   0.058031    0.013333
                   RITA_xl  0.034765   0.009277   0.060600    0.013333  0.032549   0.008369   0.054862    0.013333
                Progen3_3b  0.035902   0.007125   0.063867    0.000000  0.032193   0.005710   0.056616    0.013333
              Progen2_base  0.037105   0.008817   0.067334    0.013333  0.035974   0.009631   0.061666    0.006667
      xTrimoPGLM-100B-int4  0.042628   0.021255   0.069303    0.006667  0.031028   0.008828   0.056883    0.013333
                   ESM2_8M  0.046711   0.018537   0.071539    0.000000  0.038253   0.015418   0.061573    0.000000
                    Unirep  0.047706   0.022994   0.074025    0.000000  0.037549   0.015763   0.061251    0.000000
                  ESM2_15B  0.047733   0.024203   0.075734    0.000000  0.045438   0.022479   0.069842    0.000000
            Progen2_medium  0.047990   0.018319   0.074748    0.000000  0.044653   0.017815   0.068154    0.000000
               ProteinMPNN  0.048729   0.029672   0.066616    0.000000  0.038166   0.018906   0.055911    0.000000
         xTrimoPGLM-3B-MLM  0.050396   0.029013   0.073236    0.000000  0.042179   0.020744   0.065937    0.000000
              Progen3_762m  0.052598   0.027442   0.076687    0.000000  0.047489   0.022263   0.070214    0.000000
                   ESM2_3B  0.054520   0.031674   0.080733    0.000000  0.048149   0.026530   0.070823    0.000000
        xTrimoPGLM-10B-MLM  0.055082   0.031948   0.079916    0.000000  0.047380   0.025840   0.070156    0.000000
             Tranception_L  0.055365   0.031096   0.080554    0.000000  0.050060   0.026081   0.072951    0.000000
             Progen2_large  0.056800   0.029872   0.086226    0.000000  0.052751   0.027666   0.077102    0.000000
                   Wavenet  0.057514   0.029627   0.084307    0.000000  0.046473   0.021719   0.071200    0.000000
            Progen2_xlarge  0.058688   0.035007   0.083674    0.000000  0.050773   0.025995   0.075749    0.000000
            Unirep_evotune  0.058791   0.031618   0.087919    0.000000  0.057060   0.032131   0.082107    0.000000
          Site_Independent  0.063966   0.038836   0.087473    0.000000  0.051579   0.028496   0.073640    0.000000
                    SiteRM  0.064323   0.039397   0.092956    0.000000  0.053038   0.028884   0.079181    0.000000
    MSA_Transformer_single  0.066429   0.041876   0.093145    0.000000  0.063738   0.040143   0.086940    0.000000
             TranceptEVE_L  0.066924   0.039749   0.093197    0.000000  0.057803   0.032548   0.082371    0.000000
              ESM1v_single  0.067808   0.044785   0.092276    0.000000  0.061313   0.037131   0.084075    0.000000
  MSA_Transformer_ensemble  0.067901   0.042716   0.094571    0.000000  0.064131   0.041168   0.087848    0.000000
       DeepSequence_single  0.071365   0.045832   0.098618    0.000000  0.057917   0.031191   0.084454    0.000000
                    VespaG  0.071511   0.045181   0.097165    0.000000  0.061668   0.036592   0.084938    0.000000
                 ProSST-20  0.071634   0.046691   0.097125    0.000000  0.058052   0.035131   0.081862    0.000000
                EVE_single  0.072827   0.047968   0.101017    0.000000  0.059516   0.035917   0.086537    0.000000
         ProtSSN_k10_h1280  0.073303   0.045450   0.100900    0.000000  0.059878   0.032704   0.086266    0.000000
Tranception_M_no_retrieval  0.074483   0.047294   0.101336    0.000000  0.064165   0.038978   0.088951    0.000000
              EVE_ensemble  0.074602   0.051088   0.102530    0.000000  0.061734   0.036016   0.088824    0.000000
          ProtSSN_k20_h512  0.075102   0.047379   0.101448    0.000000  0.059826   0.033551   0.084584    0.000000
                  CARP_38M  0.075566   0.049781   0.101061    0.000000  0.058116   0.034364   0.082401    0.000000
                     GEMME  0.075770   0.049856   0.102602    0.000000  0.064798   0.040009   0.088980    0.000000
               ProSST-4096  0.075958   0.049828   0.099001    0.000000  0.062682   0.040001   0.083417    0.000000
     DeepSequence_ensemble  0.076136   0.051015   0.103963    0.000000  0.062785   0.035188   0.088050    0.000000
                ProSST-128  0.076333   0.051675   0.101830    0.000000  0.064912   0.042548   0.089346    0.000000
                ProSST-512  0.076500   0.049520   0.099391    0.000000  0.062943   0.036833   0.086908    0.000000
                EVmutation  0.076539   0.052656   0.103151    0.000000  0.062452   0.038701   0.086785    0.000000
         ProtSSN_k20_h1280  0.076840   0.048447   0.104596    0.000000  0.061162   0.034836   0.087538    0.000000
            ESM1v_ensemble  0.076873   0.051092   0.100663    0.000000  0.068169   0.043166   0.090793    0.000000
                 ESMC-600M  0.079918   0.056059   0.105585    0.000000  0.069010   0.045996   0.093503    0.000000
             TranceptEVE_M  0.080040   0.056274   0.105742    0.000000  0.067007   0.043884   0.090993    0.000000
             Tranception_M  0.080256   0.056982   0.104472    0.000000  0.067522   0.045869   0.089760    0.000000
               ProSST-1024  0.080384   0.057384   0.104175    0.000000  0.064873   0.042426   0.088522    0.000000
                      PoET  0.081023   0.057245   0.103644    0.000000  0.067101   0.045211   0.089717    0.000000
                    RSALOR  0.081112   0.053568   0.105686    0.000000  0.067749   0.040532   0.091784    0.000000
                    ESCOTT  0.082567   0.057305   0.109210    0.000000  0.073542   0.048188   0.097575    0.000000
          ProtSSN_k10_h768  0.082626   0.054028   0.109871    0.000000  0.069863   0.043297   0.097816    0.000000
          ProtSSN_k20_h768  0.082907   0.055128   0.109841    0.000000  0.068699   0.042106   0.094137    0.000000
          ProtSSN_k10_h512  0.083076   0.056805   0.109957    0.000000  0.069266   0.042820   0.095551    0.000000
               ProSST-2048  0.084017   0.058351   0.110063    0.000000  0.065962   0.041454   0.090509    0.000000
          ProtSSN_ensemble  0.085229   0.058095   0.112019    0.000000  0.069699   0.043310   0.096542    0.000000
                 ESM2_650M  0.085391   0.060008   0.110618    0.000000  0.069895   0.045963   0.094220    0.000000
          ProtSSN_k30_h768  0.085757   0.059674   0.113234    0.000000  0.069304   0.042451   0.096894    0.000000
                   S3F_MSA  0.087055   0.060484   0.111769    0.000000  0.072645   0.047285   0.097687    0.000000
                  VenusREM  0.087454   0.060078   0.112696    0.000000  0.069567   0.044212   0.093230    0.000000
                   S2F_MSA  0.088481   0.061681   0.113360    0.000000  0.074438   0.049564   0.098012    0.000000
                       S3F  0.088769   0.060353   0.115145    0.000000  0.074181   0.048503   0.097626    0.000000
                       S2F  0.090411   0.065112   0.115479    0.000000  0.076535   0.052238   0.097906    0.000000
          ProtSSN_k30_h512  0.090596   0.063142   0.117729    0.000000  0.073083   0.047557   0.098179    0.000000
                       MIF  0.091707   0.066905   0.120182    0.000000  0.075151   0.050689   0.104297    0.000000
               MULAN_small  0.094248   0.069077   0.120272    0.000000  0.079928   0.056859   0.105765    0.000000
                     ESM1b  0.094641   0.070954   0.118638    0.000000  0.078431   0.056058   0.103394    0.000000
         ProtSSN_k30_h1280  0.095003   0.066874   0.122836    0.000000  0.077958   0.051683   0.103045    0.000000
           SaProt_650M_AF2  0.096433   0.070543   0.123137    0.000000  0.084766   0.061033   0.111929    0.000000
                 CARP_640M  0.098566   0.075404   0.125242    0.000000  0.075254   0.050403   0.100548    0.000000
             TranceptEVE_S  0.105430   0.080566   0.130282    0.000000  0.085482   0.062407   0.109159    0.000000
                     MIFST  0.107277   0.082956   0.137458    0.000000  0.085269   0.059529   0.110674    0.000000
              Progen3_339m  0.113636   0.089011   0.136963    0.000000  0.089904   0.066922   0.110894    0.000000
             Tranception_S  0.114348   0.091595   0.134532    0.000000  0.090148   0.069443   0.110841    0.000000
            SaProt_35M_AF2  0.116969   0.093506   0.142349    0.000000  0.095712   0.073871   0.120660    0.000000
                   ESM-IF1  0.117750   0.091960   0.145328    0.000000  0.096178   0.072914   0.124234    0.000000
             Progen2_small  0.122719   0.096658   0.149038    0.000000  0.092231   0.068412   0.118184    0.000000
         xTrimoPGLM-1B-MLM  0.128326   0.102289   0.155839    0.000000  0.097637   0.072947   0.123826    0.000000
                  CARP_76M  0.128340   0.103021   0.151939    0.000000  0.101457   0.075501   0.122712    0.000000
                  ESM2_35M  0.129356   0.101710   0.152658    0.000000  0.103943   0.079272   0.126304    0.000000
              Progen3_112m  0.132184   0.105132   0.155094    0.000000  0.101271   0.073829   0.124062    0.000000
              Progen3_219m  0.135300   0.108472   0.158742    0.000000  0.102709   0.075085   0.125252    0.000000
                    RITA_s  0.139547   0.114832   0.161868    0.000000  0.107562   0.083714   0.129181    0.000000
Tranception_S_no_retrieval  0.142166   0.119400   0.166100    0.000000  0.105874   0.084431   0.127216    0.000000
                      ESM3  0.147204   0.123327   0.171821    0.000000  0.123481   0.098776   0.146340    0.000000
                 ESMC-300M  0.153130   0.127381   0.180463    0.000000  0.122173   0.098146   0.148830    0.000000
                 ESM2_150M  0.162231   0.136548   0.186001    0.000000  0.128456   0.104980   0.152422    0.000000

top 5 / bottom 5 by own_rho:
                model   own_rho  own_ci_lo  own_ci_hi
REF_delta_ESM_our_run -0.088118  -0.117583  -0.060596
    xTrimoPGLM-7B-CLM -0.003085  -0.025413   0.020298
             ProtGPT2  0.000660  -0.022950   0.028406
               VESPAl  0.016658  -0.013301   0.046083
            CARP_600K  0.020578  -0.007619   0.044826
                     model  own_rho  own_ci_lo  own_ci_hi
                    RITA_s 0.139547   0.114832   0.161868
Tranception_S_no_retrieval 0.142166   0.119400   0.166100
                      ESM3 0.147204   0.123327   0.171821
                 ESMC-300M 0.153130   0.127381   0.180463
                 ESM2_150M 0.162231   0.136548   0.186001
  REF_delta_ESM_our_run      own_rho=-0.088118 CI=[-0.1176,-0.0606] p=<0.00333 | pub_rho=-0.070705
  ESM2_650M                  own_rho=+0.085391 CI=[+0.0600,+0.1106] p=<0.00333 | pub_rho=+0.069895
  ESM2_150M                  own_rho=+0.162231 CI=[+0.1365,+0.1860] p=<0.00333 | pub_rho=+0.128456
  ESM1v_single               own_rho=+0.067808 CI=[+0.0448,+0.0923] p=<0.00333 | pub_rho=+0.061313
  ESM1v_ensemble             own_rho=+0.076873 CI=[+0.0511,+0.1007] p=<0.00333 | pub_rho=+0.068169
  EVmutation                 own_rho=+0.076539 CI=[+0.0527,+0.1032] p=<0.00333 | pub_rho=+0.062452
  Site_Independent           own_rho=+0.063966 CI=[+0.0388,+0.0875] p=<0.00333 | pub_rho=+0.051579
  EVE_ensemble               own_rho=+0.074602 CI=[+0.0511,+0.1025] p=<0.00333 | pub_rho=+0.061734
  GEMME                      own_rho=+0.075770 CI=[+0.0499,+0.1026] p=<0.00333 | pub_rho=+0.064798
  MSA_Transformer_ensemble   own_rho=+0.067901 CI=[+0.0427,+0.0946] p=<0.00333 | pub_rho=+0.064131
  DeepSequence_ensemble      own_rho=+0.076136 CI=[+0.0510,+0.1040] p=<0.00333 | pub_rho=+0.062785

AB2 column facts: ESM-1v columns present = ['ESM1v_single', 'ESM1v_ensemble'] (TWO aggregates, not five seeds -> AB2b/AC4 cross-ref); EVmutation column present = True (AB2c/T cross-ref)

LIMITATIONS (R5): aggregate columns are not seeds; rows share one e.b vector and are not independent of each other; descriptive table, no multiple-comparison claim; reproducing script 32's anchor row validates this pipeline against script 32 (reproduction, not replication).
total runtime 22.0s
```

Full run at N_BOOT=10000 — the quotable run (ab2a_full.log, 156 lines):
```text
Script 71 / AB2a  N_BOOT=10000 seed=0 smoke=False  (N_PERM=10000 read but UNUSED -- R3)
row accounting: task32 table = 11344 rows -> non-null on own_e_b + GI_folinate_independent + delta_esm = 10757 rows / 654 positions (script 32's published set = 10757 / 654)
ProteinGym file: 12464 rows, 95 model score columns, NaNs = 0
join: matched 10757 / 10757 base rows (coverage 1.0000); dropped 0
POST-HOC DISCLOSURE (AGENTS 6): R2 identity-gate anchor row swapped A222V -> H354R under explicit user authorization 2026-09-25 (A222V is structurally absent: zero rows at position 222 in the analysis table; gate mechanism unchanged -- identity atol 1e-12 vs an independently measured constant; full text in docstring R2)
R2 identity gate H354R ESM2_650M = -4.309727668762207 (expected -4.309727668762207) -> PASS
analysis frame: 10757 rows / 654 positions (R1 expectation 10757 / 654: MATCH)
engine: 98 columns x 10000 boot draws, 192 pairs (shared-draw, R4)
POST-HOC IMPLEMENTATION FIX (2026-09-25, disclosed per AGENTS 6): A = d[cols].to_numpy().T -- docstring R4 specifies (K, n) but pandas returns (n, K); the pre-fix code crashed with IndexError at the first bootstrap draw (this engine had NEVER executed before -- [AB2] flag 2, the original smoke died at the R2 gate first). Code changed to match the FROZEN docstring; no threshold, seed, set, or rule changed. The pre-fix 'obs' pass had the same wrong orientation; with the fix, G-anchor's 1e-12 identity check vs -0.08811806424891734 is the independent confirmation of correctness.
  1000/10000 draws, 65s elapsed, eta 584s
  2000/10000 draws, 130s elapsed, eta 519s
  3000/10000 draws, 195s elapsed, eta 454s
  4000/10000 draws, 260s elapsed, eta 390s
  5000/10000 draws, 325s elapsed, eta 325s
  6000/10000 draws, 390s elapsed, eta 260s
  7000/10000 draws, 454s elapsed, eta 195s
  8000/10000 draws, 519s elapsed, eta 130s
  9000/10000 draws, 584s elapsed, eta 65s
  10000/10000 draws, 649s elapsed, eta 0s
engine done: 649.2s
G-anchor: observed rho(delta_esm, own) = np.float64(-0.08811806424891734) vs -0.08811806424891734 |diff| = 0.000e+00 -> PASS
G-lib delta_esm x own_e_b: engine rho=-0.088118064249 CI=[-0.117333445895,-0.059511384495] p=0.000000 | lib rho=-0.088118064249 CI=[-0.117333445895,-0.059511384495] p=0.000000 | max|diff|=1.388e-17
G-lib ESM2_650M x own_e_b: engine rho=+0.085391103105 CI=[+0.058861369894,+0.112293963053] p=0.000000 | lib rho=+0.085391103105 CI=[+0.058861369894,+0.112293963053] p=0.000000 | max|diff|=6.939e-18
G-lib EVmutation x GI_folinate_independent: engine rho=+0.062451801231 CI=[+0.037668764520,+0.087566310284] p=0.000000 | lib rho=+0.062451801231 CI=[+0.037668764520,+0.087566310284] p=0.000000 | max|diff|=1.388e-17
G-lib overall max|diff| = 1.388e-17 (threshold 1e-9) -> PASS

wrote /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task_AB2_proteingym_model_comparison.csv  (96 model rows, sorted by own_rho ascending)

full table (own block, then pub block):
                     model   own_rho  own_ci_lo  own_ci_hi  own_p_boot   pub_rho  pub_ci_lo  pub_ci_hi  pub_p_boot
     REF_delta_ESM_our_run -0.088118  -0.117333  -0.059511      0.0000 -0.070705  -0.097972  -0.043840      0.0000
         xTrimoPGLM-7B-CLM -0.003085  -0.028153   0.021164      0.8042 -0.008465  -0.031990   0.014762      0.4840
                  ProtGPT2  0.000660  -0.026063   0.027290      0.9680  0.001187  -0.023504   0.025962      0.9334
                    VESPAl  0.016658  -0.014466   0.048038      0.2888  0.016861  -0.010928   0.045129      0.2424
                 CARP_600K  0.020578  -0.005329   0.047431      0.1188  0.016904  -0.007515   0.042161      0.1762
         xTrimoPGLM-3B-CLM  0.023231  -0.005667   0.051879      0.1128  0.022697  -0.004123   0.049365      0.0964
                    RITA_m  0.026164  -0.002048   0.054411      0.0692  0.030092   0.002996   0.056502      0.0262
                    RITA_l  0.026328   0.000038   0.053460      0.0498  0.029838   0.004566   0.055927      0.0220
                     VESPA  0.029222  -0.001020   0.059639      0.0596  0.029421   0.001872   0.057242      0.0344
         xTrimoPGLM-1B-CLM  0.030084   0.001578   0.058515      0.0398  0.027702   0.001076   0.054260      0.0412
                Progen3_1b  0.032046   0.004443   0.060219      0.0248  0.033127   0.006865   0.059324      0.0130
Tranception_L_no_retrieval  0.032382   0.006481   0.058612      0.0156  0.033471   0.008788   0.058892      0.0096
                   RITA_xl  0.034765   0.008947   0.060539      0.0070  0.032549   0.007547   0.057384      0.0086
                Progen3_3b  0.035902   0.008828   0.062721      0.0078  0.032193   0.006598   0.057584      0.0130
              Progen2_base  0.037105   0.010282   0.064004      0.0054  0.035974   0.010402   0.061458      0.0054
      xTrimoPGLM-100B-int4  0.042628   0.015661   0.069819      0.0022  0.031028   0.005504   0.056987      0.0170
                   ESM2_8M  0.046711   0.021072   0.072079      0.0008  0.038253   0.014229   0.062495      0.0026
                    Unirep  0.047706   0.021215   0.074267      0.0006  0.037549   0.012703   0.062612      0.0028
                  ESM2_15B  0.047733   0.022209   0.073891      0.0000  0.045438   0.021116   0.070245      0.0000
            Progen2_medium  0.047990   0.020346   0.076209      0.0004  0.044653   0.018568   0.071110      0.0008
               ProteinMPNN  0.048729   0.028080   0.068731      0.0000  0.038166   0.018298   0.057683      0.0002
         xTrimoPGLM-3B-MLM  0.050396   0.025137   0.076017      0.0000  0.042179   0.018019   0.067182      0.0012
              Progen3_762m  0.052598   0.024416   0.080522      0.0002  0.047489   0.020885   0.073912      0.0008
                   ESM2_3B  0.054520   0.028451   0.081022      0.0000  0.048149   0.023462   0.072697      0.0002
        xTrimoPGLM-10B-MLM  0.055082   0.029781   0.080809      0.0000  0.047380   0.023103   0.072200      0.0002
             Tranception_L  0.055365   0.029627   0.081329      0.0000  0.050060   0.025368   0.074953      0.0002
             Progen2_large  0.056800   0.028477   0.084844      0.0000  0.052751   0.026038   0.079285      0.0000
                   Wavenet  0.057514   0.031187   0.084059      0.0000  0.046473   0.021290   0.071552      0.0002
            Progen2_xlarge  0.058688   0.032748   0.084110      0.0000  0.050773   0.025713   0.075298      0.0000
            Unirep_evotune  0.058791   0.030802   0.087011      0.0000  0.057060   0.030810   0.083531      0.0000
          Site_Independent  0.063966   0.037646   0.090564      0.0000  0.051579   0.026642   0.076736      0.0004
                    SiteRM  0.064323   0.037106   0.092400      0.0000  0.053038   0.026972   0.079496      0.0002
    MSA_Transformer_single  0.066429   0.041856   0.092411      0.0000  0.063738   0.040023   0.088399      0.0000
             TranceptEVE_L  0.066924   0.040054   0.093981      0.0000  0.057803   0.032298   0.083545      0.0000
              ESM1v_single  0.067808   0.040928   0.095568      0.0000  0.061313   0.036126   0.087597      0.0000
  MSA_Transformer_ensemble  0.067901   0.042889   0.094260      0.0000  0.064131   0.039826   0.089115      0.0000
       DeepSequence_single  0.071365   0.043485   0.099591      0.0000  0.057917   0.031256   0.084559      0.0000
                    VespaG  0.071511   0.044913   0.098240      0.0000  0.061668   0.036566   0.087100      0.0000
                 ProSST-20  0.071634   0.043774   0.098267      0.0000  0.058052   0.032607   0.082595      0.0000
                EVE_single  0.072827   0.046035   0.099933      0.0000  0.059516   0.033798   0.085401      0.0002
         ProtSSN_k10_h1280  0.073303   0.045283   0.101964      0.0000  0.059878   0.033078   0.087196      0.0000
Tranception_M_no_retrieval  0.074483   0.048187   0.100767      0.0000  0.064165   0.039238   0.089330      0.0000
              EVE_ensemble  0.074602   0.046911   0.102542      0.0000  0.061734   0.035419   0.088246      0.0000
          ProtSSN_k20_h512  0.075102   0.046804   0.104172      0.0000  0.059826   0.032589   0.087392      0.0000
                  CARP_38M  0.075566   0.048940   0.102034      0.0000  0.058116   0.033617   0.082822      0.0000
                     GEMME  0.075770   0.049144   0.102862      0.0000  0.064798   0.039784   0.090454      0.0000
               ProSST-4096  0.075958   0.050064   0.100812      0.0000  0.062682   0.038845   0.085910      0.0000
     DeepSequence_ensemble  0.076136   0.048423   0.103985      0.0000  0.062785   0.036373   0.089292      0.0000
                ProSST-128  0.076333   0.050432   0.101774      0.0000  0.064912   0.040424   0.088894      0.0000
                ProSST-512  0.076500   0.050390   0.101423      0.0000  0.062943   0.038670   0.086781      0.0000
                EVmutation  0.076539   0.050796   0.102662      0.0000  0.062452   0.037669   0.087566      0.0000
         ProtSSN_k20_h1280  0.076840   0.049226   0.104979      0.0000  0.061162   0.034812   0.088043      0.0000
            ESM1v_ensemble  0.076873   0.050369   0.104075      0.0000  0.068169   0.042615   0.094119      0.0000
                 ESMC-600M  0.079918   0.052049   0.107856      0.0000  0.069010   0.042709   0.095377      0.0000
             TranceptEVE_M  0.080040   0.052951   0.106663      0.0000  0.067007   0.041706   0.092726      0.0000
             Tranception_M  0.080256   0.054466   0.106245      0.0000  0.067522   0.043202   0.092284      0.0000
               ProSST-1024  0.080384   0.054704   0.105695      0.0000  0.064873   0.040544   0.088630      0.0000
                      PoET  0.081023   0.054720   0.107527      0.0000  0.067101   0.042077   0.092463      0.0000
                    RSALOR  0.081112   0.052183   0.109504      0.0000  0.067749   0.040168   0.094901      0.0000
                    ESCOTT  0.082567   0.055555   0.109674      0.0000  0.073542   0.047891   0.099602      0.0000
          ProtSSN_k10_h768  0.082626   0.054960   0.110767      0.0000  0.069863   0.043933   0.096773      0.0000
          ProtSSN_k20_h768  0.082907   0.055217   0.110967      0.0000  0.068699   0.042138   0.095789      0.0000
          ProtSSN_k10_h512  0.083076   0.054798   0.111509      0.0000  0.069266   0.042636   0.096094      0.0000
               ProSST-2048  0.084017   0.056807   0.110805      0.0000  0.065962   0.040240   0.091048      0.0000
          ProtSSN_ensemble  0.085229   0.057617   0.113436      0.0000  0.069699   0.043265   0.096997      0.0000
                 ESM2_650M  0.085391   0.058861   0.112294      0.0000  0.069895   0.044525   0.095681      0.0000
          ProtSSN_k30_h768  0.085757   0.058184   0.114021      0.0000  0.069304   0.042994   0.096327      0.0000
                   S3F_MSA  0.087055   0.060340   0.114172      0.0000  0.072645   0.046855   0.098694      0.0000
                  VenusREM  0.087454   0.060177   0.114708      0.0000  0.069567   0.043597   0.095714      0.0000
                   S2F_MSA  0.088481   0.061553   0.115244      0.0000  0.074438   0.048956   0.100122      0.0000
                       S3F  0.088769   0.061412   0.115850      0.0000  0.074181   0.048457   0.100526      0.0000
                       S2F  0.090411   0.064225   0.116945      0.0000  0.076535   0.051456   0.102066      0.0000
          ProtSSN_k30_h512  0.090596   0.063330   0.118454      0.0000  0.073083   0.047165   0.099741      0.0000
                       MIF  0.091707   0.064921   0.117912      0.0000  0.075151   0.049398   0.100633      0.0000
               MULAN_small  0.094248   0.067291   0.121284      0.0000  0.079928   0.054991   0.105109      0.0000
                     ESM1b  0.094641   0.068753   0.120669      0.0000  0.078431   0.053499   0.103759      0.0000
         ProtSSN_k30_h1280  0.095003   0.068495   0.122920      0.0000  0.077958   0.051965   0.104818      0.0000
           SaProt_650M_AF2  0.096433   0.069116   0.124173      0.0000  0.084766   0.058743   0.111540      0.0000
                 CARP_640M  0.098566   0.071996   0.124878      0.0000  0.075254   0.049877   0.100576      0.0000
             TranceptEVE_S  0.105430   0.080078   0.130994      0.0000  0.085482   0.060788   0.109899      0.0000
                     MIFST  0.107277   0.080757   0.133993      0.0000  0.085269   0.058798   0.111275      0.0000
              Progen3_339m  0.113636   0.088629   0.138816      0.0000  0.089904   0.065686   0.114512      0.0000
             Tranception_S  0.114348   0.090499   0.137646      0.0000  0.090148   0.066829   0.113031      0.0000
            SaProt_35M_AF2  0.116969   0.090820   0.142105      0.0000  0.095712   0.071481   0.119120      0.0000
                   ESM-IF1  0.117750   0.090414   0.144345      0.0000  0.096178   0.069638   0.122042      0.0000
             Progen2_small  0.122719   0.097223   0.148501      0.0000  0.092231   0.067954   0.116725      0.0000
         xTrimoPGLM-1B-MLM  0.128326   0.102215   0.154680      0.0000  0.097637   0.072378   0.123044      0.0000
                  CARP_76M  0.128340   0.103200   0.153300      0.0000  0.101457   0.077867   0.125356      0.0000
                  ESM2_35M  0.129356   0.104098   0.154541      0.0000  0.103943   0.080146   0.127760      0.0000
              Progen3_112m  0.132184   0.106987   0.156991      0.0000  0.101271   0.077022   0.125252      0.0000
              Progen3_219m  0.135300   0.110691   0.159844      0.0000  0.102709   0.079057   0.126595      0.0000
                    RITA_s  0.139547   0.115259   0.163582      0.0000  0.107562   0.084119   0.130648      0.0000
Tranception_S_no_retrieval  0.142166   0.118137   0.166279      0.0000  0.105874   0.082667   0.129117      0.0000
                      ESM3  0.147204   0.121557   0.172141      0.0000  0.123481   0.098696   0.147649      0.0000
                 ESMC-300M  0.153130   0.127339   0.178552      0.0000  0.122173   0.097418   0.146577      0.0000
                 ESM2_150M  0.162231   0.137511   0.186473      0.0000  0.128456   0.104719   0.152125      0.0000

top 5 / bottom 5 by own_rho:
                model   own_rho  own_ci_lo  own_ci_hi
REF_delta_ESM_our_run -0.088118  -0.117333  -0.059511
    xTrimoPGLM-7B-CLM -0.003085  -0.028153   0.021164
             ProtGPT2  0.000660  -0.026063   0.027290
               VESPAl  0.016658  -0.014466   0.048038
            CARP_600K  0.020578  -0.005329   0.047431
                     model  own_rho  own_ci_lo  own_ci_hi
                    RITA_s 0.139547   0.115259   0.163582
Tranception_S_no_retrieval 0.142166   0.118137   0.166279
                      ESM3 0.147204   0.121557   0.172141
                 ESMC-300M 0.153130   0.127339   0.178552
                 ESM2_150M 0.162231   0.137511   0.186473
  REF_delta_ESM_our_run      own_rho=-0.088118 CI=[-0.1173,-0.0595] p=<0.00010 | pub_rho=-0.070705
  ESM2_650M                  own_rho=+0.085391 CI=[+0.0589,+0.1123] p=<0.00010 | pub_rho=+0.069895
  ESM2_150M                  own_rho=+0.162231 CI=[+0.1375,+0.1865] p=<0.00010 | pub_rho=+0.128456
  ESM1v_single               own_rho=+0.067808 CI=[+0.0409,+0.0956] p=<0.00010 | pub_rho=+0.061313
  ESM1v_ensemble             own_rho=+0.076873 CI=[+0.0504,+0.1041] p=<0.00010 | pub_rho=+0.068169
  EVmutation                 own_rho=+0.076539 CI=[+0.0508,+0.1027] p=<0.00010 | pub_rho=+0.062452
  Site_Independent           own_rho=+0.063966 CI=[+0.0376,+0.0906] p=<0.00010 | pub_rho=+0.051579
  EVE_ensemble               own_rho=+0.074602 CI=[+0.0469,+0.1025] p=<0.00010 | pub_rho=+0.061734
  GEMME                      own_rho=+0.075770 CI=[+0.0491,+0.1029] p=<0.00010 | pub_rho=+0.064798
  MSA_Transformer_ensemble   own_rho=+0.067901 CI=[+0.0429,+0.0943] p=<0.00010 | pub_rho=+0.064131
  DeepSequence_ensemble      own_rho=+0.076136 CI=[+0.0484,+0.1040] p=<0.00010 | pub_rho=+0.062785

AB2 column facts: ESM-1v columns present = ['ESM1v_single', 'ESM1v_ensemble'] (TWO aggregates, not five seeds -> AB2b/AC4 cross-ref); EVmutation column present = True (AB2c/T cross-ref)

LIMITATIONS (R5): aggregate columns are not seeds; rows share one e.b vector and are not independent of each other; descriptive table, no multiple-comparison claim; reproducing script 32's anchor row validates this pipeline against script 32 (reproduction, not replication).
total runtime 692.1s
```

Output CSV verification:
```text
      97 data/processed/task_AB2_proteingym_model_comparison.csv
model,own_rho,own_ci_lo,own_ci_hi,own_p_boot,own_n,own_n_positions,pub_rho,pub_ci_lo,pub_ci_hi,pub_p_boot,pub_n,pub_n_positions
REF_delta_ESM_our_run,-0.08811806424891734,-0.11733344589533189,-0.059511384495117385,0.0,10757,654,-0.07070516222228716,-0.0979720380194354,-0.043839529991425104,0.0,10757,654
REF_delta_ESM_our_run,-0.08811806424891734,-0.11733344589533189,-0.059511384495117385,0.0,10757,654,-0.07070516222228716,-0.0979720380194354,-0.043839529991425104,0.0,10757,654
ESM1v_single,0.06780795371221343,0.040927862239273215,0.09556753765567869,0.0,10757,654,0.06131258548847305,0.036125562878152724,0.0875973527181565,0.0,10757,654
EVmutation,0.0765388135872782,0.050795716426816996,0.10266187118174226,0.0,10757,654,0.06245180123067018,0.03766876451981932,0.0875663102835194,0.0,10757,654
ESM1v_ensemble,0.07687349800315775,0.050368876851309294,0.104075077314902,0.0,10757,654,0.06816858731502308,0.04261463673239216,0.09411920305202258,0.0,10757,654
ESM2_650M,0.0853911031053886,0.058861369894065874,0.11229396305341609,0.0,10757,654,0.069895293733652,0.04452527472090113,0.09568061701980234,0.0,10757,654
ESM2_150M,0.16223117588303074,0.13751059376527455,0.1864730155632388,0.0,10757,654,0.1284562479851809,0.10471893839293045,0.152125220515805,0.0,10757,654
```

Verdict: PASS — AB2a's deliverable exists with every pre-registered
gate green at full N. Two things [AB2] left open are now closed:
(1) the gate row: fixed by user authorization, mechanism untouched,
disclosed in script output and docstring; (2) [AB2] flag 2's warning
that the shared-draw engine was UNVALIDATED: it is now validated —
G-anchor reproduces the frozen -0.08811806424891734 with |diff| =
0.000e+00 and G-lib matches three independent lib reruns to
1.388e-17 at N_BOOT=10000 (reproduction of script 32's row = pipeline
unit test, not replication, per §6). Descriptive headline of the full
table, reported as-is: the REF delta_ESM row (own -0.088118,
CI [-0.117333, -0.059511], p < 1/10000) is the only row whose CI
excludes zero on the negative side; all 95 ProteinGym model columns
correlate POSITIVELY with own e_b (ESM2_650M +0.0854,
ESM2_150M +0.1622, ESM1v_single +0.0678, ESM1v_ensemble +0.0769,
EVmutation +0.0765; the one non-positive model, xTrimoPGLM-7B-CLM
-0.0031, is null, p = 0.8042). Orientation caution per the script's
own docstring: those columns are raw single-mutation severity scores
while REF is the two-background epistatic delta — different
quantities, so the sign difference is descriptive, not a contradiction.
The REF CI matches task67's rerun CI to float precision, consistent
with the shared seed=0 draw sequence (same draws, not an independent
confirmation). Smoke numbers remain machinery-only per the script's
own banner.

Files: CLOSEOUT_LOG.md (this entry). scripts/71_proteingym_model_
comparison.py — MODIFIED under the explicit user authorization (7
edits total across two patches: 4 anchor/provenance + 3 orientation;
every edit disclosed in the script's printed output and docstring;
the file had been left untouched since its tree-#2 stop, as recorded
in [AB2]). Outputs: data/processed/task_AB2_proteingym_model_
comparison.csv (the deliverable) and ..._smoke.csv. Session-tmp logs:
ab2a_smoke.log, ab2a_smoke2.log, ab2a_full.log. No other repo files
touched; no commits.

Unexpected: (1) The engine's first-ever execution crashed — a latent
bug exactly where [AB2] flag 2 said the unvalidated code was; fixed to
the frozen docstring and disclosed, not papered over. (2) The md5
provenance slip (an MSA's hash written against the scores file) was
found by pre-run reconciliation and explained, not left dangling. (3)
AB1 measured only A222V, so the swap needed a fresh independent
measurement — the selection rule and method were stated before any
value was read. (4) The full table's uniform positive-sign structure
vs the negative REF is the table's most striking descriptive feature;
flagged with the orientation caution rather than interpreted as a
finding. (5) Actual time ~18 min against the 30-min budget.
---

## [Z3f] — Score all resolvable positions, WT and A222V background (SaProt STAGE=score) — EXECUTED — PASS (rc=0, never capped; 585s on MPS)

Status: EXECUTED — PASS for this task's own scope (score stage + its
exclusion-accounting reports). The score-stage deliverable exists on disk
and every gate that stage runs was True. The separate stats stage
(Z3g/Z3h) is BLOCKED at a later guard — logged as [Z3g-h] immediately
after this entry; Z3f's verdict does not depend on it.

Time: smoke re-verified 2026-09-25 15:33 (exit 0); launched 15:36:26
(detached supervisor pid=60088, sid=60088; child pid=60090); child exit
15:46:13 — rc=0 after 587s, score stage wall-clock 585s on device=mps.
First health poll 16:04:25 (job already finished). Entry appended ~16:45.
Cap 21600s backstop: ~2.7% used.

What I did:
- Re-ran SMOKE=1 STAGE=all before the full run (exit 0, 14s). All
  registered gates True at smoke: G1 get_struc_seq == Z3c tokens True;
  G2 AA blocks consecutive True; G3 batched-vs-single max|diff|=2.00e-05
  (limit 1e-3) True; G4 self-logodds 0.0 True; G5 zero variants at
  position 222 True; G6 script-33 ±1 identity checks max|diff|=9.714e-17
  (both directions); G7 the frozen 59 unresolved positions == the frozen
  set, phase5 1,046 MATCH. Smoke numbers were carried nowhere (§1).
- Mandatory pre-launch heavy-job check: NONE running. Session-detached
  supervisor reused the proven z2c/z3f pattern (setsid own session so it
  survives harness turn-end; merged log writer outlives the launching
  shell; mechanical cap via SIGTERM→SIGKILL — no timeout/gtimeout binary
  exists here).
- Disclosures stamped into the status file BEFORE launch: no
  pre-registered cap exists for Z3f → 21600s is a backstop only
  (≥12.7× the smoke-measured CPU extrapolation 80 rows/14s → ~1705s for
  9740 rows; MPS rate explicitly disclosed unmeasured, not asserted);
  stall detection = this session's 30–45 min polls, not the cap;
  cap-kill = BUDGET STOP (partial, not negative, no retry without user
  decision); PYTHONUNBUFFERED=1 child env + progress stamps widened to
  any '['-prefixed line (script 70 prints "(Ns elapsed)", not "t=");
  no checkpoint → any kill would lose the stage.
- Ran STAGE=score only; watched via the status file; never touched,
  never killed.

Actual output:

From tmp z3f_score.log (verbatim):
```text
script 70 | STAGE=score SMOKE=False N_BOOT=10000 N_PERM=10000 SEED=0 BATCH=16
device=mps
[score] chain-A fused length 596 residues 40..651
[G1] their get_struc_seq == Z3c tokens: True
[G2] AA blocks consecutive from aa+struc[0]: True
[bg] A222V swaps fused token Ah -> Vh at index 171; all other 595 tokens identical (frozen structure)
[G3] batched vs single forward, max|diff| = 0.00e+00 (limit 1e-3): True
[G4] self-logodds at fused pos 1 (residue 40, E) = 0.0: True
[score] wt background done (278s elapsed)
[score] av background done (579s elapsed)
[score] saved /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task_Z3f_saprot_scores.csv (11940 rows = 596 positions x 20 alts; smoke-limited=False)
[score] stage wall-clock 585s on device=mps
[total] 585s
*** Z3f score run FINISHED rc=0 after 587s ***
```
(The red "contact_head weights not initialized" line in the log is
fair-esm's normal ESM-2 contact-head message — present in the smoke and
in script 10's historical runs too; LM weights load. Cosmetic.)

Deliverable on disk: data/processed/task_Z3f_saprot_scores.csv —
537,084 bytes, mtime 2026-09-25 15:46, 11,941 lines = header + 11,940
rows (596 positions × 20 alts; 20 = 19 substitutions + the self
alternative G4 checks):
```csv
res_num,ori_aa,mut_aa,av_logodds,wt_logodds
40,E,A,0.8166425228118896,0.7831742763519287
40,E,C,-1.680105209350586,-1.7233279943466187
```

Exclusion accounting (this task's text: exact excluded count + compare to
V2's 1,046). These lines print during STAGE=stats; today's stats run
printed them (all True/MATCH) before failing at a later guard, so they
are quoted from tmp z3g_stats_status.txt, not re-derived:
```text
[G5] variants at position 222 in analysis set: 0 (expect 0): True
[G7] unresolved atlas positions: 59 == 59 and == 2-39/161-171/392-396/652-656: True
[G7] phase5 base (n=11344) rows at those positions: 1046 (V2's own figure: 1,046) -> MATCH
[G7] task_V2 rows present at those positions: 0 (expect 0: V2 dropped them at construction -- structure-based scoring cannot cover unresolved residues)
[Z3f] analysis set 10757 -> excluded at 59 unresolved positions: 1017 rows; scored set 9740 (595 positions)
[Z3f] reconciliation vs V2's 1,046: that figure = phase5 rows at the same 59 positions (measured here: 1046); ours (1017) = the subset of those inside script 32's pre-registered 10,757-row set after delta_esm/own_e_b filtering (29 of the 1,046 are not in it); task_V2 itself holds 0 unresolved rows -- dropped at its construction. Same 59 positions, three bases, all consistent.
[Z3f] scored set vs ThermoMPNN's coverage: ours 9740 vs task_V2 10141 rows (9595 with own_e_b) -- bases differ by design (script 32 = ESM-2+e.b filters; V2 = ddG+structure filters), so an exact match is NOT expected and is not asserted.
```

Verdict:
- PASS: all resolvable chain-A positions (596 fused residues, 40..651)
  scored on both backgrounds; every registered gate True; row accounting
  11,940 = 596×20 exact; exclusion set = the frozen 59 positions with
  the exact counts the task asks for (1,017 of 10,757 rows excluded;
  phase5-absolute 1,046 MATCHES V2's figure on the same positions);
  scored-vs-V2 coverage reconciled on bases that differ by design.
- Disclosed cosmetic deviation: the supervisor stamped
  "SUPERVISOR ERROR: SystemExit(0)" AFTER "SUPERVISOR done rc=0
  capped=False" — my z3f supervisor's BaseException handler caught the
  clean sys.exit(0) and mislabeled it. Cosmetic only (rc=0,
  capped=False, file written, gates True); same class as [Z2c]'s
  disclosed rc=-15 labels; tonight's generic supervisor treats
  SystemExit(0) as clean (disclosed in its header).
- No pre-registered rule changed, no number re-derived, no script
  edited for this run.

Files: data/processed/task_Z3f_saprot_scores.csv (deliverable).
Session-tmp evidence: z3f_score.log, z3f_status.txt, z3f_smoke.log,
z3f_supervisor.py. Read-only inputs: scripts/70_saprot_delta_epistasis.py,
task doc spec L160-167. No scripts modified; no commits.

Unexpected: (1) Runtime 585s vs my ~1705s CPU-based projection — MPS ran
~3× faster than the CPU extrapolation; reported as an observation only
(rate was disclosed unmeasured beforehand; no claim is built on it).
(2) The "SystemExit(0) ERROR" cosmetic stamp, described above. (3) Later,
during the stats stage's diagnosis, it emerged that 145 of the 9,740
analysis rows sit at 9 positions where 6FCX's residues differ from the
reference (SEQADV: 2 engineered variants + a 7-residue expression tag at
645-651) — Z3f's own gates are structure-token integrity checks and were
True by design; reference-identity is checked only in stats, where it
halted the run. Fully documented in [Z3g-h], next entry.
---

## [Z3g-h] — SaProt delta statistic + nulls (STAGE=stats) — BLOCKED at a script-70 guard: structure-vs-reference identity fails at 9 positions (145 rows). Open decision for the user; no script edited, no result computed

Status: BLOCKED — open decision required (§10). Z3g (delta_SaProt vs
e.b. with position-cluster bootstrap + the script-33 sign-flip/position-
block nulls) and Z3h (regional split) never ran: the stats stage exited
at a guard 2 seconds in, before any null or rho was computed. **No
SaProt epistasis result exists yet — this is neither a positive nor a
negative finding about the hypothesis; it is an unrun analysis.** Both
coherent ways forward change frozen script 70's decision rules, which
§10 reserves for the user. Z3i is parked behind this (see below).

Time: launched 16:09:24 (generic supervisor pid=61302, child pid=61305,
cap 14400s backstop — never approached); child exit 16:09:26, rc=1 after
2s — the guard's own sys.exit(1), i.e. an intended stop, NOT an
infrastructure death (no retry attempted, per §10: a failed sanity check
is not something to relaunch). Diagnosis 16:10–16:45, read-only.
Entry appended ~16:55.

What I did:
- Launched STAGE=stats (re-reads task_Z3f_saprot_scores.csv; loads no
  model) through the generic supervisor, cap/disclosed estimate in its
  status file: mechanism-level ~15–40 min (smoke 0s at n=74/300 draws +
  10k position-block/sign-flip rho re-derivations + 4 regional
  bootstraps), backstop >6× that, cap-kill = BUDGET STOP.
- Everything printed before the guard was green (verbatim from tmp
  z3g_stats_status.txt):
```text
[G5] variants at position 222 in analysis set: 0 (expect 0): True
[G7] unresolved atlas positions: 59 == 59 and == 2-39/161-171/392-396/652-656: True
[G7] phase5 base (n=11344) rows at those positions: 1046 (V2's own figure: 1,046) -> MATCH
[G7] task_V2 rows present at those positions: 0 (expect 0: V2 dropped them at construction -- structure-based scoring cannot cover unresolved residues)
[Z3f] analysis set 10757 -> excluded at 59 unresolved positions: 1017 rows; scored set 9740 (595 positions)
[Z3f] reconciliation vs V2's 1,046: that figure = phase5 rows at the same 59 positions (measured here: 1046); ours (1017) = the subset of those inside script 32's pre-registered 10,757-row set after delta_esm/own_e_b filtering (29 of the 1,046 are not in it); task_V2 itself holds 0 unresolved rows -- dropped at its construction. Same 59 positions, three bases, all consistent.
[Z3f] scored set vs ThermoMPNN's coverage: ours 9740 vs task_V2 10141 rows (9595 with own_e_b) -- bases differ by design (script 32 = ESM-2+e.b filters; V2 = ddG+structure filters), so an exact match is NOT expected and is not asserted.
[Z3f] wt_aa agrees with chain-A ori_aa on all scored rows: False (9595/9740)
child exited rc=1 after 2s
```
  and the guard's own stop line (z3g_stats.log): `wt_aa/ori_aa identity
  FAILED. Stop.` — script 70 L313-316:
```python
    print(f"[Z3f] wt_aa agrees with chain-A ori_aa on all scored rows: "
          f"{wt_ok == len(df)} ({wt_ok}/{len(df)})")
    if wt_ok != len(df):
        print("wt_aa/ori_aa identity FAILED. Stop.")
        sys.exit(1)
```
- Diagnosed READ-ONLY (no re-run, no edit). (i) The 145 disagreeing
  rows sit at exactly 9 positions — verbatim diagnosis output:
```text
MISMATCH rows: 145 positions: [429, 594, 645, 646, 647, 648, 649, 650, 651]
per-position detail (position, table_wt, fasta, ori6FCX, n_rows):
  pos 429: table_wt=E fasta=E ori=A n_rows=19
  pos 594: table_wt=R fasta=R ori=Q n_rows=19
  pos 645: table_wt=R fasta=R ori=A n_rows=15
  pos 646: table_wt=P fasta=P ori=E n_rows=14
  pos 647: table_wt=T fasta=T ori=N n_rows=16
  pos 648: table_wt=Q fasta=Q ori=L n_rows=18
  pos 649: table_wt=N fasta=N ori=Y n_rows=10
  pos 650: table_wt=A fasta=A ori=F n_rows=19
  pos 651: table_wt=R fasta=R ori=Q n_rows=15
table wt_aa == fasta everywhere?: True
```
  → the atlas labels are CORRECT on every row; this is not a labeling or
  alignment bug (a bug would not spare 586 of 595 positions while
  leaving labels identical to the FASTA).
  (ii) The structure's own file explains all 9, per-residue provenance
  (verbatim grep of data/raw/6FCX.pdb; trailing whitespace trimmed;
  chain B carries the identical set, and the M37/L37 initiator line
  falls outside the scored span 40..651):
```text
DBREF  6FCX A   37   644  UNP    P42898   MTHR_HUMAN      37    644
SEQADV 6FCX MET A   37  UNP  P42898    LEU    37 INITIATING METHIONINE
SEQADV 6FCX ALA A  429  UNP  P42898    GLU   429 VARIANT
SEQADV 6FCX GLN A  594  UNP  P42898    ARG   594 VARIANT
SEQADV 6FCX ALA A  645  UNP  P42898              EXPRESSION TAG
SEQADV 6FCX GLU A  646  UNP  P42898              EXPRESSION TAG
SEQADV 6FCX ASN A  647  UNP  P42898              EXPRESSION TAG
SEQADV 6FCX LEU A  648  UNP  P42898              EXPRESSION TAG
SEQADV 6FCX TYR A  649  UNP  P42898              EXPRESSION TAG
SEQADV 6FCX PHE A  650  UNP  P42898              EXPRESSION TAG
SEQADV 6FCX GLN A  651  UNP  P42898              EXPRESSION TAG
```
  The chain's MTHFR span ENDS at 644 (DBREF 37-644); residues 645-651
  are an expression tag (letters AENLYFQ — a TEV-site-like remnant)
  numbered contiguously, coincidentally overlapping where reference
  645-651 would sit. Chain arithmetic checks out: 40..644 reference span
  (605) − unresolved-in-span {161-171, 392-396} (16) = 589 reference
  residues + 7 tag = 596 fused ✓ matches the score stage's "fused length
  596".
  (iii) Guard classification: this check is NOT one of the registered
  G1-G7 gates — no [G#] label, not in script 70's docstring gate list
  (grep: "wt_aa"/"ori" appears only at code lines 299/313) — it is a
  script-internal guard whose premise (every scored row's reference
  residue sits at that number in the structure) is false for 6FCX. Its
  FIRST full-scale exposure was today: the smoke passed it
  `True (74/74)` because smoke samples only residues 40-43, which all
  agree.
  (iv) What the 145 rows would mean if kept: at 429/594 the structure
  holds the correct SITE with an engineered side chain (38 rows); at
  645-651 the model's context is not MTHFR at all (107 rows). The
  statistic's subtraction (av − wt per row) cancels the shared
  −logP(ori) term, but the surrounding context is non-reference either
  way — so the rows are questionable as MTHFR-context measurements.
  (v) In-repo precedent found during diagnosis: the FROZEN
  task_V2_thermompnn_ddg.csv has ZERO rows at the same 9 sites; its
  position range ends at exactly 644; within 40..644 its missing
  positions are exactly {161-171, 392-396} ∪ {222} ∪ {429, 594}. That
  pattern is fully consistent with a "structure residue must equal the
  reference residue" construction discipline — mechanism inferred from
  the position pattern, NOT verified in V2's construction code (marked
  inference; the zero-rows fact itself is verified).
- Why BLOCKED rather than fixed (§10 + the Sep-25 prompt's tree: fix
  only for a clear code-vs-spec bug; this is not one — the code
  faithfully implements its stated guard, and the guard's premise is
  factually false for 6FCX): both coherent options change frozen
  script 70's decision rules, i.e. a pre-registered-population or
  stopping-rule change:
  **Option A — keep n=9,740 / 595 positions.** Replace the all-rows
  guard with an integrity check that tests what it was designed to test
  (labels-vs-FASTA: passes; structure tokens vs Z3c/G1: passes) plus a
  documented SEQADV exception for the known 9. Accepts keeping 107
  tag-context + 38 variant-site rows in the analysis.
  **Option B — exclude the 9 positions → n=9,595 / 586 positions.**
  Extend decision 2's settled exclusion policy ("the structure cannot
  represent the position → exclude rather than impute") to the SEQADV
  positions; requires editing script 70's exclusion list AND its guard,
  and changes the scored-set n that Z3f's task text commits to report.
  Neither was done. Logged as an open decision instead.
- Recommendation (stated, NOT acted): Option B as primary — residues
  645-651 are not MTHFR by the PDB's own DBREF, decision 2's policy
  logic extends to them directly, and the frozen V2 pipeline already
  excludes all 9 — with Option A reported alongside as the sensitivity
  (one extra bootstrap pair; trivial once authorized). The user decides.
- Z3i parked: U5's summary is append-only; appending a SaProt row
  without Z3g outputs would be empty or later-contradicted, so the
  append waits for this decision. (U5's stale row 2 remains untouched,
  per the standing do-not-edit note.)

Actual output: the status/log/diagnosis/PDB excerpts quoted verbatim
above. Nothing else was run.

Verdict: BLOCKED with a fully diagnosed, unambiguous cause (per-residue
PDB provenance for all 9 positions) awaiting one user decision — A
(keep, guard relaxed with documented exception) or B (exclude 9
positions, n=9,595, guard exception added, sensitivity vs A reported).
No claim about SaProt's delta epistasis statistic is made in either
direction; no script, threshold, or population was changed by me.

Files: CLOSEOUT_LOG.md (this entry). Read-only: scripts/70
(lines 294-316 quoted), data/raw/6FCX.pdb (SEQADV/DBREF),
data/processed/{task_Z3f_saprot_scores.csv, task32_analysis_table.csv,
task_V2_thermompnn_ddg.csv}, data/raw/P42898.fasta, tmp
z3g_stats_status.txt + z3g_stats.log. No files written besides this
entry; no scripts touched.

Unexpected: (1) The guard's first full-scale run failed on real
construct biology (engineered variants + expression tag), not on a code
bug — the smoke's `True (74/74)` could never have caught it (4 adjacent
residues sampled). (2) The frozen V2 pipeline turns out to have already
dropped exactly these 9 sites — a precedent for Option B that nobody
recorded in the task docs (found only by querying its position set).
(3) The failure breaks the chain to Z3i as well, so the Z3 track stops
here pending the decision. (4) The supervisor machinery itself behaved
exactly as designed (rc=1 in 2s = the guard's intended exit; no
infra-death, no retry, no cap involvement) — noted so the BLOCKED
status is not misread as an infrastructure failure.
---

## [AC4] — ESM-1v across all five pretrained members (deepdive [AC4a-d]: fetch-score-delete each, size gate, ensemble diagnostic, does the delta–e.b association survive seed?) — EXECUTED — AC4d VERDICT: SEED-NOISE BRANCH

Status: EXECUTED — complete, every gate PASS, all deliverables on disk.
The pre-registered AC4d decision rule fired the SEED-NOISE branch: the
five members' delta-vs-own-e.b correlations scatter across zero (mixed
signs, 1/5 CIs excluding zero). Reported plainly (§0): this is a
negative result for the seed-robustness of the delta–e.b association —
the project working as intended, not a failure to find.

Time (all 2026-09-25): AC4a research 15:50–16:25; script 86 authored
16:00–16:29 with R1–R8 pre-registered in the docstring before any run;
parity attempt 1 16:30:29–16:32:23 (rc=1 — my code bug, below); parity
attempt 2 16:34:17–16:34:36 (rc=0, PASS); member-1 smoke 16:35:41
(exit 0, 105s); members 1–5 full 16:38:18 → 17:51:27 (all rc=0); summ
smoke 17:51:57 (exit 0, 5s at N_BOOT=300); full summ 17:53:58 →
17:56:26 (rc=0, 146s). Entry appended ~18:15. Every stage ran under
its own session-detached supervisor; no cap was ever approached (worst
member 876s of 5400s = 16%); zero infrastructure failures in this task
— nothing was killed, stalled, or retried.

What I did (chronological; full attempt history per §6):
- AC4a research (read-only): scripts 10/11 define the canonical
  masked-marginal procedure; lib/esm_scoring.get_position_logprobs is
  its implementation; A222V seq = wt[:221]+"V"+wt[222:]; loaders are
  esm.pretrained.esm1v_t33_650M_UR90S_{1..5}.
- THE WEIGHTS SAGA (disclosed decision): the canonical
  dl.fbaipublicfiles.com 7.83GB .pt is host-wide HTTP 403. Probe
  matrix at 16:09:25 and 16:16:43 (curl rc=56/403): root URL, the
  known-good esm2 file, HEAD, Range, browser UA, urllib — all 403 —
  while the host had served this project's downloads as recently as
  2026-09-24 10:28 (log: tmp ac4_fetch1.log). Re-probe ~16:52: still
  403. No byte-identical original-.pt mirror exists (Rocketknight1's
  HF copy is the same Transformers conversion). Decision: proceed via
  Meta's OFFICIAL HuggingFace org facebook/esm1v_t33_650M_UR90S_{1..5}
  (repo IDs discovered via the HF API, not guessed), fetching only
  pytorch_model.bin (2,609,603,341 B each, within the standing <3GB
  fetch cap), scoring through HuggingFace Transformers (installed into
  the venv this session: transformers 5.17.0, huggingface_hub 1.33.0;
  torch 2.14.0 / numpy 2.5.3 pre-existing). This changes the LOADER,
  not the math — procedure (per-position masked-marginal log-odds, one
  forward/position, WT+A222V backgrounds, scripts-10/11 positions,
  C−A subtraction) unchanged. Disclosed as a deviation-with-reason.
- Because direct ESM-1v parity against fair-esm is impossible while
  the canonical host 403s (disclosed limitation), R5 registered a
  THREE-WAY ESM-2-SIBLING parity gate instead: historical
  esm2_wt_scores.csv (a) vs fair-esm local get_position_logprobs (b)
  vs Transformers facebook/esm2_t33_650M_UR50D (c), both diffs <1e-3.
- Script 86 authored as the named deliverable (only new script this
  task; next-free number 86), saga + R1–R8 + limitations in the
  docstring before any run (§6/§7). Seven post-write fixes, all
  compile-checked and none touching a rule (malformed R6 f-string,
  R8 set_index assertion, wt_aa label assert in the join, device-probe
  ordering, regex {3} fidelity, dead lambda, docstring smoke wording).
- PARITY ATTEMPT 1 FAILED on a bug of mine: the size gate compared
  esm2's bin against EXPECTED_BIN, which I had probed from the esm1v
  repos — `PARITY fetch SIZE GATE FAIL: 2609621831 != 2609603341`,
  rc=1 after 114s. Verified esm2's true size via the HF API
  (2,609,621,831 B — the two files simply are not the same size),
  split the constants (EXPECTED_BIN esm1v / EXPECTED_BIN_ESM2), and
  disclosed bug + fix in the script's R2 text. Fixed before any
  scoring existed or was observed — a code correction, not a post-hoc
  analysis change (§0: no result had been seen).
- Member staging: one member's weights on disk at a time (session-tmp
  esm1v/member{k}) — fetch → size gate → md5 → AC4b → score → CSV →
  STAGED DELETE, verified after every member ("remaining staged dirs:
  none"). Member-1 smoke first because the member path had never
  executed; members 2–5 then ran the identical validated path with no
  per-member smoke (same code, different k — no rule change; stated so
  the choice is visible).
- JOIN PRE-FLIGHT (read-only, before summ): member-1 merged onto the
  10,757/654 base → 10,757 joined, 0 unmatched, wt_aa labels identical.
  The 2 NaN deltas in a member CSV are exactly position 222's two
  one-sided rows (V-row lacks av, A-row lacks wt — by construction of
  the two backgrounds; the base excludes 222 anyway).
- R8 §5 COLUMN-IDENTITY DUTY: summ smoke printed rho = 1.000000
  (6dp), which by AGENTS §5 is a suspected column duplication until
  proven otherwise. Verified at the VALUE level: |our 5-member mean wt
  − PG ESM1v_ensemble| median 2.97e-06, max 2.81e-05, only 9/10,757
  bit-identical (two independent pipelines agreeing to fp32 precision
  — a duplicated column would be identical everywhere); true Spearman
  0.9999999998 (the 6dp print rounds to 1.000000); plus a bonus
  identity check: PG's ESM1v_single matches OUR MEMBER 1 exactly
  (rho 1.000000; members 2–5: 0.873 / 0.887 / 0.890 / 0.875). R8's
  PASS is genuine — and this UPGRADES the "sibling-only parity"
  limitation: the Transformers-path ESM-1v scores themselves reproduce
  Meta's published values (via ProteinGym) to fp32 precision.

Actual output (verbatim).

R5 parity, attempt 2 (tmp ac4_parity_status.txt):
```text
[AC4] parity (a): historical esm2_wt_scores.csv rows at parity positions: 152
[AC4] parity (b): fair-esm get_position_logprobs rows: 152
[AC4] parity (c): Transformers rows: 152
[AC4] max|b-a| = 1.776e-15 at (np.int64(100), 'H') (tol 0.001)
[AC4] max|c-b| = 4.482e-05 at (np.int64(429), 'R') (tol 0.001)
[AC4] [G-AC4-PARITY] three-way parity (hist CSV / fair-esm / Transformers): PASS
[AC4] parity snapshot deleted; staged dirs now: none
[AC4] Note (disclosed): parity is fair-esm-vs-Transformers on the ESM-2 sibling; direct ESM-1v parity impossible while the canonical 7.83GB .pt 403s.
```
(a)–(c) each 152 rows = 8 parity positions × 19 alts. b−a = 1.8e-15 =
float round-trip noise — fair-esm re-derives the project's own
historical CSV essentially bit-for-bit (a unit test of consistency, not
independent evidence, §6).

AC4b + staging (identical across members; from member logs):
```text
[AC4] AC4b param count: 652,356,534 (652.4M)
[AC4] AC4b fp32 model bytes = 2,609,426,136; original .pt figure (Range probe) = 7,828,635,339; ratio = 3.0001
[AC4] AC4b VERIFIED (arithmetic): ratio ~3.00 -> original = model + Adam first moment + Adam second moment (3 fp32 copies) -- optimizer-state explanation CONFIRMED against both independently measured sizes; direct key inspection of the original .pt residual: NOT POSSIBLE while dl.fbaipublicfiles.com returns 403 (attempt history in docstring).
[AC4] size gate OK: 2,609,603,341 B == EXPECTED_BIN
```
ratio 3.0001 ∈ the pre-registered [2.99, 3.01] window → AC4b PASS on
the arithmetic arm; the direct-key arm remains impossible (host still
403 at 16:52) and is recorded as NOT PERFORMED, not as passed.

Per-member completion (status files; rc=0 each):

| member | supervisor window | rc | runtime | fetch | md5(pytorch_model.bin) | CSV bytes / rows |
|---|---|---|---|---|---|---|
| 1 | 16:38:18–16:49:26 | 0 | 668s | 0s (cached from smoke) | 29521fcaadd7b240d5c15d18b8a531ac | 836,430 / 12,446 |
| 2 | 16:51:33–17:05:43 | 0 | 850s | 92s | 7e5b00386db9b3ac4a42107376287d8d | 834,396 / 12,446 |
| 3 | 17:07:04–17:21:14 | 0 | 850s | 106s | 4a8d1f5330572fdfbaebab11d62d35f5 | 836,814 / 12,446 |
| 4 | 17:21:48–17:36:24 | 0 | 876s | 104s | a4f1a731aaea64f421ccf5b4bff768b1 | 837,584 / 12,446 |
| 5 | 17:37:05–17:51:27 | 0 | 861s | 95s | 3cdccbe311c06a1db6d22e7169570ef1 | 836,818 / 12,446 |

Distinct md5 per member (genuinely different weights), every size gate
2,609,603,341 B, staged delete verified after each, 12,446 rows =
(655−1)×19 + 20 exactly. Each member's ≤90-min budget: worst 876s
≈ 14.6 min — no budget stop, ever. Member-1 smoke (16:35:41, exit 0,
[total] 105s): fetch 94s, md5 as above, ratio 3.0001, MPS probe OK,
row accounting 76/76 (4 positions) MATCH.

R6 (full run, N_BOOT=10,000 position-cluster bootstrap, seed 0) — the
10 rows of data/processed/task_AC4_esm1v_summary.csv, verbatim:
```text
[AC4] member 1 delta-vs-own_e_b (primary): rho=-0.020573 CI=[-0.048467, +0.006286] p=0.1400
[AC4] member 1 delta-vs-GI_folinate_independent (secondary): rho=-0.014057 CI=[-0.039992, +0.011470] p=0.2802
[AC4] member 2 delta-vs-own_e_b (primary): rho=-0.040820 CI=[-0.069623, -0.011940] p=0.0046
[AC4] member 2 delta-vs-GI_folinate_independent (secondary): rho=-0.031519 CI=[-0.057703, -0.004896] p=0.0194
[AC4] member 3 delta-vs-own_e_b (primary): rho=+0.013434 CI=[-0.014563, +0.041385] p=0.3444
[AC4] member 3 delta-vs-GI_folinate_independent (secondary): rho=+0.012443 CI=[-0.013034, +0.038224] p=0.3378
[AC4] member 4 delta-vs-own_e_b (primary): rho=-0.026572 CI=[-0.053779, +0.000264] p=0.0524
[AC4] member 4 delta-vs-GI_folinate_independent (secondary): rho=-0.017147 CI=[-0.041859, +0.007487] p=0.1728
[AC4] member 5 delta-vs-own_e_b (primary): rho=-0.003409 CI=[-0.031214, +0.024562] p=0.8194
[AC4] member 5 delta-vs-GI_folinate_independent (secondary): rho=+0.000465 CI=[-0.024625, +0.025766] p=0.9632
```
R7 agreement (10 member pairs each; verbatim):
```text
[AC4] R7 member-pair Spearman on WT scores: min=0.859689 median=0.882637 max=0.890106 (10 pairs)
[AC4] R7 member-pair Spearman on delta scores: min=0.003314 median=0.084365 max=0.162631 (10 pairs)
[AC4] R7c the five delta-vs-own-e.b rhos: ['-0.020573', '-0.040820', '+0.013434', '-0.026572', '-0.003409']
[AC4] R7c mean=-0.015588 sd=0.021052 min=-0.040820 max=+0.013434; CIs excluding zero: 1/5; signs: 1 positive / 4 negative
```
R8 (verbatim):
```text
[AC4] R8 diagnostic: 10757 rows matched to ProteinGym ESM1v_ensemble
[AC4] R8 raw rho(our ensemble mean wt, PG ESM1v_ensemble) = 1.000000 (printed, convention-sensitive -- not gated)
[AC4] R8 per-position-centered rho = 1.000000 (gated > 0.99)
[AC4] [G-AC4-ENSEMBLE] PASS -- transformers-path ESM-1v scores reproduce ProteinGym's published ensemble ranks at the per-position level.
```
AC4d (verbatim):
```text
[AC4] AC4d VERDICT: SEED-NOISE BRANCH: the five members' delta-vs-e.b correlations SCATTER ACROSS ZERO (mixed signs) while WT-score agreement is min-pair-rho=0.859689 -- per AC4d this is strong evidence the 'epistasis signal' reported elsewhere in this project is seed noise rather than a stable model property.
[AC4] AC4d text honored: both branches pre-registered above; the data's branch is reported as-is, with all five rhos and CIs printed for the reader.
```
Wall-clocks: parity attempt 2 = 19s child / [total] 17s; member smoke
105s; members 668/850/850/876/861s; summ smoke 5s (N_BOOT=300); summ
full 146s. Versions printed by script 86: torch=2.14.0
transformers=5.17.0 huggingface_hub=1.33.0 numpy=2.5.3.

Verdict — AC4a–d:
- **AC4a:** all five members fetched (official HF org, size-gated,
  md5'd), scored on both backgrounds, ≤1 member's weights on disk at
  any moment (staging empty after each), every member inside its
  90-min budget. DONE.
- **AC4b:** optimizer-state explanation VERIFIED on the pre-registered
  arithmetic arm — 7,828,635,339 / 2,609,426,136 = 3.0001 ∈ [2.99,
  3.01] → model + 2 Adam moments. Direct key inspection: NOT POSSIBLE
  (403, re-verified 16:52) — recorded as not-performed.
- **AC4c:** ensemble diagnostic PASS (gated centered rho > 0.99;
  actual 0.9999999998) — and beyond the gate, value-level agreement
  with Meta's published ensemble at fp32 precision (median |Δ| 3e-6)
  plus PG-single = our member 1. The scoring path is externally
  validated.
- **AC4d: SEED-NOISE BRANCH**, by the rule fixed before the run:
  mixed signs (1 positive / 4 negative), 1/5 CIs excluding zero
  (member 2 alone, p=0.0046), cross-member agreement on DELTA vectors
  near zero (median rho 0.084, min 0.003) while WT-score agreement is
  moderate (median 0.883). Effect sizes with the sign rule (§3): all
  five |rho| ≤ 0.041 on the primary target — smaller in magnitude than
  the project's ESM-2 anchor (−0.088118, same 10,757-row base) and
  scattered around zero instead of consistently negative. k/5 = 1/5.
  Stated plainly (§0): the association does NOT survive seed change;
  a statistic that flips sign across five seeds of the same
  architecture is not a stable model property. Also stated: one
  member's CI excluding zero out of five tests (p=0.0046, |rho|=0.041)
  is not evidence against this — the pre-registered rule keys on the
  sign pattern, and 1/5 significance is unremarkable across 5
  uncorrected tests. NOT claimed: nothing here re-tests ESM-2's own
  seed stability (one seed), and no ensemble-mean delta-vs-e.b
  statistic was computed — it is not pre-registered and was
  deliberately not added post-hoc.

Files: scripts/86_ac4_esm1v_five_members.py (new, the named
deliverable; 3 size-gate edits from the parity-attempt-1 bug, all
disclosed in-script). data/processed/task_AC4_esm1v_member{1..5}_
scores.csv (12,446 rows each) and task_AC4_esm1v_summary.csv (10
rows). Smoke artifacts (clearly suffixed, not deliverables):
task_AC4_esm1v_member1_scores_smoke.csv, task_AC4_esm1v_summary_
smoke.csv. Session-tmp evidence: ac4_fetch1.log (403 matrix),
ac4_parity_status.txt/log, ac4_member1_smoke.log,
ac4_member{1..5}_status.txt/log, ac4_summ_smoke.log,
ac4_summ_status.txt/log. Venv additions: transformers,
huggingface_hub (installed this session, disclosed above). No
pre-existing script or result modified; RESULTS.md /
MTHFR_RESULTS_LOG*.md / REVIEW_TRIAGE.md / AGENTS.md untouched; no
commits.

Unexpected: (1) My own parity size-gate bug (esm1v-vs-esm2 file sizes)
burned attempt 1 — caught by its own gate before any scoring; fixed and
disclosed, no result observed in between. (2) R8's rho printed as
1.000000 — investigated per §5 instead of trusting it; it was genuine
fp32-level agreement, converting a disclosed limitation (sibling-only
parity) into direct ESM-1v external validation. (3) PG's
ESM1v_single is our member 1 (rho 1.000000 vs 0.87–0.89 for the
others) — a free identity check that per-member weights load
correctly. (4) The verdict direction: SEED-NOISE was the
pre-registered possibility that would undercut the flagship
statistic's generality — it fired on the first and only run, with no
tuning, retries, or alternative metrics (every smoke number stayed
out of the verdict; no stage of this task was ever run twice for a
result). (5) HF bandwidth ~28 MB/s made the whole 5-member campaign
≈76 min wall-clock (16:35:41 → 17:51:27) against a 7.5-h budget —
every cap kept >6× headroom.
---

## SUMMARY — closeout window 2026-09-25 (15:27 → 18:10): what completed, what is blocked, and what to inspect first

Status: WINDOW COMPLETE as far as it can go without user decisions.
No jobs running (ps clean at 18:10); nothing left to supervise; every
remaining item is blocked either on a decision only the user can make
(§10) or on the launch prompt's explicit prohibitions. Entries were
appended in completion order: [Z3f] line 1750, [Z3g-h] line 1870,
[AC4] line 2038, this SUMMARY terminal. No commits tonight (HEAD
abc7319 dated 2026-09-24 19:42 — pre-existing, verified).

COMPLETED this window (entries above; evidence on disk):
- **[Z3f] PASS** — SaProt score stage: rc=0, 585s on MPS, deliverable
  task_Z3f_saprot_scores.csv = 11,940 rows (596 positions × 20 alts),
  all gates True (G3 = 0.00e+00), exclusion accounting exact (1,017 of
  10,757 at the frozen 59 positions; phase5-absolute 1,046 MATCHES
  V2's published figure on those same positions).
- **[AC4] EXECUTED — AC4d VERDICT: SEED-NOISE BRANCH** (the headline
  scientific result of this window):
  • members 1–5 each fetched, scored, staged-deleted one at a time —
  all rc=0, runtimes 668 / 850 / 850 / 876 / 861 s (worst = 14.6 min
  of the 90-min/member budget; no budget stop, ever), distinct md5
  per member, size gate 2,609,603,341 B each, ≤1 member's weights on
  disk at any moment (staging empty verified after every member);
  • R5 three-way parity PASS: max|b−a| = 1.776e-15 (fair-esm
  re-derives the historical CSV), max|c−b| = 4.482e-05 (Transformers
  vs fair-esm) against tol 1e-3;
  • AC4b arithmetic arm VERIFIED: 7,828,635,339 / 2,609,426,136 =
  3.0001 ∈ [2.99, 3.01] → model + 2 Adam moments;
  • R8 ensemble gate PASS (centered rho 0.9999999998 > 0.99), with a
  value-level §5 check: our 5-member mean matches Meta's published
  ESM-1v ensemble (via ProteinGym) to fp32 precision (median |Δ| =
  2.97e-06; only 9/10,757 bit-identical → two pipelines, not a
  duplicated column), and PG's ESM1v_single = our member 1 exactly
  (rho 1.000000 vs 0.873–0.890 for the others);
  • five member rhos (primary, own e.b, N_BOOT=10,000):
  −0.020573 / −0.040820 / +0.013434 / −0.026572 / −0.003409 — mixed
  signs (1+/4−), 1/5 CIs excluding zero (member 2 alone, p=0.0046),
  mean −0.015588, all |rho| ≤ 0.041 vs the ESM-2 anchor −0.088118 on
  the same 10,757-row base; cross-member DELTA agreement median rho
  0.084 (min 0.003) while WT-score agreement median 0.883. Pre-
  registered branch fired as written: the delta–e.b association does
  NOT survive seed change — reported as the negative result it is
  (§0), with no tuning, no second run, and no post-hoc statistics.
- Earlier the same day, already logged in this file: [Z2c] (attempt 3
  executed, no cap ever fired), [Z2d] (direction unchanged,
  attenuation quantified), [AB2a-FIX] (96-model comparison table, all
  gates green at N_BOOT=10000).

BLOCKED — genuine, needs a decision from you (priority order):
1. **Z3g/Z3h — INSPECT THIS FIRST. Z3i waits behind it.** Script 70's
   stats stage stopped at its wt_aa-vs-structure guard:
   `wt_aa agrees with chain-A ori_aa on all scored rows: False
   (9595/9740)` → sys.exit(1) 2s in, before any null was computed —
   so this is an UNRUN analysis, not a negative result. Diagnosis is
   complete and unambiguous (full detail in [Z3g-h]): the 145
   disagreeing rows sit at exactly 9 positions where 6FCX's own
   SEQADV/DBREF records say the structure differs from reference
   P42898 — 2 engineered variants (E429A, R594Q) and a 7-residue
   EXPRESSION TAG (645–651; the chain's DBREF span ends at 644);
   atlas wt_aa == FASTA everywhere (labels are correct). Decision
   needed — either way it changes frozen script 70's decision rules
   (§10): (A) keep n=9,740/595 positions with a documented SEQADV
   exception to the guard, or (B) exclude the 9 positions →
   n=9,595/586 positions under decision 2's settled "structure cannot
   represent → exclude" policy. Recommendation: B as primary (the tag
   stretch is not MTHFR by the PDB's own DBREF, and frozen task_V2
   already has ZERO rows at all 9 sites — verified) with A reported
   as a sensitivity pair. No script was modified; nothing was run
   twice.
2. Z0/U3 cap waiver + ensemble-choice judgment (open from before).
3. AD6 AB3b-floor decision (open from before).
4. Standing fetch limit: no further ProteinGym/data fetches
   (~196.3/200 MB used) without your say-so.

BLOCKED — infrastructure (worked around; disclosed, no action needed):
- dl.fbaipublicfiles.com is host-wide HTTP 403 (probes 16:09:25,
  16:16:43, 16:52). AC4 proceeded via Meta's official HuggingFace org
  (disclosed in [AC4] and script 86's docstring; Transformers loader,
  math unchanged; R5 + R8 together cover validation). Consequences:
  AC4b's direct .pt key inspection NOT PERFORMED (arithmetic arm
  passed instead), and fair-esm parity is only possible on the ESM-2
  sibling — compensated by R8's direct ESM-1v agreement with Meta's
  published values.

BLOCKED — forbidden by the launch prompt (left untouched as instructed):
- AC6 (ESMFold), AB4 (Potts fit).

STILL RUNNING: none. All supervisor status/log files live in the
session tmp dir (…/T/opencode/): z3f_status.txt/z3f_score.log,
z3g_stats_status.txt/z3g_stats.log (the guard-failure record),
ac4_fetch1.log (403 matrix), ac4_parity_status/log,
ac4_member1_smoke.log, ac4_member{1..5}_status.txt/log,
ac4_summ_smoke.log, ac4_summ_status/log — every header carries its own
cap + disclosure text.

INFRASTRUCTURE FAILURES TONIGHT: zero. Z3f finished before its first
poll; all five members and both summ runs rc=0 first try; no cap ever
fired; no relaunches anywhere. The two rc=1s were both intended gate
exits: Z3g-h's guard (logged BLOCKED) and AC4 parity attempt 1 (my
size-gate bug — esm1v-vs-esm2 file sizes conflated — caught by its own
gate before any scoring existed, fixed, disclosed in-script; no result
was observed in between).

FILES changed this window (complete list; nothing else was touched):
docs/tasks/closeout-u2-u3-u4-v5/CLOSEOUT_LOG.md (append-only: [Z3f],
[Z3g-h], [AC4], this SUMMARY); scripts/86_ac4_esm1v_five_members.py
(new, the named deliverable, 3 disclosed size-gate edits pre-run);
venv additions transformers 5.17.0 + huggingface_hub 1.33.0
(disclosed); deliverables task_AC4_esm1v_member{1..5}_scores.csv,
task_AC4_esm1v_summary.csv, task_Z3f_saprot_scores.csv (+2 clearly
smoke-suffixed smoke CSVs). PROTECTED FILES UNTOUCHED: RESULTS.md,
MTHFR_RESULTS_LOG*.md, REVIEW_TRIAGE.md, AGENTS.md (its " M" in git
status is pre-existing user work), scripts/70 (read-only all night).
scripts/71's " M" is the earlier user-authorized [AB2a-FIX], already
logged. data/processed and data/external remain untracked by design;
untracked docs/logs are this session's long-standing state.

EXAMINE FIRST: the [Z3g-h] entry's Option A vs Option B decision
(keep n=9,740 with a guard exception, or exclude the 9 SEQADV
positions → n=9,595; recommendation B primary + A sensitivity). It is
the only item tonight that both blocks live analysis work (Z3g, Z3h,
Z3i) and requires a pre-registered-population choice that §10 reserves
for you. Everything else either completed or waits on older open
decisions.
---
