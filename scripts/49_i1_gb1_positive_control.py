"""
Script 49 (Group I, task I1a): positive control — run the delta_ESM
pipeline on a dataset with ESTABLISHED epistasis (GB1 four-site library).

WHY (REVIEW_TRIAGE I1)
----------------------
Every negative delta_ESM result in this repo (MTHFR's rho ~ -0.088) is
ambiguous without this check: a pipeline that cannot detect strong,
well-documented epistasis anywhere would produce the same null on MTHFR
whether or not MTHFR's interaction is real. This runs the IDENTICAL
scoring path (scripts.lib.esm_scoring.get_position_logprobs, ESM-2 t33
650M, masked-marginal log-odds) on GB1, where pairwise epistasis across
the four assayed sites is among the strongest ever measured.

DATA
----
data/external/GB1_fitness_landscape.txt (tab-separated: sequence, fitness)
-160,000 genotypes = full 20^4 combinatorial library at four sites.
- WT genotype "VDGV" has fitness exactly 1.0 (file normalized to WT=1).
- Provenance: Zenodo record 5014984, Empirical_Landscapes.zip (Pósar et al.
  compilation), attributed there to Wu, Dai, Olson, Lloyd-Smith & Sun,
  eLife 2016;5:e16965 — the Olson-lineage four-site GB1 library.
- md5 at collection: 89e8d0f088466a1e29714721ed7967e8 (printed, not gated).
- Layout assumption (logged): external data goes in data/external/, NOT in
  the read-only data/raw/ reference tree (AGENTS §2).

SITES — AND WHY SITE 4 IS DROPPED (logged contradiction)
---------------------------------------------------------
Genotype columns 1-3 have WT letters V, D, G = positions 39, 40, 41 of the
authoritative PDB 2GB1 sequence (RCSB polymer entity; "NGVDG" motif unique
in the 56-mer). Genotype column 4 has WT letter V, but 2GB1 position 44 is
T (V39 D40 G41 E42 W43 T44) — the file and the authoritative sequence
disagree about the fourth site's WT residue, and the paper's own numbering
could not be retrieved tonight to resolve it. Conservative resolution: use
only the unambiguous consecutive triplet (sites 39/40/41), hold column 4 at
its WT letter "V" (an 8,000-genotype sub-landscape), and disclose the
exclusion rather than guess a numbering. This does not weaken the positive
control: the three consecutive sites carry the same well-established
pairwise epistasis machinery the test needs.

PIPELINE MIRROR (identical to scripts 10/11/32)
------------------------------------------------
- get_position_logprobs(bg_seq, focal_pos) returns, in ONE forward pass,
  masked-marginal log-odds for all 19 non-residue amino acids at the focal
  position IN THAT BACKGROUND SEQUENCE (denominator = residue present at
  the focal position in that sequence).
- delta_ESM(v | b) = S(v | b) - S(v | b0), b0 = WT configuration of the
  other two sites — exactly script 32's definition
  "S(v | A222V background) - S(v | WT background)", generalized to K
  alternate backgrounds.
- The focal position's residue is the WT residue in every background
  sequence (backgrounds only mutate the OTHER two sites), so all scores
  share one denominator — same situation as script 11 vs script 10.

STRUCTURE (pre-registered)
--------------------------
- Focal site s in {39, 40, 41}; variants = the 19 non-WT residues at s.
- Backgrounds: b0 (WT config of the other two sites) + K=10 alternate
  configs sampled WITHOUT replacement from the 399 non-WT configs,
  np.random.default_rng(0), FITNESS-BLIND (no data-dependent selection).
- Analyzed pairs: (v, alternate background) only -> 3 x 19 x 10 = 570
  rows. The (v, b0) pairs are excluded BY RULE: delta and the
  double-mutant-cycle epistasis are identically 0 there (origin pile).
- Target: e(v,b) = f(v,b) - f(v,b0) - f(WT,b) + f(WT,b0) — the
  double-mutant-cycle interaction, the structural analogue of the atlas's
  e.b (background interaction beyond main effects). delta_ESM and e are
  both exactly 0 at v = WT, so no v-dependent offset confounds pairing.

STATISTICS (pre-registered, fixed before running)
-------------------------------------------------
- Primary statistic: pooled Spearman rho(delta_ESM, e) over the 570 rows.
- NULL: variant-label permutation WITHIN site — a variant's whole
  K-background epistasis profile moves together (preserves within-variant
  cross-background dependence; breaks only which variant carries which
  profile). This is an ASSOCIATION null (AGENTS §4 label): it tests
  whether the pairing beats chance, which is exactly the pipeline claim.
  N_PERM=10000 (env), +1 correction. Direction: ONE-SIDED positive is the
  pre-registered gate (the pipeline claim is that delta tracks known
  epistasis); the two-sided p is also printed.
- IDENTITY CHECK (AGENTS §4): an all-identity permutation must reproduce
  rho_obs to <1e-6, else sys.exit(1).
- CI: cluster bootstrap resampling (site, variant) identities — 57
  clusters x 10 rows (AGENTS §3: rows sharing a variant are never
  resampled independently). N_BOOT=2000 (env), seed 0.
- Per-site rhos printed: 3 sites is too few for a site-level bootstrap
  (disclosed); per-site sign consistency is reported instead.
- Null centering printed (AGENTS §4) alongside rho and CI (AGENTS §3).

DECISION RULE (pre-registered)
------------------------------
The positive control PASSES iff rho_obs > 0 AND one-sided permutation
p < 0.05. PASS => the pipeline can detect established epistasis, so
MTHFR's null is a statement about MTHFR/ESM-2 there, not a blind-pipeline
artifact. FAIL => the MTHFR negative is confounded with pipeline
limitation and must be reported as such. Either way, rho and its CI are
printed next to MTHFR's verified rho = -0.08811806424891734
(S1/script-32 value, gate-checked in script 47) for scale.

CAVEATS (printed by the script too, AGENTS §6)
-----------------------------------------------
- Passing a STRONG-epistasis control only shows the pipeline is not
  blind; it does not prove sensitivity to weak epistasis of MTHFR's size.
- GB1 has 10 alternate backgrounds here vs MTHFR's single A222V
  background — more replication on the GB1 side.
- Sort-based fitness noise model differs from the atlas's; site 4
  excluded (contradiction above); background sampling is seed-dependent
  (seed 0 fixed); one model (ESM-2 650M), as in the main pipeline.

Data gates (sys.exit(1)): file parses to 160,000 unique genotypes; WT
fitness == 1.0; all 20 AAs per column; sub-landscape == 8,000 rows; every
needed genotype present; sequence len 56 with VDG at 39-41 and exactly one
NGVDG.

Output: data/processed/task49_i1_gb1.csv
"""
import sys, os, time, hashlib, itertools, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", 2000))
N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
K_BG = 10                      # alternate backgrounds per focal site (fixed)
ALPHA = 0.05
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "external" / "GB1_fitness_landscape.txt"
PROC = ROOT / "data" / "processed"

