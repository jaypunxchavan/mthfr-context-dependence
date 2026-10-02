"""Script 161 (Phase 3a session 3a, task A4d) -- HARD gate G-1' for the
GB1 module.  Uses the model; writes only to a scratch directory.

PRE-REGISTERED: this docstring was written before the first run of this
script.  It implements PHASE3_OVERNIGHT.md Task A4d under the frozen
prereg/GB1_REGIME_PREREG_v2.md section 3 amendment A3, verbatim:

  "G-1' (hard): rescoring the V54A background and the wild-type arm at
   positions 39, 40, 41 on the PROJECT sequence (T at position 2)
   reproduces script 73's cached delta_esm for all 57 variants to 1e-6,
   and the control rho re-derives as +0.12218045112781956 (to 1e-9).
   This proves the machinery independent of the sequence choice.  V54A on
   the assayed sequence is reported, not gated."

MACHINERY, SHARED NOT REIMPLEMENTED: the scoring path is scripts/154's
own score_positions() (one unbatched masked-marginal forward pass per
(background, position) via scripts/lib/esm_scoring.py::
get_position_logprobs), loaded from scripts/154_gb1_score_backgrounds.py
by importlib -- the SAME function the 400-background stage will call.
Input sha gates G-154-1/G-154-2 are 154's own, invoked via its
load_inputs().

STATISTIC: the control rho is computed with scripts.lib.stats._spearman,
the exact statistic script 73 used (its import at script 73 line 126),
whose source is printed at run time.

THE FITNESS SIDE IS RE-DERIVED, NOT TRUSTED: e_b is rebuilt from
data/external/GB1_fitness_landscape.txt with script 73's construction
(quoted at run time from scripts/73 lines 188-231):
    f_v    = fitness(WT with v at focal site)
    f_vb   = fitness(WT with v at focal site AND 'A' at site 54)
    expct  = f_v * f_bg / f_wt
    e_b    = f_vb - expct
and cross-checked against script 73's stored e_b column to 1e-12
(internal consistency gate; the FROZEN tolerances below are untouched).

GATES (hard; a failed gate prints FAIL and exits 3; tolerances are the
frozen ones and are never widened):
  G-1'a  all 57 (site, variant) deltas rescored on the PROJECT sequence
         match script 73's cached delta_esm: max|diff| <= 1e-6.
  G-1'b  the control rho re-derives: |rho - 0.12218045112781956| <= 1e-9.
  (internal, printed but not frozen) e_b recomputed vs cached: max|diff|
         <= 1e-12; cached table: 57 rows, sites {39,40,41}, 19 variants
         each; input sha256 gates of script 154.

REPORT-ONLY (frozen A3, never gated): the same V54A + WT-arm scoring on
the ASSAYED sequence gives rho_assayed; printed with
rho_assayed - control.

DECISIONS (pre-registered here, before the first run):
  P1  The cached target table is
      data/processed/task_AA1_gb1_eb_analog.csv (script 73's own output
      file, per its docstring lines 113-114); its sha256 is printed for
      the record and pinned semantically by the 1e-12 e_b re-derivation
      check (the planning doc supplies no hash for it).
  P2  Positions are exactly {39, 40, 41} (frozen A3); the WT arm on each
      sequence is 3 passes, each background 3 passes; 12 passes total.
  P3  Scratch only: the one output table is written to
      data/processed/phase3/gb1_scratch/g1p_v54a_table.csv.  Nothing is
      written to the real GB1 out-dir; no roster file is touched; no
      roster background is scored here (V54A is the script-73 control,
      not a roster id).
  P4  Determinism caveat: script 73's cached deltas were produced on this
      same machine/model; G-1' therefore validates the full path
      (sequence choice, arm assembly, join, statistic) against the
      recorded artefact on the same device.  Cross-device determinism is
      not claimed (printed as a limitation).

Usage:
  venv/bin/python3 scripts/161_gb1_gate_g1prime.py

LIMITATIONS (AGENTS section 6, printed by the script itself): same-device
reproduction only; 57 variants at 3 sites of ONE control background --
G-1' validates machinery, it is not evidence about any statistic's value;
the assayed-sequence rho is reported, not gated, per frozen A3.
"""

