#!/usr/bin/env python3
"""scripts/phase3_driver.py -- Phase 3 overnight driver (task A7).

PRE-REGISTERED BEHAVIOR (this docstring was written before the first run of
the driver; PHASE3_OVERNIGHT.md lines 219-242 is the spec; every deviation
from that section is listed in docs/tasks/phase3-overnight/
PHASE3_A7_TEST_OUTPUT.txt and mirrored here):

  STAGES (order and budgets fixed by the spec; total = 450 min = 7.5 h):

    S1  GB1 scoring, then the two-sequence subset       100 min   A4 gates
        step score400_assayed:
          {root}/venv/bin/python3 {root}/scripts/154_gb1_score_backgrounds.py
              --sequence assayed --out-dir {home}/gb1
        step score_first20_project  (frozen A7 first-20 of the draw order,
          run into a separate dir per 154's decision S1):
          {root}/venv/bin/python3 {root}/scripts/154_gb1_score_backgrounds.py
              --sequence project --out-dir {home}/gb1_project --limit-roster 20
        precheck (A4 gates): {home}/gb1/sequences.csv and roster_v2.csv exist.

    S2  RBD scoring                                       150 min   A5 gates
        precheck (A5 gates): {home}/rbd/e_T.csv and roster_v1.csv exist.
        step gate_gr5 (GATE step -- never retried; script 156's docstring
          says G-R5 is "re-run by the A7 driver before the stage"):
          {root}/venv/bin/python3 {root}/scripts/156_rbd_score_backgrounds.py
              --g-r5
        step score100_rbd:
          {root}/venv/bin/python3 {root}/scripts/156_rbd_score_backgrounds.py

    S3  analyses                                          75 min    S1/S2 outputs
        step gb1_analysis -- runs ONLY if the GB1 coverage rule is reached,
          otherwise logged and skipped:
          {root}/venv/bin/python3 {root}/scripts/155_gb1_regime_analysis.py
              --mode full
        step rbd_analysis -- same policy for RBD:
          {root}/venv/bin/python3 {root}/scripts/157_rbd_regime_analysis.py
              --mode full
        COVERAGE RULE (interpretation, floors quoted from the scripts, no new
        threshold): GB1 = wt_arm.csv present AND every roster_v2 background
        has a bg file with >= 95% of its 54 eligible positions (script 155's
        frozen gate G-4); RBD = wt_arm.csv present AND every roster_v1
        background has a bg file with >= 95% of the 201 construct sites
        (script 156's frozen gate G-R4 / 155's analogue). All roster
        backgrounds must be present.

    S4  multidms on RBD                                   120 min   A6 gates
        precheck: {root}/venv_multidms/bin/python exists (A6b's isolated env;
          S4 runs 158 with venv_multidms, NEVER venv/bin/python3).
        step multidms_full:
          {root}/venv_multidms/bin/python {root}/scripts/158_multidms_rbd.py
              --mode full

    S5  integrity pass                                     5 min    none
        step integrity (the driver re-invokes ITSELF in --integrity mode so
        the same timeout/signal/retry machinery applies):
          {python} {driver} --integrity --home {home}
        Checks: bg file counts vs rosters, manifests present, sha256 of every
        staged script listed in STATE_FOR_LAUNCH.md, final driver_state.json.
        STATE_FOR_LAUNCH.md absent -> logged and skipped (it does not exist
        yet at build time; it is written before launch).

  FAILURE POLICY (spec): a stage that times out, is skipped by a guard, is
  skipped for a missing dependency, or hits a gate failure is LOGGED and the
  driver CONTINUES to the next stage.  Nothing scientific is inferred here.

  RETRY: up to 3 attempts per step (initial + 2 retries) after
  --retry-delay seconds (default 30) on a nonzero exit OTHER THAN 3.
  Exit code 3 = the stage script's own gate failure -> NEVER retried.
  GATE steps (gate_gr5) are never retried on any nonzero exit.
  A timeout is NOT retried (it is its own outcome in the spec): the child
  PROCESS GROUP gets TERM, --kill-grace (default 5 s) of grace, then SIGKILL.

  LOCK: mkdir {home}/.driver.lock (atomic) + driver.pid inside.  If the lock
  exists and its PID is alive -> refuse to start (printed message, exit 2).
  If the PID is dead (or driver.pid is missing) -> clear the stale lock with
  a printed message and continue.  After the lock is taken, refuse (and
  release it) if any process other than this one and its ancestors matches
  'phase3_driver|124_phase2'.

  STATE: {home}/driver_state.json written atomically at every transition and
  every --heartbeat-s seconds (default 60) during a running stage;
  {home}/driver.log gets the same transitions plus all guard readings.
  On relaunch, steps already recorded `completed` are skipped (resume);
  stages whose steps are all completed are therefore skipped entirely;
  failed/guard-skipped/dependency-skipped stages are re-evaluated.

  SIGNALS: SIGTERM/SIGINT -> forward TERM to the child process group, grace,
  SIGKILL, write state, remove the lock, exit 143.

  --dry-run prints the full plan (commands, budgets, guards, resume info)
  and runs NOTHING: no lock, no state, no directories, no stages.

  HOME: --home / PHASE3_HOME redirect every state/lock/log/precheck path
  (production default: {root}/data/processed/phase3).  Tests always redirect
  so they never touch the real outputs.  Note: the production plan's stage
  commands also embed {home}, so a redirected home redirects the scorers'
  --out-dir too.

LIMITATIONS (AGENTS section 6, also printed by --dry-run and at exit):
  * guards read macOS tools (pmset/memory_pressure/sysctl/df); a missing tool
    is logged UNGUARDED and passes -- guards cannot detect what they cannot
    read, and a passing guard is a point-in-time reading only.
  * the A4/A5/A6 "gates" here are artifact existence prechecks; the real
    gates are the stage scripts' own exit-3 checks (sha pins, per-file
    integrity), which the driver does not duplicate or override.
  * S5's sha256 parser accepts any line carrying a 64-hex digest and a
    scripts/...py path because STATE_FOR_LAUNCH.md's exact format does not
    exist yet; session 3b re-verifies (its task C0).
  * stage budgets cover attempts and retry sleeps; guard wait windows happen
    before the stage timer starts; the global cap is checked at stage start.
  * driver exit code 0 means "the run finished and the per-stage record is
    in driver_state.json" -- NOT that every stage succeeded.
"""

