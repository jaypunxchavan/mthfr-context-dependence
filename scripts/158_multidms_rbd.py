#!/usr/bin/env python3
"""158 -- multidms global-epistasis fit on the RBD per-variant tables (M2 / A6).

Planning doc: docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md Task A6
(A6c smoke fit, A6d script).  Frozen block:
docs/tasks/phase3-overnight/prereg/RBD_REPLICATION_PREREG_v1.md s6b/s6h --
multidms is fitted on the RBD per-variant data for the Wuhan, Alpha and Eta
conditions in a separate environment under a wall-clock cap; failure to
install, to converge, or to meet the held-out criterion is an ACCEPTABLE
outcome and is reported as such.  e_T^MD is used only if its held-out
predictive Pearson correlation is >= 0.5 for EACH of the Wuhan, Alpha and
Eta conditions (a judgment constant fixed in the frozen block); reported
next to the primary, never replacing it.

THIS DOCSTRING IS THE PRE-REGISTRATION.  It was written before the first
run of this script.  Fixes found after a run may repair code but must never
change decisions D1-D14 or gates G-A6-1..4; every such fix is disclosed in
the A6 log entry.

DECISIONS
D1  Environment: MUST run under venv_multidms (G-A6-1).  venv/ is never
    used or touched by this script.  The imported stack's versions are
    printed at start (freeze snapshot: PHASE3_A6B_FREEZE.txt).
D2  Input pins: bc_binding.csv and bc_expression.csv sha256 must equal the
    entries in data/external/rbd_starr2022/acquisition_log.json (A5a)
    (G-A6-2).  No other external input is read.
D3  Conditions: Wuhan_Hu_1 (reference), N501Y (frozen Alpha), E484K (frozen
    Eta).  B1351/Beta is NOT fitted -- frozen s6b names three conditions.
D4  Phenotypes: bind = bc_binding.csv / log10Ka; expr = bc_expression.csv /
    expression.  Both are fitted because 157's pre-registered R7 runs 6h
    at the primary mask for both phenotypes.
D5  Rows: measurement non-null; rows whose aa_substitutions contain '*'
    (stop variants) dropped; NaN aa_substitutions -> '' (wildtype
    variant); duplicate (condition, aa_substitutions) collapsed by mean
    func_score -- the package's own documentation example aggregates the
    same way.  Every dropped count is printed (row accounting).
D6  Splits (SEED 0): per condition, sample(frac=0.2, random_state=0) is the
    held-out set and is NEVER fitted; the rest is the training pool.
    Smoke subset (A6c): per condition round(0.05 * N_condition_full) rows
    drawn from the training pool with random_state=1 (~5% of the full
    table).  Split sizes printed.
D7  Fitting: multidms.Model(data).fit with ONLY maxiter/tol overridden
    (maxiter 500, tol 1e-6, warn_unconverged=False); every other kwarg is
    the package default and is printed.  Convergence is read from
    model.converged; the convergence trajectory (loss/error) is recorded.
D8  Held-out evaluation: model.add_phenotypes_to_df(held_out,
    unknown_as_nan=True), then Pearson r per condition over the rows the
    model can encode; n_known and n_total printed beside every r.
    Unencodable rows are excluded from r and counted, never imputed.
D9  Criterion (frozen s6h judgment constant): r >= 0.5 for EACH of the
    three conditions, assessed PER PHENOTYPE on that phenotype's full fit.
    The smoke fit's r is a feasibility signal only and is NOT the deciding
    value (stated in its output).
D10 Products (full mode): data/processed/phase3/multidms/
    multidms_report.json always; e_T_MD.csv ONLY for phenotypes whose
    three held-out r's meet D9 -- existence of the file therefore encodes
    the criterion, so 157's 6h prints 'unavailable' when it is absent.
    Columns: target, phenotype, site, mutant, wt, beta, shift, effect.
    'shift' = multidms's condition shift parameter (A6d: the shift
    parameters for N501Y and E484K); 'effect' = the model's predicted
    functional-score effect of that single mutant in that condition minus
    the condition's wildtype prediction (the e_T analogue that 157's 6h
    correlates).  Grid = every (target, site, mutant) row of e_T.csv;
    rows whose site is unseen by the fit or whose mutant equals the
    condition wildtype are skipped and counted.
D11 --smoke NEVER writes anything under
    data/processed/phase3/multidms/ (a smoke product must never be
    mistakable for the real one by 157).
D12 Timing (A6c): per phase -- Data build; warm-up fit (maxiter 2,
    discarded, isolates jit compile); timed fit (maxiter 20) on the smoke
    subset AND on the full training pool -> seconds/iteration each; a
    convergence attempt on the smoke subset (maxiter 500 / tol 1e-6,
    inner wall sub-cap) for n_iter.  Projection = s/iter(full-pool) *
    n_iter, printed against the 120-minute S4 budget with an explicit
    WITHIN/EXCEEDS line, plus a subset-scaled cross-check
    s/iter(subset) * n_iter * N_train/N_subset.  A projection is a
    measurement, not a gate.  n_iter comes from the subset fit; if that
    fit hit maxiter without converging, 500 is used and the projection is
    labelled a lower bound.
D13 Wall-clock cap (--cap-min; default 120 full, 45 smoke) enforced with
    time.monotonic() before every phase.  On breach: stop, write the
    report with cap_reached=true and NO e_T_MD.csv, exit 0 -- frozen s6b
    makes an unfinished fit an acceptable outcome, reported as such.
D14 Exit codes: 3 = gate failure (G-A6-1 env, G-A6-2 pins, G-A6-4 a
    phenotype whose three held-out r's cannot be computed) or an
    unhandled crash; 0 = the run completed its report, whether or not the
    criterion was met.  Per-phenotype line: CRITERION-MET or
    CRITERION-NOT-MET (the frozen block's acceptance words, not an
    outcome word of the block's testing vocabulary).  This script never
    prints GE-*, RBD-*, ASSOCIATED, CENTERED or any outcome word of the
    frozen blocks.

GATES
G-A6-1 env: running under venv_multidms with multidms importable;
    python version and package versions printed.        -> exit 3
G-A6-2 pins: both bc files' sha256 match the A5a acquisition log.
                                                        -> exit 3
G-A6-3 phases complete within the cap, or the cap-breach path is taken
    (prints CAP-REACHED, exits 0 per D13).
G-A6-4 held-out r is finite for all three conditions of a phenotype; a
    phenotype that cannot produce three finite r's -> exit 3 (the frozen
    criterion could not even be evaluated).

USAGE
  smoke (A6c):
    venv_multidms/bin/python scripts/158_multidms_rbd.py --smoke
  full (A6d; night stage S4 or a build-session rehearsal):
    venv_multidms/bin/python scripts/158_multidms_rbd.py [--cap-min 120]
"""
import argparse
import hashlib
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

