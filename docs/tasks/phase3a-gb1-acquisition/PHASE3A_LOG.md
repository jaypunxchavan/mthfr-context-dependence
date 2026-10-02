# PHASE 3a — GB1 acquisition log

**Session:** acquisition, verification, machinery validation, frozen pre-registration.
**Ends at:** READY-TO-SCORE. No model scoring of any kind.
**Doc:** `docs/tasks/phase3a-gb1-acquisition/PHASE3A_GB1_ACQUISITION.md`
**Executor:** OpenCode · **Date:** 2026-09-28

> This session characterises a shift statistic in GB1. Nothing here is a claim about the MTHFR
> anchor in either direction.

---
## T1 — Inventory what already exists, then acquire only what's missing
Status: PARTIAL
Time started / finished: 2026-09-28 16:05 / 2026-09-28 16:22 PDT
What I did:
1. Searched the tree for GB1 artefacts (excluding `docs/tasks/phase2-full-frame-placebo/`).
2. Identified and read in full the script that produced the V54A positive control.
3. Hashed and measured every GB1 file already on disk; dumped its verbatim columns.
4. Established the Olson 2014 matrix was NOT already present, then downloaded it
   from the publisher's own CDN (one URL tried, one 404, both recorded verbatim below).

Actual output (real numbers and quoted source text, not a paraphrase):

### 1.1 THE V54A POSITIVE CONTROL SCRIPT — `scripts/73_gb1_estimator_transplant.py`

Named in the task doc only as "the one reporting rho = +0.122, p = 0.385, n = 57". Located and
verified. Its own docstring, lines 18-19, verbatim:

> "BACKGROUND: site 54, V->A ("V54A"), fixed for all variants -- the analog
>  of MTHFR's fixed A222V."

Lines 31-34, verbatim:

> "DESIGN: variants = the 19 non-WT residues at EACH of the OTHER three
>  assayed sites {39, 40, 41} -> 3 x 19 = 57 rows; single background (like
>  MTHFR's single A222V). Fitness arms from the full 20^4 landscape
>  (single arm = variant with WT elsewhere; double arm = variant + V54A)."

Recorded statistic, `data/processed/task_AA1_gb1_signflip_nulls.csv` line 2, verbatim:

> `signflip,signed delta_ESM vs signed e_b,0.12218045112781956,-0.0003575382421571167,0.1407743165667218,0.12253798936997667,-0.00292631299734758,0.3849,10000,False`

So the recorded value to FULL PRECISION is **rho = +0.12218045112781956**, printed at 4 dp as
`observed=+0.1222` with `p=0.3849` (DEEPDIVE_LOG.md:651). n = 57 (`data/processed/task_AA1_gb1_eb_analog.csv`,
58 lines = 1 header + 57 rows). The doc's "rho = +0.122" is the 3-dp rounding; **+0.1222 is the
4-dp figure the original recorded it at** and the reproduction target is therefore +0.12218045112781956.

Data file it reads — script 73, line 131, verbatim:

> `DATA = ROOT / "data" / "external" / "GB1_fitness_landscape.txt"`

Script 73's ESM-2 dependency is at line 258 (`import esm`) and line 257
(`from scripts.lib.esm_scoring import get_position_logprobs, get_device`). **No model was loaded
this session** — see §0 constraint 1 and T3 below for how the reproduction was done from cached
data instead.

### 1.2 FILES ALREADY ON DISK (nothing downloaded for these)

| path | bytes | lines | sha256 |
|---|---|---|---|
| `data/external/GB1_fitness_landscape.txt` | 3,343,308 | 160,001 | `7c9aedcf44416ba8c3a442f041d0b53f8981f8a0bcaaf86afd8ebb8088ec0ad2` |
| `data/processed/task_AA1_gb1_eb_analog.csv` | 6,906 | 58 | `0ca45ba329441f1de3af9086c95947c8fadeb8ebb39de41dcec12501f888213c` |
| `data/processed/task_AA1_gb1_signflip_nulls.csv` | 462 | 4 | `b02363c63fb8386af4ee7e7306405b819ad9478a055ecaac3ba882d33433f45d` |
| `data/processed/task49_i1_gb1.csv` | 347 | 14 | `0706f69580d560b8a79c4ed69acae3b1250e815d234f3187f08372de8294f103` |
| `data/processed/task_AA7_second_control_eb.csv` | 80,618 | 690 | `48ff192a11e1b7cb8c1522d080c229b24410bed527559e8117e3645edd3c620d` |
| `data/processed/task_AA7_second_control_nulls.csv` | 462 | 4 | `8587d5b66f06d053d22ab6cdd9aaa57d05ec9cd6c801ad94da9752ce6fc7204f` |

**`data/external/GB1_fitness_landscape.txt` — column names verbatim** (tab-separated, line 1):

> `sequence	fitness`

Shape: 160,000 data rows = the full 20^4 combinatorial four-site library. `sequence` is a 4-character
genotype string over the assayed sites; `fitness` is a per-genotype value normalised so the wild type
is exactly 1.0. First two data lines verbatim: `VDGV	1.0` and `ADGV	0.0619096557142`.

**`data/processed/task_AA1_gb1_eb_analog.csv` — column names verbatim:**

> `site,variant,f_single,f_double,f_wt,f_bg,expected_multiplicative,e_b,delta_esm`

**`data/processed/task_AA1_gb1_signflip_nulls.csv` — column names verbatim:**

> `null,variant,observed,null_mean,null_sd,excess_over_null,frac_artifact,p,n_perm,survives`

**`data/processed/task49_i1_gb1.csv` — column names verbatim:** `quantity,value`
(single long-format key/value summary table; **not** the same quantity — see flag below).

**`data/processed/task_AA7_second_control_eb.csv` — column names verbatim:** first line
`aa1_pos,aa1_wt,aa1_mutation,aa2_pos,aa2_wt,aa2_mutation,` … (GRB2 second control, not GB1; listed
for completeness of the GB1 grep, not used).

### 1.3 THE OLSON 2014 MATRIX WAS GENUINELY ABSENT — ONE DOWNLOAD, ONE 404

Searched `data/` for the full double-mutant matrix: `find data -iname "*gb1*"` returned only the
four-site landscape, the ProteinGym index, and jackhmmer/PRISM alignments. **The 536k-variant matrix
was not on disk**, so one download was justified.

**Attempt 1 — FAILED, recorded verbatim (no substitute used):**
```
URL=https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.0/DMS_ProteinGym_substitutions/SUBSTITUTIONS/SPG1_STRSG_Olson_2014.csv
HTTP=404
LEN=0
CT=text/html; charset=iso-8859-1
```
**Attempt 2 — SUCCEEDED. This is the publisher's own supplementary file, not a mirror:**

```
URL=https://ars.els-cdn.com/content/image/1-s2.0-S0960982214012688-mmc2.xlsx
HTTP=200
BYTES=28090836
CT=application/excel
FINAL_URL=https://ars.els-cdn.com/content/image/1-s2.0-S0960982214012688-mmc2.xlsx
```
| path | bytes | sha256 |
|---|---|---|
| `data/external/gb1_olson2014/1-s2.0-S0960982214012688-mmc2.xlsx` | 28,090,836 | `e912c93cf3d1d95a7d8fc5bb8e8d50a523eb9398c51613b2a74693f07a50fe29` |

`file(1)` output verbatim: `Microsoft Excel 2007+`. Provenance: supplementary mmc2 of
doi:10.1016/j.cub.2014.09.072 (Olson, Wu & Sun 2014, *Curr Biol* 24(22):2643-2651). The URL is the
one documented by the `mavenn` project as the origin of its reformat of this dataset
(`https://mavenn.readthedocs.io/en/v1.1.3/datasets/dataset_gb1.html`). No mirror was substituted and
no alternative dataset was used.

Python package installed for the download (troubleshooting rule 1):
`venv/bin/python3 -m pip install openpyxl --break-system-packages` ->
`Successfully installed et-xmlfile-2.0.0 openpyxl-3.1.5`. No other package installed. **No torch/esm,
no model weights.**

### 1.4 THE MATRIX'S OWN STRUCTURE

One sheet: `DoubleSub.xls`, `calculate_dimension()` = `B2:V535920`, `max_row` = 535,920,
`max_col` = 22. **One sheet holds THREE side-by-side blocks**, whose header text is verbatim:

Excel row 2, columns B..V:
> `(None, 'DOUBLE MUTANTS', ..., 'SINGLE MUTANTS', ..., 'WILD TYPE')`

Excel row 3 — the verbatim column names of all three blocks:
```
DOUBLE  (cols B-K): 'Mut1 WT amino acid' | 'Mut1 Position' | 'Mut1 Mutation' |
                    'Mut2 WT amino acid' | 'Mut2 Position' | 'Mut2 Mutation' |
                    'Input Count' | 'Selection Count' | 'Mut1 Fitness' | 'Mut2 Fitness'
SINGLE  (cols N-R): 'WT amino acid' | 'Position' | 'Mutation' | 'Input Count' | 'Selection Count'
WILD    (cols U-V): 'Input Count' | 'Selection Count'
```

Row counts, measured by a streaming pass (21.4 s wall, no full in-memory load):
- **DOUBLE MUTANTS: 535,917 rows** (Excel rows 4..535,920). First data row verbatim:
  `(None, 'Q', 2, 'A', 'Y', 3, 'A', 173, 33, 1.518, 0.579)`. Last data row verbatim:
  `(None, 'E', 56, 'Y', 'T', 55, 'Y', 95, 16, 0.19, 0.663)`.
- **SINGLE MUTANTS: 1,045 rows** (Excel rows 4..1048). First verbatim `('Q', 2, 'A', 14663, 38476)`,
  last verbatim `('E', 56, 'Y', 16560, 5434)`.
- **WILD TYPE: 1 row.** `Input Count = 1759616`, `Selection Count = 3041819`.

**What the score column actually is — there is none, and this is important.** The double-mutant block
has NO fitness/score column. It carries only raw **read counts**: `Input Count` and `Selection Count`.
The two `Fitness` columns are *not* the double mutant's own score — they are the **parent single-mutant
fitness values copied in for convenience** (first data row: mut1 = Q2A, mut2 = Y3A, `Mut1 Fitness`
1.518, `Mut2 Fitness` 0.579; the last data row's E56 and T55 parents carry 0.19 and 0.19... and 0.615
respectively — i.e. they track the *singles* block, not the pair). Verified in T2.

The score is therefore computed from the counts by the paper's own formula, quoted verbatim from
MaveDB's record of this dataset (`https://mavedb.org/score-sets/urn:mavedb:00000105-a-1`):

> "$$F_{B,mut} = \frac{n_{mut,sel}}{n_{mut,in}}$$ where $F_{B,mut}$ represents the fraction bound for
> mutant $mut$... $$W = \frac{F_{B,mut}}{F_{B,wt}}$$ where $W$ represents the variant frequency
> relative to wildtype"

**Error/confidence column: none exists.** There is no standard error, no replicate, no q-value. The
only confidence signal in the file is `Input Count` (read depth). This directly determines how
T2-G1 can and cannot be gated — see T2.

Verdict:
PARTIAL. The V54A control script and every file it reads were found, quoted and hashed; its recorded
statistic was recovered to full precision (+0.12218045112781956, p=0.3849, n=57). Exactly one file was
genuinely missing and was downloaded, from the publisher's own CDN, with URL/status/bytes/sha256
recorded; one 404 is logged verbatim and no mirror was substituted.

Files created/modified:
- `docs/tasks/phase3a-gb1-acquisition/PHASE3A_LOG.md` (this log)
- `data/external/gb1_olson2014/1-s2.0-S0960982214012688-mmc2.xlsx` (new, downloaded; gitignored per AGENTS §2)

Anything unexpected or worth flagging:
- **The project already had only the FOUR-SITE GB1 library (160,000 genotypes, 4 sites: 39/40/41/54),
  not the whole-domain Olson matrix.** Script 73's V54A control is a 57-row, 3-site, single-background
  design. The 1,045-background regime map in the task doc needs the whole-domain matrix, which had to
  be acquired. T1's premise that "GB1 data is likely already on disk" was right about *some* GB1 data
  and wrong about *this* GB1 data.
- **The two numbering schemes in this repo are different GB1 sequences.** The project constant
  (script 73, line 135) is the 56-residue PDB 2GB1 construct
  `MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE` with `V54A` at 1-based position 54.
  The Olson file's positions are numbered differently (its first data row is WT `Q` at position 2 and
  WT `Y` at position 3; its last is WT `E` at position 56 and WT `T` at position 55). The two must be
  reconciled before any V54A claim is carried across. Deferred to T2, which derives the sequence from
  the data itself.
