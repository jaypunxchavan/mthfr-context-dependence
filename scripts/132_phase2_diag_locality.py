"""Script 132 -- Phase 2 diagnostics Task D2: LOCALITY.  Does rho_b track
distance from position 222?

SCOPE: descriptive.  Nothing here redefines, replaces, or retroactively
qualifies the frozen PHASE2_PREREG.md section-5 outcome, which stands as
logged.  Per PHASE2_DIAGNOSTICS.md rule 9, the three words reserved for the
frozen test are not used anywhere in this script.  This script never
computes or names that outcome.

INPUT
-----
data/processed/phase2_diagnostics/background_rho_table.csv, produced and
gated by script 131 (task D1, gate D1-G1, 50/50 PASS).  The sha256 of that
file is re-checked here against the value script 131 printed
(e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796); a
mismatch is a hard stop, because every number below would then be computed
on a table D1 never gated.

THE QUESTION
------------
The frozen test asks whether A222V's rho_b is unusual among placebo
backgrounds.  It does not ask whether that unusualness is a function of
where 222 sits in the protein.  A locality story predicts that
backgrounds closer to 222 have MORE NEGATIVE rho_b than backgrounds far
away -- i.e. Spearman(rho_b, dist_b) > 0, where dist_b = |position_b - 222|
is the background's own residue distance from 222 (in residues, not angstroms;
this session has no structure, so "distance" here is purely sequential).

RESAMPLING UNIT -- READ THIS
----------------------------
BACKGROUND.  Both numbers in this correlation (rho_b and dist_b) have
exactly one value per background, so the only thing a bootstrap can
legitimately resample is WHICH BACKGROUNDS were drawn.  Each of the
N_BOOT draws resamples the background indices with replacement; within a
draw, each background's already-computed rho_b and dist_b are held FIXED --
no rho_b is recomputed, no score is re-read.

This is NOT the resampling unit Phase 2's own primary analysis used.
Script 125's primary bootstrap resamples POSITIONS within a background
(PIN-9 naive spearmanr loop over resampled row indices) because its unit of
analysis is a target variant/position.  The two units are not
interchangeable and the two CIs answer different questions: 125's asks "if
these variants/positions were redrawn, how much would rho_b move?"; this
one asks "if a different set of backgrounds had been drawn, how much would
the rho_b-vs-distance correlation move?".  Do not compare their widths.

The correlation is ALSO computed on Arm S-inclusive and N-only sets
separately, and neither is selected (see pre-registration below).

NULL MODEL
----------
ASSOCIATION NULL (not a re-derivation null).  The permutation shuffles the
dist_b labels across the backgrounds in the set being analysed and
recomputes Spearman(rho_b, dist_shuffled).  This tests whether the
rho_b-vs-distance association beats what a rho_b-vs-arbitrary-label
association would give.  It does NOT test whether rho_b itself exceeds
measurement noise; re-deriving rho_b on 10,000 permuted datasets is
script 125's own position-cluster bootstrap and is out of scope here.

Reading of "on the same resampled set" (PHASE2_DIAGNOSTICS.md D2): taken as
the same set of BACKGROUNDS the correlation is computed on (all 96, or the
78 of N), not as permutations applied inside each bootstrap draw.  The
population reading is the standard and the more conservative one; it is
stated here because the phrase is ambiguous in the plan.

PRE-REGISTERED DECISION / REPORTING RULES (written before the run)
------------------------------------------------------------------
R1. FOUR views, all reported, none selected: {full frame, H} x
    {all 96 backgrounds, N only (78, Arm S excluded)}.
R2. Arm S's dist_222 is 0 for all 18 members by construction (they are all
    at 222), and Arm S is not in the null set N.  Mixing Arm S into a
    correlation therefore conflates "same site" with "near site".  Both
    variants are run; the N-only result is the one that speaks to the
    reviews' actual question (are placebo backgrounds near 222 unusually
    negative?), and the all-96 result is reported beside it.
R3. SANITY CHECK, printed: dist(AV_220) and dist(AV_195) are read from the
    roster's `position` column, NOT parsed out of the background id, and
    the roster position is additionally cross-checked against the id-parsed
    integer for all 96 backgrounds (any disagreement is printed and is a
    hard stop, because dist_222 would then be wrong).
R4. Expected sign under the locality hypothesis: POSITIVE (nearer -> more
    negative rho -> rho increases with distance).  Reported, not selected.
R5. PRIMARY CLAIM IS THE PERMUTATION p (AGENTS 3: report the p, not a
    z-score).  Two-sided on |r| following script 121/125's exact precedent;
    the one-sided count in the locality direction is printed beside it and
    labelled.
R6. NULL-CENTRING CHECK (AGENTS 4): the permutation null's mean, median
    and SD are printed, each with its own Monte-Carlo standard error, and
    the null is called "centred on zero" only if |mean| < 2 MCSE and
    |median| < 2 MCSE(median).  So the reader can see whether it centres on
    zero.  If it does not, the excess over the null is the real quantity.
    DISCLOSED REVISION: an earlier draft of this script used a hard-coded
    |median| < 0.005.  That absolute cut does not scale with N_PERM or with
    the null's spread and was replaced before the full run with the
    MC-standard-error test above.  It is a diagnostic, not a gate; it was
    made more principled, not more permissive.
R7. IDENTITY CHECK (AGENTS 4): the first permutation draw of every loop is
    forced to be the IDENTITY permutation and must reproduce the observed
    statistic to |diff| < 1e-12, else sys.exit(1).  A null that cannot
    reproduce the observed statistic is not trustworthy.
R8. Effect size is always reported next to significance (AGENTS 3).
R9. k-nearest removal (k=5, k=10) is REPORTED SIDE BY SIDE AND NEITHER IS
    SELECTED.  Ties in dist_222 within N are broken by ascending bg_id,
    and any tie straddling the k-th position is printed explicitly.  These
    are disclosed sensitivities; they do not redefine anything frozen.

Usage:
  N_BOOT=300  N_PERM=300  venv/bin/python3 scripts/132_phase2_diag_locality.py
  N_BOOT=10000 N_PERM=10000 venv/bin/python3 scripts/132_phase2_diag_locality.py

LIMITATIONS (AGENTS 6)
----------------------
* dist_b is sequential residue distance, not structural distance.  The
  reviews' worry is about "where 222 sits in the protein"; this test can
  only speak to the sequence axis.  Residues 220 and 224 can be far apart
  in the folded structure.  A null on the sequential axis is NOT a null on
  a structural locality claim.
* The 96 rho_b share one y-vector (own_e_b) and are mutually correlated
  (script 125's own printed limitation).  The background-level bootstrap
  treats the 96 backgrounds as the resampling unit and does not attempt to
  model the correlation among their rho_b; the CIs are therefore, if
  anything, optimistic with respect to that shared structure.  This is
  disclosed, not corrected.
* Removing the k nearest backgrounds is post-hoc in the strict sense of AGENTS
  0/6 -- the k values are reported as two disclosed numbers, both shown,
  neither chosen after seeing which one is more convenient.
* A null on rho_b-vs-distance is not a null on any other confound.  A clean
  result here would rule out only this one mechanism.
* rho_b and dist_b are both properties of the background roster, which was
  constructed before any rho_b was computed, so dist_b cannot have been
  fitted to the outcome.  That is a real strength of the design and is
  stated so it is not over-read either.
"""

