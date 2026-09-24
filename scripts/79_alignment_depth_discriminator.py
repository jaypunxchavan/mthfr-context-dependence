"""
AD6 — alignment depth as the discriminator: does |delta_ESM| track
per-position evolutionary depth while ThermoMPNN's residual does not,
region by region? (task doc L287-298). PRE-REGISTERED: this docstring
was written before the first run.

DATA (reuse, NO refetch — task AD6a: "whatever MTHFR alignment Group AB
produces"): the one MTHFR alignment that exists is
data/external/ProteinGym/MTHR_HUMAN_2023-08-07_b02.a2m (3,316,659 B),
pulled by AB1 inside the ProteinGym fetch; AB3 SKIPPED (nothing new was
produced), AB4 BLOCKED (see log). Session member-data total unchanged
(~196.3/200MB). Format measured before writing this docstring: 4,783
records; query `MTHR_HUMAN/1-656` (full-length UniProt 1..656); query
has 26 LOWERCASE residues (a3m insertions relative to match state);
filtering every record to [A-Z-] gives length 630 for ALL 4,783
records -> match state = 630 columns; query lowercase chars occupy no
match column.

AD6a — per-position depth metrics (computed, no model is fitted):
  Neff per column (PRIMARY depth metric): global sequence reweighting
  w_i = 1/|{j : id(i,j) >= 0.8}| with id(i,j) = (non-gap matching
  match-columns) / 630 (fixed denominator: gaps count against, so
  fragments are penalised; threshold 0.8 is the standard
  sequence-identity clustering level — one choice, frozen here);
  Neff(col) = sum_i w_i * 1[sequence i occupies col].
  Conservation (SECONDARY depth metric): per-column Shannon entropy
  over {20 AA + gap + other} (H_norm = H / log(22)), conservation =
  1 - H_norm.
  Mapping: UniProt position p -> query char q[p-1]; lowercase query
  chars (insertions) have NO match column -> those positions are
  EXCLUDED from the depth table (count printed; V2 spans 40..644).
  G2 verifies the mapping by three-way identity: query letter at p ==
  V2 wt_aa for every mapped row, else exit 1.

AD6b — the test, position-level (each row of the analysis table IS one
position, so row bootstrap == position bootstrap, sections 3-4):
  Signals per position (means over that position's V2 variants, all
  signals finite on all 10,141 rows — accounting printed):
    yE  = mean |delta_esm|                     (ESM-2 background shift)
    yT1 = mean |pred_eb|    ("ThermoMPNN's residual": its non-additive
          term beyond additive singles — task wording, most-literal
          reading; G3 below shows it is rank-degenerate with ddg)
    yT2 = mean |ddg|        (second always-reported ThermoMPNN scalar)
    yT3 = mean |interaction_D| (AD4's native ThermoMPNN-D double-mutant
          interaction; SECONDARY, always reported, NOT part of the
          frozen rule)
  Statistic: Spearman(signal, depth) across positions; CI via the
  house position-cluster bootstrap (scripts.lib.stats.
  position_cluster_bootstrap, seed 0) — n_boot per scope.
  Scopes: pooled + each of regions 1-4 (region from V2's own column,
  scripts.lib.regions provenance) for the PRIMARY depth metric
  (full region breakdown demanded by task L296-297); conservation run
  POOLED only for yE/yT1/yT2 (secondary metric, scope frozen here).

FROZEN DECISION RULES (stated before running; both written into the
VERDICT block):
  R1 ("ESM tracks depth"): pooled rho(yE, Neff) > 0 AND its 95%
     bootstrap CI excludes 0. Expected sign positive (mechanistic
     expectation: deeper columns -> PLM has seen more co-variation ->
     stronger background-dependent shifts); two-sided CI regardless.
  R2 ("ThermoMPNN's residual does not"): pooled CI of rho(yT1, Neff)
     includes 0 AND pooled CI of rho(yT2, Neff) includes 0.
  CONFIRMED iff R1 AND R2. If CONFIRMED, the evaluator's proposed rule
  is stated — "PLM background-awareness requires evolutionary depth;
  structure-based models don't need it" — WITH this script's printed
  scope limits attached (single, globally shallow alignment; relative
  depth only; observational). If NOT CONFIRMED, report exactly which of
  R1/R2 failed and the numbers, plainly (a null is a result, section
  0). If CONFIRMED but any region shows rho(yE,Neff) CI excluding 0
  with NEGATIVE sign, a heterogeneity caveat is printed beside the rule.

ALWAYS-REPORTED SECONDARIES (no selection after results):
  (a) yT3 (AD4 native interaction) through all 5 scopes vs Neff;
  (b) conservation pooled for yE/yT1/yT2;
  (c) paired delta-rho rho(yE,Neff) - rho(yT1,Neff), pooled, position
      bootstrap seed 1 (the discrimination itself; CI excluding 0 =
      the two signals' depth-tracking differs);
  (d) signed position means (mean delta_esm, mean pred_eb) vs Neff —
      DESCRIPTIVE point estimates only, printed without CI and labeled
      as such (the pre-registered signals are the |.| magnitudes).

GATES (failure => print, sys.exit(1); no retry, no threshold change):
  G1 file integrity: 4,783 records; query len 656; >=99% of records
     filter to exactly 630 match chars.
  G2 mapping identity: query letter at each mapped position == V2
     wt_aa for ALL rows (three-way style of AD4's G1); exit 1 on any
     mismatch.
  G3 pred_eb degeneracy: best-constant k = mean(pred_eb - ddg) must
     satisfy max|pred_eb - (ddg + k)| < 1e-9 -> pred_eb is EXACTLY
     affine in ddg (probe measured k = -0.043862 = ddG_222, max resid
     0.000000). This EXPECTED failure-of-independence is printed as a
     structural fact: signed yT1 and yT2 position means are affine =>
     identical signed Spearman; |.| versions differ only through the
     constant. G3 exists so the T-side degeneracy is on the record, not
     hidden (AGENTS section 5 column-identity duty).
  G4 depth sanity: Neff(col) finite, within [1, 4783] for all 630
     columns; occupancy >= 1 everywhere; global sum(w) printed next to
     ProteinGym metadata MSA_N_eff=646.2 (definition differences
     disclosed, NOT gated — different reweighting definitions).
  G5 region sizes >= MIN_N=20 positions (pre-registered floor; probe
     measured 108/135/174/169).

ENV: N_BOOT default 10,000; SMOKE=1 => 300. SEEDS: 0 (all CIs),
1 (delta-rho). OUTPUTS: data/processed/task79_depth_positions.csv
(position table) and task79_depth_associations.csv (every rho row).
NULL/p: the bootstrap CI + two-sided p_boot from the house _summarize
(section 3: position level throughout; no row-level resampling).

DISCLOSED JUDGMENT (section 9/10): AB3b's floor ("couplings from it
would be unusable... do not proceed") gates TRAINING A POTTS MODEL on
the shallow alignment (AB4). Task AD6a explicitly instructs computing
per-column depth statistics from this alignment; column counts/entropy
fit no model and need no couplings. Proceeding under AD6a's literal
instruction with the shallowness limitation printed (see LIMITATIONS)
was judged consistent with the floor's scope; flagged here so the user
can revisit that judgment.

LIMITATIONS (printed with results, section 6):
  1. Globally shallow alignment: Neff/L = 0.99 (646.2/656, ProteinGym
     metadata, category "Low") — only RELATIVE per-position depth is
     testable; absolute depth claims are not.
  2. One alignment, one protein, observational association — the rule
     is stated (if at all) as this project's finding on MTHFR, not as
     a demonstrated universal.
  3. Our per-column Neff definition (id>=0.8, denom 630) differs from
     ProteinGym's metadata definition; their 646.2 is printed for
     reconciliation, not equality.
  4. T1/T2 are rank-degenerate by construction (G3): the vendored
     ThermoMPNN "residual" adds no information beyond ddg shifted by
     the 222 constant; T3 (AD4 native) is the independent T-side check.
  5. The 26 insertion (lowercase-query) positions have no match column
     and are excluded; excluded count printed.
  6. Position means pool ~17 variants/position (10,141/586) — means of
     |.| are well defined; no causal reading.
"""
import os
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from scripts.lib.stats import position_cluster_bootstrap

