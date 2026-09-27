"""
Script 102 (task Z3 of DISATTENUATION_AND_LEDGER.md, Group Z):

  Fetch ClinVar data for MTHFR, cross-reference against the atlas's
  canonical variant manifest, and count how many variants are scored
  MEANINGFULLY DIFFERENTLY under background-aware vs background-naive
  ESM-2 prediction, under a pre-registered threshold.

PRE-REGISTRATION (this docstring written before any variant-level
ClinVar data was fetched; AGENTS 6. Only the record COUNT (1,078) and
the response schema were probed before writing this — no variant data,
no classifications, no outcomes.)
--------------------------------------------------------------------
FETCH (budget stated up front): NCBI E-utilities only, 4 requests
total: 1 esearch (db=clinvar, term="MTHFR[gene]", retmax=5000,
retmode=json) + 3 esummary batches (500/500/rest, retmode=json),
tool=mthfr_atlas, no API key, 0.4 s between calls. Probed count at
write time: 1,078 records (~1-4 MB expected). Raw responses saved to
data/external/clinvar/ and byte counts printed. No other endpoint,
no sub-everything: ALL records are fetched (server-side filters were
NOT trusted: probing showed ambiguous errorlist behavior, and 1,078
records is cheap enough to take whole).

MANIFEST: data/processed/task32_analysis_table.csv — the atlas's
canonical variant manifest (11,344 single-AA-substitution records,
keys f"{wt_aa}{position}{mut_aa}"). Analysis-set membership (dropna
own_e_b, GI_folinate_independent, delta_esm -> 10,757) recorded per
matched row.

MATCHING (fixed here): parse protein change p.<WT3><pos><MUT3> from a
record's `protein_change` / `title` / `variation_name` strings,
tolerating surrounding parentheses e.g. "p.(Ala222Val)"; convert
3-letter -> 1-letter (standard 20; anything else is unmatchable and
counted as a parse/match failure); accept a record as "in the atlas"
iff the triple (wt, pos, mut) is a manifest key — i.e. the wt must
agree with the atlas's own reference at that position, so isoform or
transcript numbering mismatches simply fail to match (disclosed; they
are counted, not silently dropped). Records with no parseable missense
protein change (intronic, synonymous, UTR, nonsense) are counted at
their step and excluded from matching by construction.

CLASSES (fixed here): PRIMARY = the two the task names:
  "Uncertain significance" (VUS) and "Conflicting classifications of
  pathogenicity" (ClinVar's current string; the legacy spelling
  "Conflicting interpretations of pathogenicity" maps to the same
  class, stated in advance). CONTEXT (reported separately, no
  decisions attached, pre-stated): "Pathogenic", "Likely pathogenic".
  Everything else is counted and not analyzed.

THRESHOLD FOR "MEANINGFULLY DIFFERENTLY" (pre-registered, one rule):
  |delta_esm| >= 0.1182  =  one population SD of delta_esm across the
  full 11,344-row manifest. Source: sd_delta_esm = 0.11821991945148934
  from data/processed/task_delta_esm_noise_floor.csv, independently
  recomputed from the manifest (identical to all 17 digits), both read
  BEFORE any ClinVar variant data existed in this session.
  Rationale: delta_esm = esm2_score_a222v_bg - esm2_score IS the
  background-aware minus background-naive score difference for the
  variant, so one SD of that difference distribution is the natural
  scale-relative "meaningful" cut. SENSITIVITY (pre-stated,
  descriptive only, no decisions from it): counts at >= 0.5 SD
  (0.0591100) and >= 2 SD (0.2364398).

OUTPUTS: data/processed/task102_clinvar_atlas_overlap.csv (every
manifest-matched ClinVar record with class and scores); every
filtering step's n printed (AGENTS 5 — every dropped record
accounted); LIMITATIONS printed with the result: a ClinVar record's
classification reflects submitting labs' criteria, not our data; a
non-match means numbering/absence mismatch, not absence from ClinVar;
the threshold is on the model-score difference only — it says nothing
about which score is CORRECT, only that the background choice matters
for that variant by the pre-registered amount.

Run (deterministic): venv/bin/python3 scripts/102_z3_clinvar_crossref.py
  No randomness, no N to smoke. If the raw JSON files already exist in
  data/external/clinvar/, they are reused and NOTHING is refetched;
  delete them (or set REFRESH=1) to pull again — 4 requests maximum
  either way.
"""

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "mthfr_atlas"
EXT = Path("data/external/clinvar")
PROC = Path("data/processed")