- `scripts/49_i1_gb1_positive_control.py` also reports a rho, but **it is a different statistic**:
  `pooled_rho = 0.4466626167166524` over `n_pairs = 570` with `k_backgrounds = 10`, an *association*
  null that does not centre on zero (null_mean 0.388). It is **not** the +0.122 control. It would have
  been easy to cite the wrong script; AGENTS §5 "never cite a script you have not verified exists" is
  the rule that caught it.
- `openpyxl` was missing and was installed; the only package installed this session.
- 28 MB is the only substantial write. The xlsx parse costs ~21 s per pass streamed, so the parse was
  done in a single streaming pass per script, never fully materialised in memory (memory pressure on
  this box is real).

---
## T2 — Verify the matrix against the paper's own published figures (script 128, no torch)
Status: PASS
Time started / finished: 2026-09-28 16:30 / 2026-09-28 16:55 PDT
What I did:
Wrote `scripts/128_gb1_olson_verify_and_transplant_repro.py` with the pre-registration in its
docstring **before its first run** (gates, tolerances, decision rules, and the read-depth sweep
protocol all fixed in advance). Smoke run at `N_BOOT=300 N_PERM=500` (56.5 s), which surfaced three
of my own bugs; fixed, re-smoked, then the full run at `N_BOOT=10000 N_PERM=10000` (54.7 s, exit 0).
Full output verbatim at `docs/tasks/phase3a-gb1-acquisition/PHASE3A_T2_T3_FULL_OUTPUT.txt` (285 lines).
No torch, no esm, no model weights. Only `openpyxl` was installed (in T1).

Actual output (real numbers and quoted source text, not a paraphrase):

### Structure, as the file states it
```
file            : data/external/gb1_olson2014/1-s2.0-S0960982214012688-mmc2.xlsx
bytes           : 28,090,836
sha256          : e912c93cf3d1d95a7d8fc5bb8e8d50a523eb9398c51613b2a74693f07a50fe29
sheetnames      : ['DoubleSub.xls']
sheet           : 'DoubleSub.xls'  max_row=535920 max_col=22
DOUBLE MUTANTS : 535,917 rows
SINGLE MUTANTS : 1,045 rows
WILD TYPE     : input=1,759,616 selection=3,041,819
```

### T2 STEP 1 — asked BEFORE any count was computed, so the answer cannot be shaped by it
```
VERDICT: a column literally named 'high confidence' / 'error' / 'SE' / 'SD' exists: False
  -> NO. The file has no confidence flag, no error bar, no replicate,
     no q-value. The ONLY confidence signal present is the read depth
     'Input Count'.
```

### Gate T2-G1 — high-confidence double count: **PASS**
Raw double count **535,917**. Read depth over doubles: `min=1 median=248 max=64,627 mean=539.9`.
Disclosed proxy sweep (every integer `t` on `Input Count`, threshold **swept, not chosen**):

```
   t      retained
    20     520,316
    23     516,436  <== INSIDE [509693, 517278]
    24     515,119  <== INSIDE [509693, 517278]
    25     513,808  <== INSIDE [509693, 517278]
    26     512,447  <== INSIDE [509693, 517278]
    27     511,145  <== INSIDE [509693, 517278]
    28     509,754  <== INSIDE [509693, 517278]
    30     506,920
integer thresholds t whose retained count lands inside the paper's range: 6
  t range: 23..28; first=(23, 516436) last=(28, 509754)
```
Six consecutive integer thresholds land inside the paper's stated range. **No single t is selected
as "the" filter** — the sweep is reported as a set, per the pre-registration. The gate PASSes under
the pre-registered rule (a reported count falls inside the range); the honesty caveat is that this
is a *proxy*, not the paper's own definition, because the paper's own definition is not in the file.

