"""phase3_guards.py -- environment guards for the Phase 3 overnight run (A7).

WHAT IT CHECKS (PHASE3_OVERNIGHT.md A7, lines 219-242):

  * AC power present AND battery charge >= 30%      (window: wait up to 10 min,
                                                     polled; then FAIL)
  * swap used < 3.0 GB AND free memory >= 25%       (window: wait up to 30 min
                                                     in 5-minute steps; then FAIL)
  * disk free >= 5 GiB                              (no wait window in the spec;
                                                     checked immediately)
  * the launcher additionally refuses below 35% free memory
    (LAUNCHER_MEM_FLOOR_PCT), and prints what to quit.

  If `pmset`, `memory_pressure`, `sysctl` or `df` is missing (or their output
  cannot be parsed), the affected check is logged as UNGUARDED and PASSES --
  a missing tool never fails a guard.  Every message says what was read and
  whether it came from the real tool or from a fake override.

TEST HOOKS (environment-variable fakes -- read INSTEAD of the real tool):

  PHASE3_FAKE_AC     0/1 (or no/yes, off/on, false/true) -- AC power state
  PHASE3_FAKE_BATT   percent (e.g. 12)
  PHASE3_FAKE_SWAP   swap used in GB (e.g. 4.5)
  PHASE3_FAKE_MEM    free memory percent (e.g. 10)
  PHASE3_FAKE_DISK_GIB  free disk in GiB (e.g. 1)

  The A7 spec names PHASE3_FAKE_BATT / PHASE3_FAKE_SWAP / PHASE3_FAKE_MEM
  ("environment-variable overrides such as ..."); the AC and disk fakes were
  added so all five guard readings can be tested.  Disclosed in
  docs/tasks/phase3-overnight/PHASE3_A7_TEST_OUTPUT.txt.

WAIT WINDOWS (production defaults; overridable so tests do not sleep for
10/30 minutes -- also disclosed in the test output):

  AC_MIN_BATT_PCT / SWAP_MAX_GB / MEM_MIN_PCT / DISK_MIN_GIB are the spec's
  thresholds and are NOT tunable by flag (only by editing this file).
  The windows (ac_wait_s=600, ac_poll_s=60, mem_wait_s=1800, mem_step_s=300)
  are parameters; drivers pass them from flags/env.

CLI (used by scripts/launch_phase3_overnight.sh, runnable directly):

  venv/bin/python3 scripts/lib/phase3_guards.py --conflicts
      pgrep -f 'phase3_driver|124_phase2', excluding this process and its
      ancestors.  exit 3 + printed pids if any alive, exit 0 if none,
      exit 0 + UNGUARDED notice if pgrep is unavailable.

  venv/bin/python3 scripts/lib/phase3_guards.py --launch-check [--force]
      one immediate reading of every guard with the 35% launcher memory
      floor and NO wait windows; exit 0 if all pass (or unguarded),
      exit 1 with the readings if any fails.

LIMITATIONS (AGENTS section 6):
  * macOS-only tools (pmset/memory_pressure/sysctl); on any other platform
    every check degrades to UNGUARDED and passes -- by design.
  * readings are a single point in time; nothing here predicts the machine
    state minutes later (the driver re-reads before every stage).
  * a fake reading bypasses the real tool entirely; fakes are for tests and
    are printed loudly as FAKE so a faked line can never be mistaken for a
    real one in a log.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------- constants
ROOT = Path(__file__).resolve().parents[2]

AC_MIN_BATT_PCT = 30.0        # spec: charge >= 30%
SWAP_MAX_GB = 3.0             # spec: swap used < 3.0 GB
MEM_MIN_PCT = 25.0            # spec: free memory >= 25%
DISK_MIN_GIB = 5.0            # spec: disk free >= 5 GiB
LAUNCHER_MEM_FLOOR_PCT = 35.0  # spec: launcher refuses below 35% free memory

CONFLICT_PATTERN = "phase3_driver|124_phase2"  # spec's refusal pattern

FAKE_AC = "PHASE3_FAKE_AC"
FAKE_BATT = "PHASE3_FAKE_BATT"
FAKE_SWAP = "PHASE3_FAKE_SWAP"
FAKE_MEM = "PHASE3_FAKE_MEM"
FAKE_DISK = "PHASE3_FAKE_DISK_GIB"


# ------------------------------------------------------------------ helpers
def _run(cmd, timeout=60):
    """Run a read-only command. Returns (returncode_or_None, output_text)."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None, ""
    except (OSError, subprocess.TimeoutExpired):
        return None, ""
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _fake_num(name):
    """Parse a numeric fake env var. Returns (value_or_None, note_or_None)."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return None, None
    try:
        return float(raw), None
    except ValueError:
        return None, (f"{name}={raw!r} is not a number -> ignored "
                      f"(check runs against the real tool)")


def _fake_bool(name):
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return None, None
    v = raw.strip().lower()
    if v in ("0", "no", "off", "false", "n"):
        return False, None
    if v in ("1", "yes", "on", "true", "y"):
        return True, None
    return None, (f"{name}={raw!r} is not a boolean 0/1 -> ignored "
                  f"(check runs against the real tool)")


def _state_ok(state, msg):
    return {"state": state, "msg": msg}


# ------------------------------------------------------------------ readings
def read_ac_batt():
    """-> {"ac": {...}, "batt": {...}} with states ok/fail/unguarded."""
    notes = []
    ac_v = batt_v = ac_src = batt_src = None

    ac_v, n = _fake_bool(FAKE_AC)
    if n:
        notes.append(n)
    if ac_v is not None:
        ac_src = f"FAKE from {FAKE_AC}={os.environ[FAKE_AC]}"
    batt_v, n = _fake_num(FAKE_BATT)
    if n:
        notes.append(n)
    if batt_v is not None:
        batt_src = f"FAKE from {FAKE_BATT}={os.environ[FAKE_BATT]}"

    if ac_v is None or batt_v is None:
        if shutil.which("pmset") is None:
            pass  # unguarded handled below
        else:
            rc, out = _run(["pmset", "-g", "batt"])
            if rc == 0:
                if ac_v is None:
                    if "Now drawing from 'AC Power'" in out:
                        ac_v, ac_src = True, "real: pmset -g batt (AC Power)"
                    elif "Now drawing from 'Battery Power'" in out:
                        ac_v, ac_src = False, "real: pmset -g batt (Battery Power)"
                if batt_v is None:
                    m = re.search(r"(\d+(?:\.\d+)?)%", out)
                    if m:
                        batt_v = float(m.group(1))
                        batt_src = "real: pmset -g batt"

    out = {}
    if ac_v is None:
        out["ac"] = _state_ok(
            "unguarded",
            "AC power: UNKNOWN (pmset missing or output unparsable) "
            "-> UNGUARDED, continuing")
    else:
        ok = bool(ac_v)
        out["ac"] = _state_ok(
            "ok" if ok else "fail",
            f"AC power: {'ON' if ok else 'OFF'} ({ac_src}) "
            f"{'OK (need AC power)' if ok else 'FAIL (need AC power)'}")
    if batt_v is None:
        out["batt"] = _state_ok(
            "unguarded",
            f"battery: UNKNOWN (no reading from pmset; no {FAKE_BATT}) "
            f"-> UNGUARDED, continuing")
    else:
        ok = batt_v >= AC_MIN_BATT_PCT
        out["batt"] = _state_ok(
            "ok" if ok else "fail",
            f"battery: {batt_v:.0f}% ({batt_src}) "
            f"{'OK' if ok else 'FAIL'} (need >= {AC_MIN_BATT_PCT:.0f}%)")
    if notes:
        out["_notes"] = notes
    return out


def read_swap_gb():
    v, src = _fake_num(FAKE_SWAP)
    if v is None:
        if shutil.which("sysctl") is None:
            return _state_ok(
                "unguarded",
                "swap used: UNKNOWN (sysctl missing) -> UNGUARDED, continuing")
        rc, out = _run(["sysctl", "-n", "vm.swapusage"])
        if rc == 0:
            m = re.search(r"used\s*=\s*([0-9.]+)([MG])", out)
            if m:
                val = float(m.group(1))
                v = val if m.group(2) == "G" else val / 1024.0
                src = "real: sysctl vm.swapusage"
    if v is None:
        return _state_ok(
            "unguarded",
            "swap used: UNKNOWN (sysctl output unparsable) -> UNGUARDED, "
            "continuing")
    ok = v < SWAP_MAX_GB
    return _state_ok(
        "ok" if ok else "fail",
        f"swap used: {v:.2f} GB ({src}) {'OK' if ok else 'FAIL'} "
        f"(need < {SWAP_MAX_GB:.1f} GB)")


def read_mem_free_pct(mem_floor_pct=MEM_MIN_PCT):
    v, src = _fake_num(FAKE_MEM)
    if v is None:
        if shutil.which("memory_pressure") is None:
            return _state_ok(
                "unguarded",
                "free memory: UNKNOWN (memory_pressure missing) "
                "-> UNGUARDED, continuing")
        rc, out = _run(["memory_pressure"])
        if rc == 0:
            m = re.search(r"System-wide memory free percentage:\s*(\d+)%", out)
            if m:
                v = float(m.group(1))
                src = "real: memory_pressure"
    if v is None:
        return _state_ok(
            "unguarded",
            "free memory: UNKNOWN (memory_pressure output unparsable) "
            "-> UNGUARDED, continuing")
    ok = v >= mem_floor_pct
    return _state_ok(
        "ok" if ok else "fail",
        f"free memory: {v:.0f}% ({src}) {'OK' if ok else 'FAIL'} "
        f"(need >= {mem_floor_pct:.0f}%)")


def read_disk_free_gib(path=None):
    v, src = _fake_num(FAKE_DISK)
    if v is None:
        if shutil.which("df") is None:
            return _state_ok(
                "unguarded",
                "disk free: UNKNOWN (df missing) -> UNGUARDED, continuing")
        target = str(path or ROOT)
        rc, out = _run(["df", "-Pk", target])
        if rc == 0:
            lines = [l for l in out.splitlines() if l.strip()]
            if len(lines) >= 2:
                fields = lines[-1].split()
                if len(fields) >= 4 and fields[3].isdigit():
                    v = int(fields[3]) / (1024.0 * 1024.0)  # KB -> GiB
                    src = f"real: df -Pk {target}"
    if v is None:
        return _state_ok(
            "unguarded",
            "disk free: UNKNOWN (df output unparsable) -> UNGUARDED, "
            "continuing")
    ok = v >= DISK_MIN_GIB
    return _state_ok(
        "ok" if ok else "fail",
        f"disk free: {v:.2f} GiB ({src}) {'OK' if ok else 'FAIL'} "
        f"(need >= {DISK_MIN_GIB:.0f} GiB)")


def collect(mem_floor_pct=MEM_MIN_PCT, path=None):
    """One reading of everything: {"ac","batt","swap","mem","disk"}."""
    ab = read_ac_batt()
    return {
        "ac": ab["ac"],
        "batt": ab["batt"],
        "swap": read_swap_gb(),
        "mem": read_mem_free_pct(mem_floor_pct),
        "disk": read_disk_free_gib(path),
    }


def readings_line(readings):
    return "readings: " + "; ".join(readings[k]["msg"] for k in
                                    ("ac", "batt", "swap", "mem", "disk"))


# ------------------------------------------------------- the guard evaluation
def evaluate_guards(force=False,
                    ac_wait_s=600.0, ac_poll_s=60.0,
                    mem_wait_s=1800.0, mem_step_s=300.0,
                    mem_floor_pct=MEM_MIN_PCT,
                    log=lambda m: None,
                    stop=lambda: False,
                    sleep=time.sleep):
    """Read every guard, wait out the spec's windows, return (ok, msgs).

    force=True  -> one immediate reading; failures are logged as OVERRIDDEN
                   by --force and the result is True (no waiting).
    stop()      -> checked while waiting; True aborts the wait and returns
                   (False, msgs) so the caller can handle a TERM/INT.
    Windows are 0 in tests (overridable -- disclosed in the test output).
    """
    msgs = []

    def emit(m):
        msgs.append(m)
        log(m)

    r = collect(mem_floor_pct)
    line = readings_line(r)
    emit(line)
    for k in ("ac", "batt", "swap", "mem", "disk"):
        if r[k]["state"] == "fail" and force:
            emit(f"GUARD FAIL OVERRIDDEN by --force (logged): {r[k]['msg']}")
    fails = [k for k in r if r[k]["state"] == "fail"]
    if not fails:
        emit("GUARDS PASS (all readings within spec thresholds)")
        return True, msgs
    if force:
        emit(f"GUARDS FAILED ({', '.join(fails)}) but --force given -> "
             f"continuing (logged per spec)")
        return True, msgs

    t0 = time.time()
    while True:
        if r["disk"]["state"] == "fail":
            emit("disk guard has no wait window in the spec -> FAIL "
                 "immediately: " + r["disk"]["msg"])
            return False, msgs
        ac_bad = r["ac"]["state"] == "fail" or r["batt"]["state"] == "fail"
        mem_bad = r["swap"]["state"] == "fail" or r["mem"]["state"] == "fail"
        if not ac_bad and not mem_bad:
            emit("GUARDS PASS (all readings within spec thresholds)")
            return True, msgs

        now = time.time()
        elapsed = now - t0
        if ac_bad and elapsed >= ac_wait_s:
            emit(f"AC/battery still failing after the {ac_wait_s:.0f}s wait "
                 f"window -> FAIL, skipping")
            return False, msgs
        if mem_bad and elapsed >= mem_wait_s:
            emit(f"swap/free-memory still failing after the {mem_wait_s:.0f}s "
                 f"wait window -> FAIL, skipping")
            return False, msgs
        if stop():
            emit("guard wait interrupted by signal")
            return False, msgs

        step = mem_step_s if mem_bad else ac_poll_s
        remaining = (mem_wait_s - elapsed) if mem_bad else (ac_wait_s - elapsed)
        dur = max(min(step, remaining), 0.05)
        end = time.time() + dur
        while time.time() < end:
            if stop():
                emit("guard wait interrupted by signal")
                return False, msgs
            sleep(min(0.2, max(end - time.time(), 0.01)))
        r = collect(mem_floor_pct)
        emit(readings_line(r))


# --------------------------------------------- conflicting-process detection
def _self_and_ancestors():
    pids = [os.getpid()]
    seen = set()
    pid = os.getppid()
    while pid and pid > 1 and pid not in seen:
        seen.add(pid)
        pids.append(pid)
        if shutil.which("ps") is None:
            break
        rc, out = _run(["ps", "-o", "ppid=", "-p", str(pid)])
        try:
            pid = int(out.strip())
        except ValueError:
            break
    return pids


def conflicting_processes(pattern=CONFLICT_PATTERN):
    """Alive pids whose cmdline matches `pattern`, excluding self/ancestors.

    Returns None when pgrep is unavailable (unguarded -- caller logs it).
    """
    if shutil.which("pgrep") is None:
        return None
    rc, out = _run(["pgrep", "-f", pattern], timeout=30)
    if rc == 1:
        return []
    if rc != 0:
        return None
    try:
        pids = [int(x) for x in out.split()]
    except ValueError:
        return None
    exclude = set(_self_and_ancestors())
    return [p for p in pids if p not in exclude]


# ---------------------------------------------------------------------- CLI
def _main(argv):
    if "--conflicts" in argv:
        pids = conflicting_processes()
        if pids is None:
            print("UNGUARDED: pgrep unavailable -> conflict check skipped")
            return 0
        if pids:
            print(" ".join(str(p) for p in pids))
            return 3
        print("")
        return 0
    if "--launch-check" in argv:
        force = "--force" in argv
        ok, _msgs = evaluate_guards(
            force=force, ac_wait_s=0.0, ac_poll_s=0.0,
            mem_wait_s=0.0, mem_step_s=0.0,
            mem_floor_pct=LAUNCHER_MEM_FLOOR_PCT, log=print)
        return 0 if ok else 1
    print("usage: phase3_guards.py --conflicts | --launch-check [--force]")
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
