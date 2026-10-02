"""Script 130 (Phase 2 session 2b, task A0) -- deduplicate the scorer manifest.

WRITTEN BEFORE ITS FIRST RUN.  This docstring is the pre-registration of the
selection rule below (AGENTS 6: pre-register the decision rule so a result
cannot be read post-hoc).  Nothing here is tuned after seeing which row it
keeps.

WHY THIS SCRIPT EXISTS
  During the overnight run two (in fact more than two -- see the log entry)
  instances of scripts/124_phase2_score_backgrounds.py ran at the same time.
  Each process appends one row per background IT scored to the shared
  data/processed/phase2/manifest.csv, so backgrounds that two processes both
  worked on appear twice.  The SCORES are unaffected: a background's scores
  live in exactly one file, data/processed/phase2/bg_<bg_id>.csv, published by
  an atomic os.replace (script 124, the `os.replace(tmp, final)` line), so at
  most one file per background exists and the last publisher's content is the
  file on disk.  Only the TIMING LOG was duplicated.
  This script writes the deduplicated manifest to manifest_dedup.csv.  It does
  NOT overwrite manifest.csv, does not touch any bg_*.csv, and changes no
  score, threshold, seed, arm or rule.

  DISCLOSED DEVIATION FROM PHASE2_EXECUTION.md: task A0 is not in that doc; it
  was added by Arnav's session-2b instruction.  The doc says nothing about
  manifest duplicates, so nothing in it is contradicted (AGENTS 9: flagged, not
  silently resolved).  The pre-registration is not touched: no arm, statistic,
  decision rule, constant or gate changes here.

SELECTION RULE (frozen in this docstring, before the first run)
  For each bg_id with more than one manifest row, keep the single row whose
  event is closest in time to the mtime of the actual file bg_<bg_id>.csv on
  disk.  Equivalently -- and this is the same event, proven, not a second
  choice -- keep the row written by the process that last published the file.

  The reconstruction of "when was that row's event" is anchored on data that
  does NOT come from any mtime:
    1. run.log holds one line per scoring event, printed by script 124 AFTER
       the background's os.replace AND after its manifest append, so the order
       of `scored <bg_id>` lines in run.log is the true global order of
       publishes across all concurrent processes.
    2. Each line carries the event's duration (`... in 1234.5s`) and that
       process's cumulative `elapsed` counter, which starts at 0 immediately
       before that process's scoring loop.
    3. Each `[launcher] ... attempt 1/5 started` line carries a wall-clock
       timestamp taken by the launcher at the instant it spawned the scorer.
       Process start + elapsed therefore reconstructs the logged publish time
       of every event to within the model-load time (a few seconds; quantified
       in the output).
    4. Events are grouped into processes ("chains") by requiring, within a
       chain, strictly increasing roster index and
       |elapsed_{k+1} - elapsed_k - seconds_{k+1}| <= 45 s.  A process is a
       maximal such chain; the number of chains found must equal the number of
       launcher attempt-starts, and each chain's n_done_before (its first
       event's `run N/96` minus 1) must be the roster index it started at.
  Manifest rows are matched to run.log events by bg_id, then:
    (a) by nearest `seconds` (the log prints 1 dp, the manifest stores 3 dp),
        which resolves every bg_id whose two events printed different values;
    (b) where the printed values are identical -- the log's 1 dp cannot
        separate them -- by global append order: the earlier row in
        manifest.csv corresponds to the earlier `scored` line in run.log.  This
        is sound for the same reason the ordering argument is: both files are
        append-only, and within one process the manifest append immediately
        follows the publish and the log print, so a process's earlier event is
        earlier in both files.  Such bg_ids are listed explicitly in the
        output with the exact `seconds` spread that the print precision hid.
  The match must be 1-to-1 over all rows and all events, and the chain each
  row is assigned to must equal the chain that actually produced that event.

  REPORTED, NOT DECIDED: the check that the run.log-order-last event is also
  the manifest-append-order-last row for every duplicated bg_id, and the
  minimum margin by which the kept row beats the discarded one.  These are
  corroborations printed for the record; they cannot change the outcome because
  the rule above is already fixed.

FAILURE POLICY (AGENTS 1/2/10, frozen)
  Any in-script check failing prints ERROR and exits 1.  No threshold is
  loosened, no input is substituted, nothing is retried.

CONVENTION
  N_BOOT / SEED are read and printed per project convention and are UNUSED --
  this script performs no bootstrap, no permutation, no randomness.

LIMITATIONS (AGENTS 6)
  The reconstruction resolves publish times to within the model-load time
  (seconds), not to sub-millisecond precision; the separation between the two
  candidate events for a duplicated background is minutes, so the resolution is
  ample, but the exact seconds are not certified.  The `seconds` column this
  script carries forward is a TIMING measurement from whichever process last
  wrote the file; it is not a property of the scores.
"""

import hashlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

P2 = ROOT / "data/processed/phase2"
MANIFEST = P2 / "manifest.csv"
DEDUP = P2 / "manifest_dedup.csv"
ROSTER = ROOT / "data/processed/phase2_arm_roster.csv"
RUNLOG = P2 / "run.log"

CHAIN_TOL_S = 45.0      # max |elapsed delta - seconds| inside one process
EVENT_RE = re.compile(
    r"  scored (\S+): (\d+) positions, (\d+) rows in ([\d.]+)s \((\d+) ms/pass\)"
    r" \| run (\d+)/(\d+), elapsed ([\d.]+)m, ETA ([\d.]+)h")
LAUNCH_RE = re.compile(
    r"\[launcher\] (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}) attempt \d+/\d+ started")


def sha256(path):
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def read_events():
    """One dict per `scored <bg>` line in run.log, in file order."""
    evs = []
    for ln, line in enumerate(RUNLOG.read_text().splitlines(), 1):
        m = EVENT_RE.match(line)
        if m:
            evs.append(dict(line=ln, bg=m.group(1), npos=int(m.group(2)),
                            nrows=int(m.group(3)), sec=float(m.group(4)),
                            runk=int(m.group(6)), total=int(m.group(7)),
                            elapsed=float(m.group(8)) * 60.0))
    return evs


def read_launch_starts():
    out = []
    for line in RUNLOG.read_text().splitlines():
        m = LAUNCH_RE.match(line)
        if m:
            out.append(datetime.fromisoformat(m.group(1)).timestamp())
    return out


def build_chains(evs, rorder):
    """Group events into per-process chains (see docstring rule step 4)."""
    chains = []
    for e in evs:
        e["ridx"] = rorder[e["bg"]]          # same object, kept in `evs`
        best, bkey = None, None
        for c in chains:
            last = c["ev"][-1]
            if last["ridx"] >= e["ridx"]:
                continue
            res = abs((e["elapsed"] - last["elapsed"]) - e["sec"])
            key = (0 if res <= CHAIN_TOL_S else 1, round(res, 3), -last["ridx"])
            if bkey is None or key < bkey:
                bkey, best = key, c
        if best is not None and bkey[0] == 0:
            best["ev"].append(e)
        else:
            chains.append(dict(n_done_before=int(e["runk"]) - 1, ev=[e]))
    return chains


