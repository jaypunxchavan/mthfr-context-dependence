"""
AD4 — native double-mutant scoring with ThermoMPNN-D (task doc L273-279),
PRE-REGISTERED. This docstring was written before the first run.

AD4a FINDINGS (recorded before any inference):
  Vendored ThermoMPNN (data/external/ThermoMPNN) does NOT support double-
  mutant scoring, verbatim evidence:
    * datasets.py L148: `# no insertions, deletions, or double mutants`
      (training rows whose mut_type contains ":" are skipped)
    * analysis/custom_inference.py builds single Mutation(position,wt,mut)
      objects only; transfer_model.py L113-116 ddG = (mut head) - (wt head)
      at a single aa_index
    * README L8: "A new ThermoMPNN model has been released for prediction
      of ddG for double mutant pairs at a new repo, [ThermoMPNN-D]"
  => AD4a's "if so" is FALSE locally; the upstream ThermoMPNN-D is the
  native double-mutant path, fetched and used here.

ThermoMPNN-D ACQUISITION (disclosed): git clone --depth 1
  https://github.com/Kuhlman-Lab/ThermoMPNN-D.git -> data/external/
  ThermoMPNN-D, clone size 125,488 KB (code + weights + notebooks; this
  is a code-repo fetch, NOT a member/data fetch: session member-data total
  unchanged ~196.3/200MB). Checkpoints ship in-repo, both far under the
  3GB/file weight cap: model_weights/ThermoMPNN-D-ens1.ckpt 8,097,475 B,
  model_weights/ThermoMPNN-ens1.ckpt 10,579,907 B (ens2/ens3 also present;
  ens1 is their get_model default - we use exactly what their CLI would).
  Their README's paper: Dieckhaus & Kuhlman, Protein Science 2025,
  doi 10.1002/pro.70003, "Protein stability models fail to capture
  epistatic interactions of double point mutations" - an external prior
  AGAINST detection; noted here so the interpretation of a null is
  pre-flagged as expected-by-literature, not invented post hoc.

THIRD-PARTY MODIFICATIONS (disclosed; backups kept):
  1. data/external/ThermoMPNN-D/v2_ssm.py device-portability patch,
     backup v2_ssm.py.bak_ad4, diff = 3x `device = "cuda"` -> `device =
     DEVICE`, 2x `model.cuda()` -> `model.to(DEVICE)`, +1 module-level
     DEVICE = cuda-if-available-else-cpu (+2 comment lines). Model math,
     enumeration, and postprocessing untouched (diff quoted in log entry).
  2. Process-level monkey-patch torch.load -> map_location="cpu" so
     pytorch_lightning restore of GPU-saved checkpoints works on this
     CUDA-less Mac. Applies only to this process; repo files untouched.
  Everything else is THEIR code called verbatim: get_config, get_model,
  load_pdb, tied_featurize_mut, run_single_ssm, run_double, SSMDataset,
  get_ssm_mutations_double, get_dmat. The only bespoke logic is row
  enumeration for the specific pairs we need, identity-gated against
  their own enumerator (G3, both directions).

THE QUANTITY (frozen): for every atlas variant v = (X wt->a, X != 222),
  interaction_D(v) = ddG_epi(222 A->V , X wt->a)
                   - ddG_single(X wt->a)
                   - ddG_single(222 A->V)
  * ddG_epi: their epistatic Siamese model (ThermoMPNN-D-ens1.ckpt) via
    run_double on our enumerated rows (loader shuffle=False, so row i of
    preds <-> row i of our metadata).
  * ddG_single: their single model (ThermoMPNN-ens1.ckpt) via their
    run_single_ssm; BOTH singles read from the same [L,21] wildtype-
    subtracted matrix (their L290-291), so v and 222 share one scale.
  * Units: model output units (their CSV column says "kcal/mol"; no unit
    conversion claimed - same hedge as [V3]).
  * No additive-term degeneracy: each of the three terms is an
    independent model evaluation (task L276-278).

ENUMERATION (frozen): rows = exactly the pairs {182 <-> seq_idx X} with
  the 222-side mutation fixed to V and the X-side over the 19 non-wt
  amino acids, canonical order p1<p2 with aligned wt/mut slots (their
  upper-triangle convention), wt/mut slot indices in their THERMO
  ALPHABET ("ACDEFGHIKLMNPQRSTVWYX", get_ssm_mutations_double L26).
  Unresolved positions (seq letter "-") excluded, matching their dmat>0
  filter. DataLoader: shuffle=False, batch_size=512 (AMENDED after smoke
  run 2 was SIGKILL'd (exit 137) at the forward pass: measured shapes ->
  edges [1,612,48,128], and run_double repeats them batch_size times, so
  their default 2048 needs 23.31 GiB of buffers (hid+embed+edges+E_idx;
  computed explicitly) on this 16 GiB Mac; 512 needs 5.83 GiB. Batch
  size is plumbing only - rows are processed independently (eval mode,
  no batchnorm, per-row gathers into repeated buffers), so predictions
  are batch-invariant. Measured BEFORE any statistic was computed; no
  decision rule touched. num_workers=0 (plumbing; cannot change values
  under shuffle=False).

MAPPING (frozen; script-68-style gates): their seq index = resi - 40
  (custom_parse_PDB_biounits fills gaps; min_resn = first chain-A resi;
  identical offset to the vendored model's gated map, [V3]'s 182).

GATES (failure => print reason, sys.exit(1); no threshold raising, no
larger-N retry):
  G0  model + cfg load (torch.load cpu patch working).
  G1  bounds + three-way wildtype match: every V2 seq_idx = resi-40 in
      [0, len(seq)) AND V2 wt_aa == D-pdb seq[resi-40] for all 10,141
      rows. Any failure: exit 1 (report first few).
  G2  seq[182] == "A".
  G3  enumeration identity, BOTH directions, on the V-at-222 slice:
      theirs_V = {their get_ssm_mutations_double(pdb,10.0) rows touching
      182 whose mutation at the 182-slot == V}; must EQUAL our rows with
      dmat(182,X) < 10 (exact tuple equality on pos/wt/mut), and
      ours_near must be a subset of their full set. exit 1 on any
      difference. [AMENDED after smoke run 1 failed: the original text
      demanded equality with their FULL set, but their enumerator emits
      all 19x19 combos per pair (8303 = 23 pairs x 361) while our frozen
      enumeration fixes the 222-side to V by design (23x19 = 437). The
      two docstring statements were internally inconsistent - a gate-
      definition defect found at smoke, corrected to like-for-like
      comparison; purpose unchanged: exact conformance of our row builder
      to their indexing conventions, both directions, on every row used.
      No statistic or threshold on the tested quantity changed.]
  G4  single-model cross-check: spearman(ddG_single_D(v), ddG_vendored(v))
      over the 10,141 variants >= 0.85 (their README: "should give
      similar results to the previously published ThermoMPNN models").
      Below => exit 1 (mapping/setup sanity fail; do not proceed).
  G4a single-matrix column-order resolution (pre-registered deterministic
      rule, not result-tuned): the wt-subtraction invariant makes
      column order[idx(wt_letter(L))] ~0 for every resolved L. Try their
      format_output_single order ("ACDEFGHIKLMNPQRSTVWYX") first; if
      max|.| > 1e-6 try ProteinMPNN order ("ARNDCQEGHILKMFPSTWYV"); if
      both fail => exit 1. Print which order was selected.
  G5  all 10,141 variants matched to an enumerated double; missing > 0 =>
      exit 1 with the list.
  G6  all outputs finite; row accounting printed at every step (section 5).

PRIMARY STATISTIC (frozen): row-level Spearman rho(interaction_D,
  own_e_b) on rows with finite own_e_b (expected n=9,595, 586 positions),
  position-cluster bootstrap CI (scripts.lib.stats, N_BOOT, seed 0),
  POSITION-level association null (scripts.lib.position_null: shuffle
  position means of interaction_D against fixed own_e_b position means,
  N_PERM, seed 1, two-sided |rho|, identity check mandatory).
  EXPECTED SIGN: NEGATIVE - interaction_D is in stability units
  (positive = more destabilizing than additive) while own_e_b is
  fitness-scale epistasis; the project's own additive reference has this
  orientation (AA4: ThermoMPNN signed rho -0.0733 vs own_e_b).
  VERDICT RULE (fixed now): "CAPTURES EPISTASIS" iff (i) p_pos < 0.05,
  AND (ii) rho < 0 (pre-declared orientation), AND (iii)
  |rho| > |rho_base| (beats the no-interaction-capacity baseline).
  Otherwise "DOES NOT CAPTURE" (print which conditions failed).
  A null is a result and will be reported plainly (AGENTS section 0).
SECONDARIES (frozen, always all reported):
  (a) magnitude view: rho(|interaction_D|, |own_e_b|) + cluster CI.
  (b) distance structure: rho(interaction_D, dmat[182,X] C-alpha), plus
      near (<=10 A) and far (>10 A) subset rhos with ns printed -
      descriptive only, NOT separate claim tests (the model couples via
      graph edges, so architecture can default far pairs toward
      additivity; this reports that structure rather than hiding it).
  (c) additive baseline with NO interaction capacity (AGENTS section 4):
      rho_base = rho(ddG_vendored(v), own_e_b) same rows + cluster CI.
  (d) effect sizes (section 3): mean/sd/max|interaction_D| vs mean
      |own_e_b|; also mean|interaction| within each (b) subset.
NULL LABEL: position shuffle = ASSOCIATION null (section 4). CONSTRUCTION
  NOTE (section 4, checked): ThermoMPNN-D was trained on the Tsuboyama
  mega-scale, NOT on this atlas's fitness, and own_e_b is not an input to
  D - the primary pairing has no shared-derivation structure (a strength
  relative to AD3, whose fit shared fitness inputs with own_e_b).
ENV: N_BOOT/N_PERM from env (default 10000; SMOKE=1 => 300/300).
OUTPUT: data/processed/task77_thermompnnD_doubles.csv (per-variant
  predictions + distances + flags).
LIMITATIONS (printed with results, section 6):
  1. ens1 checkpoint only (their get_model default); ens2/3 exist but
     averaging them would deviate from their own CLI behaviour - not done.
  2. CPU float path (device patch); G4 cross-check quantifies agreement
     with the published-model outputs produced on this same machine.
  3. Singles come from the single-model head, doubles from the Siamese
     epistatic head - two checkpoints in one framework (their own
     additive mode does the same: expand_additive over single-model
     outputs), so the decomposition is internally conventional but not
     one network.
  4. Far pairs may default near-additive by architecture (48-neighbour
     message passing); secondary (b) reports the distance structure
     honestly instead of averaging it away.
  5. Observational model-vs-measurement comparison; no causality.
"""
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
D_REPO = ROOT / "data" / "external" / "ThermoMPNN-D"
sys.path.insert(0, str(ROOT))            # for scripts.lib
sys.path.insert(0, str(D_REPO))          # for thermompnn/proteinmpnn/v2_ssm