ROOT = Path(__file__).resolve().parents[1]
A2M_PATH = ROOT / "data" / "external" / "ProteinGym" / \
    "MTHR_HUMAN_2023-08-07_b02.a2m"
V2_PATH = ROOT / "data" / "processed" / "task_V2_thermompnn_ddg.csv"
T77_PATH = ROOT / "data" / "processed" / "task77_thermompnnD_doubles.csv"
OUT_POS = ROOT / "data" / "processed" / "task79_depth_positions.csv"
OUT_ASSOC = ROOT / "data" / "processed" / "task79_depth_associations.csv"

N_RECORDS = 4783          # AB1-measured, grep-verified
QUERY_LEN = 656           # header MTHR_HUMAN/1-656
MATCH_LEN = 630           # measured pre-registration probe
IDENT_THRESH = 0.8
MIN_N_REGION = 20
SEED = 0
SEED2 = 1
METADATA_NEFF = 646.2     # ProteinGym metadata (reconciliation only)

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SMOKE = os.environ.get("SMOKE", "0") == "1"
if SMOKE:
    N_BOOT = min(N_BOOT, 300)
T0 = time.time()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def parse_a2m(path):
    raw = path.read_text()
    recs = []
    for blk in raw.split(">")[1:]:
        lines = blk.splitlines()
        recs.append((lines[0], "".join(lines[1:])))
    return recs