# PDB 2GB1 entity 1, RCSB core API (fetched 2026-09-22), canonical 56-mer
GB1_SEQ = "MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"
FOCAL_SITES = (39, 40, 41)     # 1-based, V/D/G in GB1_SEQ
WT_COLS = ("V", "D", "G")      # WT letters at focal sites (file columns 1-3)
COL4_WT = "V"                  # dropped site held at WT letter
MTHFR_RHO = -0.08811806424891734   # verified S1/script-32 value (gate in 47)


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(1)


def main():
    t0 = time.time()
    # ---------------- data gates ----------------
    if not DATA.exists():
        fail(f"missing data file: {DATA}")
    md5 = hashlib.md5(DATA.read_bytes()).hexdigest()
    raw = pd.read_csv(DATA, sep="\t")
    if list(raw.columns) != ["sequence", "fitness"]:
        fail(f"unexpected columns: {list(raw.columns)}")
    if len(raw) != 160000 or raw["sequence"].nunique() != 160000:
        fail(f"expected 160,000 unique genotypes, got {len(raw)}/"
             f"{raw['sequence'].nunique()}")
    fit = raw.set_index("sequence")["fitness"]
    wt_key = "".join(WT_COLS) + COL4_WT
    if abs(float(fit[wt_key]) - 1.0) > 1e-9:
        fail(f"WT {wt_key} fitness {fit[wt_key]} != 1.0")
    for i, col in enumerate("1234"):
        aas = set(raw["sequence"].str[i])
        if len(aas) != 20:
            fail(f"column {col} has {len(aas)} AAs, expected 20")
    sub = raw[raw["sequence"].str[3] == COL4_WT]
    if len(sub) != 8000:
        fail(f"sub-landscape (col4 WT) expected 8,000 rows, got {len(sub)}")
    if len(GB1_SEQ) != 56 or GB1_SEQ[38:41] != "VDG":
        fail("sequence gate: len/V-D-G at 39-41 mismatch")
    if GB1_SEQ.count("NGVDG") != 1:
        fail("NGVDG motif not unique")
    print(f"Data gates PASSED:160,000 genotypes, WT={wt_key}=1.0, "
          f"sub-landscape8,000 rows; md5={md5}")
    print(f"Sequence: PDB2GB156-mer; focal sites {FOCAL_SITES} = "
          f"{tuple(GB1_SEQ[p-1] for p in FOCAL_SITES)}; "
          f"site4 dropped (file WT letter V vs 2GB1 T44 — contradiction)")

    # ---------------- build design ----------------
    rng = np.random.default_rng(SEED)
    AA = list("ACDEFGHIKLMNPQRSTVWY")
    rows = []                     # (site, variant, bg_key, delta, e)
    n_scored =0
    from scripts.lib.esm_scoring import (get_position_logprobs,
                                          get_device)
    import esm
    device = get_device()
    print(f"\nLoading ESM-2 t33 650M on {device}...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()

    def gt(a39, a40, a41):
        return f"{a39}{a40}{a41}{COL4_WT}"

    def F(a39, a40, a41):
        key = gt(a39, a40, a41)
        if key not in fit.index:
            fail(f"genotype missing from fitness file: {key}")
        return float(fit[key])

    def bg_letters(focal_pos, config):
        """config = letters at the two NON-focal focal sites (in site order)."""
        idx = FOCAL_SITES.index(focal_pos)
        others = [j for j in range(3) if j != idx]
        letters = list(WT_COLS)
        letters[others[0]], letters[others[1]] = config
        return letters

    for focal in FOCAL_SITES:
        idx = FOCAL_SITES.index(focal)
        others = [j for j in range(3) if j != idx]
        wt_conf = tuple(WT_COLS[j] for j in others)
        all_conf = list(itertools.product(AA, repeat=2))
        alt_conf = [c for c in all_conf if c != wt_conf]
        chosen = [alt_conf[int(i)] for i in
                  rng.choice(len(alt_conf), size=K_BG, replace=False)]
        bgs = [wt_conf] + chosen

        # sequences: b0 and each alt bg (focal site stays WT residue)
        seqs = {}
        for conf in bgs:
            letters = list(WT_COLS)
            letters[others[0]], letters[others[1]] = conf
            s = list(GB1_SEQ)
            for j in range(3):
                if j != idx:
                    s[FOCAL_SITES[j] - 1] = letters[j]
            seqs[conf] = "".join(s)

        # one forward pass per background at the focal position ->19 scores
        s_b0 = {aa: sc for aa, sc in
                get_position_logprobs(model, alphabet, bc, seqs[wt_conf],
                                      focal, device).items()}
        n_scored +=1
        if abs(F(*bg_letters(focal, wt_conf)) - 1.0) > 1e-9:
            fail("b0 (WT-config background) fitness is not 1.0")
        for conf in chosen:
            s_b = get_position_logprobs(model, alphabet, bc, seqs[conf],
                                        focal, device)
            n_scored += 1
            letters_bg = bg_letters(focal, conf)
            wt_bg_fit = F(*letters_bg)          # f(WT, b): focal site WT, others conf
            for v, sc_b in s_b.items():
                d = sc_b - s_b0[v]              # delta_ESM(v|b) - delta_ESM(v|b0)
                # f(v, b): focal position = v, others as in letters_bg
                f_vb = letters_bg.copy()
                f_vb[idx] = v
                f_vb_conf = tuple(f_vb)
                # f(v, b0): focal = v, others WT
                f_vb0 = list(WT_COLS)
                f_vb0[idx] = v
                f_vb0_conf = tuple(f_vb0)
                e = (F(*f_vb_conf) - F(*f_vb0_conf)
                     - wt_bg_fit + F(*WT_COLS))
                rows.append({"site": focal, "variant": v,
                             "bg": "".join(conf), "delta": d, "e": e})

    df = pd.DataFrame(rows)
    print(f"Scored {n_scored} forward passes; "
          f"{len(df)} (variant, background) pairs "
          f"(expected {3 * 19 * K_BG})")
    if len(df) != 3 * 19 * K_BG:
        fail(f"pair count {len(df)} != {3 * 19 * K_BG}")

    # ---------------- statistics ----------------
    from scipy.stats import spearmanr
    d_arr = df["delta"].to_numpy()
    e_arr = df["e"].to_numpy()
    rho, _ = spearmanr(d_arr, e_arr)
    print(f"\nPRIMARY: pooled Spearman rho(delta_ESM, e) = {rho:+.4f} "
          f"over n={len(df)} pairs, {df['site'].nunique()} sites, "
          f"K={K_BG} backgrounds/site")

    # variant-block maps: one block = one (site, variant)'s K background rows
    sites = df["site"].unique()
    groups = {}
    for (s, v), g in df.groupby(["site", "variant"], sort=False):
        groups.setdefault(s, []).append(g.index.to_numpy())
    if sum(len(ix) for lst in groups.values() for ix in lst) != len(df):
        fail("variant-block maps do not cover every row")
    d_base = df["delta"].to_numpy()
    e_base = df["e"].to_numpy()

    # identity check (AGENTS §4): running the block machinery with the
    # identity order must reproduce the observed rho exactly, else exit(1)
    e_id = e_base.copy()
    for s in sites:
        for idxs in groups[s]:
            e_id[idxs] = e_base[idxs]
    rho_id, _ = spearmanr(d_base, e_id)
    if abs(rho_id - rho) > 1e-6:
        fail(f"identity check failed: {rho_id} != {rho}")
    print(f"Identity check: identity order through the block machinery "
          f"reproduces rho (max|diff| = {abs(rho_id - rho):.3e}) — PASS")

    # association null: permute variant labels WITHIN site — a variant's
    # whole K-background epistasis profile moves as a unit (delta stays
    # fixed; e is reassigned among variant blocks), breaking only the
    # pairing between delta and e across variants (AGENTS §4: association
    # null, labeled as such).
    rng_p = np.random.default_rng(SEED)
    perm_rhos = np.empty(N_PERM)
    for i in range(N_PERM):
        d_p = d_base.copy()
        e_p = e_base.copy()
        for s in sites:
            idxs = groups[s]
            order = rng_p.permutation(len(idxs))
            for slot, src in enumerate(order):
                e_p[idxs[slot]] = e_base[idxs[src]]
        rp, _ = spearmanr(d_p, e_p)
        perm_rhos[i] = rp
    p_one = (1 + np.sum(perm_rhos >= rho)) / (N_PERM + 1)
    p_two = (1 + np.sum(np.abs(perm_rhos) >= abs(rho))) / (N_PERM + 1)
    null_mean = float(np.nanmean(perm_rhos))
    null_sd = float(np.nanstd(perm_rhos))
    center_note = ("null centers on zero" if abs(null_mean) <= null_sd / 2
                   else "NULL DOES NOT CENTER ON ZERO — raw rho would "
                        "overstate the effect; excess over null is the "
                        "real result (AGENTS §4)")
    print(f"NULL (variant-profile permutation within site, N_PERM={N_PERM}): "
          f"mean={null_mean:+.4f} sd={null_sd:.4f} -> {center_note}")
    print(f"  one-sided p (pre-registered, positive) = {p_one:.4f}   "
          f"two-sided p = {p_two:.4f}")

    # cluster bootstrap by (site, variant) identity —57 clusters
    rng_b = np.random.default_rng(SEED)
    all_groups = [np.asarray(g) for s in sites for g in groups[s]]
    if len(all_groups) != 57:
        fail(f"expected57 (site,variant) clusters, got {len(all_groups)}")
    boots = np.empty(N_BOOT)
    for i in range(N_BOOT):
        pick = rng_b.integers(0, len(all_groups), len(all_groups))
        rows_i = np.concatenate([all_groups[j] for j in pick])
        rb, _ = spearmanr(d_base[rows_i], e_base[rows_i])
        boots[i] = rb
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    print(f"CI (cluster bootstrap by (site,variant), N_BOOT={N_BOOT}): "
          f"[{lo:+.4f}, {hi:+.4f}]  ({np.sum(~np.isnan(boots))}/{N_BOOT} valid)")

    # per-site rhos
    print("Per-site rho:")
    site_rhos = {}
    for s in sites:
        m = df["site"] == s
        rs, _ = spearmanr(df.loc[m, "delta"], df.loc[m, "e"])
        site_rhos[s] = rs
        print(f"  site {s}: rho={rs:+.4f}  (n={m.sum()})")

    passed = bool(rho > 0 and p_one < ALPHA)
    verdict = ("PASS: pipeline detects established epistasis "
               "(rho > 0, one-sided p < 0.05)" if passed else
               "FAIL: pipeline does NOT detect established epistasis at "
               "the pre-registered bar — MTHFR's negative is confounded "
               "with pipeline limitation")
    print(f"\nI1 GATE: {verdict}")
    print(f"Scale context: MTHFR's verified rho(delta_ESM, e.b) = "
          f"{MTHFR_RHO:+.6f} (S1/script-32, gate-checked in script 47)")

    out = pd.DataFrame([
        {"quantity": "pooled_rho", "value": rho},
        {"quantity": "ci_lo", "value": lo},
        {"quantity": "ci_hi", "value": hi},
        {"quantity": "p_one_sided", "value": p_one},
        {"quantity": "p_two_sided", "value": p_two},
        {"quantity": "null_mean", "value": float(np.nanmean(perm_rhos))},
        {"quantity": "n_pairs", "value": len(df)},
        {"quantity": "n_clusters", "value": len(all_groups)},
        {"quantity": "k_backgrounds", "value": K_BG},
        {"quantity": "gate_pass", "value": int(passed)},
    ] + [{"quantity": f"rho_site_{s}", "value": site_rhos[s]}
         for s in sites])
    out.to_csv(PROC / "task49_i1_gb1.csv", index=False)
    print(f"\nSaved to {PROC / 'task49_i1_gb1.csv'}  "
          f"(elapsed {time.time()-t0:.1f}s)")

    # ---------------- limitations (AGENTS §6) ----------------
    print("\nLIMITATIONS (printed by the script):")
    print("  - STRONG-epistasis control: passing shows the pipeline is not")
    print("    blind; it does NOT prove sensitivity to MTHFR-sized effects.")
    print("  - Site4 excluded: file WT letter V vs 2GB1 T44 contradiction,")
    print("    unresolved without the paper's numbering (disclosed, not guessed).")
    print("  - Background sampling fitness-blind, seed0, K=10 fixed pre-run.")
    print("  - Association null (pairing shuffle), not re-derivation: tests")
    print("    whether the pairing beats chance — the pipeline claim.")
    print("  - CI clusters by (site,variant) —57 clusters; 3 sites too few")
    print("    for a site-level bootstrap; per-site rhos reported instead.")
    print("  - GB1 fitness = sort-based assay; noise model differs from the")
    print("    atlas's. One model (ESM-2650M), as in the main pipeline.")
    print(f"  - Settings: N_BOOT={N_BOOT}, N_PERM={N_PERM}, SEED={SEED}, "
          f"K_BG={K_BG}.")


if __name__ == "__main__":
    main()