import importlib.util
import inspect
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CACHED = ROOT / "data" / "processed" / "task_AA1_gb1_eb_analog.csv"
LANDSCAPE = ROOT / "data" / "external" / "GB1_fitness_landscape.txt"
SCRATCH = ROOT / "data" / "processed" / "phase3" / "gb1_scratch"
OUT_CSV = SCRATCH / "g1p_v54a_table.csv"

FOCAL = (39, 40, 41)
SITE54, BG_LETTER = 54, "A"
WT_COLS = ("V", "D", "G", "V")        # script 73 line 137, sites (39,40,41,54)
BG_SITE_IDX = 3                       # script 73 line 138
REC_RHO = 0.12218045112781956         # frozen A3 target
TOL_DELTA = 1e-6                      # frozen A3
TOL_RHO = 1e-9                        # frozen A3
TOL_EB_INTERNAL = 1e-12               # internal consistency, not frozen
AA = list("ACDEFGHIKLMNPQRSTVWY")

GATES = []


def gate(name, verdict, value, note=""):
    GATES.append((name, verdict, value, note))
    print(f"  >>> {name}: {verdict}   value = {value}   {note}")


def rule(t=""):
    print("\n" + "=" * 76)
    if t:
        print(t)
        print("=" * 76)


def main():
    t0 = time.time()
    print("PHASE 3a Task A4d -- HARD gate G-1' (V54A control, 57 variants, "
          "project + assayed sequences)")
    print("Scratch only; no roster file touched; no roster background "
          "scored.")

    # ---- 154's machinery + input sha gates ------------------------------
    spec = importlib.util.spec_from_file_location(
        "gb154", ROOT / "scripts" / "154_gb1_score_backgrounds.py")
    m154 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m154)
    print(f"\nimported scripts/154 score_positions: "
          f"{m154.score_positions.__name__} "
          f"({m154.score_positions.__code__.co_firstlineno=})")
    proj_seq, _ = m154.load_inputs("project")      # G-154-1 / G-154-2
    assayed_seq, _ = m154.load_inputs("assayed")

    # ---- cached target table -------------------------------------------
    rule("G-1' -- CACHED TARGET TABLE (script 73's own output)")
    if not CACHED.exists():
        print(f"GATE FAILED: missing {CACHED}")
        sys.exit(3)
    import hashlib
    sha = hashlib.sha256(CACHED.read_bytes()).hexdigest()
    cache = pd.read_csv(CACHED)
    print(f"  {CACHED.relative_to(ROOT)}  sha256 {sha}  rows {len(cache)} "
          f"(decision P1: pinned semantically by the 1e-12 e_b check)")
    sites = sorted(cache["site"].unique())
    n_var_ok = (len(cache) == 57 and sites == list(FOCAL)
                and all(int((cache["site"] == s).sum()) == 19
                        for s in FOCAL))
    gate("internal cached-table structure", "PASS" if n_var_ok else "FAIL",
         f"rows {len(cache)}, sites {sites}", "57 rows, 19 per site")
    if not n_var_ok:
        sys.exit(3)

    # ---- e_b re-derived from the raw fitness file ----------------------
    rule("G-1' -- FITNESS SIDE RE-DERIVED (script 73 lines 188-231, quoted)")
    print("""    f_v    = fitness(WT with v at focal site)
    f_vb   = fitness(WT with v at focal site AND 'A' at site 54)
    expct  = f_v * f_bg / f_wt
    e_b    = f_vb - expct""")
    land = pd.read_csv(LANDSCAPE, sep="\t").set_index("sequence")["fitness"]
    f_wt = float(land["".join(WT_COLS)])
    bg_cols = list(WT_COLS)
    bg_cols[BG_SITE_IDX] = BG_LETTER
    f_bg = float(land["".join(bg_cols)])
    rows = []
    for focal in FOCAL:
        idx = FOCAL.index(focal)
        for v in AA:
            if v == WT_COLS[idx]:
                continue
            sc = list(WT_COLS)
            sc[idx] = v
            dc = list(WT_COLS)
            dc[idx] = v
            dc[BG_SITE_IDX] = BG_LETTER
            f_v, f_vb = float(land["".join(sc)]), float(land["".join(dc)])
            expct = f_v * f_bg / f_wt
            rows.append({"site": focal, "variant": v, "e_b_re": f_vb - expct})
    eb = pd.DataFrame(rows)
    merged = eb.merge(cache[["site", "variant", "e_b", "delta_esm"]],
                      on=["site", "variant"], how="outer", indicator=True)
    if (merged["_merge"] != "both").any():
        print("GATE FAILED: re-derived (site, variant) set != cached set")
        sys.exit(3)
    d_eb = float(np.abs(merged["e_b_re"] - merged["e_b"]).max())
    gate("internal e_b re-derivation vs cached", "PASS"
         if d_eb <= TOL_EB_INTERNAL else "FAIL", f"max|diff| = {d_eb:.3e}",
         f"tolerance {TOL_EB_INTERNAL}")
    print(f"  f_wt = {f_wt:.6f} (VDGV), f_bg = {f_bg:.6f} (VDAV), "
          f"n = {len(merged)}")

    # ---- model ---------------------------------------------------------
    rule("G-1' -- SCORE V54A + WT ARM AT 39/40/41, BOTH SEQUENCES "
         "(154's own score_positions)")
    if not m154.CKPT.exists():
        print(f"GATE FAILED: checkpoint missing {m154.CKPT} (never "
              f"downloads)")
        sys.exit(3)
    import esm
    from scripts.lib.esm_scoring import get_device
    device = get_device()
    print(f"device {device} | checkpoint {m154.CKPT.name} present")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()

    from scripts.lib.stats import _spearman
    print("\n  statistic (imported, script 73's own; source at run time):")
    print("    " + inspect.getsource(_spearman).strip().replace(
        "\n", "\n    "))

    def arm_deltas(seq_str, seq_name):
        """WT arm + V54A background at FOCAL, delta = S(v|b) - S(v|WT)."""
        bg_l = list(seq_str)
        assert bg_l[SITE54 - 1] == "V", (seq_name, bg_l[SITE54 - 1])
        bg_l[SITE54 - 1] = BG_LETTER
        bg_seq = "".join(bg_l)
        assert bg_seq[SITE54 - 1] == BG_LETTER
        wt_rows, wt_pass = m154.score_positions(model, alphabet, bc,
                                                seq_str, seq_name,
                                                list(FOCAL), device)
        bg_rows, bg_pass = m154.score_positions(model, alphabet, bc,
                                                bg_seq, seq_name,
                                                list(FOCAL), device)
        wt = {(r["position"], r["mut_aa"]): r["score"] for r in wt_rows}
        bg = {(r["position"], r["mut_aa"]): r["score"] for r in bg_rows}
        return ({k: bg[k] - wt[k] for k in bg},
                len(wt_rows) + len(bg_rows),
                len(wt_pass) + len(bg_pass))

    d_proj, rows_p, pass_p = arm_deltas(proj_seq, "project")
    d_assayed, rows_a, pass_a = arm_deltas(assayed_seq, "assayed")
    print(f"\n  project : {pass_p} passes (3 WT + 3 V54A), {rows_p} rows; "
          f"assayed : {pass_a} passes, {rows_a} rows\n"
          f"  totals  : {pass_p + pass_a} passes / {rows_p + rows_a} rows "
          f"(57 delta values per sequence)")

    # ---- G-1'a: 57 deltas vs cached ------------------------------------
    rule("G-1'(a) -- 57 DELTAS vs script 73's CACHED delta_esm (tol 1e-6)")
    merged["delta_proj"] = [d_proj[(int(r.site), r.variant)]
                            for r in merged.itertuples()]
    merged["delta_assayed"] = [d_assayed[(int(r.site), r.variant)]
                               for r in merged.itertuples()]
    merged["d_delta"] = (merged["delta_proj"] - merged["delta_esm"]).abs()
    worst = merged.loc[merged["d_delta"].idxmax()]
    d_max = float(merged["d_delta"].max())
    n_over = int((merged["d_delta"] > TOL_DELTA).sum())
    print(merged[["site", "variant", "delta_proj", "delta_esm", "d_delta",
                  "e_b_re", "delta_assayed"]].to_string(
                      index=False, float_format=lambda x: f"{x:+.9f}"))
    print(f"  variants compared: {len(merged)} / 57 | "
          f"max|delta_proj - delta_cached| = {d_max:.3e} "
          f"(site/variant {int(worst['site'])}/{worst['variant']}) | "
          f"over 1e-6: {n_over}")
    gate("G-1'(a) 57 deltas reproduce cached delta_esm to 1e-6",
         "PASS" if (len(merged) == 57 and n_over == 0) else "FAIL",
         f"max|diff| = {d_max:.3e}, over-tolerance {n_over}/57",
         f"frozen tolerance {TOL_DELTA}")

    # ---- G-1'b: control rho --------------------------------------------
    rule("G-1'(b) -- CONTROL RHO RE-DERIVES (frozen target, tol 1e-9)")
    rho_proj = float(_spearman(merged["delta_proj"].to_numpy(),
                               merged["e_b_re"].to_numpy()))
    d_rho = abs(rho_proj - REC_RHO)
    print(f"  rho (rescored project deltas vs re-derived e_b) = "
          f"{rho_proj!r}")
    print(f"  frozen target                          = {REC_RHO!r}")
    print(f"  |diff| = {d_rho:.3e}   (frozen tolerance {TOL_RHO})")
    # cached-delta rho, to show which side of the identity moves
    rho_cached = float(_spearman(merged["delta_esm"].to_numpy(),
                                 merged["e_b_re"].to_numpy()))
    print(f"  (same statistic on CACHED deltas: {rho_cached!r}; "
          f"|diff to target| = {abs(rho_cached - REC_RHO):.3e})")
    gate("G-1'(b) control rho re-derives to 1e-9",
         "PASS" if d_rho <= TOL_RHO else "FAIL",
         f"got {rho_proj!r}, |diff| = {d_rho:.3e}",
         f"frozen target {REC_RHO!r}")

    # ---- report-only: assayed ------------------------------------------
    rule("REPORT ONLY (frozen A3, NOT a gate) -- V54A ON THE ASSAYED "
         "SEQUENCE")
    rho_assayed = float(_spearman(merged["delta_assayed"].to_numpy(),
                                  merged["e_b_re"].to_numpy()))
    print(f"  rho (project / control) = {rho_proj!r}")
    print(f"  rho (assayed)           = {rho_assayed!r}")
    print(f"  difference (assayed - control) = "
          f"{rho_assayed - rho_proj:+.12f}")
    print("  Frozen A3: reported, not gated. The two sequences differ only "
          "at position 2, which\n  is not a focal site here; the "
          "difference above is context-only.")

    # ---- output table ---------------------------------------------------
    SCRATCH.mkdir(parents=True, exist_ok=True)
    merged[["site", "variant", "delta_proj", "delta_esm", "d_delta",
            "e_b_re", "e_b", "delta_assayed"]].to_csv(OUT_CSV, index=False)
    print(f"\n  table written: {OUT_CSV.relative_to(ROOT)} "
          f"({len(merged)} rows)")

    # ---- summary --------------------------------------------------------
    rule("SUMMARY -- A4d / G-1'")
    n_pass = 0
    for name, verdict, value, note in GATES:
        print(f"  [{verdict}] {name}: {value}  {note}")
        n_pass += verdict == "PASS"
    ok = n_pass == len(GATES)
    print(f"\n  GATES: {n_pass}/{len(GATES)} PASS -> "
          f"G-1' {'PASSES' if ok else 'FAILS'}")
    print("\n  LIMITATIONS (AGENTS 6):")
    print("    * same-device reproduction: script 73's cached deltas were "
          "made on this machine/model;")
    print("      cross-device determinism is not claimed.")
    print("    * 57 variants at 3 sites of ONE control background: G-1' "
          "validates machinery,")
    print("      it is not evidence about any statistic's value.")
    print("    * the assayed-sequence rho is reported, not gated (frozen "
          "A3).")
    print(f"\n  elapsed {time.time() - t0:.1f}s")
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
