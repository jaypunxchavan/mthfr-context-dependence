"""Session 3b, task C2 -- INDEPENDENT recomputation of headline numbers.

Run:   venv/bin/python3 docs/tasks/phase3-overnight/c2_independent_recompute.py

C2 (PHASE3_OVERNIGHT.md, Part C):
  "Independently recompute a sample of headline numbers from the raw
   per-background files (not by calling the staged script): at least 10
   per-background rho_b per module, each covariate Spearman, p_spec_abs
   for both RBD targets.  Any disagreement stops that module."

WHAT THIS SCRIPT IS AND IS NOT
  * It does NOT import or invoke scripts/153, 155 or 157 (the staged
    analysis scripts).  Every statistic below is computed here from the
    raw score files with code written in this file.
  * Imports used: pandas/numpy/scipy (maths), scripts.lib.phase2_diag
    (the project's own cached Phase-2 row construction -- the raw delta_b
    side of module M1, the same input every earlier session used), and,
    for ONE thing only, scripts.lib.phase3_common.pos_cluster_boot to
    regenerate the frozen position-cluster bootstrap draws of M1 (b).
    The bootstrap draw machinery is shared frozen infrastructure (its
    correctness is gated by A2 40/40 and by C1's reference gate
    40/40 draw-by-draw 0.000e+00); what is verified here is that script
    153 wired the right arrays into it.  Everything else -- every rho,
    every p_spec, every percentile CI, every permutation p, every
    outcome word -- is recomputed independently in this file.
  * READ-ONLY with respect to all scored data: this script never writes
    into data/processed/**.  Its only output is stdout.
  * Spearman here = scipy rankdata(average) + np.corrcoef, written
    locally; a cross-check against scipy.stats.spearmanr is printed.
  * No torch, no esm is imported (checked at the end; AGENTS rule 1).

DECISION RULES (pre-registered here, before running):
  * Tolerances: full-precision comparisons (CSV/JSON) -> 1e-12.
    Values printed to 6 decimals in the staged logs -> 5.1e-7
    (half-ulp of the printed precision); 4 decimals -> 5.1e-5;
    integers/counts/words/beater-sets -> exact.
  * "Disagreement" = any comparison outside tolerance.  The first
    disagreement in a module prints BOTH numbers and STOPS that module
    (no further checks of the module run); the module is reported FAIL
    and must not be interpreted later (C3).
  * PARSER PRECISION (bug found by the reduced-N smoke run and fixed
    BEFORE the full run; tolerance unchanged): pandas' default read_csv
    float parser is not round-trip exact -- it perturbed 8,852 of 13,134
    values of m1_own_e_b_ge.csv by up to 1 ULP, which flips near-tie
    ranks and moved Spearman rho by up to 8.1e-6 against the staged
    record (the identity/OWN columns and every row-construction check
    were unaffected, which is why the smoke caught it as a GE-only
    discrepancy).  Every CSV whose floats are compared to staged values
    at 1e-12 is therefore read with float_precision="round_trip", which
    recovers exactly what the staged script wrote (verified: staged rho
    reproduced within 5e-17).  Score/bg files that the staged scripts and
    this one each parse themselves are read with the default parser on
    both sides, so they remain identical to the staged parse.
  * Module M1 quantity (c) is computed BOTH ways -- (i) against the
    ORIGINAL Phase-2 null rhos and (ii) against rho_b^GE nulls, which is
    what the frozen prereg formula
    "p_spec^GE = (1 + #{b in N : rho_b^GE <= rho^GE}) / (1 + |N|)"
    says -- and both are compared with the staged numbers.  This is a
    verification of two candidate constructions against the record, not
    a choice made after seeing a result: the frozen prereg text and the
    staged implementation are both fixed on disk and are compared as-is.
"""

import ast
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

TOL_FULL = 1e-12       # full-precision comparisons
TOL_6DP = 5.1e-7       # printed to 6 decimals
TOL_4DP = 5.1e-5       # printed to 4 decimals
N_BOOT = int(__import__("os").environ.get("N_BOOT", "10000"))
N_PERM = int(__import__("os").environ.get("N_PERM", "10000"))
SEED = 0

S3LOG = ROOT / "data/processed/phase3/driver_stage_S3.log"
A3TXT = ROOT / "docs/tasks/phase3-overnight/PHASE3_A3_FULL_OUTPUT.txt"


# ==========================================================================
# local maths (independent of scripts/lib)
# ==========================================================================
def my_spearman(x, y):
    """Spearman rho, average ranks for ties (the standard definition)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape:
        raise ValueError(f"shape mismatch {x.shape} vs {y.shape}")
    if x.size < 3:
        return float("nan")
    rx = rankdata(x, method="average")
    ry = rankdata(y, method="average")
    if rx.std() == 0.0 or ry.std() == 0.0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def my_p_spec(rho_target, rho_nulls, mode):
    """(p, k, n), p = (1+k)/(1+n).  abs/neg/pos per the frozen project form."""
    nulls = np.asarray(rho_nulls, dtype=float)
    n = int(nulls.size)
    t = float(rho_target)
    if mode == "neg":
        k = int(np.sum(nulls <= t))
    elif mode == "pos":
        k = int(np.sum(nulls >= t))
    elif mode == "abs":
        k = int(np.sum(np.abs(nulls) >= abs(t)))
    else:
        raise ValueError(mode)
    return (1 + k) / (1 + n), k, n


def my_pct_ci(draws):
    a = np.asarray(draws, dtype=float)
    a = a[~np.isnan(a)]
    if len(a) == 0:
        return float("nan"), float("nan"), 0
    lo, hi = np.percentile(a, [2.5, 97.5])
    return float(lo), float(hi), int(len(a))


def my_background_boot(x, y=None, n_boot=N_BOOT, seed=SEED, stat=None):
    """Background-level bootstrap: resample indices, values held fixed."""
    x = np.asarray(x, dtype=float)
    y_arr = None if y is None else np.asarray(y, dtype=float)
    if stat is None:
        stat = ((lambda a, b: float(np.mean(a))) if y_arr is None
                else my_spearman)
    n = len(x)
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        draws[i] = (stat(x[idx], y_arr[idx]) if y_arr is not None
                    else stat(x[idx], None))
    return draws


def my_label_perm_p(x, y, n_perm=N_PERM, seed=SEED, mode="abs"):
    """Association null: permute y across x; p = (1+k)/(1+n)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    obs = my_spearman(x, y)
    rng = np.random.default_rng(seed)
    k = 0
    for _ in range(int(n_perm)):
        rp = my_spearman(x, rng.permutation(y))
        if mode == "abs" and abs(rp) >= abs(obs) and not np.isnan(rp):
            k += 1
    return (1 + k) / (1 + int(n_perm)), k, int(n_perm)


def my_ols_fit_predict(y, x, x_new):
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    X = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = beta[0] + beta[1] * np.asarray(x_new, dtype=float)
    return float(beta[1]), float(beta[0]), pred


def my_loo_ols_residuals(y, x):
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    n = len(y)
    res = np.empty(n, dtype=float)
    for i in range(n):
        m = np.ones(n, dtype=bool)
        m[i] = False
        _, _, pred = my_ols_fit_predict(y[m], x[m], [x[i]])
        res[i] = y[i] - float(pred[0])
    return res


def my_p_boot(draws):
    """Phase-1 p_boot: min(2*min(frac<=0, frac>=0), 1) over finite draws."""
    a = np.asarray(draws, dtype=float)
    a = a[~np.isnan(a)]
    if len(a) == 0:
        return float("nan")
    return float(min(2 * min((a <= 0).mean(), (a >= 0).mean()), 1.0))


# ==========================================================================
# check bookkeeping -- first disagreement stops the module
# ==========================================================================
class ModuleStop(Exception):
    pass