### THE PAPER'S 536,085 IS NOT A LIBRARY SIZE — IT IS THE COMBINATORIAL COUNT
```
paper's stated denominator   : 536,085 (= the COMBINATORIAL possible count C(n,2)*19^2 for n=55: 536,085)
```
C(55,2) × 19² = 1,485 × 361 = **536,085 exactly**. The task doc's phrasing "out of 536,085 possible"
is correct; the earlier MaveDB paraphrase of the paper ("The pooled library included 536,085 double
mutants") reads the same integer as a library size. It is the possible count. Resolved.

### Gate T2-G2 — position pairs: **PASS**, and the 1,485-vs-1,540 discrepancy RESOLVED
```
distinct unordered position pairs present: 1,485
paper's figure                          : 1,485
C(n,2) with n=55 positions              : 1,485
double rows with pos1 == pos2 (data defect): 0
positions present in the file            : 55 (2..56)
positions present but in NO double pair  : []  (count 0)
positions in 2..56 absent from the file: []
```
Script's own verbatim conclusion:

> "1,540 = C(56,2) is the count for a 56-mutated-position frame. The residue that a 56-position
>  frame would add is 2GB1 position 1, the initiating Met, which appears in NO row of this library
>  (the data starts at position 2 and position 1 is absent from every block). The paper's 1,485 is
>  therefore the CORRECT number for the 55-position domain actually assayed. The 1,540 figure comes
>  from assuming the full 56-residue construct including the Met."

**GB1's assayed domain here is 55 positions, not 56. The paper is right on all three numbers; the
task doc's 1,540 and 1,064 both come from the same single wrong assumption of a 56-position frame.**

### Gate T2-G3 — singles: **PASS**, and the ~1,045-vs-1,064 discrepancy RESOLVED
```
SINGLE MUTANTS block rows : 1,045
paper's figure            : ~1,045
possible at n=55         : 1,045
possible at n=56           : 1,064  (the doc's 1,064)
missing (pos, mut_aa) vs n*19 : 0 []
observed singles per position: min=19 max=19 over 55 positions (19 everywhere is complete)
```
**Zero singles are missing.** 1,045 is not an approximate coverage figure — it is the *complete*
enumeration 55 × 19 = 1,045. The doc's 1,064 is 56 × 19 and counts 19 mutants at a position
(position 1, the initiating Met) that this library never varied. The 1,045 is fully explained.

### T2-G4 — wild-type sequence as the data implies it
```
distinct positions in the data : n = 55
position range                  : 2..56  (contiguous: True; gaps: [])
WT-residue conflicts within a position: 0 []
derived WT sequence, verbatim (55 aa, positions 2..56):
  pos   2: QYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE
```
**1-based and contiguous**, no gaps, and zero WT-residue conflicts across all 536,962 rows — no
column-duplication or mis-alignment problem (AGENTS §5).

Comparison against the project's own 2GB1 constant (`scripts/73_gb1_estimator_transplant.py` L135),
computed not assumed:
```
project GB1_SEQ (script 73 L135), 56 aa:
  MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE
olson-derived, 55 aa at positions 2..56:
  QYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE
best 1-based offset of olson sequence within 2GB1 frame: 1 (1-based start 2), mismatches = 1
  per-position differences (2GB1_pos, 2GB1_aa, olson_aa): [(2, 'T', 'Q')]
olson position of 2GB1 position 54 (V, the V54A background): 54
  olson WT residue at that position: 'V' (must be 'V' for V54A to be the same substitution)
olson positions of 2GB1 39/40/41 (V/D/G): 39/40/41
```
**The two frames share numbering for positions 2..56** (same integers), with exactly one residue
difference: 2GB1 position 2 is `T` in the project's constant, `Q` in Olson's library. That is a
known, documented template change — the publisher's record of this dataset states the mutagenesis
template "includes a ... mutation **T228Q** with respect to UniProt entry SPG1_STRSG", and 228 is
the first assayed residue. Positions 39, 40, 41 and 54 are identical in both frames, so the V54A
background and the three partner sites are the *same positions and the same residues* in both
frames. Frames are compared here, not merged.

### T2-G5 — what the score actually is: **PASS** (max|diff| = 4.999e-04)
```
F_B,wt = selection/input = 3,041,819/1,759,616 = 1.728683
the file has NO score column; W is computed as
  F_B,mut = Selection Count / Input Count ;  W = F_B,mut / F_B,wt
W recomputed from the SINGLE block's own counts spans [0.0021, 5.0219] over 1,045 singles
'Mut1/Mut2 Fitness' column vs W of the PARENT SINGLE, over 1,045 shared keys: max|diff| = 4.999e-04
  (the file stores that column to 3 DECIMAL PLACES -- the first data row carries the literal
   1.518 -- so a max|diff| at the 5e-4 scale is the file's own rounding, not a disagreement.)
W over the raw doubles: min=0.0000 median=0.1415 max=14.4619 mean=0.4636
  -> the double mutant's own score is NOT in the file; it must be derived from the two read counts.
```
The two `* Fitness` columns in the double block are the **parent singles'** measured W, not the
double's own score — verified on all 1,045 keys. The 5e-4 residual is the file's 3-decimal storage.
This is the AGENTS §5 column-identity check, run before any number was built on it.

### Compacted re-distribution for script 129
```
data/external/gb1_olson2014/gb1_olson2014_doubles.csv  rows=535,917  bytes=8,973,371  sha256=89f8e394125d743b5db4bc455a64c59dc6d85f3f1d994f6de51af90f47cc4769
data/external/gb1_olson2014/gb1_olson2014_singles.csv   rows=1,045    bytes=17,183     sha256=0b2e865e007d606d885d1e8df9f4548a85e4ceeedbff8ab860db7469d65dbfc3
column names verbatim: ['pos1', 'mut1', 'pos2', 'mut2', 'input_count', 'sel_count']
column names verbatim: ['pos', 'mut', 'input_count', 'sel_count']
```
Gate table written to `data/processed/task128_gb1_olson_verification.csv`. `FAIL count: 0`.

Verdict:
PASS. T2-G1, T2-G2, T2-G3, T2-G5 all pass. Both numeric discrepancies in the task doc are resolved
from the data, and both resolve the same way: the assayed domain is **55 positions (2..56)**, not 56.
C(55,2)=1,485 = the paper's pair count exactly; 55×19=1,045 = the paper's single count exactly with
zero missing; C(55,2)×19²=536,085 = the paper's "possible" exactly. The paper is correct on all
three. T2-G1 passes only under a disclosed read-depth proxy (6 consecutive thresholds), because the
publisher's file contains no confidence column at all.

Files created/modified:
- `scripts/128_gb1_olson_verify_and_transplant_repro.py` (new)
- `data/external/gb1_olson2014/gb1_olson2014_doubles.csv`, `gb1_olson2014_singles.csv` (new)
- `data/processed/task128_gb1_olson_verification.csv` (new)
- `docs/tasks/phase3a-gb1-acquisition/PHASE3A_T2_T3_FULL_OUTPUT.txt` (new, 285 lines)

Anything unexpected or worth flagging:
- **The task doc's "1,485 vs 1,540" and "~1,045 vs 1,064" are the same error, and the paper is
  right in both cases.** One fact — 55 mutated positions, 2..56, Met1 not varied — explains all
  three of the paper's numbers exactly and both of the doc's. Neither number was waved through.
- **The doc's "out of 536,085 possible" is correct, but a widely-copied paraphrase of the same paper
  reads 536,085 as a library size.** C(55,2)×19² = 536,085 exactly, so it is the combinatorial count.
  Anyone re-deriving this from the paraphrase would get the denominator wrong.
- The publisher's file has **no score column**. W must be derived from two read counts. Anyone
  treating `Mut1 Fitness` as a double-mutant score would be reading the parent single's value.
- A **T→Q difference at position 2** exists between the project's 2GB1 constant and Olson's library,
  consistent with the documented T228Q template change. It does not touch positions 39/40/41/54, so
  it does not affect the V54A control or the partner sites, but Phase 3b's gate G-5 (WT sequence used
  for scoring must match what the fitness data implies) will have to resolve which sequence is
  scored. Flagged now, not then.
- Three bugs in my own script 128 were caught by the smoke run (swapped position/residue columns, an
  index that matched on position only and so compared the wrong single mutant, and a string-list
  concat). All fixed before the full run. The `T2-G5` first implementation reported a spurious
  max|diff| of 3.073 for exactly the second bug. Had I run at full N first, that would have been an
  expensive, wrong FAIL.
- `T3-G1p` read FAIL in the smoke run (p=0.3820 vs 0.3849, diff 2.9e-3) purely because `N_PERM=500`
  has Monte-Carlo resolution ~1/500. The pre-registered gate is at the default `N_PERM=10000`; the
  tolerance was **not** touched, and the full run gives diff 0.000e+00.

---
## T3-G1 — Rebuild and validate the transplant machinery (script 128, same run)
Status: PASS
Time started / finished: 2026-09-28 16:30 / 2026-09-28 16:55 PDT (same run as T2)
What I did:
Reused the project's existing transplant code rather than reimplementing it:
  * the statistic is **imported**, not re-derived from memory —
    `from scripts.lib.stats import _spearman` — and printed at run time via `inspect.getsource`
    so the log carries the code's own definition;
  * the fitness-side construction was reimplemented line-for-line from
    `scripts/73_gb1_estimator_transplant.py` lines 188–231 and then **checked against script 73's
    own stored output** to prove the reimplementation is faithful;
  * the sign-flip null was replicated in script 73's exact loop order and with identical RNG
    consumption, so the p-value is reproducible rather than merely similar.
**No model was loaded.** No `import torch`, no `import esm`, no weight download, no MPS/CUDA
allocation. The ESM-2 half of the control is taken from script 73's cached output table and is
labelled CACHED at every point of use.

Actual output (real numbers and quoted source text, not a paraphrase):

### The statistic's definition, quoted from `scripts/lib/stats.py` (not from memory)
```
def _spearman(a, b):
    """Spearman rho via ranks + Pearson. Matches scipy.stats.spearmanr exactly."""
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])
```

### Input provenance, re-hashed at run time
```
data/external/GB1_fitness_landscape.txt  bytes=3,343,308  sha256=7c9aedcf44416ba8c3a442f041d0b53f8981f8a0bcaaf86afd8ebb8088ec0ad2
data/processed/task_AA1_gb1_eb_analog.csv  bytes=6,906  sha256=0ca45ba329441f1de3af9086c95947c8fadeb8ebb39de41dcec12501f888213c
data/processed/task_AA1_gb1_signflip_nulls.csv  bytes=462  sha256=b02363c63fb8386af4ee7e7306405b819ad9478a055ecaac3ba882d33433f45d
raw GB1_fitness_landscape.txt: rows=160,000 columns=['sequence', 'fitness']
f(WT=VDGV)          = 1.000000
f(background VDGA)  = 1.372949   <- V54A, the recorded control
```

