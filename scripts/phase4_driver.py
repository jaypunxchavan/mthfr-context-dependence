#!/usr/bin/env python3
"""scripts/phase4_driver.py -- Phase 4 overnight driver (task A9).

PRE-REGISTERED BEHAVIOUR (this docstring was written before the driver's
first run; PHASE4_STRENGTHENING.md Task A9 lines 211-223 is the spec):

  DESIGN CREDIT: the state machine, budgets, guards, retry policy, signal
  handling and dry-run come from scripts/phase3_driver.py (read, not
  modified).  scripts/lib/phase3_guards.py is IMPORTED AND USED UNCHANGED
  (AGENTS 7: no existing script or library is edited).  This file is new
  because Phase 3's driver takes a JSON plan FILE, not a named plan, so it is
  not plan-configurable in the sense A9 needs.

  PLANS (separate state file and log per plan; ONE shared lock, so only one
  plan can ever run at a time):

    --plan A  night A   SA1 neighbour scoring on H
                       SA2 neighbour analysis   (coverage rule, below)
                       SA3 integrity pass
    --plan B  night B   SB1 ladder 150M scoring
                       SB2 ladder 35M scoring
                       [SB3, SB4, SB5, SB6 -> see NIGHT SPLIT below]
    --plan C  night C   SB3 ladder analysis, SB4 neighbour nonH scoring,
                       SB5 neighbour secondary analysis, SB6 integrity

  NIGHT SPLIT (arithmetic, from the timing smokes; nothing here is a guess):
    SA1 projection 304 min -> budget min(1.5 x 304, 330) = 330 min
    SA2 projection  15.4 min -> budget 23 min
    SA3 integrity            -> budget 10 min
      night A total = 330 + 23 + 10 = 363 min <= the 450-min ceiling
    SB1 projection 224 min -> budget 336 min
    SB2 projection  71 min -> budget 107 min
    SB3 projection  10 min -> budget  15 min
    SB4 projection 145 min -> budget 218 min
    SB5 projection  15.4 min -> budget 23 min
    SB6 integrity            -> budget 10 min
      all six = 709 min > 450.  Dropping in REVERSE priority (SB6, SB5, SB4,
      SB3) leaves SB1 + SB2 = 443 min <= 450, so SB3, SB4, SB5 and SB6 move
      to night C (15 + 218 + 23 + 10 = 266 min <= 450).  The move is stated in
      STATE_FOR_LAUNCH.md, as the spec requires.  The per-stage budget is
      1.5 x projection everywhere except SA1, which the spec caps at 330.

  THE PHASE 3 FLAKE -- what allowed a second start, and what replaces the lock
  -----------------------------------------------------------------------
  Phase 3's lock was: mkdir {home}/.driver.lock (atomic), then write
  driver.pid INSIDE it.  Those are two steps, and the window between them is
  the bug:

    driver 1:  mkdir() succeeds  ->  .driver.lock exists, driver.pid does NOT
    driver 2:  mkdir() raises FileExistsError
               -> int(pidf.read_text()) raises -> pid = None
               -> the code treats "pid is None" as a STALE lock
               -> shutil.rmtree(lock) DELETES DRIVER 1'S LOCK
               -> loop retries, mkdir() succeeds, driver 2 STARTS
    => two drivers, one home, no error anywhere.

  "driver.pid missing" is indistinguishable from "a live driver created this
  lock a millisecond ago and has not written its pid yet", so the stale-lock
  branch fires on a brand-new lock.  The window is sub-millisecond, which is
  exactly why test_double_start_second_refuses failed once and the root cause
  was never found.  Two secondary windows in the same code:
    * _pid_alive() is true for ANY live process with that PID, so after PID
      reuse a stale lock refuses forever with no way to tell why;
    * rmtree() in both acquire (stale branch) and release is unconditional on
      contents, so a slow driver's exit can delete a live peer's lock.

  REPLACEMENT (this file): the AUTHORITATIVE lock is an fcntl.flock(LOCK_EX |
  LOCK_NB) on a lock FILE.  The kernel drops a flock when the holding process
  dies, so a stale lock is impossible and there is no read-then-write window:
  either the lock is held (refuse, deterministically) or it is not (take it,
  atomically).  Two layers sit on top, as the spec asks:
    layer 2  a PID liveness check on the file's contents, to catch the
             pathological case of two processes both believing they hold the
             lock (e.g. a lock file copied onto a filesystem without working
             locks);
    layer 3  the original atomic mkdir marker, created after the flock is
             held and removed on release.  If the marker exists while the
             flock was obtainable, the previous holder died without cleaning
             up: the marker is stale, removed, and the run continues.
  A second start is refused with exit 2 and a printed reason.  This is
  demonstrated 50 of 50 in scripts/175_phase4_driver_tests.py.

  FAILURE POLICY (spec): a stage that times out, is guard-skipped,
  dependency-skipped or gate-failed is LOGGED and the driver CONTINUES to the
  next stage.  Nothing scientific is inferred by the driver.
  RETRY: up to 3 attempts per step (initial + 2 retries) on a nonzero exit
  OTHER THAN 3; exit 3 = the script's own gate failure -> NEVER retried; gate
  steps are never retried on any nonzero exit; a timeout is its own outcome
  (TERM to the child process group, --kill-grace seconds, then SIGKILL) and
  is not retried.

  COVERAGE RULE (SA2 and SB5) -- Amendment 1 item 5 of
  NEIGHBOUR_ARM_PREREG_v1, which SUPERSEDES the planning doc's ">= 24 of the
  C1 + C2 backgrounds" rule (the planning doc is protected and was not edited;
  the conflict is flagged in PHASE4A_BUILD_LOG.md): the neighbour analysis runs
  iff the COMPLETE NB has at least 30 members, where a member is complete when
  its score file covers >= 95% of its eligible H positions (its own position
  excluded).  NB = the 40 new backgrounds in cells C1, C2 and C5 (Amendment 1
  item 3) plus the six existing nulls G_I192T, AV_220, AV_155, AV_195,
  G_L178T, AV_175, which are already scored in the Phase 2 caches and so are
  always complete.  Below 30 -> the step is logged and SKIPPED (not failed).
  The UNDERPOWERED rule (|NB| < 30) inside the analysis is unchanged.

  GUARDS (before every stage, via phase3_guards.evaluate_guards, UNCHANGED):
  AC power and charge >= 30% (wait <= 10 min, polled); swap < 3.0 GB and free
  memory >= 25% (wait <= 30 min in 5-min steps); disk free >= 5 GiB (no wait
  window, fails immediately).  A missing tool is logged UNGUARDED and passes.
  --force overrides failures, logged.  The launcher refuses below 35% free
  memory and when a lock is held.

  STATE: {home}/driver_state_phase4{PLAN}.json, written atomically at every
  transition and every --heartbeat-s seconds during a running stage;
  {home}/driver_phase4{PLAN}.log gets the transitions plus all guard
  readings; per-stage output at {home}/driver_phase4{PLAN}_stage_<id>.log.
  On relaunch, steps recorded `completed` are skipped (resume); a stage whose
  steps are all completed is skipped entirely; anything else is re-evaluated.

  SIGNALS: SIGTERM/SIGINT -> TERM to the child process group, grace,
  SIGKILL, state written, lock released, exit 143.

  --dry-run prints the full plan (commands, budgets, guards, the night-split
  arithmetic, resume info) and runs NOTHING: no lock, no state, no
  directories, no stages.

  HOME: --home / PHASE4_HOME redirect every state/lock/log/precheck path
  (production default {root}/data/processed/phase4).  Tests always redirect,
  so they can never touch real outputs.  The production commands embed
  {home}, so a redirected home redirects the scorers' --out-dir too.

LIMITATIONS (AGENTS section 6; also printed by --dry-run and at exit):
  * guards read macOS tools; a missing tool is UNGUARDED and passes -- a
    passing guard is one point in time, and the driver re-reads before every
    stage;
  * the driver's stage budgets are CAPS on wall time, not estimates of
    completion; a stage can be killed at its budget with work done so far
    (every scorer is per-background atomic and resumable, so nothing is lost);
  * the integrity pass verifies what is on disk against the rosters and
    STATE_FOR_LAUNCH.md; it cannot verify that a score is scientifically
    right;
  * driver exit 0 means the run FINISHED and the per-stage record is in the
    state file -- NOT that every stage succeeded.
"""