class Module:
    def __init__(self, name):
        self.name = name
        self.n = 0
        self.failed = None

    def num(self, tag, mine, staged, tol):
        self.n += 1
        diff = abs(float(mine) - float(staged))
        ok = diff <= tol
        line = (f"  CHECK {tag}: mine={mine!r} staged={staged!r} "
                f"|diff|={diff:.3e} tol={tol:g} -> {'OK' if ok else 'DISAGREE'}")
        print(line)
        if not ok:
            self.failed = (tag, mine, staged, diff)
            raise ModuleStop()

    def exact(self, tag, mine, staged):
        self.n += 1
        ok = (mine == staged)
        print(f"  CHECK {tag}: mine={mine!r} staged={staged!r} -> "
              f"{'OK' if ok else 'DISAGREE'}")
        if not ok:
            self.failed = (tag, mine, staged, None)
            raise ModuleStop()

    def summary(self):
        if self.failed is None:
            print(f"\nMODULE {self.name} RESULT: PASS "
                  f"({self.n} checks, all within tolerance)\n")
            return True
        print(f"\nMODULE {self.name} RESULT: FAIL -- first disagreement "
              f"at {self.failed[0]}: mine={self.failed[1]!r} "
              f"staged={self.failed[2]!r} diff={self.failed[3]}\n")
        return False