from __future__ import annotations

import argparse
import csv
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

from scripts.lib import phase3_guards as guards  # noqa: E402

DEFAULT_HOME = ROOT / "data" / "processed" / "phase3"
DEFAULT_STATE_FOR_LAUNCH = (ROOT / "docs" / "tasks" / "phase3-overnight" /
                            "STATE_FOR_LAUNCH.md")

LOCK_DIRNAME = ".driver.lock"
PID_FILENAME = "driver.pid"
STATE_FILENAME = "driver_state.json"
LOG_FILENAME = "driver.log"

# Term flag shared with the signal handler; every wait loop polls it.
TERM = {"flag": False}


def _now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def log_ts():
    return _now_iso()


class Shutdown(Exception):
    pass


# ------------------------------------------------------------- production plan
def production_plan():
    """The fixed A7 stage table. Commands use {root} {home} {python} {driver}."""
    py = "{root}/venv/bin/python3"
    multidms_py = "{root}/venv_multidms/bin/python"
    return {
        "name": "phase3-overnight-production",
        "stages": [
            {
                "id": "S1",
                "label": "GB1 scoring (scripts/154) + first-20 two-sequence subset",
                "budget_s": 100 * 60,
                "guard": True,
                "precheck": {"kind": "files",
                             "label": "A4 gates (inputs written by script 160)",
                             "paths": ["{home}/gb1/sequences.csv",
                                       "{home}/gb1/roster_v2.csv"]},
                "steps": [
                    {"name": "score400_assayed",
                     "cmd": [py, "{root}/scripts/154_gb1_score_backgrounds.py",
                             "--sequence", "assayed",
                             "--out-dir", "{home}/gb1"]},
                    {"name": "score_first20_project",
                     "cmd": [py, "{root}/scripts/154_gb1_score_backgrounds.py",
                             "--sequence", "project",
                             "--out-dir", "{home}/gb1_project",
                             "--limit-roster", "20"]},
                ],
            },
            {
                "id": "S2",
                "label": "RBD scoring (scripts/156) with G-R5 pre-stage gate",
                "budget_s": 150 * 60,
                "guard": True,
                "precheck": {"kind": "files",
                             "label": "A5 gates (inputs written by scripts 163/164)",
                             "paths": ["{home}/rbd/e_T.csv",
                                       "{home}/rbd/roster_v1.csv"]},
                "steps": [
                    {"name": "gate_gr5", "gate": True,
                     "cmd": [py, "{root}/scripts/156_rbd_score_backgrounds.py",
                             "--g-r5"]},
                    {"name": "score100_rbd",
                     "cmd": [py, "{root}/scripts/156_rbd_score_backgrounds.py",
                             "--out-dir", "{home}/rbd"]},
                ],
            },
            {
                "id": "S3",
                "label": "analyses: GB1 (155 --mode full), RBD (157 --mode full)",
                "budget_s": 75 * 60,
                "guard": True,
                "steps": [
                    {"name": "gb1_analysis",
                     "requires": {"kind": "coverage", "module": "gb1"},
                     "cmd": [py, "{root}/scripts/155_gb1_regime_analysis.py",
                             "--mode", "full"]},
                    {"name": "rbd_analysis",
                     "requires": {"kind": "coverage", "module": "rbd"},
                     "cmd": [py, "{root}/scripts/157_rbd_regime_analysis.py",
                             "--mode", "full"]},
                ],
            },
            {
                "id": "S4",
                "label": "multidms on RBD (scripts/158) in venv_multidms",
                "budget_s": 120 * 60,
                "guard": True,
                "precheck": {"kind": "files",
                             "label": "A6 gates (isolated env from A6b)",
                             "paths": ["{root}/venv_multidms/bin/python"]},
                "steps": [
                    {"name": "multidms_full",
                     "cmd": [multidms_py,
                             "{root}/scripts/158_multidms_rbd.py",
                             "--mode", "full"]},
                ],
            },
            {
                "id": "S5",
                "label": "integrity pass: counts, manifests, sha256 vs STATE_FOR_LAUNCH.md",
                "budget_s": 5 * 60,
                "guard": True,
                "steps": [
                    {"name": "integrity",
                     "cmd": ["{python}", "{driver}", "--integrity",
                             "--home", "{home}"]},
                ],
            },
        ],
    }