### The fitness side re-derives from raw data EXACTLY
```
rebuilt e_b rows=57  cached rows=57
  rebuilt columns, verbatim: ['site', 'variant', 'f_single', 'f_double', 'f_wt', 'f_bg', 'expected_multiplicative', 'e_b']
  cached  columns, verbatim: ['site', 'variant', 'f_single', 'f_double', 'f_wt', 'f_bg', 'expected_multiplicative', 'e_b', 'delta_esm']
  cached has one extra column, 'delta_esm' -- the CACHED ESM-2 half; shared prefix identical: True
RE-DERIVED e_b vs SCRIPT 73's STORED e_b: max|diff| = 2.220e-16
                     f_single: max|diff| = 0.000e+00
                     f_double: max|diff| = 0.000e+00
                         f_bg: max|diff| = 0.000e+00
      expected_multiplicative: max|diff| = 4.441e-16
```
Construction, quoted from script 73 lines 223–224: `expct = f_v * f_bg / f_wt` then `e_b = f_vb - expct`.
Agreement is to floating-point epsilon on all four fitness columns, so the reimplementation is
faithful and the stored table is confirmed against the raw 160,000-genotype file.

### GATE T3-G1 (HARD) — the V54A positive control reproduces **EXACTLY**
```
n partners = 57   partner positions = [39, 40, 41]
partner position list (distinct) = [39, 40, 41]
COMPUTED rho(delta, e_b) = 0.12218045112781956   (0.12218045112781956)
RECORDED rho            = 0.12218045112781956   (0.12218045112781956)
ABSOLUTE DIFFERENCE     = 0.000000e+00
T3-G1a (|diff| <= 1e-12) : PASS
T3-G1b (|diff| <= 5e-05, the 4-dp digit the original recorded at) : PASS
```
Full precision, both to `.17g`:
- **computed ρ = 0.12218045112781956**
- **recorded ρ = 0.12218045112781956**
- **absolute difference = 0.000000e+00** (bit-for-bit identical, not merely close)

The recorded value is quoted in this session's T1 from
`data/processed/task_AA1_gb1_signflip_nulls.csv`, and the same number appears in
`docs/tasks/detection-floor-and-mechanism/DEEPDIVE_LOG.md:651` as `observed=+0.1222`.
The task doc's "ρ = +0.122" is a 3-dp rounding of this.

### The recorded p also reproduces, and so does the whole null
```
re-running script 73's sign-flip re-derivation null in its exact loop order (N_PERM=10000, SEED=0);
the ESM-2 half is cached, the e_b half is freshly re-derived:
  observed = +0.1222  null mean = -0.0004  null sd = 0.1408  p = 0.3849
  RECORDED p = 0.3849  ABSOLUTE DIFFERENCE = 0.000e+00  T3-G1p PASS
  null-centring (script 33's expression): null mean IS consistent with zero
```
`null mean = -0.0004`, `null sd = 0.1408` reproduce DEEPDIVE_LOG L651's recorded
`null mean=-0.0004 sd=+0.1408` exactly. The null, not just the point estimate, is reproduced.

Per AGENTS §4 and the project's own caveat, the sign-flip null on a signed variable **centres on zero
by construction**. It rules out one specific artifact mechanism. It is not evidence of a real effect
and it is not evidence about confounding. The recorded V54A control remains a correctly-centred null:
it did **not** detect epistasis at V54A. That is the recorded result and this session does not change it.

### GATE T3-G2 — bootstrap identity: **PASS**
```
n clusters (site,variant partner identities) = 57
every-cluster-exactly-once rho = 0.12218045112781956
point estimate                 = 0.12218045112781956
ABSOLUTE DIFFERENCE            = 0.000000e+00  (tolerance 1e-12)
```
Cluster map built with the project's own `scripts.lib.stats._cluster_indices`, not a private
reimplementation. 57 clusters = 3 sites × 19 non-WT residues, i.e. the 57 partners of V54A.

### For V54A, as the task doc requires
- **n partners = 57**
- **partner position list = [39, 40, 41]** (19 non-WT residues at each of the three assayed sites)
- **the statistic, quoted from the code:**
  `rho_b = _spearman(delta_b, e_b) = np.corrcoef(rankdata(delta_b), rankdata(e_b))[0,1]`,
  where `delta_b(v) = S(v|V54A) − S(v|WT)` and
  `e_b(v) = f(v+V54A) − f(v)·f(V54A)/f(WT)`.

### Gate table (full run, `FAIL count: 0`)
```
                                             gate verdict                                              value
               T2-G1 high-confidence double count    PASS  raw=535,917; thresholds_inside_range=6 (t=23..28)
                     T2-G2 position pairs covered    PASS  1,485 vs paper 1,485; n_positions=55; C(n,2)=1,485
                              T2-G3 singles count    PASS                   1,045 vs paper ~1,045; missing=0
T2-G5 Mut-Fitness column is the parent single's W    PASS                                max|diff|=4.999e-04
                    T3-G1a rho exact reproduction    PASS                                 abs diff=0.000e+00 tolerance 1e-12
        T3-G1b rho reproduces recorded 4-dp value    PASS                                 abs diff=0.000e+00 tolerance 5e-05
    T3-G1p sign-flip p reproduces recorded 0.3849    PASS                                 abs diff=0.000e+00 tolerance 5e-05
                         T3-G2 bootstrap identity    PASS                                 abs diff=0.000e+00 tolerance 1e-12
```

Verdict:
PASS. T3-G1 — the hard gate that licenses everything else — reproduces the recorded V54A control
bit-for-bit: ρ absolute difference 0.000000e+00 against a 1e-12 pre-registered tolerance, and the
sign-flip p reproduces to 0.000e+00. T3-G2 (bootstrap identity) passes at 0.000000e+00. The
machinery is validated to the precision it was recorded at. T4 and T5 are therefore licensed to
proceed.

Files created/modified: (same run as T2; no additional files)

Anything unexpected or worth flagging:
- **T3-G1 validates the statistic and the fitness construction, NOT the ESM-2 forward passes.** The
  `delta_esm` column is loaded from script 73's cached output because loading the model is forbidden
  this session. This is stated in the script docstring, in the script's own printed output, and here.
  Anyone reading "machinery validated" as "ESM-2 re-scored and confirmed" would be wrong. Under AGENTS
  §6 this is a reproduction, not a replication, and it is a unit test of the estimator rather than new
  evidence for any claim.
- **A real docstring/code contradiction in script 73, found and reported rather than smoothed over:**
  its docstring says "(N_PERM from env, default 10000; SEED 0; +0 correction identical to script
  33)" but its code is `pv = float((np.abs(null) >= abs(obs)).mean())` — a bare mean with **no +1**.
  The docstring's "+0 correction" is at best a typo for "+1". This script replicates the **code**,
  which is why the p reproduces exactly. The consequence is that AA1's p is *not* directly
  comparable to a +1-corrected pipeline. Flagged, not edited — script 73 is not mine to change.
- **n=57 is 3 sites, not 57 independent units.** With 57 partners at only 3 distinct positions, a
  partner position is a pseudoreplication risk. The project already recorded this (AA2; DEEPDIVE L768)
  and the frozen pre-registration's position-cluster bootstrap (Appendix A §4) is the right
  instrument for the 1,045-background map. Flagged so the V54A control is never read as
  n=57 independent evidence.
- V54A's own measured fitness is **1.372949** — above wild type. The recorded control's background
  is therefore not a deleterious background. Reported, not acted on; selecting a different letter
  after seeing this would be a data-dependent choice.
- The T3-G1p smoke-run FAIL (`p=0.3820` at N_PERM=500) was a resolution artifact of the smoke
  setting, not a gate failure. The pre-registered tolerance (5e-5 at the default N_PERM=10000) was
  not altered, and `N_PERM` was not raised to chase a pass — the full run at the pre-registered
  default gave diff 0.000e+00 on its own.

---
## T4 — Enumerate the candidate background roster (script 129, no torch, no selection)
Status: PASS
Time started / finished: 2026-09-28 17:05 / 2026-09-28 17:12 PDT
What I did:
Wrote `scripts/129_gb1_background_roster.py` with its pre-registration in the docstring before the
first run. Smoke at `N_BOOT=300 N_PERM=500` (0.4 s) caught two of my own bugs; fixed, then the full
run at `N_BOOT=10000 N_PERM=10000` (0.4 s, exit 0). No torch, no esm, no model. Full output
verbatim at `docs/tasks/phase3a-gb1-acquisition/PHASE3A_T4_FULL_OUTPUT.txt` (116 lines).
**Enumerated only. Selected nothing.** No sample drawn, no subset written, no threshold chosen.

Actual output (real numbers and quoted source text, not a paraphrase):

### Roster
```
data/external/gb1_olson2014/gb1_olson2014_doubles.csv  bytes=8,973,371  sha256=89f8e394125d743b5db4bc455a64c59dc6d85f3f1d994f6de51af90f47cc4769
data/external/gb1_olson2014/gb1_olson2014_singles.csv   bytes=17,183     sha256=0b2e865e007d606d885d1e8df9f4548a85e4ceeedbff8ab860db7469d65dbfc3
partner occurrences considered (both slots of every double): 1,071,834
  = 2 x 535,917 = 1,071,834  (matches: True)
distinct (pos, mut) partner keys enumerated: 1,045
```
Partners are **double-mutant rows only**; a single mutant is not a partner of itself. The ceiling
for any background is therefore `(n_positions-1) * 19 = 1,026`, reported so the distribution can be
read against what is combinatorially possible.