# ==========================================================================
# MODULE G -- GB1 (staged script 155)
# ==========================================================================
def module_gb1():
    m = Module("G (GB1, vs staged 155)")
    print("=" * 76)
    print("MODULE G -- GB1: rho_b from raw doubles/singles + bg scores,")
    print("             4 covariate Spearmans x 4 thresholds, vs 155's")
    print(f"             printed table in {S3LOG.name}")
    print("=" * 76)
    t0 = time.time()

    # ---- staged table, parsed from the driver log (the record) ----------
    txt = S3LOG.read_text()
    heads = [(mo.start(), mo.group(1))
             for mo in re.finditer(r"^THRESHOLD (\S+)", txt, re.M)]
    staged = {}
    for i, (pos, tag) in enumerate(heads):
        end = heads[i + 1][0] if i + 1 < len(heads) else len(txt)
        blk = txt[pos:end]
        d = {}
        mo = re.search(
            r"distribution: n=(\d+)\s+mean=([+-][\d.]+)\s+"
            r"median=([+-][\d.]+)\s+sd\(ddof=0\)=([\d.]+)\s+"
            r"range=\[([+-][\d.]+), ([+-][\d.]+)\]\s+frac<0=([\d.]+)", blk)
        d["dist"] = dict(n=int(mo.group(1)), mean=float(mo.group(2)),
                         median=float(mo.group(3)), sd=float(mo.group(4)),
                         lo=float(mo.group(5)), hi=float(mo.group(6)),
                         frac=float(mo.group(7)))
        mo = re.search(r"centering: background-level CI of mean rho_b = "
                       r"\[([+-][\d.]+), ([+-][\d.]+)\] \(\d+ finite of \d+\)"
                       r" -> (\S+)", blk)
        d["center"] = (float(mo.group(1)), float(mo.group(2)), mo.group(3))
        # NOTE staged prints the perm fraction as (k+1)/(n_perm+1), the
        # numerator/denominator of p itself -- source: 155 line 576.
        mo = re.search(r"completed (\d+) \| excluded by 100-floor: (\d+) \| "
                       r"partner rows dropped for missing delta: (\d+)", blk)
        d["counts"] = (int(mo.group(1)), int(mo.group(2)), int(mo.group(3)))
        d["covs"] = {}
        for mo in re.finditer(
                r"^  covariate \((a|b|c|d)\) [^:]+: rho=([+-][\d.]+)\s+"
                r"CI=\[([+-][\d.]+), ([+-][\d.]+)\]\s+"
                r"perm_p=([\d.]+) \((\d+)/(\d+)\) -> "
                r"(NOT RESOLVED|ASSOCIATED|UNDERPOWERED)", blk, re.M):
            d["covs"][mo.group(1)] = dict(
                rho=float(mo.group(2)), lo=float(mo.group(3)),
                hi=float(mo.group(4)), p=float(mo.group(5)),
                k1=int(mo.group(6)), nperm1=int(mo.group(7)),
                word=mo.group(8))
        staged[tag] = d
    print(f"  parsed staged table: thresholds {list(staged)}; "
          f"covariates each: "
          f"{sorted(set(len(v['covs']) for v in staged.values()))}")
    mo = re.search(r"partner rows for the 400 roster backgrounds: ([\d,]+)",
                   txt)
    staged_partner_rows = int(mo.group(1).replace(",", ""))

    # ---- raw inputs -----------------------------------------------------
    ext = ROOT / "data/external/gb1_olson2014"
    dbl = pd.read_csv(ext / "gb1_olson2014_doubles.csv")
    sgl = pd.read_csv(ext / "gb1_olson2014_singles.csv")
    ros_full = pd.read_csv(ROOT / "data/processed/gb1_background_roster.csv")
    ros400 = pd.read_csv(
        ROOT / "data/processed/phase3/gb1/roster_v2.csv"
    ).sort_values("draw_order").reset_index(drop=True)
    WT_IN, WT_SEL = 1759616, 3041819            # script 129 line 118
    F_WT = WT_SEL / WT_IN
    FLOOR, N_A8 = 100, 200
    POSITIONS = list(range(2, 57))
    print(f"  doubles {len(dbl):,} rows, singles {len(sgl):,}, "
          f"roster {len(ros_full):,}, roster_v2 {len(ros400)}")

    # ---- partner table with e_b (script 73's construction, my code) ----
    a = dbl.rename(columns={"pos1": "pos", "mut1": "mut"}).rename(
        columns={"pos2": "v_pos", "mut2": "v_mut"})
    b = dbl.rename(columns={"pos2": "pos", "mut2": "mut"}).rename(
        columns={"pos1": "v_pos", "mut1": "v_mut"})
    keep = ["pos", "mut", "v_pos", "v_mut", "input_count", "sel_count"]
    lg = pd.concat([a[keep], b[keep]], ignore_index=True)
    same_pos = int((lg["pos"] == lg["v_pos"]).sum())
    lg["W_double"] = (lg["sel_count"] / lg["input_count"]) / F_WT
    s2 = sgl.copy()
    s2["W"] = (s2["sel_count"] / s2["input_count"]) / F_WT
    lg = lg.merge(s2[["pos", "mut", "W"]].rename(
        columns={"pos": "v_pos", "mut": "v_mut", "W": "W_v"}),
        on=["v_pos", "v_mut"], how="left")
    lg = lg.merge(ros_full[["pos", "mut",
                            "background_single_fitness_W"]].rename(
        columns={"background_single_fitness_W": "W_bg"}),
        on=["pos", "mut"], how="left")
    lg["e_b"] = lg["W_double"] - lg["W_v"] * lg["W_bg"]   # f_wt = 1
    miss_v, miss_bg = int(lg["W_v"].isna().sum()), int(lg["W_bg"].isna().sum())
    lg = lg.merge(ros400[["background_id", "pos", "mut", "wt_aa"]],
                  on=["pos", "mut"], how="inner")
    lg["b_pos"] = lg["pos"]
    print(f"  partner table: {len(lg):,} rows for the 400 backgrounds | "
          f"same-position rows {same_pos} (G-2 structural, must be 0) | "
          f"missing W_v {miss_v} / W_bg {miss_bg} (must be 0)")
    if same_pos or miss_v or miss_bg:
        m.failed = ("partner-table structure", (same_pos, miss_v, miss_bg),
                    (0, 0, 0), None)
        print("  DISAGREE: partner-table structure -- module stopped")
        return m.summary()
    m.exact("gb1 partner rows for the 400 backgrounds vs staged 155",
            len(lg), staged_partner_rows)

    # ---- scores ---------------------------------------------------------
    gd = ROOT / "data/processed/phase3/gb1"
    wt = pd.read_csv(gd / "wt_arm.csv")
    wt_map = {(int(r.position), r.mut_aa): float(r.score)
              for r in wt.itertuples()}
    order = {b_: i for i, b_ in enumerate(ros400["background_id"])}
    completed = []
    for p_ in sorted(gd.glob("bg_*.csv")):
        bid = p_.stem[len("bg_"):]
        if bid in order:
            completed.append((bid, pd.read_csv(p_)))
    completed.sort(key=lambda t: order[t[0]])
    print(f"  score files: wt_arm {len(wt)} rows, completed "
          f"{len(completed)}/400 (roster order)")
    deltas = {}
    for bid, df in completed:
        mm = df.merge(pd.DataFrame(
            [(p_, v_, s_) for (p_, v_), s_ in wt_map.items()],
            columns=["position", "mut_aa", "score_wt"]),
            on=["position", "mut_aa"], how="left")
        deltas[bid] = {(int(r.position), r.mut_aa): float(r.delta)
                       for r in mm.assign(
                           delta=mm["score"] - mm["score_wt"]).itertuples()}

    # ---- staged per-background table (primary threshold) ---------------
    staged_bg = pd.read_csv(gd / "gb1_rho_b_full.csv",
                            float_precision="round_trip").set_index(
        "background_id")
    m.exact("gb1 staged rho csv ids vs my completed ids: symmetric diff",
            set(staged_bg.index) ^ {bid for bid, _ in completed}, set())

    # ---- per threshold --------------------------------------------------
    THRESHOLDS = [(25, "t25"), (23, "t23"), (28, "t28"), (None, "unfiltered")]
    for t, tag in THRESHOLDS:
        q = lg if t is None else lg[lg["input_count"] >= t]
        groups = {b_: g for b_, g in q.groupby("background_id", sort=False)}
        per_bg, dropped, below_floor = [], 0, 0
        for bid, _ in completed:
            g = groups.get(bid)
            if g is None or len(g) < FLOOR:
                below_floor += 1
                continue
            dmap = deltas[bid]
            dl, eb, vpos, bpos = [], [], [], []
            for r in g.itertuples():
                d = dmap.get((int(r.v_pos), r.v_mut))
                if d is None:
                    dropped += 1
                    continue
                dl.append(d)
                eb.append(r.e_b)
                vpos.append(int(r.v_pos))
                bpos.append(int(r.b_pos))
            if len(dl) < FLOOR:
                below_floor += 1
                continue
            dl = np.asarray(dl)
            eb = np.asarray(eb)
            vpos = np.asarray(vpos)
            bpos = np.asarray(bpos)
            per_bg.append(dict(
                background_id=bid, rho_b=my_spearman(dl, eb), n=len(dl),
                mean_abs_dpos=float(np.mean(np.abs(bpos - vpos))),
                fit=float(ros400.loc[ros400.background_id == bid,
                                     "background_single_fitness_W"].iloc[0]),
                sd_eb=float(np.std(eb))))
        rho = np.array([p_["rho_b"] for p_ in per_bg])
        st = staged[tag]
        print(f"\n  THRESHOLD {tag}{' (PRIMARY)' if t == 25 else ''}: "
              f"completed {len(per_bg)} | below "
              f"{FLOOR}-floor {below_floor} | dropped for missing delta "
              f"{dropped}")
        m.exact(f"gb1[{tag}] completed / floor-excluded / dropped "
                f"vs staged 155", (len(per_bg), below_floor, dropped),
                st["counts"])
        m.exact(f"gb1[{tag}] n completed vs staged n", len(rho),
                st["dist"]["n"])
        m.num(f"gb1[{tag}] dist mean", np.mean(rho), st["dist"]["mean"],
              TOL_6DP)
        m.num(f"gb1[{tag}] dist median", np.median(rho),
              st["dist"]["median"], TOL_6DP)
        m.num(f"gb1[{tag}] dist sd(ddof=0)", np.std(rho), st["dist"]["sd"],
              TOL_6DP)
        m.num(f"gb1[{tag}] dist lo", rho.min(), st["dist"]["lo"], TOL_6DP)
        m.num(f"gb1[{tag}] dist hi", rho.max(), st["dist"]["hi"], TOL_6DP)
        m.num(f"gb1[{tag}] dist frac<0", float(np.mean(rho < 0)),
              st["dist"]["frac"], TOL_4DP)
        # centering
        cd = my_background_boot(rho, None)
        lo, hi, nf = my_pct_ci(cd)
        word = "CENTERED" if (lo <= 0.0 <= hi) else "OFF-CENTER"
        m.num(f"gb1[{tag}] centering lo", lo, st["center"][0], TOL_6DP)
        m.num(f"gb1[{tag}] centering hi", hi, st["center"][1], TOL_6DP)
        m.exact(f"gb1[{tag}] centering word", word, st["center"][2])
        # covariates
        covs = [
            ("a", np.array([p_["mean_abs_dpos"] for p_ in per_bg])),
            ("b", np.array([p_["fit"] for p_ in per_bg])),
            ("c", np.array([p_["n"] for p_ in per_bg], dtype=float)),
            ("d", np.array([p_["sd_eb"] for p_ in per_bg])),
        ]
        for key, cov in covs:
            rk = my_spearman(rho, cov)
            bd = my_background_boot(rho, cov, stat=my_spearman)
            lo_k, hi_k, _ = my_pct_ci(bd)
            pv, kp, np_ = my_label_perm_p(rho, cov)
            w = ("UNDERPOWERED" if len(rho) < N_A8 else
                 "ASSOCIATED" if (lo_k > 0.0 or hi_k < 0.0)
                 else "NOT RESOLVED")
            s = st["covs"][key]
            m.num(f"gb1[{tag}] cov({key}) spearman", rk, s["rho"], TOL_6DP)
            m.num(f"gb1[{tag}] cov({key}) CI lo", lo_k, s["lo"], TOL_6DP)
            m.num(f"gb1[{tag}] cov({key}) CI hi", hi_k, s["hi"], TOL_6DP)
            m.num(f"gb1[{tag}] cov({key}) perm_p", pv, s["p"], TOL_4DP)
            # staged prints the fraction as (k+1)/(n_perm+1) -- 155 line 576
            m.exact(f"gb1[{tag}] cov({key}) perm numerator k+1",
                    kp + 1, s["k1"])
            m.exact(f"gb1[{tag}] cov({key}) perm denominator n+1",
                    N_PERM + 1, s["nperm1"])
            m.exact(f"gb1[{tag}] cov({key}) word", w, s["word"])
            if tag.startswith("t25"):
                print(f"      cov({key}) rho={rk:+.6f} "
                      f"CI=[{lo_k:+.6f},{hi_k:+.6f}] perm p={pv:.4f} "
                      f"(k={kp}) -> {w}")

        # primary: per-background rho_b vs the staged CSV (all 400)
        if t == 25:
            worst = dict(rho=0.0, n=0, dpos=0.0, fit=0.0, sd=0.0)
            n_bad = 0
            for p_ in per_bg:
                row = staged_bg.loc[p_["background_id"]]
                d_rho = abs(p_["rho_b"] - float(row["rho_b"]))
                d_n = abs(p_["n"] - int(row["n_partners_t25"]))
                d_dp = abs(p_["mean_abs_dpos"]
                           - float(row["mean_abs_dpos"]))
                d_ft = abs(p_["fit"] - float(row["single_fitness_W"]))
                d_sd = abs(p_["sd_eb"] - float(row["sd_eb"]))
                worst["rho"] = max(worst["rho"], d_rho)
                worst["n"] = max(worst["n"], d_n)
                worst["dpos"] = max(worst["dpos"], d_dp)
                worst["fit"] = max(worst["fit"], d_ft)
                worst["sd"] = max(worst["sd"], d_sd)
                if max(d_rho, d_dp, d_ft, d_sd) > TOL_FULL or d_n:
                    n_bad += 1
                    if n_bad <= 3:
                        print(f"      DISAGREE at "
                              f"{p_['background_id']}: mine rho="
                              f"{p_['rho_b']!r} staged={row['rho_b']!r}")
            print(f"  per-background compare (primary): {len(per_bg)} rows "
                  f"x (rho_b, n, mean_abs_dpos, fitness, sd_eb); "
                  f"max|diff| = rho {worst['rho']:.3e}, n {worst['n']}, "
                  f"mean_abs_dpos {worst['dpos']:.3e}, fit "
                  f"{worst['fit']:.3e}, sd_eb {worst['sd']:.3e}; "
                  f"rows outside 1e-12: {n_bad}")
            m.exact("gb1 per-background rho_b (all 400) vs "
                    "gb1_rho_b_full.csv: rows outside 1e-12", n_bad, 0)

    print(f"\n  module G wall {time.time() - t0:.1f}s")
    return m.summary()