# ------------------------------------------------------------------- argparse
def _env_float(name, default):
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError:
        print(f"WARNING: {name}={raw!r} not a number; using {default}",
              file=sys.stderr)
        return default


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description="Phase 3 overnight driver (task A7). See module docstring.")
    ap.add_argument("--home", default=os.environ.get("PHASE3_HOME"),
                    help="state/lock/log directory (default: "
                         "data/processed/phase3, env PHASE3_HOME)")
    ap.add_argument("--plan", default=os.environ.get("PHASE3_PLAN"),
                    help="JSON plan file overriding the built-in production plan")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the full plan; run nothing; create nothing")
    ap.add_argument("--force", action="store_true",
                    help="override failed guards for every stage (logged)")
    ap.add_argument("--retry-delay", type=float,
                    default=_env_float("PHASE3_RETRY_DELAY_S", 30.0),
                    help="seconds between retries (default 30; tests use less)")
    ap.add_argument("--heartbeat-s", type=float,
                    default=_env_float("PHASE3_HEARTBEAT_S", 60.0),
                    help="state+log heartbeat during a running stage "
                         "(default 60; tests use less)")
    ap.add_argument("--guard-ac-wait", type=float,
                    default=_env_float("PHASE3_AC_WAIT_S", 600.0),
                    help="AC/battery wait window seconds (spec: 10 min)")
    ap.add_argument("--guard-ac-poll", type=float,
                    default=_env_float("PHASE3_AC_POLL_S", 60.0),
                    help="AC/battery poll interval seconds (spec silent)")
    ap.add_argument("--guard-mem-wait", type=float,
                    default=_env_float("PHASE3_MEM_WAIT_S", 1800.0),
                    help="swap/free-mem wait window seconds (spec: 30 min)")
    ap.add_argument("--guard-mem-step", type=float,
                    default=_env_float("PHASE3_MEM_STEP_S", 300.0),
                    help="swap/free-mem re-check step seconds (spec: 5 min)")
    ap.add_argument("--kill-grace", type=float,
                    default=_env_float("PHASE3_KILL_GRACE_S", 5.0),
                    help="seconds between TERM and SIGKILL of the child group")
    ap.add_argument("--total-cap-min", type=float,
                    default=_env_float("PHASE3_TOTAL_CAP_MIN", 450.0),
                    help="global wall-clock cap in minutes (spec: ~7.5 h)")
    ap.add_argument("--state-for-launch", default=None,
                    help="STATE_FOR_LAUNCH.md path for the integrity pass")
    ap.add_argument("--integrity", action="store_true", help=argparse.SUPPRESS)
    return ap.parse_args(argv)


# ------------------------------------------------------------------- expand
def make_expander(home):
    reps = {
        "{root}": str(ROOT),
        "{home}": str(home),
        "{python}": sys.executable,
        "{driver}": str(Path(__file__).resolve()),
    }

    def expand(s):
        for k, v in reps.items():
            s = s.replace(k, v)
        return s
    return expand


# ------------------------------------------------------------------ logger
class Logger:
    def __init__(self, home):
        self.path = home / LOG_FILENAME
        self.fh = open(self.path, "a", buffering=1)

    def __call__(self, msg):
        line = f"{log_ts()} {msg}"
        print(line, flush=True)
        self.fh.write(line + "\n")
        self.fh.flush()

    def close(self):
        try:
            self.fh.close()
        except OSError:
            pass


# -------------------------------------------------------------------- state
def load_state(home):
    p = home / STATE_FILENAME
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def new_state(dry_run=False):
    return {
        "version": 1,
        "dry_run": dry_run,
        "driver_pid": os.getpid(),
        "status": "running",
        "started": _now_iso(),
        "updated": _now_iso(),
        "finished": None,
        "current_stage": None,
        "current_stage_started": None,
        "stages": {},
    }


def save_state(home, state):
    state["updated"] = _now_iso()
    p = home / STATE_FILENAME
    tmp = p.with_name("." + p.name + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, p)


def stage_rec(state, sid):
    return state["stages"].setdefault(sid, {
        "status": "pending", "start": None, "end": None,
        "note": None, "steps": {},
    })


def step_rec(state, sid, name):
    return stage_rec(state, sid)["steps"].setdefault(name, {
        "status": "pending", "attempts": 0, "exit_code": None,
        "start": None, "end": None,
    })


# --------------------------------------------------------------------- lock
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


def acquire_lock(home, print_fn=print):
    """Atomic mkdir lock. Returns Path or None (refusal already printed)."""
    lock = home / LOCK_DIRNAME
    pidf = lock / PID_FILENAME
    for _ in range(3):
        try:
            lock.mkdir()
        except FileExistsError:
            pid = None
            try:
                pid = int(pidf.read_text().strip())
            except (OSError, ValueError):
                pid = None
            if pid is not None and pid == os.getpid():
                return lock  # re-entrant: we already own it
            if pid is not None and _pid_alive(pid):
                print_fn(f"REFUSING TO START: driver lock {lock} is held by "
                         f"PID {pid} (alive). Stop it with: "
                         f"kill $(cat {pidf})")
                return None
            why = (f"driver.pid={pid} is not alive" if pid is not None
                   else "driver.pid is missing or unreadable")
            print_fn(f"STALE LOCK CLEARED: {lock} ({why}) -> removing it and "
                     f"continuing")
            shutil.rmtree(lock, ignore_errors=True)
            continue
        pidf.write_text(str(os.getpid()) + "\n")
        return lock
    print_fn(f"REFUSING TO START: could not take the lock {lock} "
             f"(kept being recreated -- another driver started?)")
    return None