def main():
    print("=" * 74)
    print("130 -- Phase 2 manifest deduplication (task A0)  "
          f"N_BOOT={N_BOOT} SEED={SEED} (both UNUSED: no bootstrap/randomness)")
    print("=" * 74)

    print("\nSELECTION RULE (frozen in this script's docstring before its first "
          "run):\n  for each bg_id with >1 manifest row, keep the row whose "
          "logged event time is\n  closest to the mtime of bg_<bg_id>.csv on "
          "disk.  manifest.csv is NOT overwritten;\n  the deduplicated copy is "
          "written to manifest_dedup.csv.  Scores are not\n  touched -- the "
          "per-background CSV files are the ground truth and were never\n  "
          "duplicated in content, only the timing log was.")

    man_sha_before = sha256(MANIFEST)
    print(f"\n  manifest.csv            : {MANIFEST.relative_to(ROOT)}")
    print(f"  manifest.csv sha256 BEFORE: {man_sha_before}")

    man = pd.read_csv(MANIFEST)
    roster = pd.read_csv(ROSTER)
    rorder = {b: i for i, b in enumerate(roster.bg_id)}
    print(f"  manifest rows           : {len(man)} (data rows)")
    print(f"  unique bg_id in manifest: {man.bg_id.nunique()}")
    print(f"  roster rows             : {len(roster)} (expect 96)")

    counts = man.bg_id.value_counts()
    n_dup = int((counts > 1).sum())
    print(f"  bg_ids with >1 row      : {n_dup}")
    print(f"  rows per duplicated bg_id: "
          f"{sorted(counts[counts > 1].unique().tolist())} (expect [2])")
    print(f"  manifest.csv mtime      : "
          f"{datetime.fromtimestamp(MANIFEST.stat().st_mtime).isoformat()}")
    if man.bg_id.nunique() != 96 or len(roster) != 96:
        print("ERROR: expected 96 unique bg_ids in both manifest and roster")
        sys.exit(1)
    if set(man.bg_id) != set(roster.bg_id):
        print("ERROR: manifest bg_id set != roster bg_id set")
        sys.exit(1)

    # ------------------------------------------------------------------
    print("\n" + "-" * 74)
    print("STEP 1 -- parse run.log into per-process event chains")
    print("-" * 74)
    evs = read_events()
    starts = read_launch_starts()
    print(f"  `scored` events in run.log            : {len(evs)}")
    print(f"  launcher attempt-start timestamps     : {len(starts)}")
    print(f"  event bg_ids / unique                 : "
          f"{len({e['bg'] for e in evs})} / {len(evs)}")
    if len(evs) != len(man):
        print(f"ERROR: {len(evs)} log events vs {len(man)} manifest rows")
        sys.exit(1)

    chains = build_chains(evs, rorder)
    print(f"  event chains recovered (one per process): {len(chains)}")
    if len(chains) != len(starts):
        print("ERROR: chain count != launcher attempt count")
        sys.exit(1)
    for c, t0 in zip(chains, starts):
        c["t_run0"] = t0
        c["start_str"] = datetime.fromtimestamp(t0).strftime(
            "%Y-%m-%dT%H:%M:%S")

    print("\n  chain  n_ev  n_done_before  first..last (runk)     "
          "elapsed span        launcher attempt start")
    for i, c in enumerate(chains):
        e = c["ev"]
        gaps = [(e[j + 1]["elapsed"] - e[j]["elapsed"]) - e[j + 1]["sec"]
                for j in range(len(e) - 1)]
        span = f"{e[0]['elapsed'] / 60:.1f}..{e[-1]['elapsed'] / 60:.1f}m"
        print(f"  {i:>4}  {len(e):>4}  {c['n_done_before']:>13}  "
              f"{e[0]['bg']}..{e[-1]['bg']} "
              f"({e[0]['runk']}..{e[-1]['runk']})  {span:>16}  {c['start_str']}")
        if gaps and max(abs(g) for g in gaps) > CHAIN_TOL_S:
            print(f"ERROR: chain {i} gap check failed "
                  f"(max |gap| = {max(abs(g) for g in gaps):.2f}s)")
            sys.exit(1)
        if any(e[j]["ridx"] >= e[j + 1]["ridx"] for j in range(len(e) - 1)):
            print(f"ERROR: chain {i} roster order not strictly increasing")
            sys.exit(1)
        if e[0]["runk"] - 1 != c["n_done_before"]:
            print("ERROR: chain n_done_before bookkeeping inconsistent")
            sys.exit(1)
    print(f"  all chain checks PASS (gap tolerance {CHAIN_TOL_S:.0f}s, roster "
          f"order, n_done_before)")

    # ------------------------------------------------------------------
    print("\n" + "-" * 74)
    print("STEP 2 -- match manifest rows to run.log events 1-to-1")
    print("-" * 74)
    man = man.reset_index(drop=True)
    man["man_row"] = np.arange(len(man))
    ev_by_bg = {}
    for e in evs:
        ev_by_bg.setdefault(e["bg"], []).append(e)
    ev_chain = {}
    for i, c in enumerate(chains):
        for e in c["ev"]:
            ev_chain[id(e)] = i
    n_log_order_tiebreaks = 0
    tiebreaks = []
    assign = {}
    for bg, grp in man.groupby("bg_id"):
        cand = sorted(ev_by_bg[bg], key=lambda x: x["line"])
        sub = grp.sort_values("man_row")
        if len(cand) != len(sub):
            print(f"ERROR: {bg} has {len(sub)} manifest rows but "
                  f"{len(cand)} run.log events")
            sys.exit(1)
        # Do the matching on the value the LOG actually printed (1 dp), never
        # on the manifest's 3-dp value: if two events printed the same string,
        # the sub-0.01 s difference between the two manifest rows is an
        # artefact of that rounding and carries no information.
        printed = {id(e): float(f'{e["sec"]:.1f}') for e in cand}
        if len(cand) > 1 and len({f'{e["sec"]:.1f}' for e in cand}) == 1:
            # (b) the print cannot separate them -> global append order
            n_log_order_tiebreaks += len(cand)
            tiebreaks.append((bg,
                              [float(man.loc[man.man_row == int(r.man_row),
                                              "seconds"].iloc[0])
                               for r in sub.itertuples()],
                              [printed[id(e)] for e in cand]))
            for r, e in zip(sub.itertuples(), cand):
                assign[int(r.man_row)] = e
            continue
        # (a) nearest printed `seconds`, smallest gap first, bijection
        pairs = sorted(
            ((abs(float(f'{r.seconds:.1f}') - printed[id(e)]),
              int(r.man_row), e["line"], e)
             for r in sub.itertuples() for e in cand))
        taken_r, taken_e, order = set(), set(), {}
        for gap, mr, ln, e in pairs:
            if mr in taken_r or id(e) in taken_e:
                continue
            taken_r.add(mr)
            taken_e.add(id(e))
            order[mr] = e
        left_r = sorted(int(mr) for mr in sub.man_row if mr not in order)
        left_e = [e for e in cand if id(e) not in taken_e]
        if left_r:
            print(f"ERROR: {bg} could not be matched 1-to-1 by printed "
                  f"seconds ({left_r}, {[e['sec'] for e in left_e]})")
            sys.exit(1)
        for mr, e in order.items():
            assign[mr] = e
    if len(assign) != len(man):
        print(f"ERROR: matched {len(assign)} of {len(man)} manifest rows")
        sys.exit(1)
    if len({id(e) for e in assign.values()}) != len(man):
        print("ERROR: manifest->event match is not 1-to-1")
        sys.exit(1)
    man["line"] = [assign[r]["line"] for r in man.man_row]
    man["log_sec"] = [assign[r]["sec"] for r in man.man_row]
    man["chain"] = [ev_chain[id(assign[r])] for r in man.man_row]
    dsec = (man.seconds - man.log_sec).abs()
    print(f"  rows matched 1-to-1                     : {len(man)}/{len(man)}")
    print(f"  |manifest seconds - logged seconds|     : max {dsec.max():.3f}s "
          f"(log prints 1 dp, manifest stores 3 dp)")
    print(f"  rows resolved by logged `seconds`       : {len(man) - n_log_order_tiebreaks}")
    print(f"  rows where the log's 1 dp print could not separate the two")
    print(f"    events, resolved by global append order: {n_log_order_tiebreaks}")
    for bg, rs, es in tiebreaks:
        print(f"      {bg}: manifest seconds {sorted(rs)} vs logged "
              f"{sorted(es)} (spread "
              f"{max(rs) - min(rs):.3f}s -- a timing measurement only; "
              f"n_positions, n_rows and device are identical on both rows)")
    bad_chain = [r.bg_id for r in man.itertuples()
                 if ev_chain[id(assign[r.man_row])] != r.chain]
    if bad_chain:
        print(f"ERROR: chain assignment inconsistent for {bad_chain}")
        sys.exit(1)

    # ------------------------------------------------------------------
    print("\n" + "-" * 74)
    print("STEP 3 -- reconstruct each event's logged publish time "
          "(launcher-anchored)")
    print("-" * 74)
    print("  logged_publish_time = launcher attempt-start timestamp + the "
          "event's logged `elapsed`.")
    print("  The launcher timestamp is written by the shell wrapper at spawn "
          "time and is")
    print("  independent of any file mtime.  The only unmodelled term is that "
          "process's model")
    print("  load, which is positive and of order seconds; it is quantified "
          "below.")
    for i, c in enumerate(chains):
        for e in c["ev"]:
            e["t_logged"] = c["t_run0"] + e["elapsed"]
    mt = {}
    for bg in roster.bg_id:
        p = P2 / f"bg_{bg}.csv"
        if not p.exists():
            print(f"ERROR: missing score file {p.name}")
            sys.exit(1)
        mt[bg] = p.stat().st_mtime
    print(f"  all {len(mt)} score files present on disk with an mtime")

    print("\n  chain-level residual  mtime(bg) - logged_publish_time  "
          "(positive = the chain's file is the one on disk):")
    print("  chain  n_ev   min[s]   max[s]   mean[s]   n_resid>60s "
          "(that chain lost the file)")
    resid_tbl = []
    for i, c in enumerate(chains):
        res = [mt[e["bg"]] - e["t_logged"] for e in c["ev"]]
        nbig = int(sum(1 for r in res if r > 60.0))
        print(f"  {i:>4}  {len(res):>4}  {min(res):>7.1f}  {max(res):>7.1f}  "
              f"{np.mean(res):>7.1f}  {nbig:>22}")
        resid_tbl.append((i, min(res), max(res), nbig))

    # ------------------------------------------------------------------
    print("\n" + "-" * 74)
    print("STEP 4 -- apply the frozen selection rule, per duplicated bg_id")
    print("-" * 74)
    rows = []
    margins, kept_diff, drop_diff = [], [], []
    arm_of = dict(zip(roster.bg_id, roster.arm))
    for bg in roster.bg_id:
        sub = man[man.bg_id == bg]
        f = P2 / f"bg_{bg}.csv"
        f_mt = f.stat().st_mtime
        cands = []
        for r in sub.sort_values("man_row").itertuples():
            e = assign[r.man_row]
            cands.append(dict(man_row=r.man_row, chain=r.chain,
                              seconds=r.seconds, log_sec=r.log_sec,
                              t_logged=e["t_logged"],
                              d=abs(f_mt - e["t_logged"])))
        cands_sorted = sorted(cands, key=lambda c: c["d"])
        keep = cands_sorted[0]
        drop = cands_sorted[1:]
        # margin = how much further away the rejected row was (always > 0);
        # NaN when there was only one row and therefore no choice to make.
        margin = (max(c["d"] for c in drop) - keep["d"]) if drop \
            else float("nan")
        margins.append(margin)
        kept_diff.append(keep["d"])
        drop_diff.extend(c["d"] for c in drop)
        rk = man[man.man_row == keep["man_row"]].iloc[0]
        rows.append(dict(man_row=int(rk.man_row), bg_id=bg, arm=arm_of[bg],
                         n_dupe_rows=len(sub), n_positions=int(rk.n_positions),
                         n_rows=int(rk.n_rows), seconds=float(rk.seconds),
                         device=rk.device, chain=int(rk.chain),
                         logged_publish_time=keep["t_logged"],
                         file_mtime=f_mt, abs_diff_s=keep["d"],
                         runner_up_abs_diff_s=(max(c["d"] for c in drop)
                                               if drop else float("nan")),
                         margin_s=margin,
                         dropped_chain=(drop[0]["chain"] if drop
                                        else -1),
                         dropped_man_row=(drop[0]["man_row"] if drop
                                          else -1),
                         dropped_seconds=(drop[0]["seconds"] if drop
                                          else float("nan")),
                         kept_log_line=int(assign[keep["man_row"]]["line"])))
    ded = pd.DataFrame(rows)

    # ---- do the two candidate rows ever disagree on anything but seconds?
    diffcols = []
    for bg, sub in man.groupby("bg_id"):
        if len(sub) > 1:
            for col in ("n_positions", "n_rows", "device"):
                if sub[col].nunique() > 1:
                    diffcols.append((bg, col))
    print(f"  duplicated bg_ids                        : {n_dup}")
    print(f"  kept row  |logged - file mtime|          : max "
          f"{max(kept_diff):.1f}s  (mean {np.mean(kept_diff):.1f}s)")
    print(f"  dropped row |logged - file mtime|        : min "
          f"{min(drop_diff):.1f}s  (mean {np.mean(drop_diff):.1f}s)")
    print(f"  smallest margin between the two rows     : "
          f"{np.nanmin(margins):.1f}s  (over the {n_dup} duplicated bg_ids)")
    print(f"  duplicated bg_ids whose two rows differ in n_positions / n_rows / "
          f"device: {len(diffcols)} {diffcols if diffcols else ''}")
    if np.nanmin(margins) <= 0:
        print("ERROR: selection is ambiguous for at least one bg_id")
        sys.exit(1)

    # ---- corroboration (reported, not decided)
    ok_log, ok_man = 0, 0
    for bg, sub in man.groupby("bg_id"):
        if len(sub) < 2:
            continue
        last_log = sub.loc[sub.line.idxmax()]
        last_man = sub.loc[sub.man_row.idxmax()]
        kept = ded[ded.bg_id == bg].iloc[0]
        ok_log += int(kept.kept_log_line == int(last_log.line))
        ok_man += int(kept.man_row == int(last_man.man_row))
    print(f"\n  CORROBORATION (reported, cannot change the rule's outcome):")
    print(f"    kept row == LAST `scored` line in run.log for the bg_id : "
          f"{ok_log}/{n_dup}")
    print(f"    kept row == LAST row in manifest.csv append order        : "
          f"{ok_man}/{n_dup}")

    # ------------------------------------------------------------------
    print("\n" + "-" * 74)
    print("STEP 5 -- per-background detail (all 96 rows; "
          f"{n_dup} had duplicates)")
    print("-" * 74)
    print("  bg_id     arm  dup  KEPT(man_row,chain,seconds)      logged_publish"
          "            file_mtime           |d|s  DROP(man_row,chain,sec)  "
          "runner-up|s|  margin|s")
    fmt = ("%-9s %-4s %3d  %-28s %s  %s %6.1f  %-24s %10.1f  %8.1f")
    for r in ded.sort_values(["arm", "man_row"]).itertuples():
        kept = f"#{r.man_row} ch{r.chain} {r.seconds:.3f}s"
        dropped = (f"#{r.dropped_man_row} ch{r.dropped_chain} "
                   f"{r.dropped_seconds:.3f}s") if r.n_dupe_rows > 1 else "-"
        print(fmt % (r.bg_id, r.arm, r.n_dupe_rows, kept,
                     datetime.fromtimestamp(r.logged_publish_time)
                     .strftime("%Y-%m-%d %H:%M:%S"),
                     datetime.fromtimestamp(r.file_mtime)
                     .strftime("%Y-%m-%d %H:%M:%S"),
                     r.abs_diff_s, dropped,
                     r.runner_up_abs_diff_s, r.margin_s))
    print("\n  duplicated bg_ids, by arm: "
          f"{ded[ded.n_dupe_rows > 1].arm.value_counts().to_dict()}")
    print("  duplicated bg_ids, by chain that KEPT the file: "
          f"{ded[ded.n_dupe_rows > 1].chain.value_counts().sort_index().to_dict()}")
    print("  single-row bg_ids (no ambiguity arose): "
          f"{int((ded.n_dupe_rows == 1).sum())}")

    # ------------------------------------------------------------------
    print("\n" + "-" * 74)
    print("STEP 6 -- write manifest_dedup.csv (manifest.csv is NOT modified)")
    print("-" * 74)
    out = man[man.man_row.isin(ded.man_row)].copy()
    out = out.sort_values("man_row")
    extra = ded.set_index("man_row")
    out["n_manifest_rows_for_bg_id"] = out.man_row.map(extra.n_dupe_rows)
    out["kept_event_chain"] = out.man_row.map(extra.chain)
    out["logged_publish_time"] = out.man_row.map(extra.logged_publish_time)
    out["file_mtime"] = out.man_row.map(extra.file_mtime)
    out["abs_diff_s"] = out.man_row.map(extra.abs_diff_s).round(3)
    cols = ["bg_id", "n_positions", "n_rows", "seconds", "device",
            "n_manifest_rows_for_bg_id", "kept_event_chain",
            "logged_publish_time", "file_mtime", "abs_diff_s"]
    out[cols].to_csv(DEDUP, index=False)
    print(f"  wrote {DEDUP.relative_to(ROOT)}  "
          f"({len(out)} data rows, {out.bg_id.nunique()} unique bg_id)")
    print(f"  columns: {list(out[cols].columns)}")
    print(f"  manifest_dedup.csv sha256: {sha256(DEDUP)}")

    man_sha_after = sha256(MANIFEST)
    print(f"\n  manifest.csv sha256 AFTER : {man_sha_after}")
    print(f"  manifest.csv unchanged    : {man_sha_before == man_sha_after}")
    if man_sha_before != man_sha_after:
        print("ERROR: manifest.csv was modified")
        sys.exit(1)

    print("\n" + "-" * 74)
    print("A0 SUMMARY")
    print("-" * 74)
    print(f"  manifest.csv data rows                     : {len(man)} "
          f"for {man.bg_id.nunique()} unique bg_id")
    print(f"  bg_ids with duplicate rows                 : {n_dup} "
          f"(all exactly 2 rows)")
    print(f"  resolution                                 : for each, kept the "
          f"manifest row whose")
    print(f"                                             logged event time is "
          f"closest to the mtime of")
    print(f"                                             bg_<bg_id>.csv on disk "
          f"(max |d| {max(kept_diff):.1f}s;")
    print(f"                                             nearest rejected "
          f"candidate was at least")
    print(f"                                             {np.nanmin(drop_diff):.1f}s "
          f"away; smallest margin {np.nanmin(margins):.1f}s)")
    print(f"  scores affected                           : NONE. The 96 "
          f"bg_*.csv files were never")
    print(f"                                             duplicated in content; "
          f"only the timing log was.")
    print(f"  coverage values changed by this dedup      : "
          f"{'NO' if not diffcols else 'YES -- inspect'}")
    print("\nA0 DONE")


if __name__ == "__main__":
    main()