# ==========================================================================
# MODULE R -- RBD (staged script 157)
# ==========================================================================
def module_rbd():
    m = Module("R (RBD, vs staged 157)")
    print("=" * 76)
    print("MODULE R -- RBD: rho_b for all 100 backgrounds x 12")
    print("             (target x phenotype x mask) frames from raw bg")
    print("             files + e_T.csv, and p_spec for both targets,")
    print("             vs analysis_results_full.json + rho_b_full.csv")
    print("=" * 76)
    t0 = time.time()
    rd = ROOT / "data/processed/phase3/rbd"
    et = pd.read_csv(rd / "e_T.csv")
    roster = pd.read_csv(rd / "roster_v1.csv")
    wt = pd.read_csv(rd / "wt_arm.csv")
    staged_rho = pd.read_csv(rd / "rho_b_full.csv",
                             float_precision="round_trip")
    staged_json = __import__("json").load(
        open(rd / "analysis_results_full.json"))

    wt_map = {(int(r.site), r.mut_aa): float(r.score)
              for r in wt.itertuples()}
    files = {}
    for row in roster.itertuples():
        p_ = rd / f"bg_{row.background_id}.csv"
        if p_.exists():
            files[row.background_id] = pd.read_csv(p_)
    print(f"  inputs: e_T {len(et):,} rows, roster {len(roster)}, "
          f"wt_arm {len(wt):,} rows, bg files {len(files)}/100")
    m.exact("rbd bg files vs roster ids: symmetric diff",
            set(files) ^ set(roster.background_id), set())
    print(f"  in_null flags: N501Y {int(roster['in_null_N501Y'].sum())}, "
          f"E484K {int(roster['in_null_E484K'].sum())} "
          f"(dtype {roster['in_null_N501Y'].dtype})")

    TARGETS = ["N501Y", "E484K"]
    PHENOS = ["bind", "expr"]
    MASKS = ["ge1", "ge3", "ge5"]
    PRIMARY_PH, PRIMARY_MK = "bind", "ge3"

    # masters + frames per target (R2), my code
    masters, frames = {}, {}
    for T in TARGETS:
        sub = et[et.target == T].reset_index(drop=True)
        masters[T] = (sub.position.to_numpy(int), sub.mutant.to_numpy(str))
        trow = roster.loc[(roster.arm == "TARGET")
                          & (roster.target_assoc == T)]
        assert len(trow) == 1, f"target rows for {T}: {len(trow)}"
        tsite = int(trow.site.iloc[0])
        excl = int((sub.position == tsite).sum())
        print(f"  target {T}: bg_id {trow.background_id.iloc[0]}, site "
              f"{tsite}, master rows {len(sub)} (rows at own site: "
              f"{excl}, must be 0)")
        if excl:
            m.failed = (f"rbd master own-site rows [{T}]", excl, 0, None)
            return m.summary()
        for ph in PHENOS:
            for mk in MASKS:
                use = sub[f"use_{ph}_{mk}"].to_numpy(bool)
                nn = sub[f"e_{ph}"].notna().to_numpy()
                sel = use & nn
                frames[(T, ph, mk)] = dict(
                    idx=np.flatnonzero(sel),
                    e=sub.loc[sel, f"e_{ph}"].to_numpy(float))

    # per-background delta arrays per target
    deltas = {}
    for bid, df in files.items():
        smap = {(int(r.site), r.mut_aa): float(r.score)
                for r in df.itertuples()}
        for T in TARGETS:
            pos, muts = masters[T]
            sc = np.array([smap.get((int(p_), mm), np.nan)
                           for p_, mm in zip(pos, muts)])
            wtv = np.array([wt_map.get((int(p_), mm), np.nan)
                            for p_, mm in zip(pos, muts)])
            deltas[(bid, T)] = sc - wtv

    # rho_b for all 100 bgs x 12 frames vs staged csv
    site_of = {r.background_id: int(r.site) for r in roster.itertuples()}
    worst, n_bad = 0.0, 0
    my_rho = {}
    for T in TARGETS:
        pos = masters[T][0]
        for ph in PHENOS:
            for mk in MASKS:
                fr = frames[(T, ph, mk)]
                idx = fr["idx"]
                for bid in files:
                    keep = pos[idx] != site_of[bid]
                    sub = idx[keep]
                    d = deltas[(bid, T)][sub]
                    e = fr["e"][keep]
                    if np.isnan(d).any():
                        m.failed = (f"rbd join gap [{bid}/{T}/{ph}/{mk}]",
                                    int(np.isnan(d).sum()), 0, None)
                        return m.summary()
                    r = my_spearman(d, e)
                    my_rho[(T, ph, mk, bid)] = (r, len(d))
    merged = 0
    for row in staged_rho.itertuples():
        key = (row.target, row.phenotype, row.mask, row.background_id)
        if key not in my_rho:
            m.failed = (f"rbd staged rho row without my recompute {key}",
                        None, None, None)
            return m.summary()
        r, n = my_rho[key]
        d_ = abs(r - float(row.rho_b))
        worst = max(worst, d_)
        if d_ > TOL_FULL or n != int(row.n_variants):
            n_bad += 1
            if n_bad <= 3:
                print(f"      DISAGREE {key}: mine rho={r!r} staged="
                      f"{row.rho_b!r} |diff|={d_:.3e}; n mine={n} staged="
                      f"{row.n_variants}")
        merged += 1
    print(f"  per-background rho_b: {merged} rows compared "
          f"(staged rho_b_full.csv), max|diff| = {worst:.3e}, "
          f"rows outside 1e-12 or n mismatch: {n_bad}")
    m.exact("rbd per-background rho_b (1200 rows) outside tolerance",
            n_bad, 0)
    m.exact("rbd rho rows compared", merged, 1200)

    # p_spec for both targets, all 12 frames (section 5) vs staged JSON
    def outcome_word(p):
        return ("RBD-REPRODUCES" if p <= 0.05 else
                "RBD-DOES-NOT-REPRODUCE" if p > 0.10 else
                "RBD-INCONCLUSIVE")

    for T in TARGETS:
        trow = roster.loc[(roster.arm == "TARGET")
                          & (roster.target_assoc == T)]
        tid = trow.background_id.iloc[0]
        nulls = list(roster.loc[roster[f"in_null_{T}"].astype(bool),
                                "background_id"])
        for ph in PHENOS:
            for mk in MASKS:
                key = f"{T}/{ph}/{mk}"
                s5 = staged_json["section5"][key]
                rho_t = my_rho[(T, ph, mk, tid)][0]
                null_rho = [my_rho[(T, ph, mk, b)][0] for b in nulls]
                p_abs, k_abs, n_ = my_p_spec(rho_t, null_rho, "abs")
                p_neg, k_neg, _ = my_p_spec(rho_t, null_rho, "neg")
                p_pos, k_pos, _ = my_p_spec(rho_t, null_rho, "pos")
                m.num(f"rbd.s5[{key}] rho_target", rho_t,
                      s5["rho_target"], TOL_FULL)
                m.exact(f"rbd.s5[{key}] n_null", n_, s5["n_null"])
                m.exact(f"rbd.s5[{key}] k_abs", k_abs, s5["k_abs"])
                m.num(f"rbd.s5[{key}] p_abs", p_abs, s5["p_abs"],
                      TOL_FULL)
                m.exact(f"rbd.s5[{key}] k_neg", k_neg, s5["k_neg"])
                m.num(f"rbd.s5[{key}] p_neg", p_neg, s5["p_neg"],
                      TOL_FULL)
                m.exact(f"rbd.s5[{key}] k_pos", k_pos, s5["k_pos"])
                m.num(f"rbd.s5[{key}] p_pos", p_pos, s5["p_pos"],
                      TOL_FULL)
                m.exact(f"rbd.s5[{key}] outcome word",
                        outcome_word(p_abs), s5["outcome_word"])
                if mk == PRIMARY_MK and ph == PRIMARY_PH:
                    m.exact(f"rbd.outcomes_primary[{T}]",
                            outcome_word(p_abs),
                            staged_json["outcomes_primary"][T])
            # end masks
        # end phenos
    print(f"\n  module R wall {time.time() - t0:.1f}s")
    return m.summary()