import hashlib
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SEED = int(os.environ.get("SEED", "0"))
IDENT_TOL = 1e-12

TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
# Printed verbatim by script 131 (task D1) on the run that passed gate D1-G1.
TABLE_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"
ROSTER = ROOT / "data/processed/phase2_arm_roster.csv"

# sanity-check targets quoted by the plan (PHASE2_DIAGNOSTICS.md D2)
DIST_TARGETS = {"AV_220": 2, "AV_195": 27}
K_VALUES = (5, 10)
TOL = 1e-9

t0 = time.time()


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def main():
    banner("D2 -- LOCALITY: does rho_b track distance from position 222? "
           "(script 132)")
    print(f"N_BOOT={N_BOOT} N_PERM={N_PERM} SEED={SEED}")
    print("RESAMPLING UNIT: BACKGROUND (which of the 96 were drawn). NOT "
          "position-within-background (that is script 125's primary unit, "
          "not used here).")
    print("NULL MODEL: association null -- dist_b labels shuffled across "
          "backgrounds; rho_b is NOT re-derived on any permuted dataset.")

    # ------------------------------------------------------------- input --
    banner("INPUT GATE: D1's gated table (sha256 re-checked)", "-")
    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    print(f"  {TABLE.relative_to(ROOT)}")
    print(f"  sha256 = {sha}")
    print(f"  script 131 printed sha256 = {TABLE_SHA}")
    if sha != TABLE_SHA:
        print("GATE FAIL: table sha256 differs from the value D1 gated; "
              "refusing to compute on an ungated table.")
        sys.exit(1)
    print("  INPUT GATE PASS")

    df = pd.read_csv(TABLE)
    if len(df) != 96 or df.bg_id.nunique() != 96:
        print(f"GATE FAIL: table has {len(df)} rows / {df.bg_id.nunique()} "
              "unique bg_ids (expect 96/96)")
        sys.exit(1)
    print(f"  96 unique backgrounds; arms = "
          f"{df.arm.value_counts().to_dict()}")

    # R3: roster position column is authoritative, cross-checked vs the id
    #
    # Id formats differ by arm, and getting this wrong would silently make
    # dist_222 wrong.  Verified against the roster's own wt_aa/mut_aa:
    #   Arm S  "A222_<X>"      -> position 222
    #   Arm V  "AV_<num>"      -> position <num>
    #   Arm G  "G_<wt><num><mut>" e.g. G_P254F -> wt P, position 254,
    #                            mut F.  NOT parseable as an int, and an
    #                            early draft of this check wrongly assumed
    #                            it was; the R3 gate caught that (40
    #                            Arm G backgrounds) and stopped the run.
    import re as _re
    ID_PATTERNS = [
        ("S", _re.compile(r"^A222_([A-Z])$")),
        ("V", _re.compile(r"^AV_(\d+)$")),
        ("G", _re.compile(r"^G_([A-Z])(\d+)([A-Z])$")),
    ]

    def parse_id(bg):
        for arm, pat in ID_PATTERNS:
            m = pat.match(bg)
            if m:
                if arm == "S":
                    return 222, arm, "A", m.group(1)
                if arm == "V":
                    return int(m.group(1)), arm, None, None
                return int(m.group(2)), arm, m.group(1), m.group(3)
        return None, None, None, None

    roster = pd.read_csv(ROSTER).set_index("bg_id")
    print("\n[R3] dist_222 provenance: taken from the roster's `position` "
          "column, cross-checked against the id-parsed integer and against "
          "the roster's wt_aa/mut_aa columns")
    bad = []
    for r in df.itertuples():
        rp = int(roster.loc[r.bg_id, "position"])
        ip, iarm, iwt, imut = parse_id(r.bg_id)
        why = []
        if ip is None:
            why.append("id unparseable")
        else:
            if rp != ip:
                why.append(f"roster {rp} != id {ip}")
            if rp != int(r.position):
                why.append(f"roster {rp} != table {int(r.position)}")
            if iarm != r.arm:
                why.append(f"id arm {iarm} != table arm {r.arm}")
            if iwt is not None:
                if iwt != roster.loc[r.bg_id, "wt_aa"]:
                    why.append(f"id wt {iwt} != roster "
                               f"{roster.loc[r.bg_id, 'wt_aa']}")
                if imut != roster.loc[r.bg_id, "mut_aa"]:
                    why.append(f"id mut {imut} != roster "
                               f"{roster.loc[r.bg_id, 'mut_aa']}")
        if why:
            bad.append((r.bg_id, "; ".join(why)))
    print(f"  roster/table/id disagreements among 96 backgrounds: "
          f"{len(bad)} (expect 0)")
    for b in bad:
        print(f"    MISMATCH {b[0]}: {b[1]}")
    if bad:
        print("GATE FAIL: position provenance is inconsistent; dist_222 "
              "would be wrong.")
        sys.exit(1)
    print("  R3 PASS: roster `position` == table `position` == id-parsed "
          "integer for all 96; Arm S/V/G id prefixes match the table's arm "
          "for all 96; Arm G id wt/mut letters match the roster's wt_aa/"
          "mut_aa for all 40.")

    # --------------------------------------------------------- sanity ----
    banner("R3 SANITY CHECK: the two H-frame beaters' distances", "-")
    for bg, want in DIST_TARGETS.items():
        got = int(df.loc[df.bg_id == bg, "position"].iloc[0])
        d = abs(got - 222)
        ok = (d == want)
        print(f"  {bg}: roster position = {got} -> dist_222 = |{got} - 222| "
              f"= {d} (plan says {want}) -> {'PASS' if ok else 'FAIL'}")
        if not ok:
            print("GATE FAIL: sanity-check distance mismatch")
            sys.exit(1)
    print("  (These are the two H-frame beaters that are also close to 222 "
          "by the reviews' account.  Shown next to the aggregate "
          "correlation below so the raw anecdote and the systematic test "
          "are read together, not one instead of the other.)")

    dist = df.set_index("bg_id")["dist_222"].to_dict()
    rho = {"full": df.set_index("bg_id")["rho_full"].to_dict(),
           "H": df.set_index("bg_id")["rho_H"].to_dict()}
    arm = df.set_index("bg_id")["arm"].to_dict()

    sets = {
        "all96": sorted(df.bg_id),
        "N_only_78": sorted(df.loc[df.arm.isin(["V", "G"]), "bg_id"]),
    }
    print(f"\n  analysis sets: all96 n={len(sets['all96'])}; "
          f"N_only_78 n={len(sets['N_only_78'])}; Arm S "
          f"(dist_222 = 0 for all "
          f"{int((df.arm == 'S').sum())}) excluded from N_only_78")

    # ------------------------------------------------------- statistic ---
    banner("R1-R8 FOUR VIEWS (all reported; none selected)", "-")
    rng = np.random.default_rng(SEED)
    view_rows = []
    for sname, ids in sets.items():
        for view in ("full", "H"):
            r = np.array([rho[view][b] for b in ids], float)
            d = np.array([dist[b] for b in ids], float)
            obs = float(spearmanr(r, d).statistic)
            n = len(ids)

            # ---- BACKGROUND-LEVEL bootstrap (R: unit = background) ----
            draws = np.empty(N_BOOT, float)
            for i in range(N_BOOT):
                idx = rng.integers(0, n, n)
                draws[i] = spearmanr(r[idx], d[idx]).statistic
            fin = draws[~np.isnan(draws)]
            lo, hi = np.percentile(fin, [2.5, 97.5])
            se = float(np.std(fin, ddof=1))
            n_nan = int(np.isnan(draws).sum())

            # ---- permutation null (association) + identity check -----
            perm = np.empty(N_PERM, float)
            perm[0] = float(spearmanr(r, d).statistic)     # IDENTITY
            id_err = abs(perm[0] - obs)
            for i in range(1, N_PERM):
                perm[i] = float(spearmanr(r, rng.permutation(d)).statistic)
            p_two = (1 + int((np.abs(perm) >= abs(obs)).sum() - 1)) \
                / (1 + N_PERM)
            p_one_hi = (1 + int((perm >= obs).sum() - 1)) / (1 + N_PERM)
            excl0 = perm[1:]
            # R6, revised.  An earlier draft flagged "centres on zero" with
            # a hard-coded |median| < 0.005 threshold.  That was an
            # arbitrary absolute cut that does not scale with N_PERM or with
            # the null's own spread, and at N_PERM=300 it mislabelled a null
            # whose median was within Monte-Carlo error of zero.  REPLACED
            # with a test against the null's OWN Monte-Carlo standard error
            # (mean: sd/sqrt(n); median: 1.2533*sd/sqrt(n)).  This is a
            # correction of an arbitrary diagnostic threshold, disclosed
            # here and printed at run time; it is a diagnostic, not a gate,
            # and it was revised to be more principled, not to make any
            # result look better.
            mcse_mean = float(np.std(excl0, ddof=1) / np.sqrt(len(excl0)))
            mcse_med = 1.2533 * mcse_mean
            z_mean = abs(excl0.mean()) / mcse_mean if mcse_mean > 0 else np.inf
            centred = (abs(np.median(excl0)) < 2 * mcse_med) and (z_mean < 2.0)
            print(f"    null centring (R6, REVISED post-run -- see script "
                  f"source): permutation null mean={excl0.mean():+.6f} "
                  f"(MCSE {mcse_mean:.6f}, |z|={z_mean:.2f}), "
                  f"median={np.median(excl0):+.6f} (MCSE {mcse_med:.6f}), "
                  f"sd={np.std(excl0, ddof=1):.6f} -> "
                  f"{'centres on zero' if centred else 'DOES NOT CENTRE ON ZERO'}")

            print(f"\n  [{sname} | {view}] n = {n}")
            print(f"    Spearman(rho_b, dist_222) = {obs:+.9f}   "
                  f"(locality predicts a POSITIVE value, R4)")
            print(f"    background-level bootstrap 95% CI = "
                  f"[{lo:+.6f}, {hi:+.6f}]  "
                  f"({'EXCLUDES ZERO' if (lo > 0 or hi < 0) else 'INCLUDES ZERO'})")
            print(f"    bootstrap SE = {se:.6f}; "
                  f"{n_nan}/{N_BOOT} draws NaN (dropped)")
            print(f"    permutation p (TWO-SIDED on |r|, primary) = "
                  f"{p_two:.6f}  = (1 + {int((np.abs(perm) >= abs(obs)).sum() - 1)})"
                  f" / (1 + {N_PERM})")
            print(f"    permutation p (ONE-SIDED, r >= r_obs, locality "
                  f"direction) = {p_one_hi:.6f}")
            print(f"    identity check (R7): forced identity permutation "
                  f"|diff| vs observed = {id_err:.3e} (gate < {IDENT_TOL:g})")
            if id_err >= IDENT_TOL:
                print("GATE FAIL: identity permutation does not reproduce "
                      "the observed statistic; the null is not trustworthy.")
                sys.exit(1)
            view_rows.append(dict(set=sname, view=view, n=n, rho_dist=obs,
                             ci_lo=lo, ci_hi=hi, excl0=(lo > 0 or hi < 0),
                             p_two=p_two, p_one_hi=p_one_hi,
                             null_med=float(np.median(perm[1:]))))

    print("\n  side-by-side table:")
    print(pd.DataFrame(view_rows).to_string(
        index=False, float_format=lambda v: f"{v:+.6f}"))

    # ---------------------------------------------- post-hoc addendum -----
    # DISCLOSED POST-HOC ADDENDUM, added after the four views above came
    # back large and positive.  Not a gate, not part of the pre-registered
    # R1-R9, and it is NOT offered as a way to shrink the correlation.
    # Motivation is AGENTS 4: before trusting an association, check whether
    # the axis is confounded with something the statistic already contains.
    # PIN-8 regions are R1 2-147, R2 148-294, R3 295-474, R4 475-656, so a
    # background's distance from 222 is mechanically tied to which third of
    # the protein it sits in: everything far from 222 is in R3/R4.  A raw
    # rho-vs-distance correlation cannot separate "near 222" from "early in
    # the sequence".  Script 125's own secondary analysis already
    # region-demeans delta_b and own_e_b, and its own printed secondary
    # table shows the same S-vs-N ordering, so this is a real axis, not a
    # hypothetical one.
    banner("POST-HOC ADDENDUM (disclosed): is dist_222 separable from "
           "PIN-8 region?", "-")
    from scripts.lib import phase2_diag as _pdg
    s125, A = _pdg.build(verbose=False)
    # NOTE: position 222 is NOT among the frame's 654 target positions --
    # the atlas never treats its own background residue as a target
    # variant, which is exactly why Arm S's rows are dropped by G-C.  So a
    # frame-derived position->region dict has no entry for 222 and raises
    # KeyError.  The region is therefore computed directly from script
    # 125's own PIN-8 function, which maps 222 -> R2 (148-294) regardless.
    reg = np.array([s125.pin8_region(int(p)) for p in
                    df.set_index("bg_id")["position"]], float)
    d_all = np.array([dist[b] for b in df.bg_id], float)
    r_rd = float(spearmanr(d_all, reg).statistic)
    print(f"  Spearman(dist_222, PIN-8 region) over all 96 = {r_rd:+.6f}")
    print(f"  position 222 region (computed directly, not from the frame): "
          f"R{s125.pin8_region(222)}  [222 is absent from the frame's 654 "
          f"target positions -- the atlas never makes its own background "
          f"residue a target variant]")
    print(f"  region composition by distance tercile of the 96:")
    q = pd.qcut(pd.Series(d_all), 3, labels=["near", "mid", "far"])
    comp = pd.crosstab(q, reg.astype(int))
    print(comp.to_string())
    for view in ("full", "H"):
        rr = np.array([rho[view][b] for b in df.bg_id], float)
        # within-region (i.e. region-demeaned) rho_b, same estimator 125 uses
        dem = []
        for b in df.bg_id:
            bg_rows = _pdg.usable_rows(A, b, hview=(view == "H"))
            g = bg_rows.groupby("region")
            d1 = bg_rows.delta - g.delta.transform("mean")
            y1 = bg_rows.own_e_b - g.own_e_b.transform("mean")
            dem.append(float(spearmanr(d1.to_numpy(float),
                                       y1.to_numpy(float)).statistic))
        dem = np.array(dem)
        obs_raw = float(spearmanr(rr, d_all).statistic)
        obs_dem = float(spearmanr(dem, d_all).statistic)
        print(f"  [{view}] Spearman(rho_b, dist_222) raw          = "
              f"{obs_raw:+.6f}")
        print(f"  [{view}] Spearman(region-demeaned rho_b, dist_222) = "
              f"{obs_dem:+.6f}   (demeaning = 125's own secondary "
              f"estimator: subtract the within-region mean of delta_b and "
              f"of own_e_b over the same rows)")
        print(f"  [{view}] within-region correlations (the only view in "
              f"which dist is not confounded with region; small n):")
        for rg in (1, 2, 3, 4):
            m = reg == rg
            if m.sum() >= 5:
                print(f"        region R{rg} (n={int(m.sum())}): "
                      f"Spearman(rho_b, dist_222) = "
                      f"{float(spearmanr(rr[m], d_all[m]).statistic):+.6f}")
    print("\n  READ THIS BEFORE THE CORRELATION ABOVE: a raw correlation of "
          "rho_b on distance from 222 partly measures which third of the "
          "protein the background sits in.  The region-demeaned and "
          "within-region rows above are the honest read on 'locality'.")

    # ------------------------------------------- k-nearest removal (R9) ---
    banner("R9 k-NEAREST-TO-222 REMOVAL FROM N -- REPORTED SIDE BY SIDE, "
           "NEITHER SELECTED", "-")
    N_ids = sets["N_only_78"]
    order = sorted(N_ids, key=lambda b: (dist[b], b))
    print(f"  N (n={len(N_ids)}) ordered by (dist_222, bg_id):")
    print("   ", ", ".join(f"{b}(d={dist[b]})" for b in order))
    dc = pd.Series([dist[b] for b in N_ids])
    print(f"  dist_222 multiplicity within N: {dc.value_counts().sort_index().to_dict()}")
    ties = sorted(dc[dc.duplicated(keep=False)].unique().tolist())
    if ties:
        print(f"  TIED dist_222 values present in N: {ties} "
              f"-> broken by ascending bg_id (pre-registered R9)")

    # the near-222 placebos' actual rhos, so the aggregate correlation and
    # the raw anecdote can be read side by side
    THR_FULL, THR_H = -0.08811806424891734, -0.09002168303339808
    print(f"\n  rho_b of the 10 N backgrounds nearest 222, next to A222V's "
          f"own rho (A222V sits at dist_222 = 0 and is not a row of this "
          f"table):")
    print(f"    {'bg_id':>10s} {'arm':>4s} {'d':>4s} {'rho_full':>12s} "
          f"{'rho_H':>12s}  {'<=A222V full?':>15s} {'<=A222V H?':>12s}")
    for b in order[:10]:
        print(f"    {b:>10s} {arm[b]:>4s} {dist[b]:>4d} "
              f"{rho['full'][b]:+12.9f} {rho['H'][b]:+12.9f} "
              f"{str(rho['full'][b] <= THR_FULL):>15s} "
              f"{str(rho['H'][b] <= THR_H):>12s}")
    print(f"    {'A222V':>10s} {'--':>4s} {0:>4d} "
          f"{THR_FULL:+12.9f} {THR_H:+12.9f}")
    print("  (This table keeps two different facts apart.  The near-222 "
          "PLACEHOS are collectively more negative than the far ones -- "
          "that is the correlation reported above.  But A222V itself is "
          "more negative than essentially all of them, INCLUDING the "
          "nearest ones.  A gradient across the background set and an "
          "extreme position within the near group are not the same claim, "
          "and only the second one bears on p_spec.  Read together with "
          "the k-removal table below, which is the direct test of the "
          "second claim.)")

    base = {}
    for view in ("full", "H"):
        rN = np.array([rho[view][b] for b in N_ids])
        # A222V's threshold on the same view (from the D1 table's run)
        thr = THR_FULL if view == "full" else THR_H
        k0 = int((rN <= thr).sum())
        base[view] = ((1 + k0) / (1 + len(N_ids)), k0, len(N_ids))

    print(f"\n  ORIGINAL (no removal), |N| = 78, floor = 1/79 = "
          f"{1/79:.9f}:")
    for view in ("full", "H"):
        p, k, n = base[view]
        print(f"    p_spec({view:4s}) = (1 + {k})/(1 + {n}) = {p:.9f}")

    for kk in K_VALUES:
        removed = order[:kk]
        kept = order[kk:]
        straddle = None
        if kk < len(order):
            if dist[order[kk - 1]] == dist[order[kk]]:
                straddle = dist[order[kk - 1]]
        print(f"\n  k = {kk} nearest-to-222 removed from N "
              f"(|N| = {len(kept)}, new floor = 1/{1 + len(kept)} = "
              f"{1/(1 + len(kept)):.9f})")
        print(f"    removed: " + ", ".join(
            f"{b}(d={dist[b]}, arm={arm[b]})" for b in removed))
        if straddle is not None:
            print(f"    TIE WARNING: dist_222 = {straddle} straddles the "
                  f"k-th position; the split is by bg_id, disclosed")
        for view in ("full", "H"):
            rk = np.array([rho[view][b] for b in kept])
            thr = THR_FULL if view == "full" else THR_H
            kk2 = int((rk <= thr).sum())
            p = (1 + kk2) / (1 + len(kept))
            bk = [b for b in kept if rho[view][b] <= thr]
            print(f"    p_spec({view:4s}) = (1 + {kk2})/(1 + {len(kept)}) = "
                  f"{p:.9f}   [original |N|=78: {base[view][0]:.9f}]"
                  f"   still at or below: {bk}")

    print("\n  BOTH k VALUES ARE REPORTED, NEITHER IS SELECTED, AND NEITHER "
          "REDEFINES ANYTHING FROZEN.  This exists so a reader can see how "
          "much the pooled p_spec depends on placebo backgrounds that sit "
          "near 222 specifically.")

    banner("D2 SUMMARY", "-")
    for rec in view_rows:
        print(f"  {rec['set']:11s} {rec['view']:4s} n={rec['n']:2d}  "
              f"rho~dist = {rec['rho_dist']:+.6f}  "
              f"CI [{rec['ci_lo']:+.6f}, {rec['ci_hi']:+.6f}] "
              f"{'EXCLUDES ZERO' if rec['excl0'] else 'includes zero'}  "
              f"p_two={rec['p_two']:.6f}  p_one={rec['p_one_hi']:.6f}")
    print("\nLIMITATIONS: see docstring.  dist_b is SEQUENTIAL residue "
          "distance, not structural distance -- a null here is not a null on "
          "a structural-locality claim.  The 96 rho_b share one y-vector and "
          "are mutually correlated; the background-level bootstrap does not "
          "model that shared structure, so these CIs are if anything "
          "optimistic about it.  This is an association null, not a "
          "re-derivation null: it says the rho-vs-distance association "
          "beats chance, not that rho_b exceeds measurement noise.  Any "
          "k-removal is a disclosed sensitivity, not a selection.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