`data/processed/gb1_background_roster.csv`:
```
rows   = 1,045
bytes  = 67,876
sha256 = ee2e7872c19530978f5e64fd3344c6a7597be025dcddb84bd50ac9230e79aae4
column names verbatim: ['background_id', 'pos', 'wt_aa', 'mut',
                        'background_single_fitness_W', 'n_partners_t23', 'n_partners_t24',
                        'n_partners_t25', 'n_partners_t26', 'n_partners_t27',
                        'n_partners_t28', 'n_partners_raw']
```
First two rows, verbatim:
```
background_id  pos wt_aa mut  background_single_fitness_W  n_partners_t23 ... n_partners_t28  n_partners_raw
         G2QA    2     Q   A                     1.517930            1004 ...             990            1026
         G2QC    2     Q   C                     1.024400             993 ...             981            1025
```

### n_partners distribution (min, quartiles, max) — every column reported
```
        column    n  min  p25  median  p75  max        mean  n_ge_50  n_ge_100  n_ge_200  n_ge_500
n_partners_raw 1045  950 1026    1026 1026 1026 1025.678469     1045      1045      1045      1045
n_partners_t23 1045  322  986    1013 1022 1026  988.394258     1045      1045      1045      1042
n_partners_t24 1045  315  982    1012 1022 1026  985.873684     1045      1045      1045      1041
n_partners_t25 1045  313  978    1010 1022 1026  983.364593     1045      1045      1045      1041
n_partners_t26 1045  306  975    1009 1021 1026  980.759809     1045      1045      1045      1041
n_partners_t27 1045  301  971    1008 1021 1026  978.267943     1045      1045      1045      1041
n_partners_t28 1045  295  967    1007 1020 1026  975.605742     1045      1045      1045      1041
```
Background single-mutant fitness W: `min=0.0021 median=0.6551 max=5.0219`.

### Appendix A qualification — reported, NOT acted on
```
threshold column       n>=100   cap binds?  qualifying   after cap
n_partners_raw           1045         True        1045         400
n_partners_t23           1045         True        1045         400
   ... (identical for t24..t28)
  >>> T4-G4: PASS   value = n_ge_100 range 1045..1045; cap binds for 7 of 7 columns

The 400 cap binds under EVERY threshold column considered (7/7), so Appendix A's
seed-0 sample is REQUIRED, not optional.
```
**How many backgrounds would qualify under Appendix A's rule: all 1,045, under every one of the
seven threshold columns considered.** The ≥100-partner floor excludes nobody: even the most
depth-starved background has 295 partners at t=28 and 950 unfiltered. Appendix A's 400 cap, not its
100-partner floor, is the binding constraint, and it binds by a factor of 2.6.

### Gate table
```
                   T4-G3 no partner at a background's own position    PASS              double rows with pos1==pos2 = 0 of 535,917
                    T4-G1 one row per single mutant, no duplicates    PASS            rows=1,045, unique ids=1,045, expected=1,045
                  T4-G2 WT residue and fitness agree with the data    PASS   rows where mut==wt_aa: 0; max|fitness diff|=0.000e+00
T4-G4 Appendix A qualification reported for every threshold column    PASS n_ge_100 range 1045..1045; cap binds for 7 of 7 columns
FAIL count: 0
```

Verdict:
PASS. 1,045 backgrounds enumerated, 0 selected, 0 filtered. The full roster is on disk with its
sha256. **No threshold was chosen** — six read-depth proxy columns (t=23..28) plus the unfiltered
count are all reported side by side and none is preferred.

Files created/modified:
- `scripts/129_gb1_background_roster.py` (new)
- `data/processed/gb1_background_roster.csv` (new, 1,045 rows)
- `data/processed/task129_gb1_n_partners_distribution.csv` (new)
- `docs/tasks/phase3a-gb1-acquisition/PHASE3A_T4_FULL_OUTPUT.txt` (new, 116 lines)

Anything unexpected or worth flagging:
- **A GAP IN THE FROZEN PRE-REGISTRATION, surfaced and left open.** Appendix A §3 says "at least 100
  **high-confidence** partners" but the publisher's file has no confidence column at all (T2-G1).
  The term is undefined in the source data. I did **not** resolve it by picking a threshold: six
  candidate columns are emitted and none is selected, and the gap is printed in the script's own
  output as requiring a **v2** pre-registration, never an edit to v1. This is the single most
  consequential open item Phase 3b inherits.
- **Appendix A's 100-partner floor is inert; the 400 cap is what actually shapes the roster.**
  Every one of the 1,045 backgrounds clears 100 partners by a wide margin under every threshold
  considered (worst case 295). If the intent of the floor was to control partner-set size, it does
  not do that here — the floor should be revisited in v2, and this is flagged rather than changed.
- `background_single_fitness_W` is a **reported column only**. It was not used to filter, rank,
  weight, cap or order anything. The roster's only ordering is lexicographic on `(pos, mut)`, which
  is a canonical identifier sort, not a ranking by any measurement.
- **Two bugs of my own, caught by the smoke run.** (i) I initially concatenated the single-mutant
  block into the partner frame, inflating every `n_partners` by 1 and pushing the apparent maximum
  to 1,027 — one above the true combinatorial ceiling of 1,026. (ii) The T4-G2 fitness check
  compared two differently-ordered arrays positionally, producing a spurious
  `max|fitness diff| = 4.832e+00` FAIL; fixed to join on `(pos, mut)`, after which it is 0.000e+00.
  The roster's sha256 consequently differs between the smoke and full runs (the smoke run's
  `7ca41f9d…` had the inflated counts); **the hash reported above is from the fixed full run.**
- `n_partners_t23` min = 322 and `n_partners_raw` min = 950 means the read-depth filter's effect is
  almost entirely on the *minimum*, not the bulk. The median moves only from 1,026 to 1,013. Any
  covariate analysis that depends on the dynamic range of `e_b` (Appendix A §4d) will be more
  sensitive to this choice than the qualification count suggests.

---
## T5 — Cost and feasibility audit for Phase 3b's scoring (read-only, no model)
Status: PASS
Time started / finished: 2026-09-28 17:15 / 2026-09-28 17:25 PDT
What I did:
Read-only audit. No model loaded, no script written, nothing scored, nothing measured by running
ESM-2. Searched the repo's logs for any recorded per-pass scoring timing.

Actual output (real numbers and quoted source text, not a paraphrase):

### GB1-scoring timing: **NOT AVAILABLE**
Every `ms/pass` / `s/pass` figure recorded anywhere in this repo is for **MTHFR**, a 656-residue
protein, on 120-position frames. Quoted verbatim:
```
docs/tasks/comparators-and-consolidation/SESSION_LOG.md:2633
M1b-timed: background 1/1 D1A_V179W -> 61.7 s for 120 positions (514 ms/pass)
docs/tasks/comparators-and-consolidation/SESSION_LOG.md:2637
M1b-timed: background 29/29 D10C_I488V -> 75.1 s for 120 positions (626 ms/pass)
docs/tasks/i1-mechanism-followup/FOLLOWUP_LOG.md:279-285
M1b timed: background 1/8 R1_L45D -> 61.3 s for 120 positions (511 ms/pass)
M1b timed: background 6/8 R3_M327V -> 63.1 s for 120 positions (526 ms/pass)
docs/tasks/detection-floor-and-mechanism/DEEPDIVE_LOG.md:2916
"timed: background 1/57 A222_C -> 77.6s for 120 positions (647 ms/pass) ..."
docs/tasks/phase1b-placebo-followup/PHASE1B_LOG.md:519
**511-647 ms/pass** (scripts 63/69/82 runs), stable +-3% per run.
```
**No GB1 per-pass timing exists anywhere in the repo.** The only GB1 scoring runs recorded
whole-script elapsed times, which are dominated by model loading and by N_PERM=10000 / N_BOOT=2000
Monte-Carlo loops, and therefore cannot be decomposed into a per-pass rate:
```
scripts/49  (GB1): "Scored 33 forward passes; 570 (variant, background) pairs"  -> elapsed 10.8s   [OVERNIGHT_LOG.md:815, :830]
scripts/73  (GB1): "Scored 6 forward passes -> 57 delta values (expect 57)"      -> "Elapsed: 42.4s | N_PERM=10000 | SEED=0"  [DEEPDIVE_LOG.md:638, :683]
scripts/74  (GRB2, not GB1): "Scored 106 forward passes -> 689 delta values"      -> "Elapsed: 26.5s"  [DEEPDIVE_LOG.md:1170, :1192]
```
Script 73 is the decisive counter-example: **6 forward passes inside a 42.4 s total.** Six passes
cannot account for 42.4 s while two 10,000-draw Python permutation loops run in the same script.
Quoting 42.4 s or 10.8 s as a per-pass rate would be wrong by a large factor in the wrong direction.

**Per AGENTS §1, this number is NOT extrapolated.** The prior estimate in this project that was off
~15x was inherited from a full-dataset script and applied to a half-dataset run. GB1's 2GB1 56-mer
is **11.7x shorter** than MTHFR's 656, and a transformer's per-pass cost is not linear in length,
so neither 511 ms/pass nor 647 ms/pass may be carried across. **Phase 3b must measure GB1 per-pass
timing in a smoke run first and must not plan against any inherited number.**