# ==========================================================================
# MODULE M1 -- MTHFR GE target (staged script 153)
# ==========================================================================
def module_m1():
    m = Module("M1 (MTHFR GE, vs staged 153)")
    print("=" * 76)
    print("MODULE M1 -- per-background rho_b^GE from Phase-2 bg files +")
    print("             m1_own_e_b_ge.csv, then headline rows (a)-(f)")
    print(f"             vs {A3TXT.name} (the full-run record)")
    print("=" * 76)
    t0 = time.time()

    # ---- staged record, parsed -----------------------------------------
    txt = A3TXT.read_text()

    def block(a, b):
        i = txt.index(a)
        j = txt.index(b, i)
        return txt[i:j]

    NUM = r"[+-]?\d+\.\d+"
    staged_a = {}
    for mo in re.finditer(r"^\s+(GE-ISO|GE-SIG|GE-LIN-CF)\s+= ([+-][\d.]+)"
                          r"\s*$",
                          block("(a) Spearman(own_e.b^GE, own_e.b) over "
                                "the 10,757 rows:",
                                "(b) rho^GE ="), re.M):
        staged_a[mo.group(1)] = float(mo.group(2))

    staged_b = {}
    for line in block("(b) rho^GE =", "(c) p_spec^GE").splitlines():
        f = line.split()
        if (f and f[0] in ("original", "GE-ISO", "GE-SIG", "GE-LIN-CF")
                and len(f) >= 5
                and re.fullmatch(r"[+-]?\d+\.\d+", f[1] or "")):
            if f[0] == "original":
                staged_b["original"] = dict(
                    rho=float(f[1]), lo=float(f[2]), hi=float(f[3]),
                    shrink=float(f[-1]), p_boot=None)
            else:
                staged_b[f[0]] = dict(
                    rho=float(f[1]), lo=float(f[2]), hi=float(f[3]),
                    p_boot=float(f[4]), shrink=float(f[5]))
    mo2 = re.search(r"/ (-?[\d.]+) \(recomputed\)", txt)
    staged_orig_full = float(mo2.group(1))

    staged_c, staged_orig_c = {}, {}
    for mo in re.finditer(
            r"^\s+(GE-ISO|GE-SIG|GE-LIN-CF)\s+(full|H)\s*:\s*rho\^GE = "
            r"([+-][\d.]+), p = \(1\+(\d+)\)/\(1\+(\d+)\) = (\d+)/(\d+) = "
            r"([\d.]+); at-or-below nulls = (\[.*\])$", txt, re.M):
        staged_c[(mo.group(1), mo.group(2))] = dict(
            rho=float(mo.group(3)), k=int(mo.group(4)),
            n=int(mo.group(5)), p=float(mo.group(8)),
            beaters=set(ast.literal_eval(mo.group(9))))
    # NOTE: the original row prints the FRACTION (1+k)/(1+|N|) directly
    # ("p = 2/79"), so stored k/n are numerator-1 / denominator-1 -- the
    # GE rows by contrast print "(1+k)/(1+n) = k/n" explicitly.
    mo = re.search(
        r"^\s+original\s+full:\s*p = (\d+)/(\d+) = ([\d.]+) beaters "
        r"(\[.*?\]); H: p = (\d+)/(\d+) = ([\d.]+) beaters (\[.*?\])",
        txt, re.M)
    staged_orig_c = dict(
        k_full=int(mo.group(1)) - 1, n_full=int(mo.group(2)) - 1,
        p_full=float(mo.group(3)),
        beaters_full=set(ast.literal_eval(mo.group(4))),
        k_h=int(mo.group(5)) - 1, n_h=int(mo.group(6)) - 1,
        p_h=float(mo.group(7)),
        beaters_h=set(ast.literal_eval(mo.group(8))))

    staged_d = {}
    for mo in re.finditer(
            r"^\s+(GE-ISO|GE-SIG|GE-LIN-CF|original)\s+(full|H)\s*:\s*"
            r"r_A = ([+-][\d.]+), k = (\d+)/(\d+), p_adj = \(1\+(\d+)\)/"
            r"\(1\+(\d+)\) = ([\d.]+), beaters = (\[.*\])$", txt, re.M):
        staged_d[(mo.group(1), mo.group(2))] = dict(
            r_A=float(mo.group(3)), k=int(mo.group(4)),
            n=int(mo.group(5)), p=float(mo.group(8)),
            beaters=set(ast.literal_eval(mo.group(9))))

    staged_e = {}
    for mo in re.finditer(
            r"^\s+(original|GE-ISO|GE-SIG|GE-LIN-CF)\s*:\s*rank = "
            r"\(1\+(\d+)\)/19 = ([\d.]+)", txt, re.M):
        staged_e[mo.group(1)] = dict(k=int(mo.group(2)),
                                     frac=float(mo.group(3)))

    staged_f = {}
    for mo in re.finditer(
            r"^\s+(GE-ISO|GE-SIG|GE-LIN-CF)\s+= ([+-][\d.]+)\s+CI "
            r"\[([+-][\d.]+), ([+-][\d.]+)\] \((\d+) usable", txt, re.M):
        staged_f[mo.group(1)] = dict(rho=float(mo.group(2)),
                                     lo=float(mo.group(3)),
                                     hi=float(mo.group(4)),
                                     nfin=int(mo.group(5)))
    mo = re.search(r"recomputed original = ([+-][\d.]+); script 140", txt)
    staged_f["original"] = dict(rho=float(mo.group(1)))
    mo = re.search(r"original with background-level bootstrap CI = "
                   r"\[([+-][\d.]+), ([+-][\d.]+)\]", txt)
    staged_f["original"].update(lo=float(mo.group(1)), hi=float(mo.group(2)))
    mo = re.search(r"^\s+original\s+-?[\d.]+\s+([+-][\d.]+)\s+([+-][\d.]+)"
                   r"\s+\d+\.\d+\s+(-?[\d.]+)\s*$", txt, re.M)
    if mo:
        staged_b["original"].update(lo=float(mo.group(1)),
                                    hi=float(mo.group(2)),
                                    shrink=float(mo.group(3)))
    # counts in the words line are the FRACTION (1+k)/(1+|N|) = "1/79",
    # so stored kf/kh are numerator-1 (k), same convention as above.
    words_staged = {}
    for mo in re.finditer(
            r"^\s+(GE-ISO|GE-SIG|GE-LIN-CF)\s*:\s*rho\^GE = .*?"
            r"p_spec\^GE\(full\) = [\d.]+ \((\d+)/(\d+)\), "
            r"p_spec\^GE\(H\) = [\d.]+ \((\d+)/(\d+)\)\s+->\s+(\S+)\s*$",
            txt, re.M):
        words_staged[mo.group(1)] = dict(kf=int(mo.group(2)) - 1,
                                         kh=int(mo.group(4)) - 1,
                                         word=mo.group(6))
    print(f"  parsed staged record: (a) {len(staged_a)}, (b) "
          f"{len(staged_b)}, (c) {len(staged_c)}, (d) {len(staged_d)}, "
          f"(e) {len(staged_e)}, (f) {len(staged_f)}, words "
          f"{len(words_staged)}")

    # ---- raw inputs -----------------------------------------------------
    from scripts.lib import phase2_diag as pdg
    print("  pdg.build() -- cached Phase-2 row construction ...", end="")
    tb = time.time()
    s125, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")
    print(f" {time.time() - tb:.1f}s")
    frame = A.frame
    bgs = list(A.bgs)
    N_ids = list(A.N_IDS)
    S_ids = list(A.S_IDS)
    Hset = set(A.Hset)
    print(f"  frame {len(frame):,} rows / {frame.position.nunique()} "
          f"positions; bgs {len(bgs)}; |N| {len(N_ids)}; |S| {len(S_ids)}; "
          f"H {len(Hset)} positions")

    ge = pd.read_csv(ROOT / "data/processed/phase3/m1_own_e_b_ge.csv",
                     float_precision="round_trip")
    col_of = {"GE-ISO": "own_e_b_ge_iso", "GE-SIG": "own_e_b_ge_sig",
              "GE-LIN-CF": "own_e_b_ge_lin_cf",
              "OWN": "own_e_b_identity"}
    frame_ge = {}
    for name, col in col_of.items():
        s = ge.set_index("hgvs")[col]
        arr = s.reindex(frame["hgvs_pro"].to_numpy()).to_numpy()
        n_nan = int(np.isnan(arr).sum())
        m.exact(f"m1 {name} maps onto all frame rows (NaN count)", n_nan, 0)
        frame_ge[name] = arr
    d_id = float(np.nanmax(np.abs(frame_ge["OWN"]
                                  - frame["own_e_b"].to_numpy(float))))
    m.num("m1 identity own_e_b vs frame recorded own_e_b (max|diff|)",
          d_id, 0.0, TOL_FULL)

    y_own = frame["own_e_b"].to_numpy(float)
    x_av = A.a222v_rows["delta"].to_numpy(float)
    pos_av = A.a222v_rows["position"].to_numpy(int)
    m.num("m1 a222v delta vs frame.delta_esm (max|diff|)",
          float(np.max(np.abs(x_av - frame["delta_esm"].to_numpy(float)))),
          0.0, TOL_FULL)
    hmask_av = np.isin(pos_av, list(Hset))
    rho_full_direct = my_spearman(x_av, y_own)
    rho_h_direct = my_spearman(x_av[hmask_av], y_own[hmask_av])
    m.num("m1 original A222V rho full vs staged repr",
          rho_full_direct, staged_orig_full, TOL_FULL)

    # ---- per-background rho_b / rho_b^GE (all 96 + A222V) --------------
    staged_rhob = pd.read_csv(
        ROOT / "data/processed/phase3/m1_rho_b_ge.csv",
        float_precision="round_trip")
    srh = {(r.bg_id, r.view, r.variant): float(r.rho)
           for r in staged_rhob.itertuples()}
    VARIANTS = ["GE-ISO", "GE-SIG", "GE-LIN-CF"]
    rho_ge = {v: {"full": {}, "H": {}} for v in VARIANTS}
    my_own = {"full": {}, "H": {}}
    worst, n_bad, rows = 0.0, 0, 0
    join_cnt_worst, pos_mis_total, delta_worst = 0, 0, 0.0
    for b_ in bgs:
        f_ = pd.read_csv(ROOT / f"data/processed/phase2/bg_{b_}.csv")
        mm = frame.merge(f_[["position", "mut_aa", "score"]],
                         on=["position", "mut_aa"], how="left")
        pos_idx = np.flatnonzero(mm["score"].notna().to_numpy())
        r = A.bg_rows[b_]
        # cross-checks: my join == 125's cached rows (aggregated below)
        join_cnt_worst = max(join_cnt_worst, abs(len(pos_idx) - len(r)))
        if len(pos_idx) == len(r):
            pos_mis_total += int(np.sum(
                r["position"].to_numpy()
                != frame["position"].to_numpy()[pos_idx]))
        d_re = (mm["score"].to_numpy()[pos_idx]
                - frame["esm2_score"].to_numpy()[pos_idx])
        d_cached = r["delta"].to_numpy(float)
        if d_re.shape == d_cached.shape:
            delta_worst = max(delta_worst, float(
                np.max(np.abs(d_re - d_cached))))
        hm = frame["position"].to_numpy()[pos_idx]
        hmask = np.isin(hm, list(Hset))
        rho_f = my_spearman(d_re, frame["own_e_b"].to_numpy()[pos_idx])
        rho_h = (my_spearman(d_re[hmask],
                             frame["own_e_b"].to_numpy()[pos_idx][hmask])
                 if hmask.any() else float("nan"))
        my_own["full"][b_] = rho_f
        my_own["H"][b_] = rho_h
        recs = {"OWN": {"full": rho_f, "H": rho_h}}
        for v in VARIANTS:
            ge_v = frame_ge[v][pos_idx]
            recs[v] = {"full": my_spearman(d_re, ge_v),
                       "H": (my_spearman(d_re[hmask], ge_v[hmask])
                             if hmask.any() else float("nan"))}
            rho_ge[v]["full"][b_] = recs[v]["full"]
            rho_ge[v]["H"][b_] = recs[v]["H"]
        for view in ("full", "H"):
            for v in ["OWN"] + VARIANTS:
                key = (b_, view, v)
                if key not in srh:
                    m.failed = (f"m1 rhob row missing {key}", None, None,
                                None)
                    return m.summary()
                d_ = abs(recs[v][view] - srh[key])
                worst = max(worst, d_)
                rows += 1
                if d_ > TOL_FULL:
                    n_bad += 1
                    if n_bad <= 3:
                        print(f"      DISAGREE {key}: mine="
                              f"{recs[v][view]!r} staged={srh[key]!r} "
                              f"|diff|={d_:.3e}")
    # A222V rows (pooled anchor)
    pooled = {"OWN": {"full": rho_full_direct, "H": rho_h_direct}}
    for v in VARIANTS:
        pooled[v] = {
            "full": my_spearman(x_av, frame_ge[v]),
            "H": my_spearman(x_av[hmask_av], frame_ge[v][hmask_av])}
        rho_ge[v]["full"]["A222V"] = pooled[v]["full"]
        rho_ge[v]["H"]["A222V"] = pooled[v]["H"]
    for view in ("full", "H"):
        for v in ["OWN"] + VARIANTS:
            key = ("A222V", view, v)
            d_ = abs(pooled[v][view] - srh[key])
            worst = max(worst, d_)
            rows += 1
            if d_ > TOL_FULL:
                n_bad += 1
                print(f"      DISAGREE {key}: mine={pooled[v][view]!r} "
                      f"staged={srh[key]!r} |diff|={d_:.3e}")
    # my row construction vs 125's cached rows (aggregated over 96 bgs)
    print(f"  row-construction cross-checks vs cached bg_rows: "
          f"max |join count diff| = {join_cnt_worst}, "
          f"position mismatches = {pos_mis_total}, "
          f"max|delta diff| = {delta_worst:.3e}")
    m.exact("m1 join count vs cached bg_rows: max |diff| over 96 bgs",
            join_cnt_worst, 0)
    m.exact("m1 position alignment mismatches vs cached (total)",
            pos_mis_total, 0)
    m.num("m1 delta (score - esm2) vs cached delta: max|diff|",
          delta_worst, 0.0, TOL_FULL)
    print(f"  per-background rho: {rows} staged rows compared "
          f"({len(bgs)} bgs + A222V, 2 views x 4 constructions), "
          f"max|diff| = {worst:.3e}, rows outside 1e-12: {n_bad}")
    m.exact("m1 per-background rho rows compared", rows, 97 * 2 * 4)
    m.exact("m1 per-background rho rows outside tolerance", n_bad, 0)

    # ---- (a) ------------------------------------------------------------
    print("\n  (a) Spearman(own_e.b^GE, own_e.b):")
    for v in VARIANTS:
        r_a = my_spearman(frame_ge[v], y_own)
        m.num(f"m1.(a) {v}", r_a, staged_a[v], TOL_6DP)

    # ---- (b) rho^GE + CI + shrinkage ------------------------------------
    print("\n  (b) rho^GE + position-cluster CI (draws via the frozen "
          "shared bootstrap; wiring verified):")
    import scripts.lib.phase3_common as p3c
    cl = pos_av
    x_cl = x_av
    draws_orig = p3c.pos_cluster_boot(x_cl, y_own, cl, N_BOOT, SEED)
    lo_o, hi_o, nf_o = my_pct_ci(draws_orig)
    sb_o = staged_b["original"]
    m.num("m1.(b) original CI lo", lo_o, sb_o["lo"], TOL_6DP)
    m.num("m1.(b) original CI hi", hi_o, sb_o["hi"], TOL_6DP)
    m.num("m1.(b) original shrinkage", 0.0, sb_o["shrink"], TOL_6DP)
    results = {}
    for v in VARIANTS:
        rho_ge_v = my_spearman(x_cl, frame_ge[v])
        draws = p3c.pos_cluster_boot(x_cl, frame_ge[v], cl, N_BOOT, SEED)
        lo, hi, nfin = my_pct_ci(draws)
        pb = my_p_boot(draws)
        shrink = 1.0 - rho_ge_v / rho_full_direct
        results[v] = dict(rho=rho_ge_v, lo=lo, hi=hi, p_boot=pb,
                          shrink=shrink)
        s = staged_b[v]
        m.num(f"m1.(b) {v} rho^GE", rho_ge_v, s["rho"], TOL_6DP)
        m.num(f"m1.(b) {v} CI lo", lo, s["lo"], TOL_6DP)
        m.num(f"m1.(b) {v} CI hi", hi, s["hi"], TOL_6DP)
        m.num(f"m1.(b) {v} p_boot", pb, s["p_boot"], TOL_4DP)
        m.num(f"m1.(b) {v} shrinkage", shrink, s["shrink"], TOL_6DP)
        m.exact(f"m1.(b) {v} finite draws", nfin, N_BOOT)
        print(f"      {v}: rho^GE={rho_ge_v:+.6f} CI=[{lo:+.6f},"
              f"{hi:+.6f}] p_boot={pb:.4f} shrink={shrink:+.6f}")

    # ---- (c) BOTH null constructions ------------------------------------
    print("\n  (c) p_spec^GE -- computed against BOTH candidate null "
          "sets (original rho_b, and rho_b^GE as the frozen prereg "
          "formula states):")
    nulls_full_orig = table.loc[N_ids, "rho_full"].to_numpy(float)
    nulls_h_orig = table.loc[N_ids, "rho_H"].to_numpy(float)
    c_ge_nulls = {}
    p_c_o, p_c_g = {}, {}          # (p, k, beaters) under each null set
    for v in VARIANTS:
        for view in ("full", "H"):
            thr = (results[v]["rho"] if view == "full"
                   else my_spearman(x_cl[hmask_av], frame_ge[v][hmask_av]))
            c_ge_nulls[(v, view)] = np.array(
                [rho_ge[v][view][b_] for b_ in N_ids])
            nulls_orig = (nulls_full_orig if view == "full"
                          else nulls_h_orig)
            p_o, k_o, n_o = my_p_spec(thr, nulls_orig, "neg")
            beat_o = set(np.array(N_ids)[nulls_orig <= thr])
            p_g, k_g, n_g = my_p_spec(thr, c_ge_nulls[(v, view)], "neg")
            beat_g = set(np.array(N_ids)[c_ge_nulls[(v, view)] <= thr])
            p_c_o[(v, view)] = (p_o, k_o, beat_o)
            p_c_g[(v, view)] = (p_g, k_g, beat_g)
            s = staged_c[(v, view)]
            print(f"      {v} {view}: thr={thr:+.6f}")
            print(f"        vs ORIGINAL rho_b nulls:  p=(1+{k_o})/"
                  f"(1+{n_o})={p_o:.6f} "
                  f"beaters={sorted(map(str, beat_o))}")
            print(f"        vs rho_b^GE nulls (prereg formula): p=(1+{k_g})/"
                  f"(1+{n_g})={p_g:.6f} "
                  f"beaters={sorted(map(str, beat_g))}")
            print(f"        staged:                    p=(1+{s['k']})/"
                  f"(1+{s['n']})={s['p']:.6f} "
                  f"beaters={sorted(s['beaters'])}")
            m.num(f"m1.(c) {v}/{view} rho^GE threshold", thr, s["rho"],
                  TOL_6DP)
            m.exact(f"m1.(c) {v}/{view} staged-vs-my ORIGINAL-null k",
                    k_o, s["k"])
            m.exact(f"m1.(c) {v}/{view} staged beaters == my "
                    "ORIGINAL-null beaters", beat_o, s["beaters"])
            m.num(f"m1.(c) {v}/{view} staged-vs-my ORIGINAL-null p",
                  p_o, s["p"], TOL_6DP)
            ge_matches = (k_g == s["k"] and beat_g == s["beaters"]
                          and abs(p_g - s["p"]) <= TOL_6DP)
            verdict = ("ALSO matches the staged numbers" if ge_matches
                       else "DIFFERS from the staged numbers")
            print(f"        -> rho_b^GE-null construction {verdict}")
    # original (frozen G-M4) row
    p_o, k_o, n_o = my_p_spec(rho_full_direct, nulls_full_orig, "neg")
    beat_o = set(np.array(N_ids)[nulls_full_orig <= rho_full_direct])
    m.exact("m1.(c) original full n (frozen G-M4 row)", n_o,
            staged_orig_c["n_full"])
    m.exact("m1.(c) original full k (frozen G-M4 row)",
            k_o, staged_orig_c["k_full"])
    m.exact("m1.(c) original full beaters (frozen)", beat_o,
            staged_orig_c["beaters_full"])
    m.num("m1.(c) original full p (frozen)", p_o,
          staged_orig_c["p_full"], TOL_6DP)
    p_h, k_h, n_h = my_p_spec(rho_h_direct, nulls_h_orig, "neg")
    beat_h = set(np.array(N_ids)[nulls_h_orig <= rho_h_direct])
    m.exact("m1.(c) original H n (frozen)", n_h, staged_orig_c["n_h"])
    m.exact("m1.(c) original H k (frozen)", k_h, staged_orig_c["k_h"])
    m.exact("m1.(c) original H beaters (frozen)", beat_h,
            staged_orig_c["beaters_h"])
    m.num("m1.(c) original H p (frozen)", p_h, staged_orig_c["p_h"],
          TOL_6DP)

    # ---- (d) shift-adjusted --------------------------------------------
    print("\n  (d) p_spec_adj (LOO OLS on mean|delta_b|):")
    mad = {"full": {}, "H": {}}
    for b_ in N_ids:
        r = A.bg_rows[b_]
        mad["full"][b_] = float(np.mean(np.abs(
            r.delta.to_numpy(float))))
        rh = r[r.position.isin(list(Hset))]
        mad["H"][b_] = float(np.mean(np.abs(rh.delta.to_numpy(float))))
    av_full = np.mean(np.abs(x_av))
    av_h = float(np.mean(np.abs(x_av[hmask_av])))
    mad_a = {"full": av_full, "H": av_h}
    for v in VARIANTS + ["original"]:
        for view in ("full", "H"):
            if v == "original":
                y_vec = np.array([float(table.loc[b_, "rho_" + view])
                                  for b_ in N_ids])
                thr = rho_full_direct if view == "full" else rho_h_direct
            else:
                y_vec = np.array([rho_ge[v][view][b_] for b_ in N_ids])
                thr = (results[v]["rho"] if view == "full"
                       else my_spearman(x_cl[hmask_av],
                                        frame_ge[v][hmask_av]))
            x_vec = np.array([mad[view][b_] for b_ in N_ids])
            r_b = my_loo_ols_residuals(y_vec, x_vec)
            _, _, pred = my_ols_fit_predict(y_vec, x_vec,
                                            [mad_a[view]])
            r_A = thr - float(pred[0])
            k = int(np.sum(r_b <= r_A))
            beat = set(np.array(N_ids)[r_b <= r_A])
            p_adj = (1 + k) / (1 + len(N_ids))
            s = staged_d[(v, view)]
            m.num(f"m1.(d) {v}/{view} r_A", r_A, s["r_A"], TOL_6DP)
            m.exact(f"m1.(d) {v}/{view} k", k, s["k"])
            m.num(f"m1.(d) {v}/{view} p_adj", p_adj, s["p"], TOL_6DP)
            m.exact(f"m1.(d) {v}/{view} beaters", beat, s["beaters"])

    # ---- (e) rank fraction ---------------------------------------------
    print("\n  (e) A222V rank within Arm S u {A222V}:")
    k_orig = int(np.sum(table.loc[S_ids, "rho_full"].to_numpy(float)
                        <= rho_full_direct))
    m.exact("m1.(e) original k", k_orig, staged_e["original"]["k"])
    m.num("m1.(e) original frac", (1 + k_orig) / 19.0,
          staged_e["original"]["frac"], TOL_6DP)
    for v in VARIANTS:
        s_nulls = np.array([rho_ge[v]["full"][b_] for b_ in S_ids])
        k = int(np.sum(s_nulls <= results[v]["rho"]))
        frac = (1 + k) / 19.0
        m.exact(f"m1.(e) {v} k", k, staged_e[v]["k"])
        m.num(f"m1.(e) {v} frac", frac, staged_e[v]["frac"], TOL_6DP)

    # ---- (f) gradient ---------------------------------------------------
    print("\n  (f) Spearman(rho_b, d3_b) over the resolved nulls:")
    d3 = pd.read_csv(ROOT /
                     "data/processed/phase2_diagnostics/"
                     "background_3d_distance.csv").set_index("bg_id")
    resN = [b_ for b_ in N_ids if bool(d3.loc[b_, "resolved"])]
    m.exact("m1.(f) resolved-null count", len(resN), 67)
    g = np.array([float(d3.loc[b_, "d3_CA"]) for b_ in resN])
    x_orig = np.array([float(table.loc[b_, "rho_full"]) for b_ in resN])
    grad_orig = my_spearman(x_orig, g)
    m.num("m1.(f) original gradient", grad_orig,
          staged_f["original"]["rho"], TOL_6DP)
    bd = my_background_boot(x_orig, g, stat=my_spearman)
    lo, hi, _ = my_pct_ci(bd)
    m.num("m1.(f) original CI lo", lo, staged_f["original"]["lo"], TOL_6DP)
    m.num("m1.(f) original CI hi", hi, staged_f["original"]["hi"], TOL_6DP)
    for v in VARIANTS:
        x_v = np.array([rho_ge[v]["full"][b_] for b_ in resN])
        gv = my_spearman(x_v, g)
        bd = my_background_boot(x_v, g, stat=my_spearman)
        lo, hi, nf = my_pct_ci(bd)
        s = staged_f[v]
        m.num(f"m1.(f) {v} gradient", gv, s["rho"], TOL_6DP)
        m.num(f"m1.(f) {v} CI lo", lo, s["lo"], TOL_6DP)
        m.num(f"m1.(f) {v} CI hi", hi, s["hi"], TOL_6DP)
        m.exact(f"m1.(f) {v} finite draws", nf, s["nfin"])
        print(f"      {v} = {gv:+.6f} CI [{lo:+.6f}, {hi:+.6f}]")

    # ---- outcome words --------------------------------------------------
    print("\n  outcome words (frozen rule, applied to MY numbers):")

    def ge_word(hi, p_full, p_h):
        if hi < 0:
            return ("GE-SURVIVES" if (p_full <= 0.05 and p_h <= 0.10)
                    else "GE-WEAKENS")
        return "GE-DOES-NOT-SURVIVE"

    for v in VARIANTS:
        s = words_staged[v]
        p_o_f, k_o_f, _ = p_c_o[(v, "full")]
        p_o_h, k_o_h, _ = p_c_o[(v, "H")]
        p_g_f, k_g_f, _ = p_c_g[(v, "full")]
        p_g_h, k_g_h, _ = p_c_g[(v, "H")]
        m.exact(f"m1 outcome row {v}: staged (c) full count k", k_o_f,
                s["kf"])
        m.exact(f"m1 outcome row {v}: staged (c) H count k", k_o_h, s["kh"])
        w = ge_word(results[v]["hi"], p_o_f, p_o_h)
        m.exact(f"m1 outcome word {v} (my CI, my p's)", w, s["word"])
        w_prereg = ge_word(results[v]["hi"], p_g_f, p_g_h)
        note = "" if w_prereg == w else (
            "   <-- NOTE: under the prereg formula's rho_b^GE nulls the "
            "word would be " + w_prereg)
        print(f"      {v}: CI hi {results[v]['hi']:+.6f} | p_full="
              f"{p_o_f:.6f} p_H={p_o_h:.6f} -> {w}{note}")

    print(f"\n  module M1 wall {time.time() - t0:.1f}s")
    return m.summary()


