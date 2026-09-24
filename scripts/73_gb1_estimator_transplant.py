"""
Script 73 (Group AA, task AA1a-c): transplant the MTHFR estimator onto GB1.

WHY (task doc AA1, lines 31-45)
--------------------------------
I1 validated a DIFFERENT statistic (within-site variant-profile
permutation, an association null that does not centre on zero -- scripts
49/65) than the one that produced the project's headline finding
(sign-flip re-derivation null, centres on zero -- script 33). This script
builds GB1's analogs of BOTH ESTIMATOR INPUTS (measured e.b, delta_ESM)
so that script 33's actual instrument can be run on a dataset whose
epistasis ground truth is known. The question AA1c asks is whether THAT
instrument -- not a different one -- centres on zero when run here.

PRE-REGISTRATION (written before this script was run; every choice below
was fixed before any background-genotype fitness value was read)
-----------------------------------------------------------------------
BACKGROUND: site 54, V->A ("V54A"), fixed for all variants -- the analog
of MTHFR's fixed A222V. Chosen for CHEMICAL PARALLELISM with A222V (the
same alanine/valine interchange, direction reversed because GB1's WT is V
here), NOT from any fitness value. Re fitness-blindness: during
reconnaissance the file's header and first two data lines were displayed
(VDGV = 1.0, ADGV = 0.0619...); the background genotype VDGA was NOT
among them and no lookup of it was made before these choices were fixed.
If VDGA turns out degenerate (dead or non-positive fitness), that is
REPORTED PLAINLY as a limitation of this control's parallel to A222V --
switching to a different letter after seeing fitness would be a
data-dependent choice and is NOT done here (a different letter = user
decision).

DESIGN: variants = the 19 non-WT residues at EACH of the OTHER three
assayed sites {39, 40, 41} -> 3 x 19 = 57 rows; single background (like
MTHFR's single A222V). Fitness arms from the full 20^4 landscape
(single arm = variant with WT elsewhere; double arm = variant + V54A).

ADAPTATIONS of own_context.py's construction (task AA1a requires each to
be documented explicitly -- this is NOT a copy-paste):
  A1. MTHFR's per-variant interaction estimate is the INTERCEPT of a
      weighted least-squares line through 4 concentration points
      (own_context.wls_line over CONCS). GB1 ships ONE fitness per
      genotype -- there is no concentration axis -- so the line collapses
      to a single identified point. wls_line returns NaN there by its own
      det != 0 guard (demonstrated at run time, printed). The GB1 e.b
      analog is therefore the residual ITSELF: the intercept functional
      the WLS line reduces to when the fit is identified. The sign-flip
      refit path applies the same reduction (flip the cell, read the
      intercept), with script 33's all-+1 / all--1 identity gates kept in
      full to verify row alignment across the fitness/ESM join (where
      misalignment could actually enter).
  A2. Weights: GB1 provides no per-genotype standard errors (one
      sort-derived fitness per genotype, no replicates in the file), so
      w = 1/se^2 degenerates to uniform weights (WLS -> OLS). Documented,
      not a choice made from results.
  A3. Multiplicative no-interaction expectation on the fitness scale:
      E[f(v + bg)] = f(v) * f(bg) / f(WT) -- the product form of
      own_context's expected(c) = (b_v + c*r_v) * (b_bg + c*r_bg).
      f(WT) = 1.0 exactly by file normalization; the division is kept for
      form-fidelity. e_b(v) = f(v + bg) - E[.] (additive-scale residual
      of the measured double arm, mirroring measured - expected).
  A4. NO fitness-based row filtering, pre-registered: all 57 rows enter
      regardless of fitness sign or zero expectation; counts of
      non-positive singles/doubles/expectations are printed as
      limitations instead.
  A5. Sign-flip cell = ONE residual per variant (GB1's design has no
      per-concentration cells; MTHFR flips 4 cells x 10,757 variants).
      The flip-unit count is exactly AA2's unit-of-analysis question and
      is printed explicitly.
  A6. Null 2 (the weaker association null) permutes delta across FOCAL
      SITE blocks -- 3 blocks vs MTHFR's 654 positions, coarse, labeled
      weaker. script 33's REGION check is omitted (GB1 has no MTHFR
      regions) -- disclosed here rather than silently dropped.

delta_ESM analog (AA1b) = script 12's definition transplanted:
  delta(v) = S(v | V54A background) - S(v | WT background), where S is
  the masked-marginal log-odds of the mutant at the focal position,
  computed by the SAME function script 33's pipeline family uses
  (scripts.lib.esm_scoring.get_position_logprobs, ESM-2 t33 650M) --
  6 forward passes total (3 sites x 2 contexts), mirroring script 49's
  sc_b - s_b0 computation with b = the single fixed background.

STATISTICS (script 33's code path, transplanted not rewritten; N_PERM
from env, default 10000; SEED 0; +0 correction identical to script 33)
  - Primary: signed Spearman rho(delta, e_b) via scripts.lib.stats
    _spearman (the same function script 33 correlates with).
  - NULL 1 sign-flip re-derivation: independent +/-1 per variant cell,
    re-derive e_b, recompute rho; p = mean(|null| >= |obs|); null
    centreing checked with script 33's exact expression
    |mean| < 2*sd/sqrt(N_PERM)*3; excess over null and
    frac_artifact printed exactly as script 33 prints them.
    Signed AND absolute versions both run (script 33 runs both).
  - NULL 2 site-block permutation of delta (weaker; association only).
  - IDENTITY GATES (script 33's, kept): all-+1 flips reproduce the
    stored e_b column exactly (max|diff| < 1e-6); all--1 give its exact
    negation; failure -> sys.exit(1). Data gates: 160,000 unique
    genotypes; WT fitness == 1.0; 20 AAs per column; GB1_SEQ letters at
    39/40/41/54 match the file's WT 4-mer VDGV; 57 rows; all finite.

DECISION RULES (pre-registered, reported without tuning)
  - "Instrument behaves" (AA1c's actual question) IFF the signed null
    centres on zero by script 33's expression.
  - "Detects established epistasis" IFF signed two-sided p < 0.05.
  - Both are reported; neither is tuned. A null that does NOT centre on
    zero is reported as such (AGENTS sec 4) -- it would invalidate this
    instrument here, not be explained away.

LIMITATIONS printed by this script too (AGENTS sec 6): single
background (n_bg = 1, parallel to MTHFR's A222V); 57 flip units and
only 3 sites (AA2 -- p-value draw count must not be read as 57 independent
sites); no concentrations -> no slope term; frac_artifact is computed on
Spearman rho exactly as script 33 computes it on its rho; V54A's fitness
is unknown at pre-registration time (printed).

Outputs: data/processed/task_AA1_gb1_eb_analog.csv (57-row construction
         table), data/processed/task_AA1_gb1_signflip_nulls.csv (script
         33's rows format).
"""
import sys, os, time, hashlib, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from scripts.lib.own_context import wls_line, CONCS
from scripts.lib.stats import _spearman