from __future__ import annotations

import argparse
import csv
import errno
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.lib import phase3_guards as guards        # noqa: E402

DEFAULT_HOME = ROOT / "data" / "processed" / "phase4"
DEFAULT_SFL = (ROOT / "docs" / "tasks" / "phase4-strengthening" /
               "STATE_FOR_LAUNCH.md")

LOCK_FILE = ".driver.lockfile"          # authoritative: fcntl.flock
LOCK_DIR = ".driver.lock"               # second layer: the atomic mkdir marker
PID_NAME = "driver.pid"
CONFLICT_PATTERN = "phase4_driver|171_neigh_score|173_ladder_score"

NB_CELL_MIN = 30                        # Amendment 1 item 5
COV_MIN = 0.95                          # script 171/173's frozen coverage floor
SIX_NULLS = ["G_I192T", "AV_220", "AV_155", "AV_195", "G_L178T", "AV_175"]
AMENDED_CELLS = ("C1", "C2", "C5")      # Amendment 1 item 3

TERM = {"flag": False}


def _now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


# ======================================================================== plan
def plan_A():
    py = "{root}/venv/bin/python3"
    return {
        "name": "phase4-night-A",
        "stages": [
            {"id": "SA1", "label": "neighbour-arm scoring on H (script 171)",
             "budget_s": 330 * 60, "guard": True,
             "precheck": {"kind": "files",
                          "label": "G-N1 handoff: the frozen roster and its "
                                   "sha256 sidecar must be present",
                          "paths": ["{home}/neigh/roster_v1.csv",
                                    "{home}/neigh/roster_v1.sha256"]},
             "steps": [{"name": "score_neigh_H",
                        "cmd": [py, "{root}/scripts/171_neigh_score.py",
                                "--frame", "H", "--out-dir", "{home}/neigh"]}]},
            {"id": "SA2", "label": "neighbour-arm analysis (script 172), "
                                   "Amendment 1 item 5 coverage rule",
             "budget_s": 23 * 60, "guard": True,
             "steps": [{"name": "neigh_analysis",
                        "requires": {"kind": "nb_coverage"},
                        "cmd": [py, "{root}/scripts/172_neigh_analysis.py",
                                "--mode", "full"]}]},
            {"id": "SA3", "label": "integrity pass (driver --integrity)",
             "budget_s": 10 * 60, "guard": True,
             "steps": [{"name": "integrity",
                        "cmd": ["{python}", "{driver}", "--integrity",
                                "--plan", "{plan}", "--home", "{home}"]}]},
        ],
    }


def plan_B():
    py = "{root}/venv/bin/python3"
    return {
        "name": "phase4-night-B",
        "stages": [
            {"id": "SB1", "label": "ladder scoring, ESM-2 150M (script 173)",
             "budget_s": 336 * 60, "guard": True,
             "steps": [{"name": "ladder_150M",
                        "cmd": [py, "{root}/scripts/173_ladder_score.py",
                                "--model", "150M",
                                "--out-dir", "{home}/ladder/150M"]}]},
            {"id": "SB2", "label": "ladder scoring, ESM-2 35M (script 173)",
             "budget_s": 107 * 60, "guard": True,
             "steps": [{"name": "ladder_35M",
                        "cmd": [py, "{root}/scripts/173_ladder_score.py",
                                "--model", "35M",
                                "--out-dir", "{home}/ladder/35M"]}]},
        ],
    }