# torch.load -> CPU (disclosed in docstring, applies to THIS process only;
# must be installed before any checkpoint restore)
import torch  # noqa: E402
_orig_torch_load = torch.load


def _torch_load_cpu(*args, **kwargs):
    kwargs["map_location"] = "cpu"
    return _orig_torch_load(*args, **kwargs)


torch.load = _torch_load_cpu

from scripts.lib.stats import position_cluster_bootstrap  # noqa: E402
from scripts.lib.position_null import position_shuffle_test  # noqa: E402
from thermompnn.datasets.dataset_utils import Mutation  # noqa: E402
from thermompnn.datasets.v2_datasets import tied_featurize_mut  # noqa: E402
from thermompnn.ssm_utils import (  # noqa: E402
    get_config,
    get_dmat,
    get_model,
    load_pdb,
)
from v2_ssm import (  # noqa: E402
    SSMDataset,
    get_ssm_mutations_double,
    run_double,
    run_single_ssm,
)
from torch.utils.data import DataLoader  # noqa: E402

PROC = ROOT / "data" / "processed"
PDB_PATH = ROOT / "data" / "raw" / "6FCX.pdb"
V2_PATH = PROC / "task_V2_thermompnn_ddg.csv"
OUT_PATH = PROC / "task77_thermompnnD_doubles.csv"