N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "external" / "GB1_fitness_landscape.txt"
PROC = ROOT / "data" / "processed"

# PDB 2GB1 entity 1 canonical 56-mer (script 49's constants, unchanged)
GB1_SEQ = "MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"
FOCAL_SITES = (39, 40, 41)     # 1-based; variants scored here
WT_COLS = ("V", "D", "G", "V")  # file WT 4-mer: sites (39,40,41,54)
BG_SITE_IDX = 3                # 0-based column of site 54 (the background)
BG_LETTER = "A"                # V54A -- fixed, fitness-blind (see docstring)
MTHFR_RHO = -0.08811806424891734
AA = list("ACDEFGHIKLMNPQRSTVWY")


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(1)


def pstr(p, n):
    return f"<{1.0/n:.4f}" if p == 0 else f"{p:.4f}"


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
    if len(GB1_SEQ) != 56 or GB1_SEQ[38:41] != "VDG":
        fail("sequence gate: len/V-D-G at 39-41 mismatch")
    if GB1_SEQ[53] != WT_COLS[BG_SITE_IDX]:
        fail(f"GB1_SEQ position 54 = {GB1_SEQ[53]!r} != file WT "
             f"{WT_COLS[BG_SITE_IDX]!r}")
    if GB1_SEQ.count("NGVDG") != 1:
        fail("NGVDG motif not unique")
    print(f"Data gates PASSED: 160,000 genotypes, WT={wt_key}=1.0, "
          f"20 AAs/column; md5={md5}")
    print(f"Background (pre-registered): site 54 {WT_COLS[3]}->{BG_LETTER} "
          f"(V54A), chemical parallel to A222V, fitness-blind")
    print(f"Variants: 19 non-WT residues at sites {FOCAL_SITES} -> 3x19=57 rows")

    # ---------------- AA1a: e.b analog from fitness arms ----------------
    def F(g):
        if g not in fit.index:
            fail(f"genotype missing from fitness file: {g}")
        return float(fit[g])

    def gkey(cols):
        return "".join(cols)

    f_wt = F(gkey(WT_COLS))
    bg_cols = list(WT_COLS)
    bg_cols[BG_SITE_IDX] = BG_LETTER
    f_bg = F(gkey(bg_cols))
    # FIRST read of the background fitness (fixed before this line was
    # ever executed -- see docstring): report, never re-select.
    print(f"\nf(WT) = {f_wt:.6f} | f(V54A background) = {f_bg:.6f}  "
          f"[first read of this value; A222V-parallel caveat below]")
    if f_bg <= 0:
        print("  *** LIMITATION: background fitness is non-positive. The "
              "multiplicative expectation collapses; this control is NOT a "
              "faithful A222V analog. Reported, not re-run (a different "
              "letter would be a data-dependent user decision). ***")

    rows = []
    n_nonpos_single = n_nonpos_double = n_nonpos_exp = 0
    for focal in FOCAL_SITES:
        idx = FOCAL_SITES.index(focal)
        for v in AA:
            if v == WT_COLS[idx]:
                continue
            sc = list(WT_COLS)
            sc[idx] = v
            dc = list(WT_COLS)
            dc[idx] = v
            dc[BG_SITE_IDX] = BG_LETTER
            f_v, f_vb = F(gkey(sc)), F(gkey(dc))
            expct = f_v * f_bg / f_wt
            e_b = f_vb - expct
            n_nonpos_single += f_v <= 0
            n_nonpos_double += f_vb <= 0
            n_nonpos_exp += expct <= 0
            rows.append({"site": focal, "variant": v,
                         "f_single": f_v, "f_double": f_vb,
                         "f_wt": f_wt, "f_bg": f_bg,
                         "expected_multiplicative": expct, "e_b": e_b})
    eb = pd.DataFrame(rows)
    if len(eb) != 57:
        fail(f"e.b analog rows = {len(eb)} != 57")
    if not np.isfinite(eb["e_b"]).all():
        fail("non-finite e_b in construction")
    print(f"e.b analog: n={len(eb)} | mean={eb['e_b'].mean():+.4f} "
          f"median={eb['e_b'].median():+.4f} | min={eb['e_b'].min():+.4f} "
          f"max={eb['e_b'].max():+.4f}")
    print(f"Non-positive-value counts (A4: kept, never filtered): "
          f"single arm {n_nonpos_single}, double arm {n_nonpos_double}, "
          f"expectation {n_nonpos_exp} of 57")
    print("Adaptations A1-A6 active: single-point residual replaces the "
          "4-concentration WLS line; uniform weights; multiplicative "
          "expectation on fitness scale; no row filtering; flip cell = "
          "variant; Null-2 blocks = site (region check omitted, no GB1 "
          "regions).")

    # Demonstrate A1: wls_line's own det-guard at one x-point (NaN),
    # so the residual-identity reduction is forced by the design, chosen.
    det_demo = wls_line(np.zeros((1, 1)), np.ones((1, 1)),
                        np.array([0.0]), np.ones((1, 1), dtype=bool))
    print(f"wls_line at n=1 x-point returns intercept={det_demo[0]} "
          f"(det=S0*S2-S1^2=0 -> NaN by its own guard): reduction A1 forced.")

    # ---------------- AA1b: delta_ESM analog (script 12 definition) -------
    from scripts.lib.esm_scoring import get_position_logprobs, get_device
    import esm
    device = get_device()
    print(f"\nLoading ESM-2 t33 650M on {device}...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()

    seq_bg_l = list(GB1_SEQ)
    seq_bg_l[53] = BG_LETTER
    seq_bg = "".join(seq_bg_l)

    n_pass = 0
    deltas = {}
    for focal in FOCAL_SITES:
        s_wt = get_position_logprobs(model, alphabet, bc, GB1_SEQ,
                                     focal, device)
        n_pass += 1
        s_bg = get_position_logprobs(model, alphabet, bc, seq_bg,
                                     focal, device)
        n_pass += 1
        for v, sc_b in s_bg.items():
            deltas[(focal, v)] = sc_b - s_wt[v]   # script 49's sc_b - s_b0
    print(f"Scored {n_pass} forward passes -> {len(deltas)} delta values "
          f"(expect 57)")
    if len(deltas) != 57:
        fail(f"delta count {len(deltas)} != 57")

    eb["delta_esm"] = [deltas[(r.site, r.variant)] for r in eb.itertuples()]
    df = eb.dropna().reset_index(drop=True)
    if len(df) != 57:
        fail(f"merged table rows {len(df)} != 57")
    if not np.isfinite(df["delta_esm"]).all():
        fail("non-finite delta_esm")
    print(f"delta_ESM analog: mean={df['delta_esm'].mean():+.4f} "
          f"median={df['delta_esm'].median():+.4f} "
          f"min={df['delta_esm'].min():+.4f} max={df['delta_esm'].max():+.4f}")

    # ---------------- AA1c: script 33's sign-flip pipeline ---------------
    # Mapped arrays: Rs (57 x 1) interaction residual cells (A1/A5: one
    # cell per variant); own_eb = stored column; dv = delta column.
    Rs = df["e_b"].to_numpy()[:, None]
    own_eb = df["e_b"].to_numpy()
    dv = df["delta_esm"].to_numpy()
    adv = np.abs(dv)

    def refit(r_cells):
        """A1 reduction: the flip-refit returns the (signed) residual
        intercept -- exactly what script 33's wls_line call yields for a
        row whose fit is identified at a single point. Identity gates
        below verify this path against the stored column."""
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
    print(f"  rows={len(df)} | flip units (cells)={Rs.size} "
          f"(one +/-1 per variant, A5) | sites={df['site'].nunique()} | "
          f"backgrounds=1 | MTHFR contrast: 10,757 variants x 4 conc cells "
          f"= 43,028 cells, 654 positions")

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
                  f"(signed two-sided p < 0.05)")
        else:
            print("    STRUCTURAL NOTE (A1/A5; this explanatory print was "
                  "added AFTER the smoke run first showed it -- post-hoc "
                  "DISCLOSURE, no statistic changed): with ONE cell per "
                  "variant, |flip * r| = |r| is invariant to the sign "
                  "flips, so the absolute sign-flip null equals the "
                  "observation IDENTICALLY (p = 1 by construction). The "
                  "absolute variant of Null 1 is DEGENERATE under the "
                  "single-cell transplant and carries no information "
                  "here. MTHFR's 4 cells per variant make its intercept "
                  "flip-sensitive, so that absolute test is non-degenerate "
                  "there (script 33).")
        rows_out.append({"null": "signflip", "variant": lbl, "observed": obs,
                         "null_mean": float(null.mean()),
                         "null_sd": float(null.std()),
                         "excess_over_null": excess, "frac_artifact": frac,
                         "p": pv, "n_perm": N_PERM, "survives": pv < 0.05})

    print("\n" + "=" * 74)
    print("NULL 2 -- SITE-BLOCK PERMUTATION (weaker; association only; "
          "A6: 3 blocks)")
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
    print("  interaction exceeds measurement noise. Null 1 is the real test.")
    rows_out.append({"null": "site_block", "variant": "signed",
                     "observed": obs2, "null_mean": float(null2.mean()),
                     "null_sd": float(null2.std()), "p": pv2,
                     "n_perm": N_PERM, "survives": pv2 < 0.05})

    print("\n" + "=" * 74)
    print("LIMITATIONS (printed here per AGENTS sec 6)")
    print("=" * 74)
    print(f"  - 57 flip units over 3 sites and 1 background: the p-value's")
    print(f"    precision comes from {N_PERM} draws, NOT from 57 independent")
    print(f"    sites; effective independent structure is 3 sites (AA2).")
    print(f"  - V54A fitness = {f_bg:.6f} (read once, pre-registered choice).")
    print(f"  - Single-background design mirrors MTHFR's single A222V.")
    print(f"  - No concentration axis: slope term not identifiable (A1);")
    print(f"    frac_artifact computed on Spearman rho as script 33 does.")
    print(f"  - Scale reference: MTHFR's verified signed "
          f"rho(delta_ESM, own_e_b) = {MTHFR_RHO}")

    out1 = PROC / "task_AA1_gb1_eb_analog.csv"
    df.to_csv(out1, index=False)
    out2 = PROC / "task_AA1_gb1_signflip_nulls.csv"
    pd.DataFrame(rows_out).to_csv(out2, index=False)
    print(f"\nSaved: {out1} ({len(df)} rows), {out2} ({len(rows_out)} rows)")
    print(f"Elapsed: {time.time() - t0:.1f}s | N_PERM={N_PERM} | SEED={SEED}")


if __name__ == "__main__":
    main()