def plan_C():
    """Night C: the stages that did not fit night B, in priority order."""
    py = "{root}/venv/bin/python3"
    return {
        "name": "phase4-night-C",
        "stages": [
            {"id": "SB3", "label": "ladder analysis (script 174) with the "
                                   "150M and 35M columns and cross-model "
                                   "agreement",
             "budget_s": 15 * 60, "guard": True,
             "steps": [{"name": "ladder_analysis",
                        "cmd": [py, "{root}/scripts/174_ladder_analysis.py",
                                "--mode", "full"]}]},
            {"id": "SB4", "label": "neighbour-arm secondary scoring, nonH "
                                   "frame (script 171) completing the 654-"
                                   "position frame",
             "budget_s": 218 * 60, "guard": True,
             "steps": [{"name": "score_neigh_nonH",
                        "cmd": [py, "{root}/scripts/171_neigh_score.py",
                                "--frame", "nonH",
                                "--out-dir", "{home}/neigh_nonH"]}]},
            {"id": "SB5", "label": "neighbour-arm secondary analysis "
                                   "(script 172): the full-frame version",
             "budget_s": 23 * 60, "guard": True,
             "steps": [{"name": "neigh_secondary_analysis",
                        "requires": {"kind": "state", "stage": "SB4",
                                     "status": "completed"},
                        "cmd": [py, "{root}/scripts/172_neigh_analysis.py",
                                "--mode", "full"]}]},
            {"id": "SB6", "label": "integrity pass (driver --integrity)",
             "budget_s": 10 * 60, "guard": True,
             "steps": [{"name": "integrity",
                        "cmd": ["{python}", "{driver}", "--integrity",
                                "--plan", "{plan}", "--home", "{home}"]}]},
        ],
    }


PLANS = {"A": plan_A, "B": plan_B, "C": plan_C}


# ======================================================================= state
def state_name(plan):
    return f"driver_state_phase4{plan}.json"


def log_name(plan):
    return f"driver_phase4{plan}.log"


def stage_log_name(plan, sid):
    return f"driver_phase4{plan}_stage_{sid}.log"


def load_state(home, plan):
    p = home / state_name(plan)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def new_state(plan):
    return {"version": 1, "plan": plan, "driver_pid": os.getpid(),
            "status": "running", "started": _now_iso(), "updated": _now_iso(),
            "finished": None, "current_stage": None,
            "current_stage_started": None, "stages": {}}


def save_state(home, plan, state):
    state["updated"] = _now_iso()
    p = home / state_name(plan)
    tmp = p.with_name("." + p.name + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, p)


def stage_rec(state, sid):
    return state["stages"].setdefault(sid, {
        "status": "pending", "start": None, "end": None, "note": None,
        "steps": {}})


def step_rec(state, sid, name):
    return stage_rec(state, sid)["steps"].setdefault(name, {
        "status": "pending", "attempts": 0, "exit_code": None, "start": None,
        "end": None})


# ======================================================================== lock
def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except (OverflowError, ValueError):
        return False
    return True