def release_lock(lock):
    if lock is None or not lock.exists():
        return
    try:
        pid = int((lock / PID_FILENAME).read_text().strip())
    except (OSError, ValueError):
        pid = None
    if pid is not None and pid != os.getpid():
        return  # not ours; do not touch
    shutil.rmtree(lock, ignore_errors=True)


# --------------------------------------------------------------- requires
def _count_bg_rows(path):
    """Data rows of a scorer bg file (header + 19 rows per position)."""
    lines = 0
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(1 << 20)
            if not chunk:
                break
            lines += chunk.count(b"\n")
    return max(lines - 1, 0)


def check_coverage(home, module):
    """Artifact-based coverage rule for S3 dependencies.

    Floors are quoted from the scripts (155 G-4, 156 G-R4): 0.95 of the
    eligible positions, per background, over the WHOLE roster.
    """
    if module == "gb1":
        roster = home / "gb1" / "roster_v2.csv"
        out = home / "gb1"
        eligible = 54          # frozen A2: positions 2..56 minus own (155 G-4)
        denom_note = "54 eligible positions (155 G-4)"
    elif module == "rbd":
        roster = home / "rbd" / "roster_v1.csv"
        out = home / "rbd"
        eligible = 201         # construct sites (156 G-R4)
        denom_note = "201 construct sites (156 G-R4)"
    else:
        return False, f"unknown coverage module {module!r} -> dependency NOT met"
    if not roster.exists():
        return False, f"roster {roster} missing"
    if not (out / "wt_arm.csv").exists():
        return False, f"wt_arm.csv missing in {out}"
    ids = []
    with open(roster, newline="") as fh:
        for row in csv.DictReader(fh):
            bid = row.get("background_id")
            if bid:
                ids.append(bid)
    if not ids:
        return False, f"roster {roster} has no background_id rows"
    bad, min_frac, min_id = [], 1.0, None
    for bid in ids:
        f = out / f"bg_{bid}.csv"
        if not f.exists():
            bad.append(f"{bid}: file missing")
            continue
        rows = _count_bg_rows(f)
        if rows % 19 != 0:
            bad.append(f"{bid}: {rows} rows not divisible by 19")
            continue
        frac = (rows / 19.0) / eligible
        if frac < min_frac:
            min_frac, min_id = frac, bid
        if frac < 0.95:
            bad.append(f"{bid}: {rows // 19}/{eligible} = {frac:.3f} < 0.95")
    if bad:
        return False, (f"coverage {module}: FAIL {len(bad)}/{len(ids)} "
                       f"backgrounds below the 0.95 floor of {denom_note}; "
                       f"first offenders: {bad[:3]}")
    return True, (f"coverage {module}: PASS {len(ids)}/{len(ids)} roster "
                  f"backgrounds present, min coverage {min_id} "
                  f"{min_frac:.3f} >= 0.95 of {denom_note}")


def check_requires(req, home, log):
    kind = req.get("kind")
    expand = make_expander(home)
    if kind == "files":
        missing = [expand(p) for p in req.get("paths", [])
                   if not os.path.exists(expand(p))]
        if missing:
            return False, f"required files missing: {missing}"
        return True, "required files present"
    if kind == "coverage":
        return check_coverage(home, req.get("module"))
    log(f"UNKNOWN requires kind {kind!r} -> treating dependency as NOT met")
    return False, f"unknown requires kind {kind!r}"


def check_precheck(pc, home):
    kind = pc.get("kind")
    if kind != "files":
        return False, f"unknown precheck kind {kind!r}"
    expand = make_expander(home)
    missing = [expand(p) for p in pc.get("paths", [])
               if not os.path.exists(expand(p))]
    if missing:
        return False, f"missing required input(s): {', '.join(missing)}"
    return True, "all required inputs present"


# ------------------------------------------------------------------ integrity
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
PY_TOKEN = re.compile(r"[\w./-]+\.py")


def parse_state_for_launch(text):
    """Best-effort (path, sha256) pairs for staged scripts.

    STATE_FOR_LAUNCH.md does not exist yet, so the format is not fixed;
    any line carrying a 64-hex digest and a scripts/*.py-looking token is
    accepted (disclosed).  Only paths under scripts/ are verified.
    """
    pairs = []
    for line in text.splitlines():
        m_hex = HEX64.search(line)
        if not m_hex:
            continue
        cands = PY_TOKEN.findall(line)
        if not cands:
            continue
        path = None
        for c in cands:
            if "scripts/" in c or re.match(r"^\d{2,3}_", Path(c).name):
                path = c
                break
        if path is None:
            path = cands[0]
        if not path.startswith("scripts/"):
            path = "scripts/" + path.lstrip("./")
        pairs.append((path, m_hex.group(0)))
    return pairs