THERMO_ALPHABET = "ACDEFGHIKLMNPQRSTVWYX"   # their format_output_single order
MPNN_ALPHABET = "ARNDCQEGHILKMFPSTWYV"      # their parser/S order candidate
FIRST_RESI = 40                              # script 68 gated map, [V3]
IDX222 = 222 - FIRST_RESI                    # 182, their seq index
V222 = THERMO_ALPHABET.index("V")
ALA_IDX_T = THERMO_ALPHABET.index("A")
G4_MIN_RHO = 0.85
WT_COL_TOL = 1e-6
BATCH = 512                                  # see docstring: their 2048
                                             # default needs 23.31 GiB
                                             # (edges repeat) on 16 GiB RAM

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SMOKE = os.environ.get("SMOKE", "0") == "1"
if SMOKE:
    N_BOOT = min(N_BOOT, 300)
    N_PERM = min(N_PERM, 300)
SEED_BOOT, SEED_PERM = 0, 1
T0 = time.time()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


if __name__ == "__main__":
    import v2_ssm

    banner("AD4 -- ThermoMPNN-D NATIVE DOUBLE-MUTANT INTERACTION "
           f"(scripts/77) SMOKE={SMOKE} N_BOOT={N_BOOT} N_PERM={N_PERM}")
    print(f"  D repo: {D_REPO} | torch.load -> map_location=cpu (disclosed)")

    # ---------------- G0: config + model -----------------------------
    cfg = get_config("epistatic")
    model = get_model("epistatic", cfg)
    model.eval()
    pdb = load_pdb(str(PDB_PATH), ["A"])
    seq = pdb["seq"]
    print(f"  G0 cfg+model(epistatic) loaded | chain A parsed: "
          f"len(seq)={len(seq)} resolved={sum(c != '-' for c in seq)} "
          f"| DEVICE={v2_ssm.DEVICE}")
    cfg_s = get_config("single")
    model_s = get_model("single", cfg_s)
    model_s.eval()

    v2 = pd.read_csv(V2_PATH)

    # ---------------- G1/G2: mapping gates ---------------------------
    seq_idx = v2["position"].to_numpy() - FIRST_RESI
    if (seq_idx < 0).any() or (seq_idx >= len(seq)).any():
        gfail(f"G1 FAIL: seq_idx out of bounds "
              f"[{seq_idx.min()}, {seq_idx.max()}] vs len(seq)={len(seq)}")
    seq_letters = np.array([seq[i] for i in seq_idx])
    mism_mask = seq_letters != v2["wt_aa"].to_numpy()
    if mism_mask.any():
        gfail(f"G1 FAIL: {int(mism_mask.sum())} wt mismatches, first:\n"
              f"{v2.loc[mism_mask, ['position', 'wt_aa']].head()}")
    print(f"  G1 bounds + three-way wt match PASS: all {len(v2)} rows "
          f"(V2 wt == D-seq[resi-40])")
    if seq[IDX222] != "A":
        gfail(f"G2 FAIL: seq[{IDX222}]={seq[IDX222]!r} != 'A'")
    print(f"  G2 seq[{IDX222}]=='A' PASS | seq_idx range "
          f"{seq_idx.min()}..{seq_idx.max()}")

    # ---------------- enumeration (frozen) ---------------------------
    rows = []
    for X, wt2 in enumerate(seq):
        if wt2 == "-" or X == IDX222:
            continue
        w1, w2 = ALA_IDX_T, THERMO_ALPHABET.index(wt2)
        for a in range(20):
            if THERMO_ALPHABET[a] == wt2:
                continue
            if IDX222 < X:
                rows.append(((IDX222, X), (w1, w2), (V222, a)))
            else:
                rows.append(((X, IDX222), (w2, w1), (a, V222)))
    n_rows = len(rows)
    print(f"  enumeration: {n_rows} doubles "
          f"({n_rows // 19} positions x 19 alts)")

    MUT_POS = torch.tensor([r[0] for r in rows])
    MUT_WT = torch.tensor([r[1] for r in rows])
    MUT_MUT = torch.tensor([r[2] for r in rows])

    # ---------------- G3: identity vs their enumerator (both ways) ----
    dmat = get_dmat(pdb)
    t_pos, t_wt, t_mut = get_ssm_mutations_double(pdb, 10.0)
    theirs = set(zip(map(tuple, t_pos.tolist()),
                     map(tuple, t_wt.tolist()),
                     map(tuple, t_mut.tolist())))
    theirs_222 = {r for r in theirs if IDX222 in r[0]}
    ours = set(zip(map(tuple, MUT_POS.tolist()),
                   map(tuple, MUT_WT.tolist()),
                   map(tuple, MUT_MUT.tolist())))
    ours_near = {r for r in ours
                 if 0 < float(dmat[r[0][0], r[0][1]]) < 10.0}
    # AMENDED (disclosed in docstring G3): compare the V-at-222 slice.
    theirs_V = set()
    for pos, wt, mut in theirs_222:
        mut222 = mut[pos.index(IDX222)]
        if mut222 == V222:
            theirs_V.add((pos, wt, mut))
    if not ours_near <= theirs or ours_near != theirs_V:
        only_ours = list(ours_near - theirs_V)[:5]
        only_theirs = list(theirs_V - ours_near)[:5]
        gfail(f"G3 FAIL: enumeration identity broken both-direction check; "
              f"|ours_near|={len(ours_near)} |theirs_V|={len(theirs_V)} "
              f"|ours_near<=theirs|={ours_near <= theirs} "
              f"only-ours sample={only_ours} only-theirs sample={only_theirs}")
    n_pairs = len({r[0] for r in theirs_222})
    print(f"  G3 enumeration identity PASS (both directions, V-at-222 slice): "
          f"{len(ours_near)} near rows == their V-slice rows at 10A "
          f"({n_pairs} of their pairs x 361 combos = {len(theirs_222)}; "
          f"their full 10A set: {len(theirs)})")

    # ---------------- epistatic forward (their run_double) ------------
    pdb["mutation"] = Mutation([0], ["A"], ["A"], [0.0], "")
    batch = tied_featurize_mut([pdb])
    (X, S, mask, lengths, chain_M, chain_encoding_all, residue_idx,
     mut_positions, mut_wildtype_AAs, mut_mutant_AAs, mut_ddGs,
     atom_mask) = batch
    X = torch.nan_to_num(X, nan=0.0)
    with torch.no_grad():
        all_mpnn_hid, mpnn_embed, _, mpnn_edges = model.prot_mpnn(
            X, S, mask, chain_M, residue_idx, chain_encoding_all
        )
    dataset = SSMDataset(MUT_POS, MUT_WT, MUT_MUT)
    loader = DataLoader(dataset, shuffle=False, batch_size=BATCH,
                        num_workers=0)
    with torch.no_grad():
        preds = run_double(all_mpnn_hid, mpnn_embed, cfg, loader, BATCH,
                           model, X, mask, mpnn_edges)
    preds = np.atleast_1d(np.asarray(preds, dtype=float))
    if len(preds) != n_rows or not np.all(np.isfinite(preds)):
        gfail(f"G6 FAIL: preds len {len(preds)} != {n_rows} or non-finite")
    print(f"  epistatic forward PASS: n={len(preds)} "
          f"ddG range [{preds.min():+.3f}, {preds.max():+.3f}]")

    # ---------------- single forward (their run_single_ssm) -----------
    with torch.no_grad():
        ddg_t, S_t = run_single_ssm(dict(pdb), cfg_s, model_s)
    ddg_mat = ddg_t.detach().cpu().numpy()      # [L, 21]
    L = ddg_mat.shape[0]
    if L != len(seq):
        gfail(f"G6 FAIL: single matrix L={L} != seq {len(seq)}")

    # ---------------- G4a: column order via wt-subtraction invariant --
    resolved = [i for i, c in enumerate(seq) if c != "-"]
    chosen = None
    for name, alph in (("THERMO", THERMO_ALPHABET), ("MPNN", MPNN_ALPHABET)):
        worst = 0.0
        for i in resolved:
            worst = max(worst, abs(float(ddg_mat[i, alph.index(seq[i])])))
        print(f"    G4a candidate {name}: max|wt-column ddg| = {worst:.3e}")
        if worst <= WT_COL_TOL and chosen is None:
            chosen = (name, alph)
    if chosen is None:
        gfail("G4a FAIL: neither column order satisfies the wt-zero "
              "invariant (<=1e-6)")
    colname, COL_ALPH = chosen
    print(f"  G4a column order selected: {colname} (wt-zero invariant)")

    # ---------------- extract singles + G4 cross-check ----------------
    def ddg_single(resi, mut_aa):
        i = resi - FIRST_RESI
        return float(ddg_mat[i, COL_ALPH.index(mut_aa)])

    ddg_222_s = ddg_single(222, "V")
    v2["ddg_single_D"] = [ddg_single(r, m) for r, m in
                          zip(v2["position"], v2["mut_aa"])]
    g4 = float(spearmanr(v2["ddg_single_D"], v2["ddg"]).statistic)
    if not np.isfinite(g4) or g4 < G4_MIN_RHO:
        gfail(f"G4 FAIL: cross-model rho {g4:.4f} < {G4_MIN_RHO} "
              "(mapping/setup sanity; not proceeding)")
    print(f"  G4 cross-model PASS: spearman(ddG_single_D, ddG_vendored) = "
          f"{g4:.4f} over n={len(v2)} (their README: 'similar results')")

    # ---------------- join epistatic preds + G5 -----------------------
    row_lookup = {}
    for k, (pos, wt, mut) in enumerate(rows):
        if pos[0] == IDX222:
            Xp, a = pos[1], mut[1]
        else:
            Xp, a = pos[0], mut[0]
        row_lookup[(Xp, a)] = preds[k]
    v2["ddg_epi_D"] = [
        row_lookup.get((int(p) - FIRST_RESI,
                        THERMO_ALPHABET.index(m)), np.nan)
        for p, m in zip(v2["position"], v2["mut_aa"])
    ]
    n_miss = int(v2["ddg_epi_D"].isna().sum())
    if n_miss:
        gfail(f"G5 FAIL: {n_miss} variants unmatched; first: "
              f"{v2.loc[v2['ddg_epi_D'].isna(), ['hgvs_pro']].head()}")
    v2["interaction_D"] = (v2["ddg_epi_D"] - v2["ddg_single_D"]
                           - ddg_222_s)
    if not np.all(np.isfinite(v2["interaction_D"].to_numpy())):
        gfail("G6 FAIL: non-finite interaction_D")
    print(f"  G5 all {len(v2)} doubles matched PASS | ddG_single(222V) = "
          f"{ddg_222_s:+.4f}")

    # ---------------- distances + analysis set ------------------------
    v2["ca_dist_222"] = [
        float(dmat[int(p) - FIRST_RESI, IDX222])
        for p in v2["position"]
    ]
    t = v2[v2["own_e_b"].notna()].copy()
    print(f"  analysis rows: {len(t)} (own_e_b finite) across "
          f"{t['position'].nunique()} positions | dropped for NaN own_e_b: "
          f"{len(v2) - len(t)}")

    banner("STAGE B -- PRIMARY: rho(interaction_D, own_e_b)", "=")
    cb = position_cluster_bootstrap(t, "position", "interaction_D",
                                    "own_e_b", n_boot=N_BOOT,
                                    seed=SEED_BOOT)
    rho_obs, p_pos, n_pos = position_shuffle_test(t, "interaction_D",
                                                  "own_e_b", N_PERM,
                                                  SEED_PERM)
    print(f"  PRIMARY rho(interaction_D, own_e_b) = "
          f"{cb['observed_rho']:+.4f} [{cb['ci_lo']:+.4f}, "
          f"{cb['ci_hi']:+.4f}] p_boot={cb['p_boot']:.4f} "
          f"n={cb['n_rows']} clusters={cb['n_clusters']}")
    print(f"  POSITION-LEVEL association null: rho_pos={rho_obs:+.4f} "
          f"p={p_pos:.4f} (N_PERM={N_PERM}, positions={n_pos}, "
          f"identity check PASS)")

    # additive baseline (verdict condition iii needs it)
    cb_base = position_cluster_bootstrap(t, "position", "ddg", "own_e_b",
                                         n_boot=N_BOOT, seed=SEED_BOOT)
    rho_base = cb_base["observed_rho"]

    cond1 = p_pos < 0.05
    cond2 = cb["observed_rho"] < 0
    cond3 = abs(cb["observed_rho"]) > abs(rho_base)
    captures = cond1 and cond2 and cond3
    verdict = ("CAPTURES EPISTASIS" if captures else
               "DOES NOT CAPTURE EPISTASIS")
    print(f"  VERDICT RULE (frozen): p<0.05 AND rho<0 AND |rho|>|rho_base|"
          f" -> {verdict}")
    print(f"    conditions: (i) p={p_pos:.4f} {'T' if cond1 else 'F'} | "
          f"(ii) rho<0 {'T' if cond2 else 'F'} | "
          f"(iii) |rho|={abs(cb['observed_rho']):.4f} vs "
          f"|base|={abs(rho_base):.4f} {'T' if cond3 else 'F'}")

    # ---------------- secondaries -------------------------------------
    t["abs_int"] = t["interaction_D"].abs()
    t["abs_eb"] = t["own_e_b"].abs()
    ca = position_cluster_bootstrap(t, "position", "abs_int", "abs_eb",
                                    n_boot=N_BOOT, seed=SEED_BOOT)
    print(f"  (a) rho(|interaction_D|, |own_e_b|) = "
          f"{ca['observed_rho']:+.4f} [{ca['ci_lo']:+.4f}, "
          f"{ca['ci_hi']:+.4f}] p_boot={ca['p_boot']:.4f}")

    rho_dist = float(spearmanr(t["interaction_D"],
                               t["ca_dist_222"]).statistic)
    near = t[t["ca_dist_222"] <= 10.0]
    far = t[t["ca_dist_222"] > 10.0]
    rho_near = (float(spearmanr(near["interaction_D"],
                                near["own_e_b"]).statistic)
                if len(near) >= 3 else float("nan"))
    rho_far = (float(spearmanr(far["interaction_D"],
                               far["own_e_b"]).statistic)
               if len(far) >= 3 else float("nan"))
    print(f"  (b) rho(interaction_D, Ca-dist 222) = {rho_dist:+.4f} | "
          f"near<=10A: n={len(near)} rho={rho_near:+.4f} | "
          f"far>10A: n={len(far)} rho={rho_far:+.4f} (descriptive)")

    print(f"  (c) additive baseline rho(ddG_vendored, own_e_b) = "
          f"{rho_base:+.4f} [{cb_base['ci_lo']:+.4f}, "
          f"{cb_base['ci_hi']:+.4f}] p_boot={cb_base['p_boot']:.4f} "
          f"(AA4's -0.0733 was the wider-set figure)")

    ii = t["interaction_D"].abs()
    eb = t["own_e_b"].abs()
    # unit labels added after smoke run 4 (cosmetic only; values and
    # statistics unchanged): the two sides are in DIFFERENT units, so
    # their ratio is cross-unit context, not a same-scale comparison.
    print(f"  (d) effect sizes [UNITS DIFFER: interaction in model output "
          f"units (their column label kcal/mol); own_e_b in fitness units "
          f"- the ratio below is CROSS-UNIT context only]:")
    print(f"      interaction_D mean="
          f"{t['interaction_D'].mean():+.5f} sd="
          f"{t['interaction_D'].std():.5f} mean|.|={ii.mean():.5f} "
          f"max|.|={ii.max():.5f}  vs own_e_b mean|.|={eb.mean():.5f} "
          f"cross-unit ratio={ii.mean() / eb.mean():.4f}")
    print(f"      mean|interaction| near="
          f"{near['interaction_D'].abs().mean():.5f} far="
          f"{far['interaction_D'].abs().mean():.5f}")

    v2["in_test"] = v2["own_e_b"].notna().astype(int)
    v2.to_csv(OUT_PATH, index=False)
    print(f"\n  saved {len(v2)} rows -> {OUT_PATH.name}")

    banner("LIMITATIONS (printed with results, AGENTS section 6)", "-")
    lim = f"""  1. ens1 checkpoint only (their get_model default); ens2/3 not
     averaged (would deviate from their CLI behaviour).
  2. CPU float path (device patch); G4 cross-check = {g4:.4f} agreement
     with the published-model outputs on this machine.
  3. Singles from single-model head, doubles from Siamese epistatic head
     (two checkpoints in one framework; their own additive mode does the
     same).
  4. Far pairs may default near-additive by architecture (48-neighbour
     message passing); (b) reports the distance structure honestly.
  5. Observational comparison; no causality. External prior: their own
     paper (doi 10.1002/pro.70003) reports stability models generally
     fail to capture double-mutant epistasis - a null here would agree
     with published findings, not contradict them."""
    print(lim)
    print(f"\nAD4 DONE  ({time.time() - T0:.1f}s)  VERDICT: {verdict}")