if __name__ == "__main__":
    banner("AD6 — ALIGNMENT DEPTH DISCRIMINATOR (scripts/79) "
           f"SMOKE={SMOKE} N_BOOT={N_BOOT}")

    # ---------------- AD6a: parse + depth metrics --------------------
    recs = parse_a2m(A2M_PATH)
    qhdr, query = recs[0]
    filtered = ["".join(c for c in s if c.isupper() or c == "-")
                for _, s in recs]
    n_bad = sum(1 for f in filtered if len(f) != MATCH_LEN)
    if len(recs) != N_RECORDS or len(query) != QUERY_LEN:
        gfail(f"G1 FAIL: records {len(recs)} != {N_RECORDS} or "
              f"query len {len(query)} != {QUERY_LEN}")
    if n_bad > 0.01 * N_RECORDS:
        gfail(f"G1 FAIL: {n_bad} records do not filter to {MATCH_LEN} "
              f"match chars (>1%)")
    print(f"  G1 file integrity PASS: {len(recs)} records, query "
          f"'{qhdr}' len {len(query)}, match state {MATCH_LEN} cols, "
          f"{n_bad} non-conforming records")

    # query lowercase -> insertion (no match column); cumsum mapping
    qcol_of_pos = {}       # UniProt pos (1-based) -> match col (0-based)
    col = 0
    n_lower = 0
    for i, c in enumerate(query, start=1):
        if c.isupper():
            qcol_of_pos[i] = col
            col += 1
        elif c.islower():
            n_lower += 1
    assert col == MATCH_LEN, f"cumsum {col} != {MATCH_LEN}"
    print(f"  query mapping: {col} match positions, {n_lower} insertion "
          f"(lowercase) positions with no column")

    A = np.full((N_RECORDS, MATCH_LEN), ord("-"), dtype=np.uint8)
    for r, f in enumerate(filtered):
        # G1 already gfails on >1% non-conforming; pad/slice the rest
        fb = f.ljust(MATCH_LEN, "-")[:MATCH_LEN]
        A[r] = np.frombuffer(fb.encode(), dtype=np.uint8)

    occ = (A != ord("-"))                      # (S, L) occupancy
    # Neff per column: reweight at id >= 0.8 (fixed denom MATCH_LEN)
    alphabet = [ch for ch in sorted(set(A.flatten().tolist()))
                if ch != ord("-")]
    matches = np.zeros((N_RECORDS, N_RECORDS), dtype=np.float32)
    for ch in alphabet:
        O = (A == ch).astype(np.float32)
        matches += O @ O.T
    np.fill_diagonal(matches, MATCH_LEN)       # self id = 1.0
    nb = (matches / MATCH_LEN >= IDENT_THRESH).sum(axis=1).astype(np.float64)
    w = 1.0 / nb
    neff_col = w @ occ.astype(np.float64)      # (L,)
    # conservation: Shannon over {AA + gap + other}
    gapc = ord("-")
    std = set(b"ACDEFGHIKLMNPQRSTVWY")
    H = np.zeros(MATCH_LEN)
    for a in range(MATCH_LEN):
        colv = A[:, a]
        cats = np.where(np.isin(colv, list(std)), colv,
                        np.where(colv == gapc, gapc, ord("X")))
        _, cnt = np.unique(cats, return_counts=True)
        p = cnt / cnt.sum()
        H[a] = float(-(p * np.log(p)).sum())
    cons_col = 1.0 - H / np.log(22.0)

    if not (np.all(np.isfinite(neff_col))
            and neff_col.min() >= 1 and neff_col.max() <= N_RECORDS
            and occ.sum(axis=0).min() >= 1):
        gfail(f"G4 FAIL: neff range [{neff_col.min()}, {neff_col.max()}] "
              f"or occupancy sanity broken")
    print(f"  G4 depth sanity PASS: Neff(col) range "
          f"[{neff_col.min():.1f}, {neff_col.max():.1f}] "
          f"| global sum(w) = {w.sum():.1f} vs ProteinGym metadata "
          f"MSA_N_eff = {METADATA_NEFF} (DIFFERENT definitions - "
          f"reconciliation note, not equality; id>={IDENT_THRESH} "
          f"denom={MATCH_LEN} here)")

    # ---------------- frames ----------------------------------------
    v2 = pd.read_csv(V2_PATH)
    t77 = pd.read_csv(T77_PATH)[["hgvs_pro", "interaction_D"]]
    df = v2.merge(t77, on="hgvs_pro", how="left")
    print(f"  merged V2 {len(df)} rows; interaction_D finite "
          f"{df['interaction_D'].notna().sum()} | delta_esm "
          f"{df['delta_esm'].notna().sum()} | pred_eb "
          f"{df['pred_eb'].notna().sum()} | ddg {df['ddg'].notna().sum()}")

    # G3: pred_eb affine-degenerate with ddg?
    k = float((df["pred_eb"] - df["ddg"]).mean())
    resid = float(np.abs(df["pred_eb"] - (df["ddg"] + k)).max())
    if resid >= 1e-9:
        gfail(f"G3 FAIL: pred_eb not affine in ddg (max resid {resid:.3e})")
    print(f"  G3 pred_eb degeneracy CONFIRMED (expected structural fact): "
          f"pred_eb = ddg {k:+.6f} exactly (max|resid| = {resid:.3e}; "
          f"k = ddG_222 = -0.0439) -> signed yT1/yT2 are affine "
          f"(identical signed rho); |.| versions differ only by the "
          f"constant. T1/T2 carry ONE ThermoMPNN information source.")

    # G2: mapping identity (query letter vs V2 wt_aa), per row.
    # [SMOKE RUN 1 FIX, disclosed in log: the first version indexed the
    # RAW 656-char query with the match-COLUMN number from qcol_of_pos,
    # conflating the two index spaces (off by the count of preceding
    # insertion positions: 16 lowercase in 1..16 made position 244 read
    # query[227]='L' instead of query[243]='T'). Standalone offset probe
    # verified identity is perfect at raw index, direct UniProt
    # numbering: "offset +0: match 586/586" (offsets -40..+40 all
    # 26-40/586), and ProteinGym scores independently say T244A/C/D.
    # The depth-column mapping (qcol_of_pos used only for column
    # extraction) was already correct and is unchanged; only the gate's
    # letter lookup was corrected. No statistic or threshold touched.]
    mapped_rows = 0
    excluded_positions = set()
    for p, wt in set(zip(df["position"], df["wt_aa"])):
        if p not in qcol_of_pos:
            excluded_positions.add(p)
            continue
        qc = query[p - 1]            # raw query index, direct UniProt
        if qc != wt:
            gfail(f"G2 FAIL: position {p}: query '{qc}' != V2 wt_aa "
                  f"'{wt}' (mapping broken)")
        mapped_rows += 1
    print(f"  G2 mapping identity PASS: {mapped_rows} distinct positions "
          f"query==V2 wt_aa; excluded (query insertion) positions: "
          f"{sorted(excluded_positions) if excluded_positions else 'none'}")

    d = df[df["position"].map(lambda p: p in qcol_of_pos)].copy()
    d["match_col"] = d["position"].map(qcol_of_pos)
    d["neff"] = neff_col[d["match_col"].to_numpy()]
    d["cons"] = cons_col[d["match_col"].to_numpy()]
    d["abs_delta_esm"] = d["delta_esm"].abs()
    d["abs_pred_eb"] = d["pred_eb"].abs()
    d["abs_ddg"] = d["ddg"].abs()
    d["abs_interaction_D"] = d["interaction_D"].abs()

    pos = (d.groupby(["position", "region"])
             .agg(neff=("neff", "first"), cons=("cons", "first"),
                  n_var=("position", "size"),
                  yE=("abs_delta_esm", "mean"),
                  yT1=("abs_pred_eb", "mean"),
                  yT2=("abs_ddg", "mean"),
                  yT3=("abs_interaction_D", "mean"),
                  sE=("delta_esm", "mean"),
                  sT1=("pred_eb", "mean"))
             .reset_index())
    print(f"  position table: {len(pos)} positions "
          f"(regions: {pos.groupby('region')['position'].count().to_dict()})")

    regions = sorted(pos["region"].unique())
    for r in regions:
        n = int((pos["region"] == r).sum())
        if n < MIN_N_REGION:
            gfail(f"G5 FAIL: region {r} has {n} positions "
                  f"(< MIN_N={MIN_N_REGION})")
    print(f"  G5 region sizes PASS: all >= {MIN_N_REGION} "
          f"({pos.groupby('region')['position'].count().to_dict()})")

    # ---------------- AD6b: associations -----------------------------
    assoc = []

    def run_rho(sub, xcol, ycol, label, scope, depth):
        r = position_cluster_bootstrap(sub, "position", xcol, ycol,
                                       n_boot=N_BOOT, seed=SEED)
        assoc.append({"depth": depth, "scope": scope, "signal": label,
                      "rho": r["observed_rho"], "ci_lo": r["ci_lo"],
                      "ci_hi": r["ci_hi"], "p_boot": r["p_boot"],
                      "n_pos": r["n_rows"]})
        print(f"  [{depth:4s}] {scope:8s} {label:4s} rho="
              f"{r['observed_rho']:+.4f} [{r['ci_lo']:+.4f}, "
              f"{r['ci_hi']:+.4f}] p_boot={r['p_boot']:.4f} "
              f"n={r['n_rows']}")

    banner("PRIMARY DEPTH METRIC: Neff per column — pooled + ALL REGIONS",
           "=")
    scopes = [("pooled", pos)] + [(f"region{int(r)}",
                                   pos[pos["region"] == r])
                                  for r in regions]
    for scope, sub in scopes:
        for sig in ("yE", "yT1", "yT2", "yT3"):
            run_rho(sub, "neff", sig, sig, scope, "neff")

    banner("SECONDARY DEPTH METRIC: conservation (pooled only, frozen)",
           "=")
    for sig in ("yE", "yT1", "yT2"):
        run_rho(pos, "cons", sig, sig, "pooled", "cons")

    banner("SECONDARY (c): paired delta-rho rho(yE) - rho(yT1), "
           "seed 1", "=")
    rng = np.random.default_rng(SEED2)
    n = len(pos)
    ye = pos["yE"].to_numpy()
    yt1 = pos["yT1"].to_numpy()
    xn = pos["neff"].to_numpy()
    obs = spearmanr(ye, xn).statistic - spearmanr(yt1, xn).statistic
    dr = np.empty(N_BOOT)
    idx = np.arange(n)
    for b in range(N_BOOT):
        i = rng.choice(idx, size=n, replace=True)
        dr[b] = (spearmanr(ye[i], xn[i]).statistic
                 - spearmanr(yt1[i], xn[i]).statistic)
    lo, hi = np.percentile(dr, [2.5, 97.5])
    pdr = min(2 * min((dr <= 0).mean(), (dr >= 0).mean()), 1.0)
    print(f"  delta-rho (yE - yT1 vs Neff, pooled) = {obs:+.4f} "
          f"[{lo:+.4f}, {hi:+.4f}] p_boot={pdr:.4f} n={n} "
          f"(CI excluding 0 = the two signals track depth differently)")
    assoc.append({"depth": "neff", "scope": "pooled",
                  "signal": "delta_rho_E_minus_T1", "rho": obs,
                  "ci_lo": lo, "ci_hi": hi, "p_boot": pdr, "n_pos": n})

    banner("SECONDARY (d): signed position means — DESCRIPTIVE only "
           "(no CI)", "=")
    for ycol, lbl in (("sE", "mean delta_esm"), ("sT1", "mean pred_eb")):
        r = float(spearmanr(pos[ycol], pos["neff"]).statistic)
        print(f"  rho({lbl}, Neff) = {r:+.4f}  [descriptive point "
              f"estimate; not a pre-registered test]")

    # ---------------- FROZEN VERDICT ---------------------------------
    def get(scope, sig):
        return next(a for a in assoc if a["depth"] == "neff"
                    and a["scope"] == scope and a["signal"] == sig)

    e = get("pooled", "yE")
    t1 = get("pooled", "yT1")
    t2 = get("pooled", "yT2")
    r1 = (e["rho"] > 0) and not (e["ci_lo"] <= 0 <= e["ci_hi"])
    r2 = ((t1["ci_lo"] <= 0 <= t1["ci_hi"])
          and (t2["ci_lo"] <= 0 <= t2["ci_hi"]))
    confirmed = r1 and r2

    banner("VERDICT (frozen rules R1/R2)", "=")
    print(f"  R1 'ESM tracks depth': pooled rho(yE,Neff)={e['rho']:+.4f} "
          f"[{e['ci_lo']:+.4f},{e['ci_hi']:+.4f}] >0 & CI excludes 0 -> "
          f"{'PASS' if r1 else 'FAIL'}")
    print(f"  R2 'ThermoMPNN residual does not': yT1 CI=[{t1['ci_lo']:+.4f},"
          f"{t1['ci_hi']:+.4f}] {'incls 0' if t1['ci_lo'] <= 0 <= t1['ci_hi'] else 'EXCLUDES 0'}"
          f" | yT2 CI=[{t2['ci_lo']:+.4f},{t2['ci_hi']:+.4f}] "
          f"{'incls 0' if t2['ci_lo'] <= 0 <= t2['ci_hi'] else 'EXCLUDES 0'}"
          f" -> {'PASS' if r2 else 'FAIL'}")
    if confirmed:
        print("  CONFIRMED -> evaluator's proposed rule, as this project "
              "found it on MTHFR:")
        print('    "PLM background-awareness requires evolutionary depth; '
              'structure-based models don\'t need it."')
        het = [a for a in assoc if a["depth"] == "neff"
               and a["scope"].startswith("region") and a["signal"] == "yE"
               and a["rho"] < 0 and not (a["ci_lo"] <= 0 <= a["ci_hi"])]
        if het:
            print(f"  HETEROGENEITY CAVEAT: region(s) with significant "
                  f"NEGATIVE yE tracking: "
                  f"{[(h['scope'], round(h['rho'], 4)) for h in het]} - "
                  f"rule holds pooled, not uniformly.")
        print("  Scope limits attached: single globally shallow "
              "alignment (Neff/L=0.99, 'Low'); relative per-position "
              "depth only; one protein; observational.")
    else:
        print(f"  NOT CONFIRMED -> R1 {'PASS' if r1 else 'FAIL'}, "
              f"R2 {'PASS' if r2 else 'FAIL'}; rule NOT stated as "
              f"proposed. Numbers above reported as-is (a null is a "
              f"result).")

    pos.to_csv(OUT_POS, index=False)
    pd.DataFrame(assoc).to_csv(OUT_ASSOC, index=False)
    print(f"\n  saved {len(pos)} position rows -> {OUT_POS.name}")
    print(f"  saved {len(assoc)} association rows -> {OUT_ASSOC.name}")

    banner("LIMITATIONS (printed with results, AGENTS section 6)", "-")
    print(f"""  1. Globally shallow alignment: Neff/L = 0.99 (646.2/656,
     ProteinGym metadata, category Low) - only RELATIVE per-position
     depth is testable here.
  2. One alignment, one protein, observational - the rule (if stated)
     is this project's finding on MTHFR, not a demonstrated universal.
  3. Our per-column Neff (id>={IDENT_THRESH}, denom={MATCH_LEN}) differs
     from ProteinGym's metadata definition; {METADATA_NEFF} printed for
     reconciliation, not equality.
  4. T1/T2 rank-degenerate by construction (G3): the vendored
     ThermoMPNN residual adds no information beyond ddg shifted by the
     222 constant; T3 (AD4 native ThermoMPNN-D) is the independent
     ThermoMPNN-side check, reported through all scopes.
  5. Insertion (lowercase-query) positions have no match column and
     are excluded: {sorted(excluded_positions) if excluded_positions else 'none'}.
  6. Signed means (d) are descriptive; pre-registered signals are |.|
     magnitudes. AD6a used the AB1-shipped a2m under the task's
     explicit reuse instruction (AB3 produced nothing new); AB3b's floor
     gates Potts/coupling training, not column statistics - judgment
     disclosed in the docstring.""")

    print(f"\nAD6 DONE  ({time.time() - T0:.1f}s)  VERDICT: "
          f"{'CONFIRMED' if confirmed else 'NOT CONFIRMED'} "
          f"(R1 {'pass' if r1 else 'fail'}, R2 {'pass' if r2 else 'fail'})")