def run_integrity(home, state_for_launch):
    """S5's pass. Prints INTEGRITY lines; exit 3 on sha256 mismatch (gate)."""
    findings = []
    fail = False

    def f(msg):
        findings.append(msg)

    # 1. file counts + manifests (discrepancies are findings, not failures)
    specs = [("gb1 (assayed, 400 expected from roster)", "gb1", "gb1/roster_v2.csv", None),
             ("gb1_project (two-seq subset, 20 from frozen A7)", "gb1_project", "gb1/roster_v2.csv", 20),
             ("rbd (100 expected from roster)", "rbd", "rbd/roster_v1.csv", None)]
    for label, out_name, roster_rel, fixed in specs:
        out = home / out_name
        if not out.is_dir():
            f(f"{label}: out-dir {out} does not exist")
            continue
        n = len(list(out.glob("bg_*.csv")))
        expected = fixed
        if expected is None:
            rp = home / roster_rel
            if rp.exists():
                with open(rp, newline="") as fh:
                    expected = sum(1 for r in csv.DictReader(fh)
                                   if r.get("background_id"))
            else:
                f(f"{label}: roster {rp} absent -> expected count unknown "
                  f"(count check skipped); {n} bg_*.csv present")
        if expected is not None:
            verdict = "OK" if n == expected else "MISMATCH (finding)"
            f(f"{label}: {n} bg_*.csv present, {expected} expected -> {verdict}")
        man = out / "manifest.csv"
        wt = out / "wt_arm.csv"
        f(f"{label}: manifest.csv {'present' if man.exists() else 'ABSENT'}; "
          f"wt_arm.csv {'present' if wt.exists() else 'ABSENT'}")

    # 2. sha256 of every staged script vs STATE_FOR_LAUNCH.md
    sfl = Path(state_for_launch) if state_for_launch else DEFAULT_STATE_FOR_LAUNCH
    if not sfl.exists():
        f(f"STATE_FOR_LAUNCH.md not found at {sfl} -> sha256 verification "
          f"SKIPPED (the file is written before launch; session 3b re-verifies)")
    else:
        pairs = parse_state_for_launch(sfl.read_text())
        if not pairs:
            f(f"{sfl}: no (sha256, scripts/*.py) lines recognised -> "
              f"sha256 verification SKIPPED (parser limitation; 3b re-verifies)")
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

    # 3. final driver_state.json
    st = home / STATE_FILENAME
    if st.exists():
        try:
            data = json.loads(st.read_text())
            summary = ", ".join(f"{k}={v.get('status')}"
                                for k, v in sorted(data.get("stages", {}).items()))
            f(f"driver_state.json present ({st}); stage statuses: "
              f"{summary or 'none'}")
        except (OSError, json.JSONDecodeError) as e:
            fail = True
            f(f"driver_state.json present but UNPARSEABLE: {e} -> FLAG")
    else:
        f(f"driver_state.json absent at {st} (the parent driver writes it)")

    for line in findings:
        print(f"INTEGRITY: {line}")
    print(f"INTEGRITY: RESULT {'FAIL' if fail else 'PASS'} "
          f"({len(findings)} findings)")
    return 3 if fail else 0


# ------------------------------------------------------------------ dry-run
def print_plan(plan, home, args, state):
    stages = plan.get("stages", [])
    total = sum(s.get("budget_s", 300) for s in stages)
    print("PHASE3 DRY RUN -- nothing is executed; no lock, no state, no "
          "directories are created by this mode.")
    print(f"plan: {plan.get('name', '<custom>')}  "
          f"({len(stages)} stages; stage budgets total {total / 60:.0f} min; "
          f"global cap {args.total_cap_min:.0f} min)")
    print(f"home (state/lock/log/prechecks): {home}")
    print(f"guards before every stage: AC power + battery >= 30% "
          f"(wait <= {args.guard_ac_wait:.0f} s, poll {args.guard_ac_poll:.0f} s); "
          f"swap < 3.0 GB + free memory >= 25% (wait <= {args.guard_mem_wait:.0f} s "
          f"in {args.guard_mem_step:.0f} s steps); disk free >= 5 GiB (no wait). "
          f"Missing tool -> UNGUARDED (logged). --force overrides (logged).")
    print(f"retry: up to 3 attempts per step, {args.retry_delay:.0f} s apart, "
          f"on nonzero exit != 3; exit 3 = gate failure, NEVER retried; gate "
          f"steps never retried; timeouts not retried (TERM, then SIGKILL of "
          f"the child process group after {args.kill_grace:.0f} s grace).")
    print(f"lock: mkdir {home}/{LOCK_DIRNAME} + {PID_FILENAME}; a stale lock "
          f"(dead PID) is cleared with a printed message; a live lock or a "
          f"conflicting process matching 'phase3_driver|124_phase2' (excluding "
          f"this process and its ancestors) refuses the start.")
    print("resume: stages/steps recorded `completed` in driver_state.json "
          "are skipped on relaunch.")
    for st in stages:
        budget = st.get("budget_s", 300)
        print(f"\n{st.get('id')}  budget {budget / 60:.0f} min  "
              f"(guard: {'before stage' if st.get('guard', True) else 'none'})  "
              f"{st.get('label', '')}")
        pc = st.get("precheck")
        if pc:
            expand = make_expander(home)
            print(f"    precheck [{pc.get('label', '')}]: "
                  + ", ".join(expand(p) for p in pc.get("paths", [])))
        for step in st.get("steps", []):
            tags = []
            if step.get("gate"):
                tags.append("GATE (never retried)")
            req = step.get("requires")
            if req:
                tags.append(f"runs only if {req.get('kind')} "
                            f"{req.get('module', '')} requirement met "
                            "-- else logged and skipped")
            tagstr = ("  [" + "; ".join(tags) + "]") if tags else ""
            expand = make_expander(home)
            print(f"    step {step.get('name')}{tagstr}:")
            print(f"      " + " ".join(expand(c) for c in step.get("cmd", [])))
    if state:
        print("\nresume info from existing driver_state.json:")
        for sid, rec in sorted(state.get("stages", {}).items()):
            steps = rec.get("steps", {})
            all_done = steps and all(s.get("status") == "completed"
                                     for s in steps.values())
            if all_done:
                print(f"  {sid}: completed -> would be SKIPPED on relaunch")
            else:
                detail = ", ".join(f"{k}={v.get('status')}"
                                   for k, v in sorted(steps.items()))
                print(f"  {sid}: status {rec.get('status')} "
                      f"({detail or 'no steps run'}) -> would be re-evaluated")
    else:
        print("\nresume info: no existing driver_state.json (fresh start)")
    print("\nLIMITATIONS (see module docstring): guards degrade to UNGUARDED "
          "when a macOS tool is missing; driver exit 0 = run finished, not "
          "every stage succeeded; per-stage statuses are in driver_state.json.")