### Pass arithmetic (PIN-4 convention: 1 masked-marginal forward pass per scored position)
The scored sequence is the project's 56-residue 2GB1 construct
(`MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE`). The fitness data supplies
partners at **55 positions (2..56)**, and G-2 forbids a partner at the background's own position
(T4-G3 verified `pos1 == pos2` occurs in 0 of 535,917 rows, so this holds structurally).

| framing | passes/background | 400 backgrounds (Appendix A) | 1,045 backgrounds (uncapped) |
|---|---|---|---|
| minimum that yields a usable delta: 55 partner positions − own position | **54** | **21,600** | 56,430 |
| task doc's literal arithmetic: GB1 length 56 − own position | 55 | 22,000 | 57,475 |

Plus a **one-time wild-type arm of 54 passes, computed once and shared by every background** — the
project's own convention, in which scripts 49 and 73 each compute `s_wt` once per focal position
rather than once per background. Totals for the Appendix A roster of 400: **21,654** (minimum) or
**22,054** (literal). The 400 figure is fixed by Appendix A's cap, which T4 showed binds under every
threshold column; the 1,045 figures are shown for reference only and are not the plan.

Scoring position 1 (the initiating Met) produces delta values with no measured partner to pair
against, so it is wasted work in the minimum framing. Which framing Phase 3b adopts is a v2
pre-registration decision, not one to make silently here.

### Phase 3b must not start until Phase 2's scoring has finished
This is a hard precondition, stated here so it is not lost:
> **Phase 3b must not start until Phase 2's scoring has completed.**

Verification of that precondition is the existence of **96 complete `bg_*.csv` files** and a
**96-row `manifest.csv`**. **I did not run that check and did not look.** `data/processed/phase2/`,
`docs/tasks/phase2-full-frame-placebo/`, `run.log`, `run.pid` and `manifest.csv` were neither read
nor written this session, by instruction. Whoever runs the check should confirm the count of
complete `bg_*.csv` files is exactly 96 and that `manifest.csv` has a 96-row body (header excluded),
and should treat a partial count as "not finished" rather than "nearly finished."

The two reasons this is not negotiable: the MPS device is committed to Phase 2, and this machine has
already thrashed to 204 MB unused physical memory and 88% swap when two large jobs competed.

Verdict:
PASS. The pass arithmetic is stated and computed (21,654 minimum / 22,054 literal for the 400-background
roster). GB1 scoring timing is **NOT AVAILABLE** and is explicitly not extrapolated from MTHFR's
511–647 ms/pass; Phase 3b must measure it in a smoke run. The Phase 2 precondition and its
verification are recorded.

Files created/modified: (none — read-only audit)

Anything unexpected or worth flagging:
- **The one number Phase 3b most needs — GB1 ms/pass — does not exist, and the repo contains a
  tempting wrong answer.** Six GB1 forward passes inside a 42.4 s script is proof that the recorded
  GB1 elapsed times are dominated by Monte-Carlo work, not scoring. Treating either 10.8 s or 42.4 s
  as a per-pass figure would overstate cost by an order of magnitude or more; treating MTHFR's
  511–647 ms/pass as applicable would overstate it differently again (11.7x length difference).
  All three are wrong. Measure it.
- The 54-vs-55 passes/background question is not cosmetic: it is 400 wasted forward passes, and it
  hinges on whether the scored sequence includes position 1. Related to the T2-G4b T→Q difference
  at position 2 — the two open items about *which* 56-mer gets scored should be settled together in
  v2, before any timing smoke run, since a smoke run on the wrong sequence wastes the measurement.
- 21,654 passes is small in absolute terms. This design is feasible on cost; the binding constraints
  on Phase 3b are the Phase 2 device contention and the two open v2 decisions, not compute.

---
## T6 — Freeze the pre-registration
Status: PASS
Time started / finished: 2026-09-28 17:30 / 2026-09-28 17:32 PDT
What I did:
Ran the task doc's **exact** line-anchored awk command, verbatim, after `mkdir -p`. No edit of any
kind was made to the frozen text, and no re-extraction was attempted.

```
mkdir -p docs/tasks/phase3b-gb1-regime-map
awk '/^<<<GB1_FROZEN_BEGIN>>>$/{f=1;next} /^<<<GB1_FROZEN_END>>>$/{f=0} f' \
  docs/tasks/phase3a-gb1-acquisition/PHASE3A_GB1_ACQUISITION.md \
  > docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md
```

Actual output (real numbers and quoted source text, not a paraphrase):
```
=== line count ===
73
=== GB1_FROZEN occurrences ===
0
0 (none)
=== sha256 ===
b170bdfff729a017def585047e503a86151ba1e89d2632ae9bc5e8eb9c137613  docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md
=== expected ===
b170bdfff729a017def585047e503a86151ba1e89d2632ae9bc5e8eb9c137613
=== bytes ===
4065
```
**Gate T6-G1: PASS — 73 lines, 0 occurrences of `GB1_FROZEN`, sha256 matches the required value exactly
on the first attempt.**

First three lines and last three lines of the extracted file, verbatim, confirming clean boundaries:
```
# GB1 regime map — pre-registration v1

Frozen 2026-09-28, before any GB1 scoring. Authors: Arnav (PI), Claude (planning).
...
The MTHFR anchor motivated building this map, but the map's rules and covariates were fixed before any
GB1 score existed and do not reference any MTHFR value. Any deviation must be disclosed in the log and,
if it changes a rule or constant, requires a new versioned pre-registration (v2), never an edit to v1.
```

**Confirmed no scoring was launched.** The only occurrences of `torch` / `esm` / `esm.pretrained` in
this session's two scripts are inside the docstrings that forbid them:
```
scripts/128_gb1_olson_verify_and_transplant_repro.py:6:NO MODEL IS LOADED BY THIS SCRIPT. No `import torch`, no `import esm`, no
scripts/128_gb1_olson_verify_and_transplant_repro.py:7:`esm.pretrained.*`, no weight download. This is a hard session constraint
scripts/129_gb1_background_roster.py:5:NO MODEL IS LOADED BY THIS SCRIPT. No `import torch`, no `import esm`, no
```
No executable import of either module exists in either script.

Verdict:
PASS. `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md` is byte-identical to the frozen
Appendix A block: 73 lines, sha256 `b170bdfff729a017def585047e503a86151ba1e89d2632ae9bc5e8eb9c137613`,
4,065 bytes. The frozen text was not edited, and v1 stands as written.

Files created/modified:
- `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md` (new, 4,065 bytes, 73 lines)

Anything unexpected or worth flagging:
- **The line-anchored pattern is doing real work, and its correctness was verified rather than
  assumed.** The source document contains **3** occurrences of the marker text, not 2: the two real
  fence lines plus the awk command quoted inside T6 itself. A looser unanchored pattern would have
  matched the T6 paragraph and leaked the command text into the frozen pre-registration. The
  `^...$` anchors exclude it because the command's lines begin with `awk '` and indentation. The
  extracted file contains **0** occurrences of `GB1_FROZEN`, which is the direct confirmation.
- **T1–T5 surfaced a genuine gap in the frozen text, and it is NOT fixed here.** Appendix A §3
  qualifies backgrounds by "at least 100 high-confidence partners", but the publisher's file has no
  confidence column (T2-G1), so the term is undefined in the data. Six proxy columns are reported
  and none is selected (T4). Appendix A v1 is frozen and its hash is gated, so the resolution is a
  **v2** pre-registration — exactly the mechanism the frozen text's own §8 provides for
  ("requires a new versioned pre-registration (v2), never an edit to v1"). The text is intact and
  hash-verified precisely so that v2 can be a new file rather than an edit.
- A second, smaller v2 item: the T2-G4b `T`/`Q` difference at position 2 and the T5 54-vs-55
  passes-per-background question are both about *which* 56-mer gets scored, and should be settled in
  the same v2, before any timing smoke run.

---
## T7 — Housekeeping (read-only)
Status: PASS
Time started / finished: 2026-09-28 17:35 / 2026-09-28 17:40 PDT
What I did:
`git status --short`, `git diff --stat`, mtime audit of every protected file and every earlier log,
and a grep of this session's own scripts for the string `phase2`. No `git add`, no commit, no push.
Did not read or list the contents of `data/processed/phase2/`,
`docs/tasks/phase2-full-frame-placebo/`, `run.log`, `run.pid` or `manifest.csv`.

Actual output (real numbers and quoted source text, not a paraphrase):

### T7's own required check — `phase2` string in my scripts
```
=== grep MY OWN scripts for the string 'phase2' (T7 requirement) ===
NONE — neither script contains the string 'phase2'
```

### `git diff --stat` (tracked files)
```
 .gitignore       | 17 +++++++++++++++++
 README.md        | 55 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 requirements.txt |  9 ++++++---
 3 files changed, 78 insertions(+), 3 deletions(-)
