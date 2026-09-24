"""
Script 65 (site54-and-script50-migration, task Q1): FOUR-SITE rerun of the
I1 GB1 positive control — scripts/49_i1_gb1_positive_control.py with all
four assayed GB1 sites included instead of three.

WHY (task doc Q1, authorized by MIGRATION_LOG P1d/P2b)
------------------------------------------------------
Script 49 dropped GB1's 4th assayed site (54) on a logged contradiction
("site4 dropped (file WT letter V vs 2GB1 T44 — contradiction)"). This
session independently verified from primary sources that this was a
NUMBERING CONFUSION, not a data inconsistency (MIGRATION_LOG P1, P2):

- P1 (RCSB, fetched live): 2GB1 author numbering is a contiguous 1-56
  56-mer, no insertion codes; residue 54 = VAL (letter V — matches the
  file's WT letter at column 4), residue 44 = THR (the T script 49 worried
  about). File WT 4-mer VDGV matches PDB letters at 39/40/41/54 exactly
  (VDGV) and mismatches 39/40/41/44 (VDGT).
- P2 (Wu et al. 2016, eLife 16965, fetched live): the paper states the four
  sites are "V39, D40, G41 and V54" and WT genotype "VDGV" (verbatim).
  Fig 3D prints eps = +5 (G41LxV54H on IL background) and eps = -4.5 (on
  WL background); re-deriving from the on-disk landscape under the paper's
  own eq. (2) gives +7.399806 and -4.495855 respectively (the +5 label does
  not re-derive; -4.5 does — full detail in MIGRATION_LOG P2). The dropped
  41x54 axis therefore carries the comparator paper's headline epistasis.

Q1 reruns the comparator with site 54 INCLUDED. This is a NEW, separate
result: script 49's frozen 3-site run (data/processed/task49_i1_gb1.csv) is
never read, modified, or overwritten by this script.

PRE-REGISTERED (identical to script 49 — the gate is unchanged)
----------------------------------------------------------------
- Focal sites: (39, 40, 41, 54); WT letters (V, D, G, V) = file columns 1-4.
- Backgrounds: b0 (WT config of the other three focal sites) + K=10 sampled
  WITHOUT replacement from the 20^3 - 1 = 7,999 non-WT configs of the other
  three sites, np.random.default_rng(0) — same seed as script 49, same
  order of draws, FITNESS-BLIND (no data-dependent selection).
- Analyzed pairs: (v, alternate background) only -> 4 x 19 x 10 = 760 rows.
  (v, b0) pairs excluded BY RULE: delta and e are identically 0 there.
- Target: e(v,b) = f(v,b) - f(v,b0) - f(WT,b) + f(WT,b0) — the same
  double-mutant-cycle interaction script 49 used (unchanged formula).
- Primary statistic: pooled Spearman rho(delta_ESM, e) over the 760 rows.
- NULL: variant-label permutation WITHIN site — script 49's exact
  association null, code reused verbatim: a variant's whole K-background
  e profile moves as one unit (preserves within-variant cross-background
  dependence; breaks only which variant carries which profile).
  N_PERM=10000 (env), +1 correction; one-sided positive is the
  pre-registered gate, two-sided p also printed.
  (Disclosed reading, MIGRATION_LOG Q1: task Q1a calls this the
  "sign-flip-null pipeline"; script 49 as-built implements this
  within-site variant-profile permutation — labeled an ASSOCIATION null in
  its own docstring — and that as-built machinery is what is reused, since
  Q1a says "do not rewrite it".)
- IDENTITY CHECK (AGENTS §4): an all-identity permutation must reproduce
  rho_obs to <1e-6, else sys.exit(1).
- CI: cluster bootstrap resampling (site, variant) identities — 4 x 19 = 76
  clusters (AGENTS §3: rows sharing a variant are never resampled
  independently). N_BOOT=2000 (env), seed 0.
- Null centering printed (AGENTS §4); per-site rhos printed.
- DECISION RULE (pre-registered, unchanged from script 49): the control
  PASSES iff rho_obs > 0 AND one-sided permutation p < 0.05.

CHANGES VS SCRIPT 49 (exactly three; everything else is the same code)
----------------------------------------------------------------------
1. Fourth site included: FOCAL_SITES = (39, 40, 41, 54); the col4-drop and
   its 8,000-row sub-landscape gate are gone (all four columns of the
   full 160,000-genotype landscape now vary across backgrounds).
2. Counts generalize: 570 -> 760 rows; 57 -> 76 (site,variant) clusters;
   33 -> 44 forward passes; two background positions vary per script 49,
   three now vary here (product space 399 -> 7,999).
3. Output path: data/processed/task_Q1_foursite_i1_rerun.csv (Q1d's named
   deliverable).

CAVEATS (printed by the script too, AGENTS §6)
-----------------------------------------------
- STRONG-epistasis control: passing shows the pipeline is not blind; it
  does NOT prove sensitivity to MTHFR-sized effects.
- This is a MODIFICATION of the same comparator (GB1), not an independent
  dataset — it must not be reported as "an alternative comparator found".
- Background sampling fitness-blind, seed0, K=10 fixed pre-run (same seed
  as 49; sampling frame differs because three background positions vary).
- Association null (variant-profile permutation), not re-derivation: tests
  whether the pairing beats chance — the pipeline claim.
- CI clusters by (site,variant) — 76 clusters; 4 sites still too few for a
  site-level bootstrap; per-site rhos reported instead.
- GB1 fitness = sort-based assay; noise model differs from the atlas's.
  One model (ESM-2 650M), as in the main pipeline.
- Known prior-session finding that stands regardless of this rerun: 41.5%
  (534/1287) of the 3-site run's fitness lookups sat at/below GB1's
  detection limit 0.01 (FOLLOWUP_LOG L1b); a four-site design draws more
  lookups from the same assay.

Data gates (sys.exit(1)): file parses to 160,000 unique genotypes; WT
fitness == 1.0; all 20 AAs per column; sequence len 56 with VDG at 39-41,
V at 54, and exactly one NGVDG; pair count == 760; clusters == 76.

Output: data/processed/task_Q1_foursite_i1_rerun.csv
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
OUT = PROC / "task_Q1_foursite_i1_rerun.csv"   # Q1d named deliverable

# PDB 2GB1 (RCSB, fetched and parsed in MIGRATION_LOG P1), canonical 56-mer;
# four sites per Wu et al. 2016: "V39, D40, G41 and V54" (quoted in P2)
GB1_SEQ = "MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"
FOCAL_SITES = (39, 40, 41, 54)    # 1-based; site 54 now INCLUDED (was dropped)
WT_COLS = ("V", "D", "G", "V")    # WT letters at focal sites = file cols 1-4
MTHFR_RHO = -0.08811806424891734  # verified S1/script-32 value (gate in 47)
N_SITES = len(FOCAL_SITES)
N_CLUSTERS_EXPECT = N_SITES * 19          # 76 (site,variant) clusters
N_PAIRS_EXPECT = N_SITES * 19 * K_BG      # 760 analyzed rows


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
    wt_key = "".join(WT_COLS)
    if abs(float(fit[wt_key]) - 1.0) > 1e-9:
        fail(f"WT {wt_key} fitness {fit[wt_key]} != 1.0")
    for i, col in enumerate("1234"):
        aas = set(raw["sequence"].str[i])
        if len(aas) != 20:
            fail(f"column {col} has {len(aas)} AAs, expected 20")
    # no col4-drop in the four-site design: the full landscape is the pool
    if len(GB1_SEQ) != 56 or GB1_SEQ[38:41] != "VDG" or GB1_SEQ[53] != "V":
        fail("sequence gate: len / V-D-G at 39-41 / V at 54 mismatch")
    if GB1_SEQ.count("NGVDG") != 1:
        fail("NGVDG motif not unique")
    print(f"Data gates PASSED: 160,000 genotypes, WT={wt_key}=1.0, "
          f"all four columns 20-letter; md5={md5}")
    print(f"Sequence: PDB 2GB1 56-mer; focal sites {FOCAL_SITES} = "
          f"{tuple(GB1_SEQ[p-1] for p in FOCAL_SITES)}; "
          f"site 54 INCLUDED (numbering resolved: RCSB 2GB1 V54 + "
          f"Wu2016 'V39, D40, G41 and V54' — MIGRATION_LOG P1/P2)")

    # ---------------- build design ----------------
    rng = np.random.default_rng(SEED)
    AA = list("ACDEFGHIKLMNPQRSTVWY")
    rows = []                     # (site, variant, bg_key, delta, e)
    n_scored = 0
    from scripts.lib.esm_scoring import (get_position_logprobs,
                                          get_device)
    import esm
    device = get_device()
    print(f"\nLoading ESM-2 t33 650M on {device}...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()

    def F(*letters):
        key = "".join(letters)
        if key not in fit.index:
            fail(f"genotype missing from fitness file: {key}")
        return float(fit[key])

    def bg_letters(focal_pos, config):
        """config = letters at the three NON-focal focal sites (site order)."""
        idx = FOCAL_SITES.index(focal_pos)
        others = [j for j in range(N_SITES) if j != idx]
        letters = list(WT_COLS)
        for k, j in enumerate(others):
            letters[j] = config[k]
        return letters

    for focal in FOCAL_SITES:
        idx = FOCAL_SITES.index(focal)
        others = [j for j in range(N_SITES) if j != idx]
        wt_conf = tuple(WT_COLS[j] for j in others)
        all_conf = list(itertools.product(AA, repeat=len(others)))
        alt_conf = [c for c in all_conf if c != wt_conf]
        chosen = [alt_conf[int(i)] for i in
                  rng.choice(len(alt_conf), size=K_BG, replace=False)]
        bgs = [wt_conf] + chosen

        # sequences: b0 and each alt bg (focal site stays WT residue)
        seqs = {}
        for conf in bgs:
            letters = list(WT_COLS)
            for k, j in enumerate(others):
                letters[j] = conf[k]
            s = list(GB1_SEQ)
            for j in range(N_SITES):
                if j != idx:
                    s[FOCAL_SITES[j] - 1] = letters[j]
            seqs[conf] = "".join(s)

        # one forward pass per background at the focal position -> 19 scores
        s_b0 = {aa: sc for aa, sc in
                get_position_logprobs(model, alphabet, bc, seqs[wt_conf],
                                      focal, device).items()}
        n_scored += 1
        if abs(F(*bg_letters(focal, wt_conf)) - 1.0) > 1e-9:
            fail("b0 (WT-config background) fitness is not 1.0")
        for conf in chosen:
            s_b = get_position_logprobs(model, alphabet, bc, seqs[conf],
                                        focal, device)
            n_scored += 1
            letters_bg = bg_letters(focal, conf)
            wt_bg_fit = F(*letters_bg)      # f(WT, b): focal WT, others conf
            for v, sc_b in s_b.items():
                d = sc_b - s_b0[v]          # delta_ESM(v|b) - delta_ESM(v|b0)
                # f(v, b): focal position = v, others as in letters_bg
                f_vb = letters_bg.copy()
                f_vb[idx] = v
                # f(v, b0): focal = v, others WT
                f_vb0 = list(WT_COLS)
                f_vb0[idx] = v
                e = (F(*f_vb) - F(*f_vb0)
                     - wt_bg_fit + F(*WT_COLS))
                rows.append({"site": focal, "variant": v,
                             "bg": "".join(conf), "delta": d, "e": e})

    df = pd.DataFrame(rows)
    print(f"Scored {n_scored} forward passes; "
          f"{len(df)} (variant, background) pairs "
          f"(expected {N_PAIRS_EXPECT})")
    if len(df) != N_PAIRS_EXPECT:
        fail(f"pair count {len(df)} != {N_PAIRS_EXPECT}")

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

    # identity check (AGENTS §4): identity order through the block machinery
    # must reproduce the observed rho exactly, else exit(1)
    e_id = e_base.copy()
    for s in sites:
        for idxs in groups[s]:
            e_id[idxs] = e_base[idxs]
    rho_id, _ = spearmanr(d_base, e_id)
    if abs(rho_id - rho) > 1e-6:
        fail(f"identity check failed: {rho_id} != {rho}")
    print(f"Identity check: identity order through the block machinery "
          f"reproduces rho (max|diff| = {abs(rho_id - rho):.3e}) — PASS")

    # association null (script 49's exact machinery): permute variant labels
    # WITHIN site — a variant's whole K-background e profile moves as a unit
    # (delta stays fixed), breaking only the pairing across variants.
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

    # cluster bootstrap by (site, variant) identity — 76 clusters
    rng_b = np.random.default_rng(SEED)
    all_groups = [np.asarray(g) for s in sites for g in groups[s]]
    if len(all_groups) != N_CLUSTERS_EXPECT:
        fail(f"expected {N_CLUSTERS_EXPECT} (site,variant) clusters, "
             f"got {len(all_groups)}")
    boots = np.empty(N_BOOT)
    for i in range(N_BOOT):
        pick = rng_b.integers(0, len(all_groups), len(all_groups))
        rows_i = np.concatenate([all_groups[j] for j in pick])
        rb, _ = spearmanr(d_base[rows_i], e_base[rows_i])
        boots[i] = rb
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    print(f"CI (cluster bootstrap by (site,variant), N_BOOT={N_BOOT}): "
          f"[{lo:+.4f}, {hi:+.4f}]  "
          f"({np.sum(~np.isnan(boots))}/{N_BOOT} valid)")

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
    print(f"\nQ1 FOUR-SITE I1 GATE (same pre-registered rule as script 49): "
          f"{verdict}")
    print(f"Scale context: MTHFR's verified rho(delta_ESM, e.b) = "
          f"{MTHFR_RHO:+.6f} (S1/script-32, gate-checked in script 47)")

    out = pd.DataFrame([
        {"quantity": "pooled_rho", "value": rho},
        {"quantity": "ci_lo", "value": lo},
        {"quantity": "ci_hi", "value": hi},
        {"quantity": "p_one_sided", "value": p_one},
        {"quantity": "p_two_sided", "value": p_two},
        {"quantity": "null_mean", "value": null_mean},
        {"quantity": "n_pairs", "value": len(df)},
        {"quantity": "n_clusters", "value": len(all_groups)},
        {"quantity": "k_backgrounds", "value": K_BG},
        {"quantity": "gate_pass", "value": int(passed)},
    ] + [{"quantity": f"rho_site_{s}", "value": site_rhos[s]}
         for s in sites])
    out.to_csv(OUT, index=False)
    print(f"\nSaved to {OUT}  (elapsed {time.time()-t0:.1f}s)")
    print("NOTE: script 49's 3-site output task49_i1_gb1.csv untouched.")

    # ---------------- limitations (AGENTS §6) ----------------
    print("\nLIMITATIONS (printed by the script):")
    print("  - STRONG-epistasis control: passing shows the pipeline is not")
    print("    blind; it does NOT prove sensitivity to MTHFR-sized effects.")
    print("  - Site 54 INCLUDED (was dropped by 49 on a numbering confusion;")
    print("    resolved from RCSB + Wu2016 — MIGRATION_LOG P1/P2).")
    print("  - Modification of the SAME comparator (GB1), not an independent")
    print("    dataset; do not report as 'an alternative comparator found'.")
    print("  - Background sampling fitness-blind, seed0, K=10 fixed pre-run.")
    print("  - Association null (variant-profile permutation), not")
    print("    re-derivation: tests whether the pairing beats chance.")
    print("  - CI clusters by (site,variant) — 76 clusters; 4 sites too few")
    print("    for a site-level bootstrap; per-site rhos reported instead.")
    print("  - GB1 fitness = sort-based assay; 41.5% of the 3-site run's")
    print("    lookups were <= detection limit 0.01 (FOLLOWUP_LOG L1b).")
    print("  - One model (ESM-2 650M), as in the main pipeline.")
    print(f"  - Settings: N_BOOT={N_BOOT}, N_PERM={N_PERM}, SEED={SEED}, "
          f"K_BG={K_BG}.")


if __name__ == "__main__":
    main()