# ==========================================================================
def main():
    print("C2 INDEPENDENT RECOMPUTE (session 3b)")
    print(f"N_BOOT={N_BOOT} N_PERM={N_PERM} SEED={SEED} "
          "(env defaults = the frozen values)")
    print("No staged analysis script (153/155/157) is imported or run.\n")
    t0 = time.time()
    # ModuleStop is raised by Module.num/exact at the FIRST disagreement
    # inside a module (the rule: first disagreement stops that module).
    # Catch it here so the remaining modules still run and the summary
    # still prints; the DISAGREE line with both numbers was printed
    # immediately before the raise.
    results = {}
    for key, fn in (("G", module_gb1), ("R", module_rbd),
                    ("M1", module_m1)):
        try:
            results[key] = fn()
        except ModuleStop:
            results[key] = False
            print(f"  MODULE {key} STOPPED at its first disagreement "
                  f"(both numbers printed above) -- not interpreted "
                  f"in C3\n")
    print("=" * 76)
    print("C2 SUMMARY")
    for k, v in results.items():
        status = ("PASS" if v
                  else "FAIL -- module must not be interpreted in C3")
        print(f"  module {k:3s}: {status}")
    bad = [k for k, v in results.items() if not v]
    print(f"  TOTAL: {len(results) - len(bad)}/3 modules PASS"
          + (f"; FAILING: {bad}" if bad else ""))
    print(f"  wall {time.time() - t0:.1f}s")
    torchish = [mm for mm in ("torch", "esm") if mm in sys.modules]
    print(f"  RULE 1 check: torch/esm imported = "
          f"{torchish if torchish else 'NONE'}")
    print(f"\nC2 {'PASS' if not bad else 'FAIL'}")
    return 0 if not bad else 3


if __name__ == "__main__":
    sys.exit(main())