```
**These three modifications are NOT mine.** mtimes, quoted:
```
2026-09-26 23:32:54  .gitignore
2026-09-26 23:37:27  README.md
2026-09-26 23:33:30  requirements.txt
```
The latest of the three is 2026-09-26 23:37, roughly **two days before this session began** (16:05 on
2026-09-28). They are pre-existing uncommitted work and were left untouched.

### Protected files — none appears in `git status`, and every mtime predates this session
```
2026-09-26 19:37:38  RESULTS.md
2026-09-22 23:18:12  AGENTS.md
2026-09-21 20:17:45  docs/tasks/results-log/MTHFR_RESULTS_LOG.md
2026-09-26 15:21:47  docs/writeups/PROJECT_SUMMARY_FINAL.md
2026-09-27 23:01:32  docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md
```
```
=== protected files: git status lines mentioning them ===
NONE of the protected files appear in git status
```

### Earlier logs — all untouched
```
2026-09-24 18:36:20  docs/tasks/detection-floor-and-mechanism/DEEPDIVE_LOG.md
2026-09-22 11:17:25  docs/tasks/review-triage/OVERNIGHT_LOG.md
2026-09-23 05:18:16  docs/tasks/comparators-and-consolidation/SESSION_LOG.md
2026-09-27 23:03:30  docs/tasks/phase1b-placebo-followup/PHASE1B_LOG.md
```
Every one predates this session's start (2026-09-28 16:05). None was written.

### The task doc itself is provably unmodified
```
=== is the task doc tracked, and is it clean? ===
docs/tasks/phase3a-gb1-acquisition/PHASE3A_GB1_ACQUISITION.md
(no output from git diff --stat = content identical to HEAD = NOT modified)
```
It is a **tracked** file and `git diff` reports it clean, so its content is identical to `HEAD`.
Independently, T6's sha256 gate passing on the first attempt is a second proof that its frozen
Appendix A block is byte-intact.

### This session's own footprint
```
2026-09-28 16:31:48  docs/tasks/phase3a-gb1-acquisition/PHASE3A_LOG.md
2026-09-28 16:31:26  docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md
2026-09-28 16:25:08  scripts/128_gb1_olson_verify_and_transplant_repro.py
2026-09-28 16:29:25  scripts/129_gb1_background_roster.py
```
plus `docs/tasks/phase3a-gb1-acquisition/PHASE3A_T2_T3_FULL_OUTPUT.txt`,
`PHASE3A_T4_FULL_OUTPUT.txt`, `data/external/gb1_olson2014/` (4 files),
`data/processed/task128_gb1_olson_verification.csv`, `task129_gb1_n_partners_distribution.csv`,
`data/processed/gb1_background_roster.csv`.

Verdict:
PASS. No protected file touched, no earlier log touched, the task doc provably unmodified, no
`git add` / commit / push, and neither of this session's scripts contains the string `phase2`.
`data/processed/phase2/` and `docs/tasks/phase2-full-frame-placebo/` were neither read nor written by
this session.

Files created/modified: (no new files beyond those already listed; this entry is the log append)

Anything unexpected or worth flagging:
- **`git status` is not clean, and most of it is not mine.** The working tree carries a large
  pre-existing uncommitted backlog (Phase 2 scripts 123–125, `launch_phase2.sh`, earlier logs,
  ~10 unrelated processed CSVs). Recording this so a future `git status` is not mistaken for damage
  by this session. Only three tracked files are modified and all three predate the session by two
  days.
- `data/processed/phase2/` and `data/processed/phase2_scratch/` show `??` in `git status` and have
  today's mtimes — that is **Phase 2 writing**, exactly as expected and as instructed. Not touched.
- No model was loaded: the only `torch`/`esm` strings in scripts 128 and 129 are inside the
  docstrings that forbid them. The only package installed all session was `openpyxl`.

---
## SUMMARY

### 1. READ THIS FIRST — T3-G1's V54A reproduction
| | |
|---|---|
| **computed rho (full precision)** | **0.12218045112781956** |
| **recorded rho (full precision)** | **0.12218045112781956** |
| **absolute difference** | **0.000000e+00** (bit-for-bit identical) |
| **GATE T3-G1** | **PASS** |
| pre-registered tolerance | 1e-12 (exact, T3-G1a) and 5e-5 (the 4-dp digit the original recorded at, T3-G1b) — both PASS |
| recorded p | 0.3849; recomputed p = 0.3849; absolute difference **0.000e+00** — PASS |
| recorded null | `null mean=-0.0004 sd=+0.1408`; recomputed `null mean = -0.0004 null sd = 0.1408` — reproduced |
| n partners / partner positions | 57 / [39, 40, 41] |
| entry | `docs/tasks/phase3a-gb1-acquisition/PHASE3A_LOG.md` **line 449** |

The recorded value in the task doc ("ρ = +0.122") is a 3-dp rounding; the script printed `+0.1222`
at 4 dp and the stored CSV carries the full double. **Limit stated plainly: the ESM-2 half was loaded
from script 73's cached `delta_esm` column, not re-scored, because loading the model is forbidden
this session.** T3-G1 validates the statistic and the fitness construction — the fitness side was
re-derived from the raw 160,000-genotype file and matched the stored table to 2.220e-16. Under
AGENTS §6 this is a reproduction, not a replication.

### 2. T2's verification gates, with the two discrepancies resolved
| gate | result | value |
|---|---|---|
| T2-G1 high-confidence doubles | **PASS (proxy only)** | raw 535,917; the paper's range [509,693, 517,278] is spanned by exactly 6 consecutive read-depth thresholds t=23..28; **no single t selected** |
| T2-G2 position pairs | **PASS** | **1,485** observed = paper's 1,485 = C(55,2) exactly; 0 rows with pos1==pos2 |
| T2-G3 singles | **PASS** | **1,045** observed = paper's ~1,045 = 55×19 exactly; **0 missing**; 19 per position at all 55 positions |
| T2-G5 Mut-Fitness column identity | **PASS** | max\|diff\| = 4.999e-04 = the file's own 3-decimal storage; it is the **parent single's W**, not the double's score |
| WT sequence | 55 aa, positions 2..56, 1-based, contiguous, 0 residue conflicts | `QYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE` |

**How 1,485-vs-1,540 and ~1,045-vs-1,064 resolved — one fact explains both, and the paper is right
in both cases.** The assayed domain is **55 positions (2..56)**, not 56. The 56th residue of the
2GB1 construct is the initiating Met at position 1, which appears in **no row** of this library.
Therefore: C(55,2) = 1,485 = the paper's pair count exactly; 55×19 = 1,045 = the paper's single count
exactly, complete with zero missing; and C(55,2)×19² = 536,085 = the paper's "possible" exactly. The
doc's 1,540 and 1,064 both come from assuming a 56-mutated-position frame. Neither number was waved
through and neither was attributed to the paper being wrong. (MTHFR's 656-residue 11.7x-length
comparison is not involved in any of this.)

### 3. T1's provenance — what existed vs what was downloaded
**Already on disk, nothing downloaded for these** (all hashed):
| path | bytes | sha256 |
|---|---|---|
| `data/external/GB1_fitness_landscape.txt` | 3,343,308 | `7c9aedcf44416ba8c3a442f041d0b53f8981f8a0bcaaf86afd8ebb8088ec0ad2` |
| `data/processed/task_AA1_gb1_eb_analog.csv` | 6,906 | `0ca45ba329441f1de3af9086c95947c8fadeb8ebb39de41dcec12501f888213c` |
| `data/processed/task_AA1_gb1_signflip_nulls.csv` | 462 | `b02363c63fb8386af4ee7e7306405b819ad9478a055ecaac3ba882d33433f45d` |
| `data/processed/task49_i1_gb1.csv` | 347 | `0706f69580d560b8a79c4ed69acae3b1250e815d234f3187f08372de8294f103` |

**V54A control script: `scripts/73_gb1_estimator_transplant.py`** (background fixed at lines 18–19;
data read at line 131: `data/external/GB1_fitness_landscape.txt`; statistic imported from
`scripts/lib/stats.py::_spearman`).

**Genuinely missing, downloaded — the whole-domain Olson matrix was NOT on disk:**
- FAILED, logged verbatim, no mirror substituted:
  `https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.0/DMS_ProteinGym_substitutions/SUBSTITUTIONS/SPG1_STRSG_Olson_2014.csv`
  → **HTTP 404**, 0 bytes, `text/html`
- SUCCEEDED, publisher's own supplementary file:
  `https://ars.els-cdn.com/content/image/1-s2.0-S0960982214012688-mmc2.xlsx`
  → **HTTP 200**, **28,090,836 bytes**, `application/excel`
  → `data/external/gb1_olson2014/1-s2.0-S0960982214012688-mmc2.xlsx`
  → **sha256 `e912c93cf3d1d95a7d8fc5bb8e8d50a523eb9398c51613b2a74693f07a50fe29`**
  (doi:10.1016/j.cub.2014.09.072; one sheet `DoubleSub.xls`; 535,917 doubles + 1,045 singles + 1 WT;
  read counts only, **no score column and no confidence column**.)
- Compacted derivatives: `gb1_olson2014_doubles.csv` sha256 `89f8e394125d743b5db4bc455a64c59dc6d85f3f1d994f6de51af90f47cc4769`;
  `gb1_olson2014_singles.csv` sha256 `0b2e865e007d606d885d1e8df9f4548a85e4ceeedbff8ab860db7469d65dbfc3`