class Lock:
    """fcntl.flock (authoritative) + PID liveness + atomic mkdir (second layer).

    Why this replaces Phase 3's mkdir+driver.pid lock: in Phase 3 the window
    between mkdir() and driver.pid's write let a second driver read "no pid",
    decide the lock was stale, rmtree it and start alongside the first.  Here
    the kernel arbitrates: LOCK_EX|LOCK_NB either fails immediately (refuse)
    or succeeds (take it), with no read-then-write step in between, and the
    kernel releases it when the holder dies, so a stale lock cannot exist.
    """

    def __init__(self, home, print_fn=print):
        self.home = home
        self.print_fn = print_fn
        self.fh = None
        self.lockfile = home / LOCK_FILE
        self.markerdir = home / LOCK_DIR

    def acquire(self):
        self.lockfile.parent.mkdir(parents=True, exist_ok=True)
        fh = open(self.lockfile, "a+")
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            fh.close()
            if e.errno in (errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK):
                held = self._holder_pid()
                self.print_fn(
                    f"REFUSING TO START: driver lock {self.lockfile} is held "
                    f"by another driver"
                    + (f" (PID {held}, alive)" if held else "")
                    + ". Stop it with: kill $(cat "
                      f"{self.home / PID_NAME}) -- nothing was created.")
                return None
            self.print_fn(f"REFUSING TO START: flock on {self.lockfile} "
                          f"failed with {e!r}")
            return None
        self.fh = fh
        # layer 2: PID liveness, for the pathological both-hold-it case
        held = self._holder_pid()
        if held is not None and held != os.getpid() and _pid_alive(held):
            self._release_flock()
            self.print_fn(f"REFUSING TO START: {self.lockfile} names PID "
                          f"{held}, which is alive, even though the flock was "
                          f"obtainable -- refusing rather than risking two "
                          f"drivers (lock released)")
            return None
        # we own it: record who we are, then take the mkdir marker (layer 3)
        fh.seek(0)
        fh.truncate()
        fh.write(json.dumps({"pid": os.getpid(), "plan": self.plan,
                             "started": _now_iso()}) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
        try:
            self.markerdir.mkdir()
            (self.markerdir / PID_NAME).write_text(str(os.getpid()) + "\n")
        except FileExistsError:
            self.print_fn(f"STALE LOCK MARKER CLEARED: {self.markerdir} "
                          f"existed although the flock was free, so its "
                          f"previous holder died without cleaning up -> "
                          f"removing the marker and continuing")
            shutil.rmtree(self.markerdir, ignore_errors=True)
            try:
                self.markerdir.mkdir()
                (self.markerdir / PID_NAME).write_text(str(os.getpid()) + "\n")
            except OSError as e:
                self.print_fn(f"REFUSING TO START: could not create the "
                              f"second-layer marker {self.markerdir}: {e!r}")
                self._release_flock()
                return None
        return self

    def _holder_pid(self):
        try:
            txt = self.lockfile.read_text().strip()
            if not txt:
                return None
            return int(json.loads(txt).get("pid"))
        except (OSError, ValueError, json.JSONDecodeError):
            return None

    def _release_flock(self):
        if self.fh is not None:
            try:
                fcntl.flock(self.fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            try:
                self.fh.close()
            except OSError:
                pass
            self.fh = None

    def release(self):
        self._release_flock()
        shutil.rmtree(self.markerdir, ignore_errors=True)
        try:
            self.lockfile.unlink()
        except OSError:
            pass


# ==================================================================== coverage
def _frame_positions(home):
    """H from the frozen roster is not needed: the coverage rule only needs
    each background's eligible-position count, which is |H| minus its own
    position when that position is in H.  H itself is read from script 125 via
    the same import the scorers use, so the driver cannot disagree with them."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "s125_phase2_analysis", str(ROOT / "scripts/125_phase2_analysis.py"))
    s125 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s125)
    return set(int(p) for p in s125.holdout(s125.build_frame()))


def check_nb_coverage(home, log=lambda m: None):
    """Amendment 1 item 5: run the neighbour analysis iff the COMPLETE NB has
    >= 30 members (a member = a score file covering >= 95% of its eligible H
    positions, own position excluded; the six existing nulls are always
    complete because Phase 2 scored them)."""
    roster = home / "neigh" / "roster_v1.csv"
    out = home / "neigh"
    if not roster.exists():
        return False, f"roster {roster} missing -> dependency NOT met"
    H = _frame_positions(home)
    nb = []
    with open(roster, newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("cell") in AMENDED_CELLS:
                nb.append((r["bg_id"], int(r["position"])))
    complete, detail = len(SIX_NULLS), [f"{len(SIX_NULLS)} existing nulls "
                                        f"(always complete)"]
    for bg_id, own in nb:
        exp = len([p for p in H if p != own])
        f = out / f"bg_{bg_id}.csv"
        if not f.exists():
            detail.append(f"{bg_id}: file absent")
            continue
        with open(f, "rb") as fh2:
            lines = sum(chunk.count(b"\n")
                        for chunk in iter(lambda: fh2.read(1 << 20), b""))
        got = (max(lines - 1, 0)) / 19.0
        if got >= COV_MIN * exp:
            complete += 1
        else:
            detail.append(f"{bg_id}: {got:.0f}/{exp} < {COV_MIN:.0%}")
    ok = complete >= NB_CELL_MIN
    msg = (f"NB coverage (Amendment 1 item 5): {complete}/{len(nb) + len(SIX_NULLS)} "
           f"members complete ({NB_CELL_MIN} needed) -> "
           f"{'dependency met' if ok else 'dependency NOT met'}; "
           + "; ".join(detail[:6]))
    log(msg)
    return ok, msg


def check_requires(req, home, plan, state, log):
    kind = req.get("kind")
    if kind == "files":
        expand = make_expander(home, plan)
        missing = [expand(p) for p in req.get("paths", [])
                   if not os.path.exists(expand(p))]
        return (not missing), (f"required files present"
                              if not missing
                              else f"required files missing: {missing}")
    if kind == "nb_coverage":
        return check_nb_coverage(home, log)
    if kind == "state":
        sid, want = req.get("stage"), req.get("status", "completed")
        other = state.get("stages", {}).get(sid, {})
        got = other.get("status")
        return got == want, (f"stage {sid} status is {got!r} (need "
                             f"{want!r})")
    log(f"UNKNOWN requires kind {kind!r} -> treating dependency as NOT met")
    return False, f"unknown requires kind {kind!r}"


def check_precheck(pc, home, plan):
    if pc.get("kind") != "files":
        return False, f"unknown precheck kind {pc.get('kind')!r}"
    expand = make_expander(home, plan)
    missing = [expand(p) for p in pc.get("paths", [])
               if not os.path.exists(expand(p))]
    if missing:
        return False, f"missing required input(s): {', '.join(missing)}"
    return True, "all required inputs present"


# ================================================================== integrity
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")


def parse_state_for_launch(text):
    """One 'path sha256 <hash>' per line (the format A9 fixes)."""
    pairs = []
    for line in text.splitlines():
        m = HEX64.search(line)
        if not m:
            continue
        toks = line.split()
        paths = [t for t in toks if "/" in t and not t.startswith("<")]
        if not paths:
            continue
        pairs.append((paths[0].lstrip("./"), m.group(0)))
    return pairs


def run_integrity(home, plan, sfl_path):
    findings, fail = [], False

    def f(msg):
        findings.append(msg)

    # 1. the neighbour roster and its outputs
    roster = home / "neigh" / "roster_v1.csv"
    if roster.exists():
        ids = [r["bg_id"] for r in csv.DictReader(open(roster, newline=""))]
        n = len(list((home / "neigh").glob("bg_*.csv")))
        verdict = "OK" if n == len(ids) else "MISMATCH (finding)"
        f(f"neigh (H frame): {n} bg_*.csv present, {len(ids)} in the roster "
          f"-> {verdict}")
        f(f"neigh: manifest.csv "
          f"{'present' if (home / 'neigh' / 'manifest.csv').exists() else 'ABSENT'}")
        nn = len(list((home / "neigh_nonH").glob("bg_*.csv"))) \
            if (home / "neigh_nonH").is_dir() else 0
        f(f"neigh_nonH (secondary frame): {nn} bg_*.csv present")
    else:
        f(f"roster {roster} absent -> neighbour checks skipped")
    # 2. ladder outputs per model that has any
    for model in ("650M", "150M", "35M"):
        d = home / "ladder" / model
        if not d.is_dir():
            f(f"ladder/{model}: directory absent")
            continue
        n = len(list(d.glob("bg_*.csv")))
        f(f"ladder/{model}: {n} bg_*.csv present (97 expected); wt_H.csv "
          f"{'present' if (d / 'wt_H.csv').exists() else 'ABSENT'}; "
          f"manifest.csv {'present' if (d / 'manifest.csv').exists() else 'ABSENT'}")
        if n not in (0, 97):
            fail = True
            f(f"ladder/{model}: {n} is neither 0 nor 97 -> FLAG")
    # 3. sha256 of every staged script vs STATE_FOR_LAUNCH.md
    sfl = Path(sfl_path) if sfl_path else DEFAULT_SFL
    if not sfl.exists():
        f(f"STATE_FOR_LAUNCH.md not found at {sfl} -> sha256 verification "
          f"SKIPPED (written before launch; session 4b re-verifies)")
    else:
        pairs = parse_state_for_launch(sfl.read_text())
        if not pairs:
            f(f"{sfl}: no 'path sha256 <hash>' lines recognised -> sha256 "
              f"verification SKIPPED (parser limitation; 4b re-verifies)")
        for rel, want in pairs:
            p = ROOT / rel if not os.path.isabs(rel) else Path(rel)
            if not p.exists():
                fail = True
                f(f"sha256: LISTED BUT MISSING {rel} (expected {want}) -> FLAG")
                continue
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            got = h.hexdigest()
            if got == want:
                f(f"sha256: MATCH {rel}")
            else:
                fail = True
                f(f"sha256: MISMATCH {rel} got {got} expected {want} -> FLAG")
    # 4. the plan's state file
    st = home / state_name(plan)
    if st.exists():
        try:
            data = json.loads(st.read_text())
            summary = ", ".join(f"{k}={v.get('status')}" for k, v in
                                sorted(data.get("stages", {}).items()))
            f(f"{state_name(plan)} present; stage statuses: {summary or 'none'}")
        except (OSError, json.JSONDecodeError) as e:
            fail = True
            f(f"{state_name(plan)} present but UNPARSEABLE: {e} -> FLAG")
    else:
        f(f"{state_name(plan)} absent at {st} (the parent driver writes it)")

    for line in findings:
        print(f"INTEGRITY: {line}")
    print(f"INTEGRITY: RESULT {'FAIL' if fail else 'PASS'} ({len(findings)} "
          f"findings)")
    return 3 if fail else 0


# ==================================================================== plumbing
def make_expander(home, plan):
    reps = {"{root}": str(ROOT), "{home}": str(home), "{python}": sys.executable,
            "{driver}": str(Path(__file__).resolve()), "{plan}": plan}

    def expand(s):
        for k, v in reps.items():
            s = s.replace(k, v)
        return s
    return expand


class Logger:
    def __init__(self, home, plan):
        self.path = home / log_name(plan)
        self.fh = open(self.path, "a", buffering=1)

    def __call__(self, msg):
        line = f"{_now_iso()} {msg}"
        print(line, flush=True)
        self.fh.write(line + "\n")
        self.fh.flush()

    def close(self):
        try:
            self.fh.close()
        except OSError:
            pass


def kill_child_group(p, grace, log, tag):
    if p.poll() is not None:
        return
    try:
        pgid = os.getpgid(p.pid)
    except ProcessLookupError:
        return

    def sig(s):
        try:
            os.killpg(pgid, s)
        except (ProcessLookupError, PermissionError, OSError):
            pass
    log(f"{tag}: forwarding TERM to child process group {pgid}")
    sig(signal.SIGTERM)
    end = time.time() + grace
    while time.time() < end:
        if p.poll() is not None:
            log(f"{tag}: child group exited on TERM (rc={p.returncode})")
            return
        time.sleep(0.05)
    log(f"{tag}: child still alive after {grace:.1f} s grace -> SIGKILL "
        f"process group {pgid}")
    sig(signal.SIGKILL)
    try:
        p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass


def supervise(p, deadline, heartbeat_s, on_heartbeat):
    last_hb = time.time()
    while True:
        rc = p.poll()
        if rc is not None:
            return ("exit", rc)
        if TERM["flag"]:
            return ("term", None)
        now = time.time()
        if now >= deadline:
            return ("timeout", None)
        if now - last_hb >= heartbeat_s:
            on_heartbeat()
            last_hb = now
        time.sleep(0.1)


def interruptible_sleep(sec, what):
    end = time.time() + sec
    while time.time() < end:
        if TERM["flag"]:
            raise Shutdown(f"signal during {what}")
        time.sleep(min(0.2, max(end - time.time(), 0.01)))


class Shutdown(Exception):
    pass


# ================================================================= stage runner
def run_stage(stage, ctx):
    sid = stage.get("id", "?")
    log, state, home, args, plan = (ctx["log"], ctx["state"], ctx["home"],
                                    ctx["args"], ctx["plan"])
    expand = make_expander(home, plan)
    budget = float(stage.get("budget_s", 300))
    steps = stage.get("steps", [])
    rec = stage_rec(state, sid)

    pending = [s for s in steps
               if step_rec(state, sid, s.get("name", "?")).get("status")
               != "completed"]
    if steps and not pending:
        log(f"{sid}: all {len(steps)} step(s) already completed -> skipped "
            f"(resume)")
        if rec.get("status") != "completed":
            rec["status"] = "completed"
            rec["note"] = "resume: all steps previously completed"
            save_state(home, plan, state)
        return
    log(f"{sid}: {len(pending)}/{len(steps)} step(s) pending; budget "
        f"{budget:.0f} s ({budget / 60:.0f} min)")

    if stage.get("guard", True):
        ok, msgs = guards.evaluate_guards(
            force=args.force, ac_wait_s=args.guard_ac_wait,
            ac_poll_s=args.guard_ac_poll, mem_wait_s=args.guard_mem_wait,
            mem_step_s=args.guard_mem_step,
            log=lambda m: log(f"[{sid}] guard: {m}"),
            stop=lambda: TERM["flag"])
        if TERM["flag"]:
            raise Shutdown("signal during guard wait")
        if not ok:
            rec.update(status="skipped_guard", end=_now_iso(),
                       note="guards failed after their wait windows (readings "
                            "logged above)")
            save_state(home, plan, state)
            log(f"{sid}: SKIPPED (guard failure) -> continuing")
            return
        if args.force and any("OVERRIDDEN" in m for m in msgs):
            log(f"[{sid}] guards FAILED but --force given -> stage FORCED")

    pc = stage.get("precheck")
    if pc:
        ok, why = check_precheck(pc, home, plan)
        if not ok:
            rec.update(status="gate_failed", end=_now_iso(),
                       note=f"precheck failed: {why}")
            save_state(home, plan, state)
            log(f"{sid}: GATE FAILED precheck ({pc.get('label', '')}): {why} "
                f"-> skipping stage, continuing")
            return
        log(f"{sid}: precheck OK ({pc.get('label', '')})")

    t0 = time.time()
    deadline = t0 + budget
    rec.update(status="running", start=_now_iso(), end=None, note=None)
    state["current_stage"] = sid
    state["current_stage_started"] = _now_iso()
    save_state(home, plan, state)
    log(f"{sid}: START budget {budget:.0f} s")
    stage_log = home / stage_log_name(plan, sid)

    def on_heartbeat():
        save_state(home, plan, state)
        log(f"[{sid}] heartbeat: running {time.time() - t0:.0f} s of "
            f"{budget:.0f} s; output: {stage_log}")

    for step in steps:
        name = step.get("name", "?")
        srec = step_rec(state, sid, name)
        if TERM["flag"]:
            raise Shutdown("signal between steps")
        if srec.get("status") == "completed":
            log(f"{sid}.{name}: already completed -> skipped (resume)")
            continue
        req = step.get("requires")
        if req:
            met, why = check_requires(req, home, plan, state,
                                      lambda m: log(f"[{sid}] {m}"))
            log(f"[{sid}] dependency {name}: "
                f"{'met ->' if met else 'NOT met ->'} {why}")
            if not met:
                srec.update(status="skipped_dependency", end=_now_iso())
                save_state(home, plan, state)
                log(f"{sid}.{name}: dependency NOT met -> logged and skipped")
                continue
        cmd = [expand(c) for c in step.get("cmd", [])]
        max_attempts = 1 if step.get("gate") else 3
        attempt = 0
        while True:
            attempt += 1
            if time.time() >= deadline:
                rec.update(status="timeout", end=_now_iso(),
                           note=f"stage budget {budget:.0f} s exhausted before "
                                f"step {name} finished")
                state["current_stage"] = None
                save_state(home, plan, state)
                log(f"{sid}: TIMEOUT (stage budget) -> continuing")
                return
            srec["attempts"] = attempt
            srec["start"] = srec.get("start") or _now_iso()
            save_state(home, plan, state)
            log(f"{sid}.{name}: attempt {attempt}/{max_attempts}: "
                f"executing: {' '.join(cmd)}")
            with open(stage_log, "ab") as fh:
                try:
                    p = subprocess.Popen(cmd, cwd=str(ROOT), stdout=fh,
                                         stderr=subprocess.STDOUT,
                                         start_new_session=True,
                                         env=dict(os.environ))
                except OSError as e:
                    srec.update(status="failed", exit_code=None, end=_now_iso())
                    rec.update(status="failed", end=_now_iso(),
                               note=f"could not spawn {cmd[0]!r}: {e}")
                    state["current_stage"] = None
                    save_state(home, plan, state)
                    log(f"{sid}.{name}: SPAWN FAILED: {e} -> stage failed")
                    return
            kind, rc = supervise(p, deadline, args.heartbeat_s, on_heartbeat)
            if kind == "term":
                kill_child_group(p, args.kill_grace, log,
                                 f"{sid}.{name} TERM")
                raise Shutdown("signal during stage")
            if kind == "timeout":
                kill_child_group(p, args.kill_grace, log,
                                 f"{sid}.{name} TIMEOUT")
                srec.update(status="killed_timeout", exit_code=None,
                            end=_now_iso())
                rec.update(status="timeout", end=_now_iso(),
                           note=f"step {name} killed at the stage budget; "
                                f"child process group terminated")
                state["current_stage"] = None
                save_state(home, plan, state)
                log(f"{sid}: TIMEOUT after {budget:.0f} s -> child group "
                    f"killed; continuing")
                return
            srec.update(exit_code=rc, end=_now_iso())
            save_state(home, plan, state)
            if rc == 0:
                srec.update(status="completed")
                save_state(home, plan, state)
                log(f"{sid}.{name}: completed (exit 0, attempt {attempt})")
                break
            if rc == 3 or step.get("gate"):
                srec.update(status="gate_failed")
                reason = ("exit 3 = the script's own gate failure (NEVER "
                          "retried, per spec)" if rc == 3
                          else f"gate step nonzero exit {rc} (gate steps are "
                               f"never retried)")
                rec.update(status="gate_failed", end=_now_iso(),
                           note=f"step {name}: {reason}")
                state["current_stage"] = None
                save_state(home, plan, state)
                log(f"{sid}.{name}: {reason} -> stage gate failure logged, "
                    f"continuing")
                return
            if attempt >= max_attempts:
                srec.update(status="failed")
                rec.update(status="failed", end=_now_iso(),
                           note=f"step {name} crashed with exit {rc} after "
                                f"{attempt} attempts (3 max)")
                state["current_stage"] = None
                save_state(home, plan, state)
                log(f"{sid}.{name}: exit {rc}; attempts exhausted -> stage "
                    f"failed, continuing")
                return
            log(f"{sid}.{name}: exit {rc} (nonzero, not 3, not a gate step) "
                f"-> retrying in {args.retry_delay:.0f} s")
            interruptible_sleep(args.retry_delay, "retry delay")

    statuses = [step_rec(state, sid, s.get("name", "?")).get("status")
                for s in steps]
    if statuses and all(s == "completed" for s in statuses):
        rec.update(status="completed", note=None)
    elif statuses and all(s == "skipped_dependency" for s in statuses):
        rec.update(status="skipped_dependency",
                   note="no step's dependency was met (logged above)")
    else:
        rec.update(status="completed",
                   note=f"{statuses.count('skipped_dependency')} "
                        f"dependency-skipped step(s) (logged above)")
    rec["end"] = _now_iso()
    state["current_stage"] = None
    save_state(home, plan, state)
    log(f"{sid}: DONE status={rec['status']}"
        + (f" ({rec['note']})" if rec.get("note") else ""))


# ====================================================================== driver
def terminate_and_cleanup(state, home, plan, lock, log, args):
    state.update(status="terminated", finished=_now_iso(), current_stage=None)
    for sid, rec in state.get("stages", {}).items():
        if rec.get("status") == "running":
            rec.update(status="interrupted",
                       note="driver received a signal while this stage ran")
    try:
        save_state(home, plan, state)
    except OSError:
        pass
    if log is not None:
        log("DRIVER TERMINATED -> lock released; per-stage record in "
            f"{home / state_name(plan)}")
        log.close()
    lock.release()
    return 143


def run_driver(args, plan, home):
    lock = Lock(home)
    lock.plan = args.plan
    if lock.acquire() is None:
        return 2
    conflicts = guards.conflicting_processes(CONFLICT_PATTERN)
    if conflicts is None:
        print(f"UNGUARDED: pgrep unavailable -> conflicting-process check "
              f"skipped (pattern '{CONFLICT_PATTERN}')")
    elif conflicts:
        lock.release()
        print(f"REFUSING TO START: conflicting process(es) alive matching "
              f"'{CONFLICT_PATTERN}' (this process and its ancestors "
              f"excluded) -> lock released")
        for pid in conflicts:
            rc, out = guards._run(["ps", "-o", "command=", "-p", str(pid)])
            print(f"  PID {pid}: {out.strip()[:160] or '?'}")
        return 2

    log = Logger(home, args.plan)
    state = load_state(home, args.plan) or new_state(args.plan)
    state.update(driver_pid=os.getpid(), status="running", dry_run=False,
                 plan=args.plan)
    log(f"DRIVER START pid={os.getpid()} plan={args.plan} home={home} "
        f"force={args.force}")
    for sid, rec in sorted(state.get("stages", {}).items()):
        if rec.get("status") in ("running", "terminated", "interrupted"):
            rec.update(status="interrupted",
                       note="previous driver run ended while this stage ran")
            log(f"{sid}: previous run left status 'interrupted' -> will be "
                f"re-evaluated")
    save_state(home, args.plan, state)
    signal.signal(signal.SIGTERM, lambda *_: TERM.__setitem__("flag", True))
    signal.signal(signal.SIGINT, lambda *_: TERM.__setitem__("flag", True))

    ctx = {"log": log, "state": state, "home": home, "args": args,
           "plan": args.plan}
    cap_deadline = time.time() + args.total_cap_min * 60
    try:
        for stage in plan.get("stages", []):
            if TERM["flag"]:
                raise Shutdown("signal between stages")
            sid = stage.get("id", "?")
            steps = stage.get("steps", [])
            pending = [s for s in steps
                       if step_rec(state, sid, s.get("name", "?")).get("status")
                       != "completed"]
            if pending and time.time() >= cap_deadline:
                rec = stage_rec(state, sid)
                rec.update(status="skipped_cap", end=_now_iso(),
                           note=f"global {args.total_cap_min:.0f}-min cap "
                                f"reached before this stage started")
                save_state(home, args.plan, state)
                log(f"{sid}: SKIPPED -- global cap reached")
                continue
            run_stage(stage, ctx)
        state.update(status="finished", finished=_now_iso(),
                     current_stage=None)
        save_state(home, args.plan, state)
        summary = ", ".join(f"{k}={v.get('status')}" for k, v in
                            sorted(state["stages"].items()))
        log(f"DRIVER FINISHED: {summary}")
        log("LIMITATIONS: exit 0 = run finished, not every stage succeeded; "
            "read the state file; guard readings are point-in-time; UNGUARDED "
            "checks prove nothing.")
        log.close()
        lock.release()
        return 0
    except Shutdown as e:
        log(f"DRIVER TERMINATED: {e}")
        return terminate_and_cleanup(state, home, args.plan, lock, log, args)
    except Exception as e:
        log(f"DRIVER ERROR: {type(e).__name__}: {e} -> lock released, exit 1")
        state.update(status="error", finished=_now_iso())
        try:
            save_state(home, args.plan, state)
        except OSError:
            pass
        log.close()
        lock.release()
        return 1


# ===================================================================== dry-run
def print_plan(plan, home, args, state):
    stages = plan.get("stages", [])
    total = sum(s.get("budget_s", 300) for s in stages)
    print("PHASE 4 DRY RUN -- nothing is executed; no lock, no state, no "
          "directories are created by this mode.")
    print(f"plan: {plan.get('name')} (--plan {args.plan}); {len(stages)} "
          f"stage(s); stage budgets total {total / 60:.0f} min; global cap "
          f"{args.total_cap_min:.0f} min")
    print(f"home (state/lock/log/prechecks): {home}")
    print(f"state file: {state_name(args.plan)}   log: {log_name(args.plan)}")
    print("NIGHT SPLIT (from the timing smokes, nothing assumed): SA1 304 -> "
          "330 (capped); SA2 15.4 -> 23; SA3 10; SB1 224 -> 336; SB2 71 -> "
          "107; SB3 10 -> 15; SB4 145 -> 218; SB5 15.4 -> 23; SB6 10.  "
          "Night A = 363 min, night B = 443 min, both <= 450; SB3+SB4+SB5+SB6 "
          "= 266 min move to night C in that order.")
    print("guards before every stage: AC power + battery >= 30% (wait <= "
          f"{args.guard_ac_wait:.0f} s); swap < 3.0 GB + free memory >= 25% "
          f"(wait <= {args.guard_mem_wait:.0f} s in {args.guard_mem_step:.0f} s "
          "steps); disk free >= 5 GiB (no wait).  Missing tool -> UNGUARDED "
          "(logged).  --force overrides (logged).")
    print(f"retry: up to 3 attempts per step, {args.retry_delay:.0f} s apart, "
          f"on nonzero exit != 3; exit 3 never retried; gate steps never "
          f"retried; timeouts not retried (TERM then SIGKILL after "
          f"{args.kill_grace:.0f} s).")
    print(f"lock: fcntl.flock(LOCK_EX|LOCK_NB) on {LOCK_FILE} (authoritative; "
          f"the kernel releases it when the holder dies, so no stale lock and "
          f"no read-then-write window) + a PID liveness check + the atomic "
          f"mkdir marker {LOCK_DIR} as a second layer.  A held lock refuses "
          f"the start with exit 2; a marker left by a dead holder is removed "
          f"with a printed message.")
    print("coverage rule (SA2/SB5): run the neighbour analysis iff the "
          f"COMPLETE NB has >= {NB_CELL_MIN} members, a member complete at "
          f">= {COV_MIN:.0%} of its eligible H positions (Amendment 1 item 5, "
          f"which supersedes the planning doc's >= 24 of C1+C2 rule).")
    for st in stages:
        b = st.get("budget_s", 300)
        print(f"\n{st.get('id')}  budget {b / 60:.0f} min  {st.get('label', '')}")
        pc = st.get("precheck")
        if pc:
            ex = make_expander(home, args.plan)
            print(f"    precheck [{pc.get('label', '')}]: "
                  + ", ".join(ex(p) for p in pc.get("paths", [])))
        for step in st.get("steps", []):
            tags = []
            if step.get("gate"):
                tags.append("GATE (never retried)")
            if step.get("requires"):
                r = step["requires"]
                tags.append(f"runs only if {r.get('kind')} "
                            f"{r.get('module', r.get('stage', ''))} is met")
            ex = make_expander(home, args.plan)
            print(f"    step {step.get('name')}"
                  + (f"  [{'; '.join(tags)}]" if tags else "") + ":")
            print("      " + " ".join(ex(c) for c in step.get("cmd", [])))
    if state:
        print("\nresume info from the existing state file:")
        for sid, rec in sorted(state.get("stages", {}).items()):
            steps = rec.get("steps", {})
            done = steps and all(s.get("status") == "completed"
                                 for s in steps.values())
            print(f"  {sid}: {'completed -> would be SKIPPED' if done else rec.get('status') + ' -> would be re-evaluated'}")
    else:
        print("\nresume info: no existing state file (fresh start)")
    print("\nLIMITATIONS: guards degrade to UNGUARDED on a missing macOS tool; "
          "budgets are caps, not estimates; driver exit 0 = run finished.")


# ========================================================================= main
def _env_float(name, default):
    raw = os.environ.get(name)
    try:
        return float(raw) if raw not in (None, "") else default
    except ValueError:
        print(f"WARNING: {name}={raw!r} not a number; using {default}",
              file=sys.stderr)
        return default


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description="Phase 4 overnight driver (task A9). See module "
                    "docstring for the pre-registered behaviour.")
    ap.add_argument("--plan", choices=sorted(PLANS),
                    default=os.environ.get("PHASE4_PLAN", "A"))
    ap.add_argument("--plan-file", default=None,
                    help="JSON plan file OVERRIDING the built-in stage table "
                         "(the same mechanism Phase 3's driver used for its "
                         "tests; --plan still names the state file and log)")
    ap.add_argument("--home", default=os.environ.get("PHASE4_HOME"),
                    help="state/lock/log directory (default: "
                         "data/processed/phase4, env PHASE4_HOME)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--retry-delay", type=float,
                    default=_env_float("PHASE4_RETRY_DELAY_S", 30.0))
    ap.add_argument("--heartbeat-s", type=float,
                    default=_env_float("PHASE4_HEARTBEAT_S", 60.0))
    ap.add_argument("--guard-ac-wait", type=float,
                    default=_env_float("PHASE4_AC_WAIT_S", 600.0))
    ap.add_argument("--guard-ac-poll", type=float,
                    default=_env_float("PHASE4_AC_POLL_S", 60.0))
    ap.add_argument("--guard-mem-wait", type=float,
                    default=_env_float("PHASE4_MEM_WAIT_S", 1800.0))
    ap.add_argument("--guard-mem-step", type=float,
                    default=_env_float("PHASE4_MEM_STEP_S", 300.0))
    ap.add_argument("--kill-grace", type=float,
                    default=_env_float("PHASE4_KILL_GRACE_S", 5.0))
    ap.add_argument("--total-cap-min", type=float,
                    default=_env_float("PHASE4_TOTAL_CAP_MIN", 450.0))
    ap.add_argument("--state-for-launch", default=None)
    ap.add_argument("--integrity", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--lock-check", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--conflicts", action="store_true", help=argparse.SUPPRESS)
    return ap.parse_args(argv)


def lock_check(home, plan):
    """Exit 3 if the driver lock is held by a running driver, 0 if free.  Only
    the authoritative flock is touched -- no marker, no state, nothing created
    beyond the lock file itself (which the driver uses anyway)."""
    home.mkdir(parents=True, exist_ok=True)
    lf = home / LOCK_FILE
    fh = open(lf, "a+")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        if e.errno in (errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK):
            print(f"LOCK HELD: {lf} is locked by a running Phase 4 driver "
                  f"-> refusing to launch a second one")
            fh.close()
            return 3
        raise
    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    fh.close()
    print(f"LOCK FREE: {lf} (no Phase 4 driver is running)")
    return 0


def main(argv=None):
    args = parse_args(argv)
    home = Path(args.home).expanduser() if args.home else DEFAULT_HOME
    home = home.resolve()
    plan = PLANS[args.plan]()
    if args.plan_file:
        with open(args.plan_file) as fh:
            plan = json.load(fh)
    if args.lock_check:
        return lock_check(home, args.plan)
    if args.conflicts:
        pids = guards.conflicting_processes(CONFLICT_PATTERN)
        if pids is None:
            print(f"UNGUARDED: pgrep unavailable -> conflict check skipped "
                  f"(pattern '{CONFLICT_PATTERN}')")
            return 0
        if pids:
            print(" ".join(str(p) for p in pids))
            return 3
        print("")
        return 0
    if args.integrity:
        return run_integrity(home, args.plan, args.state_for_launch)
    if args.dry_run:
        print_plan(plan, home, args, load_state(home, args.plan))
        return 0
    home.mkdir(parents=True, exist_ok=True)
    return run_driver(args, plan, home)


if __name__ == "__main__":
    sys.exit(main())