# ------------------------------------------------------------- child handling
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
    """Poll the child until exit/timeout/signal. Returns (kind, rc)."""
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


# ---------------------------------------------------------------- stage runner
def run_stage(stage, ctx):
    """Run one stage per the spec's policy. Records everything in state."""
    sid = stage.get("id", "?")
    log, state, home, args = ctx["log"], ctx["state"], ctx["home"], ctx["args"]
    expand = make_expander(home)
    budget = float(stage.get("budget_s", 300))
    steps = stage.get("steps", [])
    rec = stage_rec(state, sid)

    # resume: nothing pending -> skip the stage entirely (before any guard)
    pending = [s for s in steps
               if step_rec(state, sid, s.get("name", "?")).get("status")
               != "completed"]
    if steps and not pending:
        log(f"{sid}: all {len(steps)} step(s) already completed -> skipped "
            f"(resume)")
        if rec.get("status") != "completed":
            rec["status"] = "completed"
            rec["note"] = "resume: all steps previously completed"
            save_state(home, state)
        return
    log(f"{sid}: {len(pending)}/{len(steps)} step(s) pending; "
        f"budget {budget:.0f} s")

    # guards before every stage (spec); --force overrides, logged
    if stage.get("guard", True):
        ok, msgs = guards.evaluate_guards(
            force=args.force,
            ac_wait_s=args.guard_ac_wait, ac_poll_s=args.guard_ac_poll,
            mem_wait_s=args.guard_mem_wait, mem_step_s=args.guard_mem_step,
            log=lambda m: log(f"[{sid}] guard: {m}"),
            stop=lambda: TERM["flag"])
        if TERM["flag"]:
            raise Shutdown("signal during guard wait")
        if not ok:
            rec["status"] = "skipped_guard"
            rec["end"] = _now_iso()
            rec["note"] = "guards failed after their wait windows (readings logged above)"
            save_state(home, state)
            log(f"{sid}: SKIPPED (guard failure) -> continuing to next stage")
            return
        if args.force and any("OVERRIDDEN" in m or "--force" in m
                              for m in msgs):
            log(f"[{sid}] guards FAILED but --force given -> stage FORCED "
                f"(logged per spec)")

    # pre-stage gate: required artifacts must exist (interpretation, see header)
    pc = stage.get("precheck")
    if pc:
        ok, why = check_precheck(pc, home)
        if not ok:
            rec["status"] = "gate_failed"
            rec["end"] = _now_iso()
            rec["note"] = f"precheck failed: {why}"
            save_state(home, state)
            log(f"{sid}: GATE FAILED precheck ({pc.get('label', '')}): {why} "
                f"-> skipping stage, continuing (exit-3 policy, no retry)")
            return
        log(f"{sid}: precheck OK ({pc.get('label', '')}): {why}")

    # stage timer starts after guards + precheck (disclosed)
    t0 = time.time()
    deadline = t0 + budget
    rec["status"] = "running"
    rec["start"] = _now_iso()
    rec["end"] = None
    rec["note"] = None
    state["current_stage"] = sid
    state["current_stage_started"] = _now_iso()
    save_state(home, state)
    log(f"{sid}: START budget {budget:.0f} s")

    stage_log = home / f"driver_stage_{sid}.log"

    def on_heartbeat():
        elapsed = time.time() - t0
        save_state(home, state)
        log(f"[{sid}] heartbeat: running {elapsed:.0f} s of {budget:.0f} s "
            f"budget; stage output: {stage_log}")

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
            met, why = check_requires(req, home, log)
            log(f"[{sid}] dependency check {name}: "
                f"{'dependency met ->' if met else 'dependency NOT met ->'} {why}")
            if not met:
                srec["status"] = "skipped_dependency"
                srec["end"] = _now_iso()
                save_state(home, state)
                log(f"{sid}.{name}: dependency NOT met -> step logged and "
                    f"skipped; continuing")
                continue

        cmd = [expand(c) for c in step.get("cmd", [])]
        max_attempts = 1 if step.get("gate") else 3
        attempt = 0
        while True:
            attempt += 1
            if time.time() >= deadline:
                rec["status"] = "timeout"
                rec["end"] = _now_iso()
                rec["note"] = (f"stage budget {budget:.0f} s exhausted before "
                               f"step {name} finished")
                state["current_stage"] = None
                state["current_stage_started"] = None
                save_state(home, state)
                log(f"{sid}: TIMEOUT (stage budget {budget:.0f} s) -> "
                    f"continuing to next stage")
                return
            srec["attempts"] = attempt
            srec["start"] = srec.get("start") or _now_iso()
            save_state(home, state)
            log(f"{sid}.{name}: attempt {attempt}/{max_attempts}: "
                f"executing: {' '.join(cmd)}")
            with open(stage_log, "ab") as fh:
                try:
                    p = subprocess.Popen(
                        cmd, cwd=str(ROOT), stdout=fh,
                        stderr=subprocess.STDOUT,
                        start_new_session=True, env=dict(os.environ))
                except OSError as e:
                    srec["status"] = "failed"
                    srec["exit_code"] = None
                    srec["end"] = _now_iso()
                    rec["status"] = "failed"
                    rec["end"] = _now_iso()
                    rec["note"] = f"could not spawn {cmd[0]!r}: {e}"
                    state["current_stage"] = None
                    state["current_stage_started"] = None
                    save_state(home, state)
                    log(f"{sid}.{name}: SPAWN FAILED: {e} -> stage failed, "
                        f"continuing")
                    return
            kind, rc = supervise(p, deadline, args.heartbeat_s, on_heartbeat)

            if kind == "term":
                kill_child_group(p, args.kill_grace, log,
                                 f"{sid}.{name} TERM")
                raise Shutdown("signal during stage")
            if kind == "timeout":
                kill_child_group(p, args.kill_grace, log,
                                 f"{sid}.{name} TIMEOUT")
                srec["status"] = "killed_timeout"
                srec["exit_code"] = None
                srec["end"] = _now_iso()
                rec["status"] = "timeout"
                rec["end"] = _now_iso()
                rec["note"] = (f"step {name} killed at the stage budget; "
                               f"child process group terminated")
                state["current_stage"] = None
                state["current_stage_started"] = None
                save_state(home, state)
                log(f"{sid}: TIMEOUT after {budget:.0f} s -> child process "
                    f"group killed; continuing to next stage")
                return

            srec["exit_code"] = rc
            srec["end"] = _now_iso()
            save_state(home, state)
            if rc == 0:
                srec["status"] = "completed"
                save_state(home, state)
                log(f"{sid}.{name}: completed (exit 0, attempt {attempt})")
                break
            if rc == 3 or step.get("gate"):
                srec["status"] = "gate_failed"
                reason = ("exit 3 = the script's own gate failure (NEVER "
                          "retried, per spec)" if rc == 3
                          else f"gate step nonzero exit {rc} (gate steps are "
                               f"never retried)")
                rec["status"] = "gate_failed"
                rec["end"] = _now_iso()
                rec["note"] = f"step {name}: {reason}"
                state["current_stage"] = None
                state["current_stage_started"] = None
                save_state(home, state)
                log(f"{sid}.{name}: {reason} -> stage gate failure logged, "
                    f"continuing to next stage")
                return
            # retryable crash (nonzero, not 3, not a gate step)
            if attempt >= max_attempts:
                srec["status"] = "failed"
                rec["status"] = "failed"
                rec["end"] = _now_iso()
                rec["note"] = (f"step {name} crashed with exit {rc} after "
                               f"{attempt} attempts (3 max)")
                state["current_stage"] = None
                state["current_stage_started"] = None
                save_state(home, state)
                log(f"{sid}.{name}: exit {rc}; {attempt}/{max_attempts} "
                    f"attempts exhausted -> stage failed, continuing")
                return
            log(f"{sid}.{name}: exit {rc} (nonzero, not 3, not a gate step) "
                f"-> retrying in {args.retry_delay:.0f} s "
                f"(attempt {attempt + 1}/{max_attempts})")
            interruptible_sleep(args.retry_delay, "retry delay")

    # all steps processed
    statuses = [step_rec(state, sid, s.get("name", "?")).get("status")
                for s in steps]
    if statuses and all(s == "completed" for s in statuses):
        rec["status"] = "completed"
        rec["note"] = None
    elif statuses and all(s == "skipped_dependency" for s in statuses):
        rec["status"] = "skipped_dependency"
        rec["note"] = "no step's dependency was met (logged above)"
    elif any(s == "skipped_dependency" for s in statuses):
        rec["status"] = "completed"
        rec["note"] = (f"completed with {statuses.count('skipped_dependency')}"
                       f" dependency-skipped step(s) (logged above)")
    else:
        rec["status"] = "completed"
    rec["end"] = _now_iso()
    state["current_stage"] = None
    state["current_stage_started"] = None
    save_state(home, state)
    log(f"{sid}: DONE status={rec['status']}"
        + (f" ({rec['note']})" if rec.get("note") else ""))