### 4. T4's roster
`data/processed/gb1_background_roster.csv` — **1,045 backgrounds**, 67,876 bytes,
**sha256 `ee2e7872c19530978f5e64fd3344c6a7597be025dcddb84bd50ac9230e79aae4`**.
Enumerated and hashed. **Selected nothing**: no threshold chosen, no sample drawn, no subset written,
no fitness-based or severity-based selection anywhere. `background_single_fitness_W` is a reported
column only; the roster's sole ordering is lexicographic on `(pos, mut)`.

`n_partners` distribution (min, p25, median, p75, max) — six alternatives plus the unfiltered count,
all reported, **none preferred**:
```
        column    n  min  p25  median  p75  max        mean  n_ge_50  n_ge_100  n_ge_200  n_ge_500
n_partners_raw 1045  950 1026    1026 1026 1026 1025.678469     1045      1045      1045      1045
n_partners_t23 1045  322  986    1013 1022 1026  988.394258     1045      1045      1045      1042
n_partners_t24 1045  315  982    1012 1022 1026  985.873684     1045      1045      1045      1041
n_partners_t25 1045  313  978    1010 1022 1026  983.364593     1045      1045      1045      1041
n_partners_t26 1045  306  975    1009 1021 1026  980.759809     1045      1045      1045      1041
n_partners_t27 1045  301  971    1008 1021 1026  978.267943     1045      1045      1045      1041
n_partners_t28 1045  295  967    1007 1020 1026  975.605742     1045      1045      1045      1041
```
**How many qualify under Appendix A: all 1,045, under every one of the 7 threshold columns.** The
≥100-partner floor excludes nobody (worst case 295 partners at t=28, 950 unfiltered), so Appendix A's
**400 cap is the binding constraint, and it binds by 2.6x**. Its seed-0 sample is therefore
**required, not optional** — and was deliberately not drawn here.

### 5. T5's pass arithmetic and timing
- **Minimum that yields a usable delta: 54 passes/background** (55 partner positions minus the
  background's own, per G-2) → 400 × 54 = **21,600**, plus a one-time 54-pass WT arm shared by all
  backgrounds (the convention scripts 49 and 73 already use) = **21,654 total**.
- **Task doc's literal arithmetic: 56 − 1 = 55 passes/background** → 400 × 55 = **22,000**; with the
  WT arm, **22,054**. Uncapped 1,045-background reference figures: 56,430 / 57,475.
- **GB1 scoring timing: NOT AVAILABLE.** Every `ms/pass` in the repo (511, 514, 519, 522, 526, 545,
  626, 647) is MTHFR, a 656-residue protein, on 120-position frames — 11.7x GB1's length. The only
  GB1 timings recorded are whole-script elapsed times that cannot be decomposed: script 49 = 33 passes
  in 10.8 s; script 73 = **6 passes in 42.4 s** (dominated by two N_PERM=10000 loops). Quoting any of
  them as a per-pass rate would be wrong. Per AGENTS §1 the number was **not extrapolated** from
  MTHFR. **Phase 3b must measure it in a smoke run and must not plan against any inherited figure.**
- **Phase 3b must not start until Phase 2's scoring has finished.** Verify: exactly **96 complete
  `bg_*.csv` files** and a **96-row `manifest.csv`** (header excluded). I did not run that check and
  did not look at those paths.

### 6. T6's sha256 and line count
```
docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md
73 lines | 4,065 bytes | 0 occurrences of "GB1_FROZEN"
sha256 = b170bdfff729a017def585047e503a86151ba1e89d2632ae9bc5e8eb9c137613
```
Extracted with the task doc's exact line-anchored awk command on the first attempt. **GATE T6-G1:
PASS.** The frozen text was not edited; v1 stands as written.

### 7. Every gate
| gate | verdict | value |
|---|---|---|
| T2-G1 high-confidence double count | **PASS (proxy only)** | raw 535,917; t=23..28 span the paper's range; no t selected |
| T2-G2 position pairs covered | **PASS** | 1,485 vs 1,485; n_positions=55; C(55,2)=1,485 |
| T2-G3 singles count | **PASS** | 1,045 vs ~1,045; 0 missing |
| T2-G5 Mut-Fitness is the parent single's W | **PASS** | max\|diff\|=4.999e-04 (file's 3-dp storage) |
| T3-G1a rho exact reproduction | **PASS** | abs diff = 0.000e+00, tol 1e-12 |
| T3-G1b rho reproduces recorded 4-dp value | **PASS** | abs diff = 0.000e+00, tol 5e-5 |
| T3-G1p sign-flip p reproduces 0.3849 | **PASS** | abs diff = 0.000e+00, tol 5e-5 |
| T3-G2 bootstrap identity | **PASS** | abs diff = 0.000e+00, tol 1e-12 |
| T4-G1 one row per single mutant, no duplicates | **PASS** | 1,045 rows, 1,045 unique ids |
| T4-G2 WT residue and fitness agree with the data | **PASS** | 0 rows mut==wt_aa; max\|diff\|=0.000e+00 |
| T4-G3 no partner at a background's own position | **PASS** | 0 of 535,917 rows have pos1==pos2 |
| T4-G4 Appendix A qualification reported per column | **PASS** | n≥100 is 1,045 for all 7 columns; cap binds 7/7 |
| T6-G1 frozen extraction byte-exact | **PASS** | 73 lines, 0 `GB1_FROZEN`, sha256 `b170bdff…c137613` |
| **Total FAIL count** | **0** | |

### 8. Confirmations
- **No model was loaded.** No `import torch`, no `import esm`, no `esm.pretrained.*`, no weight
  download, no MPS/CUDA allocation, in either of this session's scripts. The only occurrences of the
  strings `torch` / `esm` are inside the docstrings that forbid them. The only package installed all
  session was `openpyxl`. Nothing was scored.
- **Nothing under Phase 2 paths was read or written.** `data/processed/phase2/`,
  `data/processed/phase2_scratch/`, `docs/tasks/phase2-full-frame-placebo/`, `run.log`, `run.pid` and
  `manifest.csv` were neither read nor listed nor written. Grepping this session's own scripts for the
  string `phase2` returns **NONE**. (The `?? data/processed/phase2/` line in `git status` is Phase 2
  writing, as expected.)
- **No protected file was touched.** `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `PROJECT_SUMMARY_FINAL.md`,
  `AGENTS.md` and `PHASE2_PREREG.md` appear nowhere in `git status`; every mtime predates this
  session. The task doc itself is tracked and `git diff`-clean. No earlier log was modified. **No
  `git add`, no commit, no push.**

### 9. What this session establishes about the MTHFR anchor
**Nothing. "Nothing" is the expected and correct answer.** This session verified a dataset, a
combinatorial count and an estimator's arithmetic on GB1. It characterises the shift statistic's
regime map in one protein and says nothing — in either direction — about MTHFR. The two systems
differ in protein, length, background, assay (sort-based GB1 binding vs the MTHFR atlas) and
measurement platform. No result here may be described as confirming, supporting or undermining the
MTHFR anchor, and none is. The recorded V54A control remains a correctly-centred null
(ρ = +0.1222, p = 0.3849) that did **not** detect epistasis at that background; reproducing it
exactly reproduces a null, and this session makes no attempt to turn it into anything else.

### 10. The single most important thing to look at first
**`docs/tasks/phase3a-gb1-acquisition/PHASE3A_LOG.md` line 449** — the T3-G1 hard-gate block:

> `COMPUTED rho(delta, e_b) = 0.12218045112781956`
> `RECORDED rho            = 0.12218045112781956`
> `ABSOLUTE DIFFERENCE     = 0.000000e+00`

It is the gate that licenses everything else. A machinery that cannot reproduce the one GB1 result
already in this repo could not be trusted across a thousand backgrounds; this one reproduces it
bit-for-bit, along with the null's mean, sd and p.

**Open items handed to Phase 3b (a v2 pre-registration, never an edit to v1):**
1. **"High-confidence" is undefined in the source data** (T2-G1, T4). Appendix A §3's ≥100
   "high-confidence partners" has no corresponding column. Six proxy columns are reported; none
   selected. **This is the biggest open decision.**
2. **Appendix A's ≥100 floor is inert** — every one of the 1,045 backgrounds clears it by a wide
   margin, so the 400 cap alone shapes the roster. Revisit in v2.
3. **Which 56-mer gets scored** — the T→Q difference at position 2 between the project's 2GB1
   constant and Olson's library (T2-G4b), and the resulting 54-vs-55 passes/background (T5). Settle
   both before any timing smoke run, or the measurement is wasted.
4. **GB1 ms/pass must be measured**, not inherited (T5).
5. Noted, not acted on: `scripts/73_gb1_estimator_transplant.py`'s docstring claims a "+0 correction
   identical to script 33" while its code is a bare `.mean()` with no +1. The code was replicated
   (which is why p reproduces exactly); script 73 is not this session's to edit.
6. Noted, not acted on: n = 57 V54A partners occupy only **3 distinct positions**. The 57 partners
   are not 57 independent units, and the V54A control must never be read that way.