SD_THRESHOLD = 0.11821991945148934   # task_delta_esm_noise_floor.csv, pre-fetch
HALF_SD = 0.05910995972574467
DOUBLE_SD = 0.23643983890297867
PRIMARY_CLASSES = {"Uncertain significance",
                   "Conflicting classifications of pathogenicity",
                   "Conflicting interpretations of pathogenicity"}
CONTEXT_CLASSES = {"Pathogenic", "Likely pathogenic"}

AA3to1 = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C",
          "Gln": "Q", "Glu": "E", "Gly": "G", "His": "H", "Ile": "I",
          "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P",
          "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V"}

PC_RE = re.compile(r"p\.\s*\(?\s*([A-Z][a-z]{2})(\d{1,4})([A-Z][a-z]{2})")


def log(msg=""):
    print(msg, flush=True)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": TOOL})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    return raw


def main():
    EXT.mkdir(parents=True, exist_ok=True)

    # ---------- manifest (pre-fetch side) ----------
    m = pd.read_csv(PROC / "task32_analysis_table.csv",
                    usecols=["hgvs_pro", "position", "wt_aa", "mut_aa",
                             "esm2_score", "esm2_score_a222v_bg", "delta_esm",
                             "own_e_b", "GI_folinate_independent"])
    manifest = {}
    for row in m.itertuples(index=False):
        manifest[f"{row.wt_aa}{int(row.position)}{row.mut_aa}"] = row
    ana = m.dropna(subset=["own_e_b", "GI_folinate_independent",
                           "delta_esm"])
    ana_keys = set(f"{r.wt_aa}{int(r.position)}{r.mut_aa}"
                   for r in ana.itertuples(index=False))
    log(f"manifest: {len(manifest)} keys; analysis set: {len(ana_keys)} "
        f"(expect 11344 / 10757)")
    if (len(manifest), len(ana_keys)) != (11344, 10757):
        log("*** manifest size mismatch — STOP")
        sys.exit(1)
    sd_chk = float(m["delta_esm"].std(ddof=0))
    log(f"pre-fetch threshold check: sd(delta_esm) on manifest = "
        f"{sd_chk!r} vs pre-registered {SD_THRESHOLD!r}")
    if abs(sd_chk - SD_THRESHOLD) > 1e-12:
        log("*** threshold source changed since pre-registration — STOP")
        sys.exit(1)

    # ---------- fetch (4 requests max, byte budget printed) ----------
    import os
    es_f = EXT / "clinvar_mthfr_esearch.json"
    sum_f = EXT / "clinvar_mthfr_esummary.json"
    if es_f.exists() and sum_f.exists() and not os.environ.get("REFRESH"):
        raw = es_f.read_bytes()
        ids = json.loads(raw)["esearchresult"]["idlist"]
        saved = json.loads(sum_f.read_text())
        records = saved["records"]
        total_bytes = 0
        log(f"CACHE HIT: reusing {es_f} and {sum_f} — nothing refetched "
            f"({len(ids)} ids, {len(records)} records)")
    else:
        total_bytes = 0
        es_url = (f"{EUTILS}/esearch.fcgi?db=clinvar&term=MTHFR%5Bgene%5D"
                  f"&retmax=5000&retmode=json&tool={TOOL}")
        raw = fetch(es_url)
        total_bytes += len(raw)
        es_f.write_bytes(raw)
        ids = json.loads(raw)["esearchresult"]["idlist"]
        log(f"esearch: {len(ids)} ids (probe said 1078), "
            f"{len(raw):,} bytes")
        time.sleep(0.4)

        records = []
        BATCH = 500
        for start in range(0, len(ids), BATCH):
            batch = ",".join(ids[start:start + BATCH])
            su = (f"{EUTILS}/esummary.fcgi?db=clinvar&id={batch}"
                  f"&retmode=json&tool={TOOL}")
            sraw = fetch(su)
            total_bytes += len(sraw)
            res = json.loads(sraw)["result"]
            for uid in res["uids"]:
                records.append(res[uid])
            log(f"esummary batch {start//BATCH + 1}: {len(res['uids'])} "
                f"records, {len(sraw):,} bytes")
            time.sleep(0.4)
        sum_f.write_text(json.dumps({"uids": ids, "records": records}))
        log(f"FETCH TOTAL: {total_bytes:,} bytes "
            f"({total_bytes/1e6:.2f} MB), {len(records)} records saved")

    # ---------- parse + match ----------
    n_rec = len(records)
    n_class = {"primary": 0, "context": 0, "other": 0}
    n_pc = 0
    rows = []
    unparseable = 0
    for r in records:
        cls = (r.get("germline_classification") or {}).get(
            "description", "") or ""
        grp = ("primary" if cls in PRIMARY_CLASSES else
               "context" if cls in CONTEXT_CLASSES else "other")
        n_class[grp] += 1
        texts = [r.get("title") or ""]
        pc = r.get("protein_change")
        if isinstance(pc, str):
            texts.append(pc)
        elif isinstance(pc, list):
            texts.extend(str(x) for x in pc)
        for v in r.get("variation_set", []):
            texts.append(str(v.get("variation_name") or ""))
        hit = None
        for t in texts:
            mm = PC_RE.search(t)
            if mm:
                hit = mm
                break
        if hit is None:
            unparseable += 1
            continue
        wt3, pos, mut3 = hit.group(1), int(hit.group(2)), hit.group(3)
        if wt3 not in AA3to1 or mut3 not in AA3to1:
            unparseable += 1
            continue
        n_pc += 1
        key = f"{AA3to1[wt3]}{pos}{AA3to1[mut3]}"
        if key not in manifest:
            continue
        mr = manifest[key]
        rows.append({
            "uid": r.get("uid"), "accession": r.get("accession"),
            "title": r.get("title"), "classification": cls,
            "class_group": grp, "review_status":
                (r.get("germline_classification") or {}).get(
                    "review_status", ""),
            "key": key, "position": pos,
            "esm2_score": mr.esm2_score,
            "esm2_score_a222v_bg": mr.esm2_score_a222v_bg,
            "delta_esm": mr.delta_esm,
            "abs_delta_ge_half_sd": int(abs(mr.delta_esm) >= HALF_SD),
            "abs_delta_ge_1sd": int(abs(mr.delta_esm) >= SD_THRESHOLD),
            "abs_delta_ge_2sd": int(abs(mr.delta_esm) >= DOUBLE_SD),
            "in_analysis_set": int(key in ana_keys),
        })

    out = pd.DataFrame(rows)
    log(f"\nFILTERING ACCOUNTING (every step's n):")
    log(f"  ClinVar MTHFR records fetched          : {n_rec}")
    log(f"    class: primary (VUS+conflicting)     : {n_class['primary']}")
    log(f"    class: context (P/LP)                : {n_class['context']}")
    log(f"    class: other (benign/etc)            : {n_class['other']}")
    log(f"  no parseable missense p. change        : {unparseable}")
    log(f"  parseable missense p. change           : {n_pc}")
    log(f"  matched to atlas manifest (wt+pos+mut) : {len(out)}")

    for grp, lbl in [("primary", "VUS + conflicting (task-mandated)"),
                     ("context", "Pathogenic/Likely pathogenic (context)")]:
        sub = out[out["class_group"] == grp]
        log(f"\n  {lbl}: n_in_atlas = {len(sub)}")
        for tag, col in [("|delta| >= 0.5 SD (0.0591)", "abs_delta_ge_half_sd"),
                         ("|delta| >= 1 SD (0.1182) PRE-REGISTERED",
                          "abs_delta_ge_1sd"),
                         ("|delta| >= 2 SD (0.2364)", "abs_delta_ge_2sd")]:
            k = int(sub[col].sum()) if len(sub) else 0
            log(f"    {tag:<48}: {k}")
        if len(sub):
            top = sub.reindex(sub["delta_esm"].abs().sort_values(
                ascending=False).index).head(8)
            log("    top |delta_esm| in this class:")
            for r in top.itertuples(index=False):
                log(f"      {r.key:<7} {r.classification:<45} "
                    f"delta_esm={r.delta_esm:+.4f} "
                    f"({'>=1SD' if r.abs_delta_ge_1sd else '<1SD'}) "
                    f"{r.accession}")

    out_csv = PROC / "task102_clinvar_atlas_overlap.csv"
    out.to_csv(out_csv, index=False)
    log(f"\nSaved: {out_csv} ({len(out)} rows)")

    n1 = int(out["abs_delta_ge_1sd"].sum()) if len(out) else 0
    n1p = int(out.loc[out.class_group == "primary",
                      "abs_delta_ge_1sd"].sum()) if len(out) else 0
    n1c = int(out.loc[out.class_group == "context",
                      "abs_delta_ge_1sd"].sum()) if len(out) else 0
    log(f"\nZ3 ANSWER (threshold pre-registered before fetch):")
    log(f"  Of {len(out)} ClinVar variants in our measured set, "
        f"{n1} are scored meaningfully differently "
        f"(|delta_esm| >= 0.1182 = 1 SD):")
    log(f"    {n1p} in VUS/conflicting (primary), {n1c} in "
        f"pathogenic/likely-pathogenic (context).")
    log("  LIMITATIONS: classification is submitters' criteria, not our "
        "data; non-match != absent from ClinVar (numbering/isoform or "
        "non-missense); the threshold says the background choice moves "
        "the score by >=1 SD — it does NOT say which score is right.")


if __name__ == "__main__":
    main()
