"""
Script 74 (Group AA, task AA7): a second, independently sourced positive
control -- AA1's exact transplant-and-test methodology re-run on a
double-mutant DMS dataset that is NOT GB1.

WHY / AA7a's BRANCH (task doc lines 118-123 of the task file, lines
100-105 as printed): "Check Group AB's results FIRST (ProteinGym may
supply this for free).  Only if it doesn't: search for a second
double-mutant DMS dataset distinct from GB1, pre-register the exact same
transplant-and-test methodology as AA1 BEFORE running it on the new
dataset, and execute."

AA7a VERDICT (structural check, executed before writing this script):
ProteinGym DOES supply double-mutant assays -- 69 of 217 rows of its
catalog have includes_multiple_mutants == True (data/external/ProteinGym/
DMS_substitutions.csv, copied verbatim from the AB1 fetch, md5
c434631737013fceb56efc98056151e0; reference_files_description.md lines
12-13 define the columns).  The "only if it doesn't" EXTERNAL SEARCH
branch is therefore NOT triggered (disclosed: no web search was done).
Pre-registration + execution apply unconditionally under either branch,
so this script carries AA1's methodology in full, pinned below.

AMBIGUITY LOGGED (most-literal reading, disclosed): the task's happy
path (ProteinGym supplies) does not re-state the pre-register/execute
clause; it is read as applying regardless, because the task's title
("a second, independently sourced positive control") can only be
satisfied by actually running the control.

GB1 DERIVATIVES EXCLUDED (verified from the catalog's own target_seq
before writing this script):
  SPG1_STRSG_Olson_2014 region 228-282 = "QYKLILNGKTLKGETTTEAVDAATAE
  KVFKQYANDNGVDGEWTYDDATKTFTVTE" -- the GB1 B1 domain itself (contains
  the NGVDG motif; identical to GB1_SEQ but for the initiator).  It is
  GB1's full single+pairwise library -> excluded as "not distinct".
  SPG1_STRSG_Wu_2016    region 265-280 = "VDGEWTYDDATKTFTV" -- exactly
  GB1 positions 39-54, i.e. Wu's own four-site library mapped onto the
  precursor (76 singles = 4 x 19 confirms) -> excluded.

PRE-REGISTRATION (fixed in this docstring BEFORE any run and before any
fitness value of any candidate dataset was read; AGENTS sec 6)
-----------------------------------------------------------------------
SELECTION RULE (structural only -- mutant labels, sequences, row counts;
the DMS_score column is not read for selection; see code order):
  S1. Candidate list = catalog rows with includes_multiple_mutants True,
      minus the two GB1 derivatives above.
  S2. Rank: DMS_number_multiple_mutants descending, ties DMS_id
      ascending (deterministic).
  S3. Iterate in rank order.  For each: member must exist in
      zero_shot_substitutions_scores.zip (central directory read by HTTP
      Range, ~KB; the approach was proven feasible in AB1; the parser is
      re-derived here and disclosed as such -- AB1's one-off extractor
      was not committed) and have compressed size <= 60,000,000 B
      (per-member cap) ; cumulative bytes fetched by this script <=
      120,000,000 B (hard stop -> BLOCKED).  Downloaded members are
      cached under data/external/ProteinGym/members/ so smoke + full run
      fetch each member once (the cap counts network bytes only).
  S4. Per-candidate STRUCTURE GATES (failure prints the reason and the
      next candidate is tried -- this ladder is fixed here, pre-run):
        a. seq_len <= 1022 (ESM-2 context limit);
        b. scores schema has mutant / mutated_sequence / DMS_score;
        c. all rows' mutated_sequence length == seq_len;
        d. mutant labels parse as substitutions (single "A5C"-style or
           delimiter-joined triples; delimiter list below); unparseable
           non-WT rows <= 1%;
           *** POST-HOC AMENDMENT, DISCLOSED (AGENTS sec 6): the
           delimiter list was written without having displayed a single
           real multi-mutant label and listed only "_", "-", "+".
           Gate S4d fired exactly as registered in the smoke run
           (GRB2 62,332/63,366 and Sarkisyan 50,630/51,714 labels
           rejected), and inspecting those labels (mutant column only,
           no fitness) showed the real format is ":"-joined
           ("T159M:D166V").  The amendment ADDS ":" to the list.  The
           gate, its <=1% threshold, the ranking, and the ladder are
           UNCHANGED; no fitness value was involved in the amendment;
           the wasted member fetch is disclosed in the [AA7] log entry
           and printed by this script at startup. ***
        e. every single-mutant label's WT letter matches target_seq at
           its stated 1-based position (positioning gate; any mismatch
           rejects the candidate -- no offset is guessed);
        f. >= 50 exact-double rows (|mutations| == 2) usable for the
           background choice below (N_ROWS_MIN = 50, chosen BEFORE any
           run to match/exceed AA1's 57-row scale as closely as a
           pairwise-structured assay allows).
  S5. BACKGROUND: the substitution (position, alt) that (i) exists as a
      measured single row and (ii) appears in the most exact-double
      rows; ties broken by lexicographic (position, alt).  Count-based =
      fitness-blind (library structure, not fitness).
  S6. PARTNERS (= AA1's 57 variants, generalized): every measured single
      substitution s at a position != bg's position, with standard
      residue letter, for which the exact double row {s, bg} also
      exists.  NO fitness filter (A4).  Post-join n must be >= 50 (the
      S4f threshold applied again after the join); a candidate landing
      below 50 continues down the same pre-registered ladder (its
      reason printed) -- the first candidate reaching >= 50 partners
      wins.  No candidate is ever re-entered or re-ranked.
  S7. First eligible candidate in rank order is SELECTED; the script
      prints "SELECTION FROZEN" with its structural fingerprint BEFORE
      any fitness value is read (DMS_score is loaded in a second pass
      after freezing).

ADAPTATIONS of AA1's construction (AA1's A1-A6 carried verbatim, new
ones named explicitly -- this is NOT a copy-paste):
  A1-A6 identical to script 73: single-point residual replaces the
     4-concentration WLS line; uniform weights (no per-genotype SEs);
     multiplicative no-interaction expectation on the fitness scale;
     no fitness-based row filtering; sign-flip cell = ONE residual per
     variant; Null 2 blocks = partner SITE (script 33's region check
     omitted -- no MTHFR regions here -- as AA1 omitted it).
  A7. WT ANCHOR (new, forced by the data): AA1 had f(WT) = 1.0 exactly
     by GB1 file normalization.  ProteinGym score files ship only
     mutant rows (verified on the fetched MTHR file: labels are
     A5C/A54C/A222V-style only, no zero-mutation row).  Fixed rule:
       A7a. IF a zero-mutation row exists (mutated_sequence ==
            target_seq), f(WT) = mean of its DMS_score values;
       A7b. ELSE c-hat = median over partner rows of f(v+bg)/f(v)
            (rows with f(v) == 0 excluded from the median ONLY, with
            count printed) and E[f(v+bg)] = f(v) * c-hat, where c-hat
            plays the role of f(bg)/f(WT).  This is a FIXED estimator
            chosen before any value was read; it is disclosed as this
            control's main construction difference from AA1, not tuned.
  A8. BACKGROUND SELECTION (new): AA1's background was chemically
     fixed (V54A, parallel to A222V).  With no chemical analog in an
     arbitrary assay, the pre-registered rule is S5's most-frequent
     count rule -- fitness-blind, deterministic.  The difference from
     AA1's chemical parallelism is disclosed in the limitations print.
  A9. PARTNER SET: AA1 had exactly the other three assayed sites; here
     partners may span many positions (library-determined).  Position
     spread vs the background is printed (min/median distance) so the
     local-vs-distant scope question (AA5) is visible, not hidden.

delta_ESM (AA1b definition, identical machinery): delta(v) =
S(v | background sequence) - S(v | WT target sequence), S = masked
marginal log-odds at v's position via scripts.lib.esm_scoring
.get_position_logprobs, ESM-2 t33 650M (the same cached model AA1
used); forward passes = 2 x number of distinct partner positions.

STATISTICS (script 33's code path, as transplanted in script 73;
N_PERM from env, default 10000; SEED 0):
  - Primary: signed Spearman rho(delta_ESM, e_b) via scripts.lib.stats
    _spearman.
  - NULL 1 sign-flip re-derivation: independent +/-1 per variant cell,
    re-derive e_b, recompute rho; p = mean(|null| >= |obs|); centreing
    by script 33's exact expression |mean| < 2*sd/sqrt(N_PERM)*3;
    excess over null and frac_artifact printed as script 33 prints
    them; signed AND absolute versions both run.
  - IDENTITY GATES (script 33's): all-+1 reproduce the stored e_b
    exactly (max|diff| < 1e-6), all--1 give its exact negation;
    failure -> sys.exit(1).
  - NULL 2 site-block permutation of delta over partner positions.
  - ABSOLUTE null 1 is DEGENERATE under single-cell flips (|flip*r| =
    |r|) -- AA1 found this post-hoc and disclosed it; here it is
    pre-registered as a known structural fact and printed as such.

DECISION RULES (pre-registered, reported without tuning)
  - "Instrument behaves" IFF the signed null centres on zero by script
    33's expression.  AA1's answer on GB1 was YES; this run asks
    whether that centreing REPLICATES on an independent dataset.
  - "Detects established epistasis" IFF signed two-sided p < 0.05.
  - Both reported; neither tuned.

LIMITATIONS printed by this script (AGENTS sec 6): single background;
flip units = n rows over #partner positions (p-precision from
N_PERM draws, not n independent sites); A7b branch if fired; A8
count-based background has no chemical parallel to A222V; absolute
sign-flip null degenerate; partner position spread printed.

Outputs: data/processed/task_AA7_second_control_eb.csv
         data/processed/task_AA7_second_control_nulls.csv
"""
import sys, os, time, hashlib, warnings, io, re, struct, zlib, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from scripts.lib.stats import _spearman