# ------------------------------------------------------------------- driver
def terminate_and_cleanup(state, home, lock, log, current_child, args,
                          status="terminated", exit_code=143):
    if current_child is not None:
        kill_child_group(current_child, args.kill_grace, log, "DRIVER TERM")
    state["status"] = status
    state["finished"] = _now_iso()
    state["current_stage"] = None
    for sid, rec in state.get("stages", {}).items():
        if rec.get("status") == "running":
            rec["status"] = "interrupted"
            rec["note"] = "driver received a signal while this stage ran"
    try:
        save_state(home, state)
    except OSError:
        pass
    if log is not None:
        log(f"DRIVER {status.upper()} -> lock released; per-stage record in "
            f"{home / STATE_FILENAME}")
        log.close()
    release_lock(lock)
    return exit_code


def run_driver(args, plan, home):
    lock = acquire_lock(home)
    if lock is None:
        return 2

    # conflicting live processes (spec), after the lock, before anything else
    conflicts = guards.conflicting_processes()
    if conflicts is None:
        print(f"UNGUARDED: pgrep unavailable -> conflicting-process check "
              f"skipped (pattern '{guards.CONFLICT_PATTERN}')")
    elif conflicts:
        release_lock(lock)
        cmds = []
        for pid in conflicts:
            rc, out = guards._run(["ps", "-o", "command=", "-p", str(pid)])
            cmds.append(f"PID {pid}: {out.strip()[:160] or '?'}")
        print(f"REFUSING TO START: conflicting process(es) alive matching "
              f"'{guards.CONFLICT_PATTERN}' (this process and its ancestors "
              f"excluded) -> lock released")
        for c in cmds:
            print(f"  {c}")
        return 2

    log = Logger(home)
    state = load_state(home) or new_state()
    state["driver_pid"] = os.getpid()
    state["status"] = "running"
    state["dry_run"] = False
    if state.get("started") is None:
        state["started"] = _now_iso()
    log(f"DRIVER START pid={os.getpid()} home={home} "
        f"plan={plan.get('name', '<custom>')} force={args.force}")
    for sid, rec in sorted(state.get("stages", {}).items()):
        if rec.get("status") in ("running", "terminated", "interrupted"):
            rec["status"] = "interrupted"
            rec["note"] = "previous driver run ended while this stage ran"
            log(f"{sid}: previous run left status 'interrupted' -> will be "
                f"re-evaluated")
    save_state(home, state)

    signal.signal(signal.SIGTERM, lambda *_: TERM.__setitem__("flag", True))
    signal.signal(signal.SIGINT, lambda *_: TERM.__setitem__("flag", True))

    ctx = {"log": log, "state": state, "home": home, "args": args}
    current = {"child": None}  # kept for the signal path
    exit_code = 0
    t_start = time.time()
    cap_deadline = t_start + args.total_cap_min * 60
    try:
        for stage in plan.get("stages", []):
            if TERM["flag"]:
                raise Shutdown("signal between stages")
            sid = stage.get("id", "?")
            rec = stage_rec(state, sid)
            steps = stage.get("steps", [])
            pending = [s for s in steps
                       if step_rec(state, sid, s.get("name", "?")).get("status")
                       != "completed"]
            if pending and time.time() >= cap_deadline:
                rec["status"] = "skipped_cap"
                rec["end"] = _now_iso()
                rec["note"] = (f"global {args.total_cap_min:.0f}-min cap "
                               f"reached before this stage started")
                save_state(home, state)
                log(f"{sid}: SKIPPED -- global {args.total_cap_min:.0f}-min "
                    f"cap reached")
                continue
            run_stage(stage, ctx)
        state["status"] = "finished"
        state["finished"] = _now_iso()
        state["current_stage"] = None
        save_state(home, state)
        summary = ", ".join(f"{k}={v.get('status')}"
                            for k, v in sorted(state["stages"].items()))
        log(f"DRIVER FINISHED: {summary}")
        log("LIMITATIONS: exit 0 means the run finished, not that every "
            "stage succeeded -- read driver_state.json; guard readings are "
            "point-in-time; UNGUARDED checks prove nothing.")
        log.close()
    except Shutdown as e:
        log(f"DRIVER TERMINATED: {e} -> forwarding TERM to the child, "
            f"releasing the lock, exit 143")
        return terminate_and_cleanup(state, home, lock, log,
                                     current["child"], args)
    except Exception as e:  # unexpected bug: record it, never leave the lock
        log(f"DRIVER ERROR: {type(e).__name__}: {e} -> lock released, exit 1")
        state["status"] = "error"
        state["finished"] = _now_iso()
        for sid, rec in state.get("stages", {}).items():
            if rec.get("status") == "running":
                rec["status"] = "interrupted"
        try:
            save_state(home, state)
        except OSError:
            pass
        log.close()
        release_lock(lock)
        return 1
    finally:
        if not TERM["flag"]:
            release_lock(lock)
    return exit_code


# --------------------------------------------------------------------- main
def main(argv=None):
    args = parse_args(argv)
    home = Path(args.home).expanduser() if args.home else DEFAULT_HOME
    home = home.resolve()

    if args.plan:
        with open(args.plan) as fh:
            plan = json.load(fh)
    else:
        plan = production_plan()

    if args.integrity:
        return run_integrity(home, args.state_for_launch)

    if args.dry_run:
        print_plan(plan, home, args, load_state(home))
        return 0

    home.mkdir(parents=True, exist_ok=True)
    return run_driver(args, plan, home)


if __name__ == "__main__":
    sys.exit(main())