warnings.filterwarnings("ignore")

EXT = ROOT / "data" / "external" / "rbd_starr2022"
MDDIR = ROOT / "data" / "processed" / "phase3" / "multidms"
ET_CSV = ROOT / "data" / "processed" / "phase3" / "rbd" / "e_T.csv"
ACQ = EXT / "acquisition_log.json"

REF = "Wuhan_Hu_1"
CONDS = ("Wuhan_Hu_1", "N501Y", "E484K")
TARGETS = ("N501Y", "E484K")
PHES = {
    "bind": (EXT / "bc_binding.csv", "log10Ka"),
    "expr": (EXT / "bc_expression.csv", "expression"),
}
SEED, SEED_SUB = 0, 1
HELD_FRAC, SUB_FRAC = 0.2, 0.05
MAXITER, TOL = 500, 1e-6
TIMING_ITERS = 20
CRIT_R = 0.5  # frozen s6h judgment constant

GATES = []


def note(msg=""):
    print(msg, flush=True)


def gate(name, ok, value):
    GATES.append([name, "PASS" if ok else "FAIL", str(value)])
    note(f"  >>> {name}: {'PASS' if ok else 'FAIL'}   value = {value}")
    return ok


def sha256_of(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Cap:
    """D13 wall-clock cap."""

    def __init__(self, minutes):
        self.limit = minutes * 60.0
        self.t0 = time.monotonic()
        self.breached = False

    @property
    def elapsed(self):
        return time.monotonic() - self.t0

    @property
    def remaining(self):
        return self.limit - self.elapsed

    def check(self, phase):
        if self.elapsed > self.limit:
            self.breached = True
            note(f"CAP-REACHED before phase '{phase}': elapsed "
                 f"{self.elapsed:.0f}s > cap {self.limit:.0f}s "
                 f"(acceptable outcome, frozen s6b; no product written)")
            return False
        return True


def check_env():
    ok_prefix = "venv_multidms" in sys.prefix or \
        "venv_multidms" in sys.executable
    note(f"  python {sys.version.split()[0]} at {sys.executable}")
    if not ok_prefix:
        gate("G-A6-1 env: running under venv_multidms", False,
             f"prefix {sys.prefix}")
        sys.exit(3)
    try:
        import multidms
        import jax
        import scipy
        import sklearn
    except Exception as e:  # pragma: no cover
        gate("G-A6-1 env: multidms stack importable", False,
             f"{type(e).__name__}: {e}")
        sys.exit(3)
    versions = (f"multidms {multidms.__version__}, jax {jax.__version__}, "
                f"numpy {np.__version__}, pandas {pd.__version__}, "
                f"scipy {scipy.__version__}, sklearn {sklearn.__version__}")
    gate("G-A6-1 env: running under venv_multidms with the stack importable",
         True, versions)
    note(f"  jax devices: {[d.platform for d in jax.devices()]}"
         "  (no GPU required; CPU fits are expected)")
    return multidms


def check_pins():
    acq = {Path(r["dest"]).name: r["sha256"] for r in json.loads(ACQ.read_text())}
    ok = True
    for ph, (path, _) in PHES.items():
        want = acq.get(path.name)
        got = sha256_of(path)
        match = (want is not None and got == want)
        ok &= match
        note(f"  {path.name} ({ph}): {got} "
             f"{'==' if match else '!='} A5a log {want}")
    if not gate("G-A6-2 pins: bc_binding + bc_expression sha256 == A5a log",
                ok, "2/2 match" if ok else "MISMATCH"):
        sys.exit(3)


def load_pheno(ph):
    """D5 rows, with full row accounting."""
    path, meas = PHES[ph]
    raw = pd.read_csv(path)
    note(f"\n[{ph}] {path.name}: {len(raw):,} raw rows")
    keep_cond = raw["target"].isin(CONDS)
    notna = raw[meas].notna()
    no_stop = ~raw["aa_substitutions"].fillna("").str.contains(r"\*", regex=True)
    note(f"  dropped: outside 3 conditions {int((~keep_cond).sum()):,}; "
         f"null {meas} {int((keep_cond & ~notna).sum()):,}; "
         f"stop variants {int((keep_cond & notna & ~no_stop).sum()):,}")
    df = raw[keep_cond & notna & no_stop].copy()
    df = df.rename(columns={"target": "condition"})
    df["aa_substitutions"] = df["aa_substitutions"].fillna("")
    n_raw_kept = len(df)
    agg = (df.groupby(["condition", "aa_substitutions"], as_index=False)
             .agg(func_score=(meas, "mean")))
    note(f"  after filters {n_raw_kept:,} rows -> aggregated "
         f"{len(agg):,} unique (condition, aa_substitutions) "
         f"(collapsed {n_raw_kept - len(agg):,} duplicates by mean)")
    note(f"  per condition: {agg['condition'].value_counts().sort_index().to_dict()}")
    return agg


def split_df(agg, ph):
    """D6 splits, deterministic, printed."""
    held = (agg.groupby("condition", sort=True)
               .sample(frac=HELD_FRAC, random_state=SEED))
    train = agg.drop(index=held.index)
    note(f"  split [{ph}]: held-out {len(held):,} / train {len(train):,} "
         f"(frac {HELD_FRAC}, seed {SEED}); per-condition held-out "
         f"{held['condition'].value_counts().sort_index().to_dict()}")
    return train, held


def pearson(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or np.std(a[m]) == 0 or np.std(b[m]) == 0:
        return float("nan"), int(m.sum())
    return float(np.corrcoef(a[m], b[m])[0, 1]), int(m.sum())


def heldout_r(model, held, ph):
    """D8: predictions with unknown_as_nan, Pearson per condition."""
    df = held.copy()
    try:
        res = model.add_phenotypes_to_df(df, unknown_as_nan=True)
        if res is not None:
            df = res
    except TypeError:
        res = model.add_phenotypes_to_df(df)
        if res is not None:
            df = res
    pred_col = "predicted_func_score"
    if pred_col not in df.columns:
        cand = [c for c in df.columns if "pred" in c]
        if not cand:
            raise RuntimeError(f"no prediction column; columns={list(df.columns)}")
        pred_col = cand[0]
    out = {}
    for c in CONDS:
        sub = df[df["condition"] == c]
        r, n = pearson(sub[pred_col].values, sub["func_score"].values)
        out[c] = dict(r=r, n_known=n, n_total=len(sub))
    return out


def print_r(label, rd, deciding):
    for c in CONDS:
        v = rd[c]
        note(f"  {label} {c}: r = {v['r']:.4f} on {v['n_known']:,}/"
             f"{v['n_total']:,} held-out rows"
             + ("" if v["n_known"] == v["n_total"]
                else " (unencodable excluded, counted, never imputed)"))
    finite = all(np.isfinite(rd[c]["r"]) for c in CONDS)
    meets = finite and all(rd[c]["r"] >= CRIT_R for c in CONDS)
    verdict = ("CRITERION-MET" if meets else "CRITERION-NOT-MET")
    note(f"  {label}: held-out r >= {CRIT_R} for EACH of Wuhan/Alpha(N501Y)/"
         f"Eta(E484K) -> {verdict}"
         + ("" if deciding else "  [smoke signal only; the deciding value "
                                "comes from the full fit (D9)]"))
    return finite, meets


def timed_fit(data, iters, multidms, tag):
    """Warm-up fit (discard) then timed fit -> seconds/iteration."""
    t_w = time.monotonic()
    m0 = multidms.Model(data)
    m0.fit(maxiter=2, tol=TOL, warn_unconverged=False)
    warm = time.monotonic() - t_w
    t0 = time.monotonic()
    m = multidms.Model(data)
    m.fit(maxiter=iters, tol=TOL, warn_unconverged=False)
    dt = time.monotonic() - t0
    note(f"  [{tag}] warm-up fit(maxiter=2): {warm:.2f}s (jit compile); "
         f"timed fit(maxiter={iters}): {dt:.2f}s -> {dt / iters:.4f} s/iter "
         f"({data.variants_df.shape[0]:,} variants, {len(data.mutations)} mutations)")
    return m, dt / iters, warm


def convergence_fit(data, multidms, cap, tag):
    """D7 full-parameter convergence attempt within the cap."""
    if not cap.check(f"{tag} convergence fit"):
        return None, 0
    t0 = time.monotonic()
    m = multidms.Model(data)
    m.fit(maxiter=MAXITER, tol=TOL, warn_unconverged=False)
    dt = time.monotonic() - t0
    traj = m.convergence_trajectory_df
    note(f"  [{tag}] convergence fit(maxiter={MAXITER}, tol={TOL}): "
         f"{dt:.1f}s, converged={m.converged}, final loss="
         f"{(traj['loss'].iloc[-1] if traj is not None and len(traj) else float('nan')):.6g}, "
         f"trajectory rows={0 if traj is None else len(traj)}")
    return m, dt


def profile_frame(model, data, ph, et):
    """D10: e_T-compatible effect grid for both targets, one phenotype."""
    sm = data.site_map
    idx = {int(s): s for s in sm.index}
    # Numbering alignment: the barcode tables number RBD sites relative to
    # the library (1..201) while e_T.csv uses spike-absolute positions
    # (331..531).  Derive the offset, then VERIFY it against every
    # (target, position, wildtype) row of e_T; a failed verification
    # refuses the profile rather than guessing (AGENTS: never assume a
    # mapping).
    offset = int(min(idx)) - int(et["position"].min())
    probe = et.assign(site_lib=et["position"] + offset)
    in_map = probe["site_lib"].isin(idx)
    mism = 0
    checked = 0
    for r in probe[in_map].itertuples(index=False):
        wt_sm = str(sm.loc[idx[int(r.site_lib)], r.target])
        checked += 1
        if wt_sm != str(r.wildtype):
            mism += 1
    note(f"  profile [{ph}]: numbering offset {offset:+d} "
         f"(site_map {min(idx)}..{max(idx)} vs e_T "
         f"{int(et['position'].min())}-{int(et['position'].max())}); "
         f"wildtype letters verified {checked - mism}/{checked} "
         f"(mismatches {mism})")
    if mism or checked < len(et):
        note(f"  profile [{ph}]: REFUSED -- numbering/wildtype verification "
             f"failed ({mism} mismatches, {len(et) - checked} rows outside "
             f"site_map); no rows written (never impute a mapping)")
        return None, dict(offset=offset, verified_ok=False,
                          mismatches=mism, outside=len(et) - checked, rows=0)
    rows = []
    skipped_site = skipped_wt = unknown = 0
    grid = et[["target", "position", "mutant", "wildtype"]].assign(
        site_lib=et["position"] + offset)
    pred_df = []
    for t in TARGETS:
        sub = grid[grid["target"] == t]
        for r in sub.itertuples(index=False):
            a_site, m_site, mut = int(r.position), int(r.site_lib), str(r.mutant)
            if m_site not in idx:
                skipped_site += 1
                continue
            wt = str(sm.loc[idx[m_site], t])
            if wt == mut:
                skipped_wt += 1
                continue
            pred_df.append(dict(condition=t,
                                aa_substitutions=f"{wt}{m_site}{mut}",
                                target=t, site=a_site, lib_site=m_site,
                                mutant=mut, wt=wt))
    if not pred_df:
        note(f"  profile [{ph}]: NO rows survived filtering "
             f"(unseen site {skipped_site}, mutant==wt {skipped_wt}) "
             f"-- refusing to write an empty product")
        return None, dict(skipped_site=skipped_site, skipped_wt=skipped_wt,
                          unknown=0, rows=0)
    pdf = pd.DataFrame(pred_df)
    res = model.add_phenotypes_to_df(pdf, unknown_as_nan=True)
    if res is not None:
        pdf = res
    pred_col = "predicted_func_score" if "predicted_func_score" in pdf.columns else \
        [c for c in pdf.columns if "pred" in c][0]
    params = model.get_condition_params(pdf["condition"].iloc[0])
    shift_map = dict(zip(data.mutations, np.asarray(params["shift"], dtype=float)))
    beta_map = dict(zip(data.mutations, np.asarray(params["beta"], dtype=float)))
    n_unknown = 0
    for r in pdf.itertuples(index=False):
        key = f"{r.wt}{r.lib_site}{r.mutant}"
        if key not in shift_map:
            n_unknown += 1
            continue
        eff = getattr(r, pred_col)
        rows.append(dict(target=r.target, phenotype=ph, site=r.site,
                         mutant=r.mutant, wt=r.wt,
                         beta=float(beta_map[key]),
                         shift=float(shift_map[key]),
                         effect=float(eff) if pd.notna(eff) else float("nan")))
    out = pd.DataFrame(rows)
    n_nan = int(out["effect"].isna().sum()) if len(out) else 0
    note(f"  profile [{ph}]: grid {len(grid):,} rows -> wrote-ready "
         f"{len(out):,} (skipped unseen site {skipped_site}, "
         f"mutant==wt {skipped_wt}, mutation not in fit {n_unknown}, "
         f"effect NaN {n_nan})")
    return out, dict(skipped_site=skipped_site, skipped_wt=skipped_wt,
                     unknown=n_unknown, rows=len(out), nan_effect=n_nan)


def run_pheno(ph, mode, multidms, cap, et):
    """One phenotype: load -> split -> fit(s) -> held-out r -> profile."""
    note("\n" + "=" * 76)
    note(f"PHENOTYPE {ph} ({PHES[ph][1]}) -- mode '{mode}', "
         f"elapsed {cap.elapsed:.0f}s / cap {cap.limit:.0f}s")
    note("=" * 76)
    agg = load_pheno(ph)
    train, held = split_df(agg, ph)
    if mode == "smoke":
        n_sub = {c: max(50, round(SUB_FRAC * (agg["condition"] == c).sum()))
                 for c in CONDS}
        fit_df = pd.concat(
            [train[train["condition"] == c].sample(n=n_sub[c],
                                                   random_state=SEED_SUB)
             for c in CONDS], ignore_index=True)
        note(f"  smoke subset: {len(fit_df):,} rows (~{100 * len(fit_df) / len(agg):.1f}% "
             f"of full table; per condition {n_sub})")
    else:
        fit_df = train
        note(f"  full fit uses the whole training pool: {len(fit_df):,} rows")

    if not cap.check(f"{ph} Data build"):
        return None
    t0 = time.monotonic()
    data = multidms.Data(fit_df, reference=REF, assert_site_integrity=True,
                         name=f"{ph}_{mode}")
    note(f"  Data built in {time.monotonic() - t0:.1f}s: "
         f"{data.variants_df.shape[0]:,} variants, "
         f"{len(data.mutations)} mutations, conditions {data.conditions}")
    if tuple(data.conditions) != tuple(sorted(CONDS)) and \
            set(data.conditions) != set(CONDS):
        gate("G-A6-4 held-out r computable for all three conditions", False,
             f"Data conditions {data.conditions} != {CONDS}")
        sys.exit(3)

    if mode == "smoke":
        # A6c: timed fits at subset and full-pool scale + convergence attempt
        m_sub, s_iter_sub, _ = timed_fit(data, TIMING_ITERS, multidms,
                                         f"{ph} subset")
        if not cap.check(f"{ph} full-pool timing fit"):
            return None
        t0 = time.monotonic()
        data_full = multidms.Data(train, reference=REF,
                                  assert_site_integrity=True,
                                  name=f"{ph}_{mode}_pool")
        note(f"  full-pool Data built in {time.monotonic() - t0:.1f}s: "
              f"{data_full.variants_df.shape[0]:,} variants, "
              f"{len(data_full.mutations)} mutations")
        m_pool, s_iter_pool, _ = timed_fit(data_full, TIMING_ITERS, multidms,
                                           f"{ph} full-pool")
        del m_pool
        if not cap.check(f"{ph} smoke convergence fit"):
            return None
        sub_cap = Cap(min(cap.remaining, 300) / 60.0)
        m_conv, conv_s = convergence_fit(data, multidms, sub_cap,
                                         f"{ph} smoke-converge")
        if m_conv is None:
            note(f"  [{ph}] smoke convergence fit skipped (sub-cap) -- "
                 f"n_iter falls back to {MAXITER} (projection lower bound)")
            n_iter = MAXITER
            conv_converged = False
        else:
            n_iter = MAXITER if not m_conv.converged else _iters_used(m_conv)
            conv_converged = bool(m_conv.converged)
        rd = heldout_r(m_conv, held, ph) if m_conv is not None else \
            {c: dict(r=float("nan"), n_known=0, n_total=int((held['condition'] == c).sum()))
             for c in CONDS}
        finite, _ = print_r(f"[{ph} smoke]", rd, deciding=False)
        if not finite:
            gate("G-A6-4 held-out r computable for all three conditions", False,
                 "non-finite r in smoke evaluation")
            sys.exit(3)
        gate("G-A6-4 held-out r computable for all three conditions", True,
             ", ".join(f"{c} {rd[c]['r']:.4f}" for c in CONDS))
        # D12 projections against the 120-minute S4 budget
        proj_pool = s_iter_pool * n_iter
        proj_sub = s_iter_sub * n_iter * (len(train) / max(1, len(fit_df)))
        budget = 120 * 60.0
        lb = "" if conv_converged else " (LOWER BOUND: subset fit hit maxiter)"
        note(f"\n  PROJECTION [{ph}]: n_iter = {n_iter} from the subset "
             f"convergence fit{' (maxiter)' if not conv_converged else ''}{lb}")
        note(f"    primary  s/iter(full-pool {s_iter_pool:.4f}) x {n_iter} "
             f"= {proj_pool:.0f}s = {proj_pool / 60:.1f} min -> "
             f"{'WITHIN' if proj_pool <= budget else 'EXCEEDS'} the 120-min S4 budget")
        note(f"    cross-chk s/iter(subset {s_iter_sub:.4f}) x {n_iter} x "
             f"(N_train/N_subset {len(train) / max(1, len(fit_df)):.1f}) = "
             f"{proj_sub:.0f}s = {proj_sub / 60:.1f} min -> "
             f"{'WITHIN' if proj_sub <= budget else 'EXCEEDS'} the 120-min S4 budget")
        note(f"    (both projections assume full-data iterations match the "
             f"subset fit's; a measurement against the S4 budget, not a gate)")
        return dict(ph=ph, split=dict(full=len(agg), train=len(train),
                                      held=len(held), subset=len(fit_df)),
                    s_iter_sub=s_iter_sub, s_iter_pool=s_iter_pool,
                    n_iter=n_iter, converged_subset=conv_converged,
                    proj_pool_s=proj_pool, proj_sub_s=proj_sub,
                    heldout=rd, r_finite=True, r_meets=False,
                    timing=dict(data_build_s=None), profile=None)

    # ---- full mode ----
    m_time, s_iter_pool, _ = timed_fit(data, TIMING_ITERS, multidms,
                                       f"{ph} full-scale timing")
    del m_time
    m, _conv_s = convergence_fit(data, multidms, cap, f"{ph} full")
    if m is None:
        return None
    rd = heldout_r(m, held, ph)
    finite, meets = print_r(f"[{ph} full]", rd, deciding=True)
    if not finite:
        gate("G-A6-4 held-out r computable for all three conditions", False,
             "non-finite r in full evaluation")
        sys.exit(3)
    gate("G-A6-4 held-out r computable for all three conditions", True,
         ", ".join(f"{c} {rd[c]['r']:.4f}" for c in CONDS))
    note(f"  [{ph}] CRITERION-{'' if meets else 'NOT '}MET "
         f"(each condition r >= {CRIT_R}) -> "
         f"{'writes' if meets else 'does NOT write'} {ph} rows to e_T_MD.csv")
    prof, pstats = (None, None)
    if meets and cap.check(f"{ph} e_T^MD profile"):
        prof, pstats = profile_frame(m, data, ph, et)
    return dict(ph=ph, split=dict(full=len(agg), train=len(train),
                                  held=len(held), subset=len(fit_df)),
                s_iter_pool=s_iter_pool, converged=bool(m.converged),
                n_iter=MAXITER if not m.converged else _iters_used(m),
                heldout=rd, r_finite=finite, r_meets=meets,
                s_iter_sub=None, profile=(prof if meets else None),
                profile_stats=pstats)


def _iters_used(model):
    """Iterations actually run, from the trajectory length x resolution."""
    traj = model.convergence_trajectory_df
    if traj is None or not len(traj):
        return MAXITER
    return min(MAXITER, max(TIMING_ITERS, (len(traj) - 1) * 10))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke", action="store_true",
                    help="A6c smoke: 5% subset, timings, projection, "
                         "non-deciding held-out r; writes nothing")
    ap.add_argument("--mode", choices=["smoke", "full"], default=None,
                    help="explicit mode (default: full unless --smoke)")
    ap.add_argument("--cap-min", type=float, default=None,
                    help="hard internal wall-clock cap in minutes "
                         "(default 120 full, 45 smoke)")
    args = ap.parse_args()
    mode = args.mode or ("smoke" if args.smoke else "full")
    cap_min = args.cap_min if args.cap_min is not None else (45.0 if mode == "smoke" else 120.0)
    cap = Cap(cap_min)

    note("=" * 76)
    note(f"A6c/A6d -- MULTIDMS FIT (scripts/158) -- mode '{mode}', "
         f"internal cap {cap_min:g} min")
    note("=" * 76)
    note("  pre-registered: scripts/158 docstring D1-D14 / G-A6-1..4 "
         "(written before first run); frozen s6b/s6h")
    note(f"  env knobs: SEED={SEED} SEED_SUB={SEED_SUB} "
         f"HELD_FRAC={HELD_FRAC} SUB_FRAC={SUB_FRAC} MAXITER={MAXITER} "
         f"TOL={TOL} TIMING_ITERS={TIMING_ITERS} CRIT_R={CRIT_R}")
    note(f"  fit kwargs: maxiter={MAXITER}, tol={TOL}, "
         f"warn_unconverged=False; all others multidms defaults")

    multidms = check_env()
    check_pins()

    if mode == "full" and not ET_CSV.exists():
        gate("G-A6-4 held-out r computable for all three conditions", False,
             f"missing grid {ET_CSV}")
        sys.exit(3)
    et = pd.read_csv(ET_CSV) if ET_CSV.exists() else None

    results = {}
    for ph in ("bind", "expr"):
        if cap.breached or not cap.check(f"phenotype {ph}"):
            results[ph] = dict(ph=ph, skipped_cap=True)
            continue
        r = run_pheno(ph, mode, multidms, cap, et)
        results[ph] = r if r is not None else dict(ph=ph, skipped_cap=True)

    # ---- products ----
    if mode == "smoke":
        note("\n" + "-" * 76)
        note("SMOKE SUMMARY (A6c) -- nothing written (D11)")
        for ph, r in results.items():
            if r is None or r.get("skipped_cap"):
                note(f"  {ph}: CAP-REACHED before completion")
                continue
            note(f"  {ph}: s/iter subset {r['s_iter_sub']:.4f} / pool "
                 f"{r['s_iter_pool']:.4f}; n_iter {r['n_iter']}; projections "
                 f"pool {r['proj_pool_s'] / 60:.1f} min, subset-scaled "
                 f"{r['proj_sub_s'] / 60:.1f} min; held-out r "
                 + ", ".join(f"{c} {r['heldout'][c]['r']:.4f}" for c in CONDS))
        all_done = (not cap.breached) and all(
            r is not None and not r.get("skipped_cap")
            for r in results.values())
        gate("G-A6-3 phases completed within the cap", all_done,
             f"{cap.elapsed:.0f}s of {cap.limit:.0f}s"
             + ("" if all_done else "  (cap reached: acceptable per D13 / "
                                    "frozen s6b; exit 0 per D14)"))
        note(f"  GATES: {sum(1 for g in GATES if g[1] == 'PASS')}/{len(GATES)} "
              f"PASS -> A6 smoke "
              f"{'complete' if all_done else 'completed-with-cap-breach'} "
              f"(exit 0 per D14)")
        note(f"  elapsed {cap.elapsed:.1f}s")
        sys.exit(0)

    note("\n" + "-" * 76)
    note("FULL-MODE SUMMARY (A6d)")
    MDDIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for ph, r in results.items():
        if r is None or r.get("skipped_cap"):
            note(f"  {ph}: not completed (cap reached) -- no product for it")
            continue
        note(f"  {ph}: criterion {'MET' if r['r_meets'] else 'NOT MET'}; "
             + ", ".join(f"{c} {r['heldout'][c]['r']:.4f}" for c in CONDS))
        if r.get("profile") is not None:
            frames.append(r["profile"])
    cap_ok = gate("G-A6-3 phases completed within the cap", not cap.breached,
                  f"{cap.elapsed:.0f}s of {cap.limit:.0f}s"
                  + (" CAP-REACHED" if cap.breached else ""))
    wrote = ""
    if frames:
        out = pd.concat(frames, ignore_index=True).sort_values(
            ["target", "phenotype", "site", "mutant"])
        path = MDDIR / "e_T_MD.csv"
        out.to_csv(path, index=False)
        wrote = f"{path.relative_to(ROOT)} ({out.shape[0]:,} rows x {out.shape[1]} cols)"
        note(f"  wrote {wrote}")
        note("  6h contract: 157 joins this on (site, mutant) per "
             "(target, phenotype) at the primary mask; existence encodes "
             "the frozen criterion (D10)")
    else:
        note("  e_T_MD.csv NOT written (no phenotype met the frozen "
             "criterion, or the cap was reached) -- 157's 6h will print "
             "'unavailable' (acceptable outcome, frozen s6b)")
    rep = dict(
        script="scripts/158_multidms_rbd.py", mode=mode, seed=SEED,
        seed_sub=SEED_SUB, crit_r=CRIT_R, cap_min=cap_min,
        cap_reached=cap.breached, elapsed_s=round(cap.elapsed, 1),
        reference=REF, conditions=list(CONDS),
        fit_kwargs=dict(maxiter=MAXITER, tol=TOL),
        env=dict(python=sys.version.split()[0], multidms=multidms.__version__),
        results={ph: ({k: v for k, v in (r or {}).items()
                       if k not in ("profile",)}
                      if r is not None else None)
                 for ph, r in results.items()},
        product=wrote, gates=GATES,
        notes=[
            "e_T_MD.csv exists only for phenotypes meeting the frozen "
            "held-out criterion (D10); absence is an acceptable outcome "
            "(frozen s6b).",
            "Smoke held-out r is non-deciding (D9).",
            "Projection formulas in D12; a measurement, not a gate.",
        ],
    )
    rpath = MDDIR / "multidms_report.json"
    rpath.write_text(json.dumps(rep, indent=1, default=str) + "\n")
    note(f"  wrote {rpath.relative_to(ROOT)}")
    npass = sum(1 for g in GATES if g[1] == "PASS")
    phrase = ("complete" if npass == len(GATES)
              else "completed with a non-D14 gate failure (see above)")
    note(f"  GATES: {npass}/{len(GATES)} PASS -> A6 full run {phrase}")
    note(f"  elapsed {cap.elapsed:.1f}s")
    # D14: exit 3 only for G-A6-1/2/4, which already exited inline; a cap
    # breach or criterion-not-met is an acceptable outcome (exit 0).
    sys.exit(0)


if __name__ == "__main__":
    main()