N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "external" / "ProteinGym" / "DMS_substitutions.csv"
CACHE = ROOT / "data" / "external" / "ProteinGym" / "members"
PROC = ROOT / "data" / "processed"
ZIP_URL = ("https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/"
           "zero_shot_substitutions_scores.zip")
MEMBER_CAP = 60_000_000
CUM_CAP = 120_000_000
EXCLUDE_GB1 = {"SPG1_STRSG_Olson_2014", "SPG1_STRSG_Wu_2016"}
N_ROWS_MIN = 50
SEQ_MAX = 1022
UNPARSE_MAX_FRAC = 0.01
MTHFR_RHO = -0.08811806424891734
AA = set("ACDEFGHIKLMNPQRSTVWY")
SINGLE_RE = re.compile(r"^([A-Za-z*]+)(\d+)([A-Za-z*]+)$")
MULTI_DELIMS = [":", "_", "-", "+"]   # ":" added post-hoc, see S4d note

FETCHED = {"bytes": 0}


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(1)


def pstr(p, n):
    return f"<{1.0/n:.4f}" if p == 0 else f"{p:.4f}"


# ---------------------------------------------------------------- ZIP range
def http_range(spec):
    """Range GET; counts network bytes; enforces CUM_CAP; refuses 200s."""
    req = urllib.request.Request(ZIP_URL, headers={"Range": f"bytes={spec}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        code = r.status
        if code != 206:
            raise RuntimeError(f"server returned {code} for Range {spec}; "
                               f"refusing full download")
        body = r.read()
    FETCHED["bytes"] += len(body)
    if FETCHED["bytes"] > CUM_CAP:
        print(f"BLOCKED: cumulative fetch {FETCHED['bytes']} B > cap "
              f"{CUM_CAP} B")
        raise SystemExit(2)
    return body


def read_central_dir():
    tail = http_range("-65536")
    pos = tail.rfind(b"PK\x05\x06")
    if pos < 0:
        raise RuntimeError("EOCD signature not found in final 64KB")
    (_sig, _d, _dd, _ed, n_ent, cd_size, cd_off, _cl) = struct.unpack_from(
        "<4s4H2LH", tail, pos)
    cd = http_range(f"{cd_off}-{cd_off + cd_size - 1}")
    entries, off = {}, 0
    for _ in range(n_ent):
        vals = struct.unpack_from("<4s6H3L5H2L", cd, off)
        sig = vals[0]
        if sig != b"PK\x01\x02":
            raise RuntimeError(f"bad central-directory signature at {off}")
        method, csize, usize = vals[4], vals[8], vals[9]
        fnlen, extralen, commlen = vals[10], vals[11], vals[12]
        localoff = vals[16]
        name = cd[off + 46:off + 46 + fnlen].decode("utf-8")
        entries[name] = {"method": method, "csize": csize,
                         "usize": usize, "localoff": localoff}
        off += 46 + fnlen + extralen + commlen
    return entries


def get_member(name, ent, budget_note):
    """Cache-first; else ranged fetch + stream-inflate (AB1's proven
    approach, parser re-derived here)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / Path(name).name
    if path.exists():
        print(f"    member {name}: CACHED on disk ({path.stat().st_size} B, "
              f"0 network bytes) {budget_note}")
        return path.read_bytes()
    lh = http_range(f"{ent['localoff']}-{ent['localoff'] + 29}")
    sig, _v, _fl, _m, _t, _d, _crc, _cs, _us, fnlen, extralen = \
        struct.unpack("<4s5H3L2H", lh)
    if sig != b"PK\x03\x04":
        raise RuntimeError("bad local-header signature")
    start = ent["localoff"] + 30 + fnlen + extralen
    before = FETCHED["bytes"]
    data = http_range(f"{start}-{start + ent['csize'] - 1}")
    raw = zlib.decompress(data, -15) if ent["method"] == 8 else \
        (data if ent["method"] == 0 else
         (_ for _ in ()).throw(RuntimeError(f"method {ent['method']}")))
    path.write_bytes(raw)
    print(f"    member {name}: fetched {FETCHED['bytes'] - before} B "
          f"(csize {ent['csize']}, usize {ent['usize']}) {budget_note}; "
          f"cumulative {FETCHED['bytes']} B / cap {CUM_CAP} B")
    return raw


# ------------------------------------------------------- structure parsing
def parse_label(label):
    """-> frozenset of (pos, alt) or None (unparseable) or empty frozenset
    (WT row).  Structural only: never touches fitness."""
    if label in ("", "WT", "wt", "_WT_", "="):
        return frozenset()
    if SINGLE_RE.match(label):
        parts = [label]
    else:
        parts = None
        for d in MULTI_DELIMS:
            cand = label.split(d)
            if len(cand) >= 2 and all(SINGLE_RE.match(p) for p in cand):
                parts = cand
                break
        if parts is None:
            return None
    muts = set()
    for p in parts:
        m = SINGLE_RE.match(p)
        wt, pos, alt = m.group(1), int(m.group(2)), m.group(3)
        muts.add((pos, wt, alt))
    return frozenset(muts)


def evaluate_candidate(row, entries):
    """Return (status, detail, struct_df, seq) -- structural only."""
    name = row.DMS_filename
    seq, L = row.target_seq, int(row.seq_len)
    if L > SEQ_MAX:
        return "reject", f"seq_len {L} > {SEQ_MAX}", None, None
    if name not in entries:
        return "reject", f"{name} not in zip central directory", None, None
    ent = entries[name]
    if ent["csize"] > MEMBER_CAP:
        return "reject", (f"member csize {ent['csize']} > per-member cap "
                          f"{MEMBER_CAP}"), None, None
    note = f"(rank: {int(row.DMS_number_multiple_mutants)} multi-mutants)"
    try:
        csv_bytes = get_member(name, ent, note)
    except SystemExit:
        raise
    except Exception as e:
        return "reject", f"fetch error: {e}", None, None

    head = pd.read_csv(io.BytesIO(csv_bytes), nrows=0)
    need = {"mutant", "mutated_sequence", "DMS_score"}
    if not need.issubset(set(head.columns)):
        return "reject", f"schema lacks {need - set(head.columns)}", None, None
    st = pd.read_csv(io.BytesIO(csv_bytes),
                     usecols=["mutant", "mutated_sequence"])
    st["mutated_sequence"] = st["mutated_sequence"].astype(str)
    st["mutant"] = st["mutant"].astype(str)
    bad_len = int((st["mutated_sequence"].str.len() != L).sum())
    if bad_len:
        return "reject", f"{bad_len} rows with mutated_sequence != seq_len", \
            None, None

    parsed, n_unparse = [], 0
    for lab in st["mutant"]:
        p = parse_label(lab)
        if p is None:
            n_unparse += 1
        parsed.append(p)
    if len(st) and n_unparse / len(st) > UNPARSE_MAX_FRAC:
        return "reject", f"{n_unparse}/{len(st)} labels unparseable " \
                         f"(> {UNPARSE_MAX_FRAC:.0%})", None, None

    st["muts"] = [frozenset() if (p is None or len(p) == 0) else p
                  for p in parsed]
    st["is_wt_seq"] = st["mutated_sequence"] == seq
    # position/letter gate: every SINGLE label's WT letter vs target_seq
    bad_single = []
    singles = []
    for i, rowi in st.iterrows():
        p = parsed[i]
        if p is None or len(p) != 1:
            continue
        (pos, wt, alt), = tuple(p)
        if not (1 <= pos <= L) or seq[pos - 1] != wt:
            bad_single.append(rowi["mutant"])
        else:
            singles.append(((pos, alt), i))
    if bad_single:
        return "reject", (f"{len(bad_single)} single labels disagree with "
                          f"target_seq (e.g. {bad_single[:3]}) -- no offset "
                          f"guessing"), None, None

    # _key elements are 3-tuples (pos, wt, alt) -> normalize to (pos, alt)
    st["_key"] = [tuple(sorted((pp, aa) for (pp, _w, aa) in p))
                  if len(p) == 2 else None for p in st["muts"]]
    n_double = int(sum(1 for p in st["muts"] if len(p) == 2))
    if n_double < N_ROWS_MIN:
        return "reject", f"only {n_double} exact-double rows < {N_ROWS_MIN}", \
            None, None
    st.attrs["n_unparse"] = n_unparse
    st.attrs["n_double"] = n_double
    st = st.drop(columns=["mutated_sequence"])
    return "accept", (f"{len(st)} rows, {n_double} exact doubles, "
                      f"{n_unparse} unparseable dropped"), st, seq


def choose_bg_and_partners(st, seq):
    """S5/S6: count-based, fitness-blind."""
    singles = {}   # (pos, alt) -> struct row index
    for i in st.index:
        p = st.at[i, "muts"]
        if len(p) == 1:
            (pos, wt, alt), = tuple(p)
            if 1 <= pos <= len(seq) and seq[pos - 1] == wt:
                singles[(pos, alt)] = i
    dbl = {}       # key tuple -> struct row index
    for i in st.index:
        if len(st.at[i, "muts"]) == 2:
            dbl[st.at[i, "_key"]] = i
    counts = {}
    for k in dbl:
        for mut in k:                 # (pos, alt); wt letters already gated
            if mut in singles:
                counts[mut] = counts.get(mut, 0) + 1
    if not counts:
        raise RuntimeError("no bg candidate with a measured single")
    bg = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    partners = []
    for (pos, alt), si in singles.items():
        if pos == bg[0] or alt not in AA:
            continue
        key = tuple(sorted((bg, (pos, alt))))
        if key in dbl:
            partners.append({"site": pos, "variant": alt,
                             "single_row": si, "double_row": dbl[key]})
    bg_info = {"bg": bg, "bg_count_in_doubles": counts[bg],
               "n_candidates": len(counts), "bg_single_row": singles[bg]}
    return partners, bg_info


def main():
    t0 = time.time()
    print("=" * 74)
    print("AA7 -- second double-mutant positive control (AA1 methodology "
          "re-run, pre-registered)")
    print("=" * 74)
    print("POST-HOC AMENDMENT ACTIVE (disclosed per AGENTS sec 6): "
          "multi-label delimiter list amended to include ':' after gate "
          "S4d fired in the smoke run (00:08 run, GRB2+Sarkisyan labels; "
          "diagnosis: every rejected label's only non-alnum char is ':'). "
          "Gate, threshold (<=1%), ranking and ladder unchanged; no "
          "fitness value involved. Prior smoke-run member fetches: "
          "GRB2 49,594,484 B (cached, reused), Sarkisyan 41,507,707 B "
          "(cached, NOT reused -- GRB2 won at the higher rank), one "
          "further member 34,129,661 B fetched but "
          "discarded when the script's own 120 MB cumulative cap fired "
          "(WASTED -- disclosed).")
    if not META.exists():
        fail(f"missing metadata: {META}")
    md5 = hashlib.md5(META.read_bytes()).hexdigest()
    if md5 != "c434631737013fceb56efc98056151e0":
        fail(f"metadata md5 {md5} != c434631737013fceb56efc98056151e0")
    cat = pd.read_csv(META)
    print(f"Catalog gate PASSED: {len(cat)} assays, md5={md5}")

    cand = cat[cat["includes_multiple_mutants"].astype(str).str.upper()
               .isin(["TRUE", "1"]) & ~cat["DMS_id"].isin(EXCLUDE_GB1)]
    cand = cand.sort_values(["DMS_number_multiple_mutants", "DMS_id"],
                            ascending=[False, True]).reset_index(drop=True)
    print(f"S1/S2: {len(cand)} candidates with multiple mutants after "
          f"excluding the 2 GB1 derivatives (SPG1_STRSG_Olson_2014, "
          f"SPG1_STRSG_Wu_2016); ranked by multi-mutant count desc")

    entries = read_central_dir()
    print(f"Central directory parsed: {len(entries)} members "
          f"({FETCHED['bytes']} B fetched so far)")

    selected = None
    for rank, row in cand.iterrows():
        status, detail, st, seq = evaluate_candidate(row, entries)
        print(f"[rank {rank}] {row.DMS_id}: {status} -- {detail}")
        if status == "accept":
            partners, bg_info = choose_bg_and_partners(st, seq)
            print(f"    -> bg (S5): {bg_info['bg']} appears in "
                  f"{bg_info['bg_count_in_doubles']} exact doubles among "
                  f"{bg_info['n_candidates']} countable candidates | "
                  f"partners with both arms (S6): {len(partners)}")
            if len(partners) >= N_ROWS_MIN:
                selected = (row, st, seq, partners, bg_info)
                print("SELECTION FROZEN -- structural counts only; no "
                      "fitness value has been read or printed for any "
                      "candidate (DMS_score loaded only now, second pass)")
                break
            print(f"    -> rejected post-join: {len(partners)} partners "
                  f"< {N_ROWS_MIN} (pre-registered continuation rule: the "
                  f"first candidate with >= 50 partners wins)")
        # structural rejects continue down the pre-registered ladder
    if selected is None:
        print(f"BLOCKED: no eligible candidate after {len(cand)} ranked "
              f"tries (cumulative fetch {FETCHED['bytes']} B)")
        raise SystemExit(2)
    row, st, seq, partners, bg_info = selected
    bg = bg_info["bg"]
    L = len(seq)
    print(f"\nSELECTED: {row.DMS_id} ({row.first_author} {int(row.year)}), "
          f"seq_len={L}, region {row.region_mutated}, "
          f"{int(row.DMS_number_single_mutants)} singles / "
          f"{int(row.DMS_number_multiple_mutants)} multi in catalog")
    print(f"Background (S5, count-based fitness-blind): position "
          f"{bg[0]} {seq[bg[0]-1]}->{bg[1]} (B{bg[0]}{bg[1]}), "
          f"present in {bg_info['bg_count_in_doubles']} exact doubles")
    dists = sorted(abs(p["site"] - bg[0]) for p in partners)
    print(f"Partners (S6): n={len(partners)} over "
          f"{len(set(p['site'] for p in partners))} positions; distance "
          f"from bg position: min={dists[0]}, median={dists[len(dists)//2]}, "
          f"max={dists[-1]} (A9 -- local/distant mix printed, not hidden)")
    print(f"Frozen structural fingerprint: struct rows in member = "
          f"{len(st)}, exact doubles = {st.attrs['n_double']}, "
          f"unparseable dropped = {st.attrs['n_unparse']}")

    # ---- second pass: fitness values are read only NOW -------------------
    csv_bytes = (CACHE / Path(row.DMS_filename).name).read_bytes()
    sc = pd.read_csv(io.BytesIO(csv_bytes),
                     usecols=["mutant", "DMS_score"])
    sc["mutant"] = sc["mutant"].astype(str)
    if len(sc) != len(st) or not (sc["mutant"].values ==
                                  st["mutant"].values).all():
        fail("fitness pass misaligned with structure pass")
    st = st.reset_index(drop=True)
    sc = sc.reset_index(drop=True)
    st["f"] = pd.to_numeric(sc["DMS_score"], errors="coerce")

    f_bg = float(st.at[bg_info["bg_single_row"], "f"])
    wt_idx = [i for i in st.index if bool(st.at[i, "is_wt_seq"])]
    n_nan_needed = 0
    rows = []
    branch, f_wt, chat = None, np.nan, np.nan
    if wt_idx:
        branch = "A7a"
        f_wt = float(st.loc[wt_idx, "f"].mean())
    else:
        branch = "A7b"
    for p in partners:
        f_v, f_d = float(st.at[p["single_row"], "f"]), \
            float(st.at[p["double_row"], "f"])
        rows.append({**p, "f_single": f_v, "f_double": f_d})
    eb = pd.DataFrame(rows)
    nan_mask = eb[["f_single", "f_double"]].isna().any(axis=1)
    n_nan_needed = int(nan_mask.sum())
    if n_nan_needed:
        eb = eb[~nan_mask].reset_index(drop=True)
        print(f"DROPPED (NaN fitness in a needed arm, structural not "
              f"fitness-based): {n_nan_needed} rows -> n={len(eb)}")
    if branch == "A7b":
        pos_ratio = eb[(eb["f_single"] != 0) & np.isfinite(eb["f_single"])]
        chat = float((pos_ratio["f_double"] / pos_ratio["f_single"]).median())
        n_zero_single = int((eb["f_single"] == 0).sum())
        if n_zero_single:
            print(f"  A7b: {n_zero_single} rows with f(v)==0 excluded from "
                  f"the c-hat MEDIAN only (kept in construction; A4)")
        eb["expected"] = eb["f_single"] * chat
        eb["e_b"] = eb["f_double"] - eb["expected"]
        print(f"WT-anchor branch {branch}: no zero-mutation row in the "
              f"scores file (as verified on the MTHR file) -> "
              f"c-hat = median f(v+bg)/f(v) = {chat:.6f} over "
              f"{len(pos_ratio)} partner rows")
    else:
        eb["expected"] = eb["f_single"] * f_bg / f_wt
        eb["e_b"] = eb["f_double"] - eb["expected"]
        print(f"WT-anchor branch {branch}: {len(wt_idx)} zero-mutation "
              f"row(s) -> f(WT) = {f_wt:.6f}")
    print(f"f(bg) = {f_bg:.6f}  [first read of this value, S5 was frozen "
          f"before this line]")
    if f_bg <= 0:
        print("  *** LIMITATION: background fitness non-positive; "
              "multiplicative expectation collapses; reported, not "
              "re-selected (switching bg after seeing fitness = "
              "data-dependent, NOT done). ***")
    n_np_s = int((eb["f_single"] <= 0).sum())
    n_np_d = int((eb["f_double"] <= 0).sum())
    n_np_e = int((eb["expected"] <= 0).sum())
    if not np.isfinite(eb["e_b"]).all():
        fail("non-finite e_b in construction")
    print(f"e.b analog: n={len(eb)} | mean={eb['e_b'].mean():+.4f} "
          f"median={eb['e_b'].median():+.4f} | min={eb['e_b'].min():+.4f} "
          f"max={eb['e_b'].max():+.4f}")
    print(f"Non-positive-value counts (A4: kept, never filtered): single "
          f"arm {n_np_s}, double arm {n_np_d}, expectation {n_np_e} of "
          f"{len(eb)}")
    print("Adaptations A1-A9 active: single-point residual replaces WLS "
          "line; uniform weights; multiplicative expectation; no row "
          "filtering; flip cell = variant; Null-2 blocks = partner site "
          "(region check omitted); WT anchor branch " + branch +
          "; bg = count rule (no chemical parallel to A222V, A8); "
          "partners = all library-determined positions (A9).")

    # ---------------- delta_ESM analog (AA1b, identical machinery) --------
    from scripts.lib.esm_scoring import get_position_logprobs, get_device
    import esm
    device = get_device()
    print(f"\nLoading ESM-2 t33 650M on {device}...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()

    seq_bg_l = list(seq)
    seq_bg_l[bg[0] - 1] = bg[1]
    seq_bg = "".join(seq_bg_l)
    positions = sorted(set(eb["site"]))
    n_pass, deltas, n_vocab_drop = 0, {}, 0
    for p in positions:
        s_wt = get_position_logprobs(model, alphabet, bc, seq, p, device)
        n_pass += 1
        s_bg = get_position_logprobs(model, alphabet, bc, seq_bg, p, device)
        n_pass += 1
        for v in eb.loc[eb["site"] == p, "variant"]:
            if v in s_bg and v in s_wt:
                deltas[(p, v)] = s_bg[v] - s_wt[v]   # script 49: sc_b - s_b0
            else:
                n_vocab_drop += 1
    if n_vocab_drop:
        print(f"DROPPED (residue absent from scorer vocabulary): "
              f"{n_vocab_drop} deltas")
    print(f"Scored {n_pass} forward passes -> {len(deltas)} delta values")
    eb["delta_esm"] = [deltas.get((r.site, r.variant), np.nan)
                       for r in eb.itertuples()]
    n_delta_drop = int(eb["delta_esm"].isna().sum())
    if n_delta_drop:
        print(f"DROPPED (delta missing after scorer-vocabulary gate): "
              f"{n_delta_drop} rows")
    df = eb.dropna().reset_index(drop=True)
    if len(df) < N_ROWS_MIN:
        fail(f"merged table rows {len(df)} < {N_ROWS_MIN}")
    if not np.isfinite(df["delta_esm"]).all():
        fail("non-finite delta_esm")
    print(f"delta_ESM analog: mean={df['delta_esm'].mean():+.4f} "
          f"median={df['delta_esm'].median():+.4f} "
          f"min={df['delta_esm'].min():+.4f} max={df['delta_esm'].max():+.4f}")

    # ------------- script 33's sign-flip path (as in script 73) -----------
    Rs = df["e_b"].to_numpy()[:, None]
    own_eb = df["e_b"].to_numpy()
    dv = df["delta_esm"].to_numpy()
    adv = np.abs(dv)

    def refit(r_cells):
        return r_cells.ravel()

    print("\n" + "=" * 74)
    print("SANITY CHECKS (script 33's, transplanted: test the test first)")
    print("=" * 74)
    chk_p = refit(Rs * 1.0)
    chk_m = refit(Rs * -1.0)
    ok = np.isfinite(chk_p) & np.isfinite(own_eb)
    dpos = np.abs(chk_p[ok] - own_eb[ok]).max()
    dneg = np.abs(chk_m[ok] + own_eb[ok]).max()
    print(f"  all-+1 flips reproduce own_e_b exactly: max|diff|={dpos:.3e}")
    print(f"  all--1 flips give exactly -own_e_b:     max|diff|={dneg:.3e}")
    if dpos > 1e-6 or dneg > 1e-6:
        print("  *** SANITY CHECK FAILED -- row alignment is wrong. Stop. ***")
        sys.exit(1)

    print("\nDesign summary for AA2 (unit of analysis):")
    print(f"  rows={len(df)} | flip units (cells)={Rs.size} (one +/-1 per "
          f"variant, A5) | partner positions={df['site'].nunique()} | "
          f"backgrounds=1 | MTHFR contrast: 10,757 variants x 4 conc cells "
          f"= 43,028 cells, 654 positions | AA1 contrast: 57 rows, "
          f"3 sites, 1 background")

    rng = np.random.default_rng(SEED)
    rows_out = []
    print("\n" + "=" * 74)
    print(f"NULL 1 -- SIGN-FLIP RE-DERIVATION ({N_PERM} permutations)")
    print("=" * 74)
    for pred, lbl, signed in [(dv, "signed delta_ESM vs signed e_b", True),
                              (adv, "absolute |delta_ESM| vs |e_b|", False)]:
        obs = _spearman(pred, own_eb if signed else np.abs(own_eb))
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            eb_p = refit(Rs * rng.choice([-1.0, 1.0], size=Rs.shape))
            g = np.isfinite(eb_p) & np.isfinite(pred)
            null[p] = _spearman(pred[g], eb_p[g] if signed
                                else np.abs(eb_p[g]))
        pv = float((np.abs(null) >= abs(obs)).mean())
        excess = obs - null.mean()
        frac = 1 - abs(excess) / abs(obs) if obs != 0 else np.nan
        print(f"  {lbl}")
        print(f"    observed={obs:+.4f}  null mean={null.mean():+.4f} "
              f"sd={null.std():+.4f}  p={pstr(pv, N_PERM)}")
        print(f"    excess over null={excess:+.4f}  "
              f"({100*frac:.0f}% of the raw value is structural artifact)")
        print(f"    -> {'SURVIVES' if pv < 0.05 else 'does NOT survive'}")
        if signed:
            centred = abs(null.mean()) < 2 * null.std() / np.sqrt(N_PERM) * 3
            print(f"    null-centring check: null mean {'IS' if centred else 'is NOT'} "
                  f"consistent with zero -- {'machinery behaving' if centred else 'INVESTIGATE'}")
            print(f"    PRE-REGISTERED READS: instrument behaves = "
                  f"{'YES' if centred else 'NO'}; detects established "
                  f"epistasis = {'YES' if pv < 0.05 else 'NO'} "
                  f"(signed two-sided p < 0.05); AA1's GB1 centreing "
                  f"answer was YES -- replication question answered by "
                  f"the line above")
        else:
            print("    STRUCTURAL NOTE (pre-registered from AA1's "
                  "disclosed post-hoc finding): with ONE cell per "
                  "variant, |flip * r| = |r| is invariant to the sign "
                  "flips, so the absolute sign-flip null equals the "
                  "observation IDENTICALLY (p = 1 by construction); "
                  "DEGENERATE here, carries no information.")
        rows_out.append({"null": "signflip", "variant": lbl, "observed": obs,
                         "null_mean": float(null.mean()),
                         "null_sd": float(null.std()),
                         "excess_over_null": excess, "frac_artifact": frac,
                         "p": pv, "n_perm": N_PERM, "survives": pv < 0.05})

    print("\n" + "=" * 74)
    print(f"NULL 2 -- SITE-BLOCK PERMUTATION (weaker; association only; "
          f"A6: {df['site'].nunique()} blocks)")
    print("=" * 74)
    sub = df[["site", "delta_esm", "e_b"]].dropna()
    blocks = [g["delta_esm"].to_numpy()
              for _, g in sub.groupby("site")]
    ebv = np.concatenate([g["e_b"].to_numpy()
                          for _, g in sub.groupby("site")])
    obs2 = _spearman(np.concatenate(blocks), ebv)
    null2 = np.empty(N_PERM)
    for p in range(N_PERM):
        null2[p] = _spearman(
            np.concatenate([blocks[i] for i in rng.permutation(len(blocks))]),
            ebv)
    pv2 = float((np.abs(null2) >= abs(obs2)).mean())
    print(f"  observed={obs2:+.4f}  null mean={null2.mean():+.4f} "
          f"sd={null2.std():+.4f}  p={pstr(pv2, N_PERM)}")
    print("  This asks whether the pairing beats chance, NOT whether the")
    print("  interaction exceeds measurement noise.  Null 1 is the real test.")
    rows_out.append({"null": "site_block", "variant": "signed",
                     "observed": obs2, "null_mean": float(null2.mean()),
                     "null_sd": float(null2.std()), "p": pv2,
                     "n_perm": N_PERM, "survives": pv2 < 0.05})

    print("\n" + "=" * 74)
    print("LIMITATIONS (printed here per AGENTS sec 6)")
    print("=" * 74)
    print(f"  - {len(df)} flip units over {df['site'].nunique()} partner "
          f"positions and 1 background: p-precision comes from {N_PERM} "
          f"draws, NOT from independent sites.")
    print(f"  - WT-anchor branch {branch}"
          + (f" (f(WT) = {f_wt:.6f})" if branch == "A7a"
             else f" (c-hat = {chat:.6f}; fixed pre-run estimator, main "
                  f"construction difference from AA1's f(WT)=1.0)")
          + "; background chosen by count rule (A8) -- NO chemical "
            "parallel to A222V/V54A.")
    print(f"  - Background fitness f(bg) = {f_bg:.6f} (read once).")
    print(f"  - Absolute sign-flip null degenerate under single-cell "
          f"flips (pre-registered structural fact from AA1).")
    print(f"  - Partner positions span distances {dists[0]}-{dists[-1]} "
          f"from bg (A9): includes non-adjacent pairs -- do not read "
          f"this run as a purely local control or vice versa.")
    print(f"  - Scale references: MTHFR signed "
          f"rho(delta_ESM, own_e_b) = {MTHFR_RHO}; AA1/GB1 signed "
          f"rho = +0.1222 (n=57, p=0.3849 plain null -- value verified "
          f"post-run from task_AA1_gb1_signflip_nulls.csv; an earlier "
          f"build of this line printed a wrong '0.7405-ish' reference "
          f"from memory, DISCLOSED in DEEPDIVE_LOG [AA7]; no statistic "
          f"of this run depends on that line).")
    print(f"  - Fetch accounting: {FETCHED['bytes']} network bytes this "
          f"run / per-member cap {MEMBER_CAP} / script cap {CUM_CAP}.")

    out1 = PROC / "task_AA7_second_control_eb.csv"
    df.to_csv(out1, index=False)
    out2 = PROC / "task_AA7_second_control_nulls.csv"
    pd.DataFrame(rows_out).to_csv(out2, index=False)
    print(f"\nSaved: {out1} ({len(df)} rows), {out2} ({len(rows_out)} rows)")
    print(f"Elapsed: {time.time() - t0:.1f}s | N_PERM={N_PERM} | SEED={SEED}")


if __name__ == "__main__":
    main()
