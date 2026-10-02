#!/usr/bin/env python3
"""test_phase3_driver.py -- A7 orchestration test harness (stdlib only).

Run with:  venv/bin/python3 scripts/test_phase3_driver.py
(Never bare python3 -- AGENTS section 1.)

WHAT IS BEING TESTED (PHASE3_OVERNIGHT.md line 239 "Tests (all hard)", plus
the launcher/dependency items named in the A7 task and the session brief):

   T01  start twice -> the second start refuses (live lock, PID alive)
   T02  stale lock (dead PID) -> cleared with a printed message, proceeds
   T03  kill $(cat driver.pid) forwards TERM to the child process group and
        removes the lock
   T04  stage timeout kills the child (tiny 2.5 s budget, sleeping stub) and
        the driver continues to the next stage
   T05  retry on a crash: stub exits 7 -> exactly 3 attempts (2 retries)
   T06  NO retry on exit 3: stub exits 3 -> exactly 1 attempt (gate failure)
   T07  AC-power guard with PHASE3_FAKE_AC=0 -> stage skipped and logged
        (exercises a short override wait window: 0.8 s / 0.3 s poll)
   T08  battery guard with PHASE3_FAKE_BATT=10 -> stage skipped and logged
   T09  swap guard with PHASE3_FAKE_SWAP=4.5 -> stage skipped and logged
   T10  free-memory guard with PHASE3_FAKE_MEM=10 -> stage skipped and logged
   T11  disk guard with PHASE3_FAKE_DISK_GIB=1 -> stage skipped and logged
   T12  --force overrides a failed guard -> stage runs, logged as FORCED
   T13  missing guard tools (empty PATH) -> UNGUARDED, logged, stage runs
   T14  --dry-run prints the full plan and runs nothing (custom + production
        plan: no state, no lock, no directories, stubs never executed)
   T15  resume: a completed stage is skipped on relaunch; the failed stage
        is re-run and can succeed
   T16  S3-style dependency: files required -> step skipped and logged when
        absent, runs when present (re-evaluated on relaunch)
   T17  S3 coverage rule: fabricated roster/manifest-free artifacts ->
        FAIL (short background file) then PASS (full file); step skipped vs run
   T18  state + heartbeat: driver_state.json schema and >= 2 heartbeats
        during a running stage (heartbeat forced to 0.3 s)
   T19  conflicting live process matching 'phase3_driver|124_phase2'
        (decoy script) -> driver refuses, releases the lock, writes no state
   T20  S5 integrity pass with STATE_FOR_LAUNCH.md absent -> logged and
        skipped, stage completes (graceful absence handling)
   T21  launcher refuses below the 35% memory floor and prints what to quit
        (OpenCode window, browsers, Spotify, Claude, ChatGPT)
   T22  launcher --dry-run: prints the plan, creates nothing

FIXTURES ARE GENERATED IN AN ISOLATED TEMP DIRECTORY (tempfile.mkdtemp ==
`mktemp -d`) PER TEST.  The REAL stages (scripts/154..158) are NEVER
executed; the driver's --home is redirected in every test so the real
data/processed/phase3/ is never written; no git commands, no network.
A final sentinel check asserts that the real home gained no driver
artifacts (.driver.lock, driver.pid, driver_state.json, driver.log).

TEST-ONLY OVERRIDES OF PRODUCTION DEFAULTS (all disclosed, all reachable by
flag or env var; production values in parentheses):
   PHASE3_RETRY_DELAY_S=0.2 (30 s), PHASE3_AC_WAIT_S/PHASE3_MEM_WAIT_S=0
   (600/1800 s; one test uses --guard-ac-wait 0.8), PHASE3_KILL_GRACE_S=1
   (5 s), test-local budgets 2.5-60 s (600-9000 s).  Guard THRESHOLDS are
   never overridden -- only readings (fakes), windows and delays.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DRIVER = REPO / "scripts" / "phase3_driver.py"
LAUNCHER = REPO / "scripts" / "launch_phase3_overnight.sh"
REAL_HOME = REPO / "data" / "processed" / "phase3"
PY = sys.executable

GOOD_FAKES = {
    "PHASE3_FAKE_AC": "1",
    "PHASE3_FAKE_BATT": "95",
    "PHASE3_FAKE_SWAP": "1.0",
    "PHASE3_FAKE_MEM": "60",
    "PHASE3_FAKE_DISK_GIB": "10",
}
TEST_OVERRIDES = {
    "PHASE3_RETRY_DELAY_S": "0.2",
    "PHASE3_AC_WAIT_S": "0",
    "PHASE3_AC_POLL_S": "0.3",
    "PHASE3_MEM_WAIT_S": "0",
    "PHASE3_MEM_STEP_S": "0",
    "PHASE3_KILL_GRACE_S": "1",
}

TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


# ------------------------------------------------------------------ helpers
def base_env(fakes=True, extra=None):
    env = dict(os.environ)
    env.update(TEST_OVERRIDES)
    if fakes:
        env.update(GOOD_FAKES)
    else:
        for k in GOOD_FAKES:
            env.pop(k, None)
    if extra:
        env.update(extra)
    return env


def home_of(sb):
    return Path(sb) / "home"


def write_stub(sb, name, body):
    p = Path(sb) / f"{name}.sh"
    p.write_text("#!/bin/sh\n" + body + "\n")
    p.chmod(0o755)
    return p


def write_plan(sb, stages, name="test-plan"):
    p = Path(sb) / "plan.json"
    p.write_text(json.dumps({"name": name, "stages": stages}))
    return p


def run_driver(sb, *extra_args, fakes=True, env_extra=None, timeout=120):
    cmd = [PY, str(DRIVER), "--home", str(home_of(sb))] + list(extra_args)
    return subprocess.run(cmd, cwd=str(REPO),
                          env=base_env(fakes, env_extra),
                          capture_output=True, text=True, timeout=timeout)


def start_driver(sb, *extra_args, fakes=True, env_extra=None, out_name="d.out"):
    cmd = [PY, str(DRIVER), "--home", str(home_of(sb))] + list(extra_args)
    out = Path(sb) / out_name
    fh = open(out, "wb")
    p = subprocess.Popen(cmd, cwd=str(REPO), env=base_env(fakes, env_extra),
                         stdout=fh, stderr=subprocess.STDOUT)
    return p, fh, out


def read_state(sb):
    p = home_of(sb) / "driver_state.json"
    assert_true(p.exists(), f"driver_state.json missing at {p}")
    return json.loads(p.read_text())


def out_of(proc):
    return (proc.stdout or "") + (proc.stderr or "")


def wait_for(cond, timeout=10.0, step=0.05, what="condition"):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return True
        time.sleep(step)
    raise AssertionError(f"timed out after {timeout}s waiting for {what}")


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def dead_pid():
    """A pid that is guaranteed dead right now (reaped child)."""
    for _ in range(5):
        p = subprocess.Popen([PY, "-c", "pass"])
        p.wait(timeout=30)
        if p.returncode == 0 and not pid_alive(p.pid):
            return p.pid
    raise AssertionError("could not obtain a dead pid")


def simple_stage(sid, stub_path, budget=60, guard=True, extra_steps=None,
                 step_name="run", precheck=None):
    st = {"id": sid, "label": f"stub stage {sid}", "budget_s": budget,
          "guard": guard,
          "steps": [{"name": step_name, "cmd": [str(stub_path)]}]}
    if precheck:
        st["precheck"] = precheck
    if extra_steps:
        st["steps"].extend(extra_steps)
    return st


def real_home_sentinels():
    return {n: ((home := REAL_HOME / n).exists(),
                 home.stat().st_mtime_ns if home.exists() else None)
            for n in (".driver.lock", "driver.pid", "driver_state.json",
                      "driver.log")}


# ------------------------------------------------------------------- tests
@test
def test_double_start_second_refuses(sb):
    mark = Path(sb) / "ran.marker"
    pidf = Path(sb) / "stub.pid"
    stub = write_stub(sb, "long",
                      f'echo x >> "{mark}"; echo $$ > "{pidf}"; sleep 15')
    plan = write_plan(sb, [simple_stage("S1", stub)])
    p1, fh1, out1 = start_driver(sb, "--plan", str(plan))
    diag = ""
    try:
        lock_pidf = home_of(sb) / ".driver.lock" / "driver.pid"
        wait_for(lock_pidf.exists, 10, what="driver lock")
        assert_true(int(lock_pidf.read_text().strip()) == p1.pid,
                    "driver.pid should hold driver 1's pid")
        time.sleep(0.3)  # the lock must STAY while driver 1 runs its stage
        assert_true(p1.poll() is None,
                    f"driver 1 died during startup (rc={p1.poll()}): "
                    f"{out1.read_text()[-1500:]}")
        assert_true(lock_pidf.exists(),
                    f"driver 1 must still hold the lock: {out1.read_text()[-1500:]}")
        p2 = run_driver(sb, "--plan", str(plan), timeout=60)
        o2 = out_of(p2)
        if p2.returncode != 2:
            snap = subprocess.run(
                ["pgrep", "-fl", "phase3_driver|124_phase2"],
                capture_output=True, text=True)
            diag = (f"\ndriver1 output: {out1.read_text()[-1500:]}"
                    f"\nlive matches at failure: {snap.stdout}")
        assert_true(p2.returncode == 2,
                    f"second start must refuse with rc=2, got "
                    f"{p2.returncode}: {o2}{diag}")
        assert_true("REFUSING TO START" in o2 and "alive" in o2,
                    f"refusal message missing: {o2}{diag}")
        st = read_state(sb)
        assert_true(st["driver_pid"] == p1.pid,
                    "second start must not clobber driver 1's state")
    finally:
        p1.send_signal(signal.SIGTERM)
        try:
            p1.wait(timeout=15)
        except subprocess.TimeoutExpired:
            p1.kill()
        fh1.close()
    assert_true(not (home_of(sb) / ".driver.lock").exists(),
                "lock must be removed when driver 1 stops")


@test
def test_stale_lock_cleared_with_message(sb):
    d = dead_pid()
    lock = home_of(sb) / ".driver.lock"
    lock.mkdir(parents=True)
    (lock / "driver.pid").write_text(str(d) + "\n")
    mark = Path(sb) / "ran.marker"
    stub = write_stub(sb, "quick", f'echo x >> "{mark}"; exit 0')
    plan = write_plan(sb, [simple_stage("S1", stub)])
    p = run_driver(sb, "--plan", str(plan))
    o = out_of(p)
    assert_true(p.returncode == 0, f"driver should proceed, got: {o}")
    assert_true("STALE LOCK CLEARED" in o and str(d) in o,
                f"stale-lock message missing: {o}")
    assert_true(mark.exists(), "stage should have run after clearing stale lock")
    st = read_state(sb)
    assert_true(st["stages"]["S1"]["status"] == "completed",
                f"stage should be completed: {st['stages']['S1']}")
    assert_true(not lock.exists(), "lock must be released after the run")


@test
def test_term_forwards_to_child_and_removes_lock(sb):
    mark = Path(sb) / "ran.marker"
    termf = Path(sb) / "term.marker"
    stub = write_stub(
        sb, "trap_term",
        f'echo x >> "{mark}"\n'
        f'echo $$ > "{Path(sb) / "stub.pid"}"\n'
        f"trap 'echo yes > \"{termf}\"; exit 0' TERM\n"
        f"sleep 30\nexit 0")
    plan = write_plan(sb, [simple_stage("S1", stub)])
    p, fh, out = start_driver(sb, "--plan", str(plan))
    try:
        wait_for(termf.parent.joinpath("stub.pid").exists, 10,
                 what="stub pid")
        lock_pidf = home_of(sb) / ".driver.lock" / "driver.pid"
        wait_for(lock_pidf.exists, 10, what="driver lock")
        driver_pid = int(lock_pidf.read_text().strip())
        os.kill(driver_pid, signal.SIGTERM)
        p.wait(timeout=20)
        o = out.read_text()
        assert_true(p.returncode == 143, f"driver should exit 143, got {p.returncode}")
        assert_true(termf.exists(),
                    "TERM must be forwarded to the child (stub trap marker)")
        assert_true("forwarding TERM to child process group" in o,
                    f"driver should log the TERM forwarding: {o[-800:]}")
        assert_true(not (home_of(sb) / ".driver.lock").exists(),
                    "lock must be removed after TERM")
    except AssertionError:
        raise
    finally:
        if p.poll() is None:
            p.kill()
        fh.close()
    st = read_state(sb)
    assert_true(st["status"] == "terminated",
                f"state status should be terminated: {st['status']}")


@test
def test_stage_timeout_kills_child(sb):
    pidf = Path(sb) / "stub.pid"
    stub_slow = write_stub(sb, "slow", f'echo $$ > "{pidf}"; sleep 60')
    mark = Path(sb) / "after.marker"
    stub_next = write_stub(sb, "next", f'echo x > "{mark}"')
    plan = write_plan(sb, [
        simple_stage("S1", stub_slow, budget=2.5),
        simple_stage("S2", stub_next, budget=30),
    ])
    p = run_driver(sb, "--plan", str(plan), timeout=90)
    o = out_of(p)
    assert_true(p.returncode == 0, f"driver should finish: {o[-600:]}")
    assert_true("TIMEOUT" in o and "child process group killed" in o,
                f"timeout kill not logged: {o[-800:]}")
    st = read_state(sb)
    assert_true(st["stages"]["S1"]["status"] == "timeout",
                f"S1 status should be timeout: {st['stages']['S1']}")
    assert_true(st["stages"]["S2"]["status"] == "completed",
                "driver must continue to the next stage after a timeout")
    assert_true(mark.exists(), "stage 2 should have run")
    spid = int(pidf.read_text().strip())
    wait_for(lambda: not pid_alive(spid), 5, what="timed-out child to die")
    assert_true(not pid_alive(spid), "timed-out child must be killed")


@test
def test_retry_on_crash_three_attempts(sb):
    att = Path(sb) / "attempts.txt"
    stub = write_stub(sb, "crash", f'echo x >> "{att}"; exit 7')
    plan = write_plan(sb, [simple_stage("S1", stub, budget=60)])
    p = run_driver(sb, "--plan", str(plan), timeout=90)
    o = out_of(p)
    st = read_state(sb)
    n = len(att.read_text().splitlines()) if att.exists() else 0
    assert_true(n == 3, f"stub must run exactly 3 times (initial + 2 retries), ran {n}")
    rec = st["stages"]["S1"]["steps"]["run"]
    assert_true(rec["attempts"] == 3,
                f"state attempts should be 3, got {rec}")
    assert_true(rec["status"] == "failed" and st["stages"]["S1"]["status"] == "failed",
                f"stage should be failed: {st['stages']['S1']}")
    assert_true("retrying in" in o and "attempt 3/3" in o,
                f"retry log lines missing: {o[-800:]}")


@test
def test_no_retry_on_exit_3(sb):
    att = Path(sb) / "attempts.txt"
    stub = write_stub(sb, "gate", f'echo x >> "{att}"; exit 3')
    plan = write_plan(sb, [simple_stage("S1", stub, budget=60)])
    p = run_driver(sb, "--plan", str(plan), timeout=60)
    o = out_of(p)
    st = read_state(sb)
    n = len(att.read_text().splitlines()) if att.exists() else 0
    assert_true(n == 1, f"exit 3 must never be retried; stub ran {n} times")
    rec = st["stages"]["S1"]["steps"]["run"]
    assert_true(rec["attempts"] == 1 and rec["status"] == "gate_failed",
                f"record should show 1 attempt / gate_failed: {rec}")
    assert_true("NEVER retried" in o, f"gate-failure policy not logged: {o[-800:]}")
    assert_true(st["stages"]["S1"]["status"] == "gate_failed",
                f"stage status should be gate_failed: {st['stages']['S1']}")


def _guard_skip_test(sb, fake_env, needle, extra_args=()):
    mark = Path(sb) / "ran.marker"
    stub = write_stub(sb, "guarded", f'echo x > "{mark}"; exit 0')
    plan = write_plan(sb, [simple_stage("S1", stub, budget=60)])
    env = dict(GOOD_FAKES)
    env.update(fake_env)
    env.update(TEST_OVERRIDES)
    p = subprocess.run([PY, str(DRIVER), "--home", str(home_of(sb)),
                        "--plan", str(plan), *extra_args],
                       cwd=str(REPO),
                       env={**dict(os.environ), **env},
                       capture_output=True, text=True, timeout=90)
    o = out_of(p)
    assert_true(p.returncode == 0, f"driver should finish: {o[-600:]}")
    assert_true(not mark.exists(),
                f"stage must be skipped when {needle!r} reads bad: {o[-800:]}")
    st = read_state(sb)
    assert_true(st["stages"]["S1"]["status"] == "skipped_guard",
                f"status should be skipped_guard: {st['stages']['S1']}")
    assert_true(needle in o, f"reading {needle!r} not logged: {o}")
    assert_true("FAKE" in o, f"fake provenance must be logged: {o}")
    assert_true("SKIPPED (guard failure)" in o,
                f"guard skip must be logged: {o[-800:]}")
    return o


@test
def test_guard_ac_off_skips_stage(sb):
    t0 = time.time()
    o = _guard_skip_test(sb, {"PHASE3_FAKE_AC": "0"}, "AC power: OFF",
                         extra_args=["--guard-ac-wait", "0.8",
                                     "--guard-ac-poll", "0.3"])
    elapsed = time.time() - t0
    assert_true(elapsed >= 0.7,
                f"driver must wait out the (overridden) AC window; took {elapsed:.2f}s")
    assert_true(o.count("AC power: OFF") >= 2,
                "AC readings must be re-emitted during the wait window")


@test
def test_guard_low_battery_skips_stage(sb):
    _guard_skip_test(sb, {"PHASE3_FAKE_BATT": "10"}, "battery: 10%")


@test
def test_guard_high_swap_skips_stage(sb):
    _guard_skip_test(sb, {"PHASE3_FAKE_SWAP": "4.5"}, "swap used: 4.50 GB")


@test
def test_guard_low_memory_skips_stage(sb):
    _guard_skip_test(sb, {"PHASE3_FAKE_MEM": "10"}, "free memory: 10%")


@test
def test_guard_low_disk_skips_stage(sb):
    _guard_skip_test(sb, {"PHASE3_FAKE_DISK_GIB": "1"}, "disk free: 1.00 GiB")


@test
def test_force_overrides_guard_and_logs(sb):
    mark = Path(sb) / "ran.marker"
    stub = write_stub(sb, "forced", f'echo x > "{mark}"; exit 0')
    plan = write_plan(sb, [simple_stage("S1", stub, budget=60)])
    env = dict(GOOD_FAKES)
    env.update({"PHASE3_FAKE_BATT": "10"})
    env.update(TEST_OVERRIDES)
    p = subprocess.run([PY, str(DRIVER), "--home", str(home_of(sb)),
                        "--plan", str(plan), "--force"],
                       cwd=str(REPO), env={**dict(os.environ), **env},
                       capture_output=True, text=True, timeout=90)
    o = out_of(p)
    assert_true(p.returncode == 0, f"driver should finish: {o[-600:]}")
    assert_true(mark.exists(), f"--force must run the stage: {o[-800:]}")
    assert_true("OVERRIDDEN by --force" in o and "FORCED" in o,
                f"the forced override must be logged: {o}")
    st = read_state(sb)
    assert_true(st["stages"]["S1"]["status"] == "completed",
                f"stage should complete under --force: {st['stages']['S1']}")


@test
def test_missing_tools_run_unguarded(sb):
    empty_bin = Path(sb) / "emptybin"
    empty_bin.mkdir()
    mark = Path(sb) / "ran.marker"
    stub = write_stub(sb, "unguarded", f'echo x > "{mark}"; exit 0')
    plan = write_plan(sb, [simple_stage("S1", stub, budget=60)])
    p = run_driver(sb, "--plan", str(plan), fakes=False,
                   env_extra={"PATH": str(empty_bin)}, timeout=90)
    o = out_of(p)
    assert_true(p.returncode == 0, f"driver should finish: {o[-600:]}")
    assert_true(mark.exists(),
                f"missing tools must not fail the guard (stage runs): {o[-800:]}")
    assert_true("UNGUARDED" in o,
                f"UNGUARDED must be logged: {o}")
    st = read_state(sb)
    assert_true(st["stages"]["S1"]["status"] == "completed",
                f"stage should complete unguarded: {st['stages']['S1']}")


@test
def test_dry_run_prints_plan_runs_nothing(sb):
    mark = Path(sb) / "never.marker"
    stub = write_stub(sb, "never", f'echo x > "{mark}"; exit 0')
    plan = write_plan(sb, [simple_stage("S1", stub),
                           simple_stage("S2", stub)])
    p = run_driver(sb, "--plan", str(plan), "--dry-run")
    o = out_of(p)
    assert_true(p.returncode == 0, f"dry-run rc: {p.returncode} {o}")
    assert_true("PHASE3 DRY RUN" in o and "S1" in o and "S2" in o,
                f"plan not printed: {o}")
    assert_true(not mark.exists(), "dry-run must not execute stubs")
    assert_true(not home_of(sb).exists(),
                f"dry-run must create no directories (home: {home_of(sb)})")

    # production plan, still a dry-run: assert the exact command table prints
    home2 = Path(sb) / "home2"
    p2 = subprocess.run([PY, str(DRIVER), "--home", str(home2), "--dry-run"],
                        cwd=str(REPO), env=base_env(),
                        capture_output=True, text=True, timeout=60)
    o2 = out_of(p2)
    for needle in ("154_gb1_score_backgrounds.py", "gb1_project",
                   "--limit-roster 20", "156_rbd_score_backgrounds.py",
                   "--g-r5", "155_gb1_regime_analysis.py",
                   "157_rbd_regime_analysis.py", "158_multidms_rbd.py",
                   "venv_multidms", "phase3_driver.py", "--integrity",
                   "budget 100 min", "budget 150 min", "budget 75 min",
                   "budget 120 min", "budget 5 min"):
        assert_true(needle in o2, f"production plan must print {needle!r}: {o2}")
    assert_true(not home2.exists(), "production dry-run must create no directories")


@test
def test_resume_skips_completed_stage(sb):
    count_a = Path(sb) / "a_count.txt"
    count_b = Path(sb) / "b_count.txt"
    stub_a = write_stub(sb, "stage_a", f'echo x >> "{count_a}"; exit 0')
    stub_b_bad = write_stub(sb, "stage_b_bad", f'echo x >> "{count_b}"; exit 9')
    plan = write_plan(sb, [simple_stage("S1", stub_a),
                           simple_stage("S2", stub_b_bad)])
    p1 = run_driver(sb, "--plan", str(plan), timeout=90)
    assert_true(p1.returncode == 0, f"run1: {out_of(p1)[-500:]}")
    st1 = read_state(sb)
    assert_true(st1["stages"]["S1"]["status"] == "completed", "S1 completed in run1")
    assert_true(st1["stages"]["S2"]["status"] == "failed", "S2 failed in run1")
    assert_true(len(count_b.read_text().splitlines()) == 3,
                "crashing stub should have run 3 times in run1")

    stub_b_ok = write_stub(sb, "stage_b_ok", f'echo x >> "{count_b}"; exit 0')
    plan2 = write_plan(sb, [simple_stage("S1", stub_a),
                            simple_stage("S2", stub_b_ok)])
    p2 = run_driver(sb, "--plan", str(plan2), timeout=90)
    o2 = out_of(p2)
    assert_true(p2.returncode == 0, f"run2: {o2[-500:]}")
    assert_true(len(count_a.read_text().splitlines()) == 1,
                "completed S1 must NOT re-run on relaunch")
    assert_true("already completed -> skipped (resume)" in o2,
                f"resume skip must be logged: {o2}")
    st2 = read_state(sb)
    assert_true(st2["stages"]["S2"]["status"] == "completed",
                f"S2 should now be completed: {st2['stages']['S2']}")


@test
def test_dependency_skip_then_run_on_relaunch(sb):
    dep = home_of(sb) / "dep.ok"
    mark = Path(sb) / "ran.marker"
    stub = write_stub(sb, "dependent", f'echo x > "{mark}"; exit 0')
    st = {"id": "S3", "label": "dep stage", "budget_s": 60, "guard": True,
          "steps": [{"name": "needs_dep", "cmd": [str(stub)],
                     "requires": {"kind": "files",
                                  "paths": ["{home}/dep.ok"]}}]}
    plan = write_plan(sb, [st])
    p1 = run_driver(sb, "--plan", str(plan), timeout=60)
    o1 = out_of(p1)
    assert_true("dependency NOT met -> step logged and skipped" in o1,
                f"skip must be logged: {o1[-600:]}")
    assert_true(not mark.exists(), "step must not run without its dependency")
    stt = read_state(sb)
    assert_true(stt["stages"]["S3"]["status"] == "skipped_dependency",
                f"stage status should be skipped_dependency: {stt['stages']['S3']}")

    dep.parent.mkdir(parents=True, exist_ok=True)
    dep.write_text("ok\n")
    p2 = run_driver(sb, "--plan", str(plan), timeout=60)
    assert_true("dependency met" in out_of(p2),
                f"dependency re-evaluated on relaunch: {out_of(p2)[-600:]}")
    assert_true(mark.exists(), "step must run once the dependency exists")
    stt2 = read_state(sb)
    assert_true(stt2["stages"]["S3"]["steps"]["needs_dep"]["status"] == "completed",
                f"step should be completed: {stt2['stages']['S3']}")


def _write_gb1_artifacts(sb, bg2_positions):
    gb1 = home_of(sb) / "gb1"
    gb1.mkdir(parents=True, exist_ok=True)
    (gb1 / "roster_v2.csv").write_text("draw_order,background_id\n1,b1\n2,b2\n")
    (gb1 / "wt_arm.csv").write_text("bg_id,sequence,position,mut_aa,score\n")
    hdr = "bg_id,sequence,position,mut_aa,score\n"
    for bid, npos in (("b1", 54), ("b2", bg2_positions)):
        rows = "\n".join(f"{bid},seq,p{i % 19},A,0.0" for i in range(19 * npos))
        (gb1 / f"bg_{bid}.csv").write_text(hdr + rows + "\n")


@test
def test_coverage_rule_fail_then_pass(sb):
    mark = Path(sb) / "ran.marker"
    stub = write_stub(sb, "analysis", f'echo x > "{mark}"; exit 0')
    st = {"id": "S3", "label": "coverage stage", "budget_s": 60,
          "guard": True,
          "steps": [{"name": "gb1_analysis", "cmd": [str(stub)],
                     "requires": {"kind": "coverage", "module": "gb1"}}]}
    plan = write_plan(sb, [st])

    # FAIL: b2 has only 40/54 positions = 0.741 < 0.95 floor (155's G-4)
    _write_gb1_artifacts(sb, bg2_positions=40)
    p1 = run_driver(sb, "--plan", str(plan), timeout=60)
    o1 = out_of(p1)
    assert_true("coverage gb1: FAIL" in o1, f"coverage FAIL not logged: {o1[-600:]}")
    assert_true("40/54 = 0.741 < 0.95" in o1,
                f"offender detail missing: {o1}")
    assert_true(not mark.exists(), "analysis must not run below the floor")
    stt = read_state(sb)
    assert_true(stt["stages"]["S3"]["status"] == "skipped_dependency",
                f"status: {stt['stages']['S3']}")

    # PASS: both files full -> relaunch runs the step
    _write_gb1_artifacts(sb, bg2_positions=54)
    p2 = run_driver(sb, "--plan", str(plan), timeout=60)
    o2 = out_of(p2)
    assert_true("coverage gb1: PASS 2/2" in o2, f"coverage PASS not logged: {o2[-600:]}")
    assert_true(mark.exists(), "analysis must run once coverage is reached")


@test
def test_state_and_heartbeat(sb):
    stub = write_stub(sb, "sleeper", "sleep 1.4; exit 0")
    plan = write_plan(sb, [simple_stage("S1", stub, budget=60)])
    p = run_driver(sb, "--plan", str(plan), "--heartbeat-s", "0.3", timeout=60)
    assert_true(p.returncode == 0, f"driver: {out_of(p)[-500:]}")
    st = read_state(sb)
    for key in ("status", "started", "updated", "stages", "driver_pid",
                "current_stage"):
        assert_true(key in st, f"driver_state.json missing key {key}: {list(st)}")
    assert_true(st["status"] == "finished", f"final status: {st['status']}")
    rec = st["stages"]["S1"]
    for key in ("status", "start", "end", "steps"):
        assert_true(key in rec, f"stage record missing {key}: {list(rec)}")
    assert_true(rec["status"] == "completed", f"stage: {rec}")
    log = (home_of(sb) / "driver.log").read_text()
    n_hb = log.count("heartbeat:")
    assert_true(n_hb >= 2,
                f"expected >= 2 heartbeats during a 1.4 s stage at 0.3 s "
                f"interval, got {n_hb}")
    assert_true(log.count("START budget") >= 1 and "DRIVER FINISHED" in log,
                "transitions must be written to driver.log")


@test
def test_conflicting_process_refuses(sb):
    decoy = Path(sb) / "phase3_driver_decoy.sh"
    decoy.write_text("#!/bin/sh\nsleep 20\n")
    decoy.chmod(0o755)
    d = subprocess.Popen(["/bin/sh", str(decoy)], cwd=str(sb))
    try:
        stub = write_stub(sb, "quick", "exit 0")
        plan = write_plan(sb, [simple_stage("S1", stub)])
        p = run_driver(sb, "--plan", str(plan), timeout=60)
        o = out_of(p)
        assert_true(p.returncode == 2, f"should refuse, rc={p.returncode}: {o}")
        assert_true("conflicting process" in o and "phase3_driver" in o,
                    f"conflict message missing: {o}")
        assert_true(not (home_of(sb) / ".driver.lock").exists(),
                    "refusal must release the lock")
        assert_true(not (home_of(sb) / "driver_state.json").exists(),
                    "refusal must write no state")
    finally:
        d.kill()
        d.wait(timeout=10)


@test
def test_integrity_absent_state_for_launch(sb):
    st = {"id": "S5", "label": "integrity", "budget_s": 60, "guard": True,
          "steps": [{"name": "integrity",
                     "cmd": ["{python}", "{driver}", "--integrity",
                             "--home", "{home}", "--state-for-launch",
                             str(Path(sb) / "STATE_FOR_LAUNCH_ABSENT.md")]}]}
    plan = write_plan(sb, [st])
    p = run_driver(sb, "--plan", str(plan), timeout=60)
    o = out_of(p)
    assert_true(p.returncode == 0, f"driver: {o[-500:]}")
    stt = read_state(sb)
    assert_true(stt["stages"]["S5"]["status"] == "completed",
                f"integrity stage must complete when STATE_FOR_LAUNCH is "
                f"absent: {stt['stages']['S5']}")
    slog = home_of(sb) / "driver_stage_S5.log"
    assert_true(slog.exists(), "stage log missing")
    txt = slog.read_text()
    assert_true("STATE_FOR_LAUNCH.md not found" in txt and "SKIPPED" in txt,
                f"absent STATE_FOR_LAUNCH must be logged and skipped: {txt}")
    assert_true("INTEGRITY: RESULT PASS" in txt,
                f"integrity result line missing: {txt}")


@test
def test_launcher_refuses_below_memory_floor(sb):
    env = dict(os.environ)
    env.update(GOOD_FAKES)
    env.update(TEST_OVERRIDES)
    env["PHASE3_FAKE_MEM"] = "20"
    env["PHASE3_HOME"] = str(home_of(sb))
    p = subprocess.run(["bash", str(LAUNCHER)], cwd=str(REPO), env=env,
                       capture_output=True, text=True, timeout=90)
    o = out_of(p)
    assert_true(p.returncode != 0, f"launcher must refuse: {o}")
    assert_true("REFUSING TO LAUNCH" in o and "free memory: 20%" in o,
                f"refusal must show the reading: {o}")
    for quit_item in ("OpenCode", "browsers", "Spotify", "Claude", "ChatGPT"):
        assert_true(quit_item in o, f"quit list must mention {quit_item}: {o}")
    assert_true(not (home_of(sb) / ".driver.lock").exists(),
                "refused launch must create no lock")
    assert_true(not (home_of(sb) / "driver_state.json").exists(),
                "refused launch must write no state")


@test
def test_launcher_dry_run_creates_nothing(sb):
    env = dict(os.environ)
    env.update(GOOD_FAKES)
    env.update(TEST_OVERRIDES)
    env["PHASE3_HOME"] = str(home_of(sb))
    p = subprocess.run(["bash", str(LAUNCHER), "--dry-run"], cwd=str(REPO),
                       env=env, capture_output=True, text=True, timeout=90)
    o = out_of(p)
    assert_true(p.returncode == 0, f"launcher --dry-run rc: {p.returncode}: {o}")
    assert_true("PHASE3 DRY RUN" in o and "154_gb1_score_backgrounds.py" in o,
                f"plan not printed: {o[:600]}")
    assert_true("GUARDS PASS" in o, f"launcher should show guard readings: {o[:400]}")
    assert_true(not home_of(sb).exists(),
                f"launcher --dry-run must create nothing (home {home_of(sb)})")


# --------------------------------------------------------------------- main
HEADER = """\
================================================================================
PHASE3 A7 TEST OUTPUT -- orchestration: guards, driver, launcher (task A7)
================================================================================
Spec: docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md lines 219-242
      (Task A7), esp. line 239 "Tests (all hard)".
Record: this file is tee'd verbatim from the harness run.

WHAT IS BEING TESTED (T01-T22, harness docstring has the full list):
  lock/refusal semantics (double start, stale lock, conflicting process),
  signal forwarding (TERM -> child process group -> lock removed), stage
  timeout kills the child, retry policy (3 attempts on crash, NEVER on
  exit 3), all five guards with simulated bad readings (PHASE3_FAKE_*),
  --force override (logged), missing-tool UNGUARDED path, --dry-run prints
  the full plan and runs nothing, resume skips completed stages, S3
  dependency and coverage-rule skip/run, state + heartbeat writes, the S5
  integrity pass with STATE_FOR_LAUNCH.md absent, and the launcher's
  memory-floor refusal (with its quit list) and --dry-run.

RULES ENFORCED BY THE HARNESS:
  * run with venv/bin/python3 only; an isolated temp dir (mktemp -d via
    tempfile.mkdtemp) per test; stub stages only -- the real stages
    scripts/154..158 are NEVER executed; driver --home redirected in every
    test; no git commands; no network; a sentinel check proves the real
    data/processed/phase3 gained no driver artifacts.
  * production thresholds are never overridden -- only readings (fakes),
    wait windows and delays (see "TEST-ONLY OVERRIDES" in the docstring).

interpreter: %s
python:      %s
================================================================================
"""

DEVIATIONS = """\
================================================================================
DEVIATIONS / INTERPRETATIONS / LIMITATIONS (verbatim; every one of these is
also written into the driver's or guards' own docstring/output)
================================================================================
D01  Guard fake env vars: the spec names PHASE3_FAKE_BATT / PHASE3_FAKE_SWAP /
     PHASE3_FAKE_MEM ("such as"); PHASE3_FAKE_AC and PHASE3_FAKE_DISK_GIB were
     added so all five guard readings can be simulated.
D02  Wait-window overrides: production windows (AC/battery 600 s, swap/mem
     1800 s in 300 s steps) are reachable by flag (--guard-ac-wait,
     --guard-ac-poll, --guard-mem-wait, --guard-mem-step) and env
     (PHASE3_AC_WAIT_S, PHASE3_AC_POLL_S, PHASE3_MEM_WAIT_S,
     PHASE3_MEM_STEP_S) so tests run in seconds. Thresholds (30%, 3.0 GB,
     25%, 5 GiB, launcher 35%) are NOT overridable at runtime.
D03  The spec gives the 5-minute step only for swap/mem; AC/battery is
     polled every 60 s inside its 10-minute window (interpretation;
     --guard-ac-poll/PHASE3_AC_POLL_S).
D04  The spec gives disk no wait window: disk free is checked once, failure
     skips the stage immediately.
D05  The launcher runs the guards ONCE with no wait windows and refuses
     immediately (the 10/30-minute waits are per-stage in the driver, per
     spec line 225); its memory floor is the spec's 35%.
D06  A4/A5/A6 gates (the spec does not define predicates): interpreted as
     artifact prechecks -- S1: gb1/sequences.csv + roster_v2.csv exist;
     S2: rbd/e_T.csv + roster_v1.csv exist AND the G-R5 mode is re-run as a
     non-retried gate step (`156 --g-r5`) before scoring, because 156's own
     docstring says G-R5 is "re-run by the A7 driver before the stage"; S4:
     venv_multidms/bin/python exists. The scripts' own sha/gate checks
     (exit 3) remain the authoritative gates and are not duplicated.
D07  S3 coverage rule (spec: "each runs only if its scoring reached the
     coverage rule"): concrete artifact checks using the floors the scripts
     themselves define -- GB1: wt_arm.csv present AND every roster_v2
     background file present with >= 95% of its 54 eligible positions
     (155's frozen G-4); RBD: wt_arm.csv present AND every roster_v1
     background file present with >= 95% of 201 construct sites (156's
     frozen G-R4). All roster backgrounds must be present. No threshold was
     invented; both are quoted from the scripts.
D08  Retry granularity: the spec says "per-stage retry"; implemented per
     step, which is identical for single-step stages (S2's scoring, S4, S5)
     and for multi-step stages reduces to retrying only the failed step
     (safe: 154/156 skip already-complete files on rerun). A timeout is NOT
     retried (the spec lists timeout and crash as separate outcomes); gate
     steps are never retried on any nonzero exit; exit 3 never retried.
D09  Budget accounting: the stage timer starts after guards and the precheck;
     stage budgets cover all attempts and retry sleeps. The global cap
     (--total-cap-min, default 450 min = 7.5 h, the spec's "about 7.5 h") is
     checked at stage start. Guard wait windows sit outside both timers.
D10  Output files beyond the spec's two: each stage's child stdout/stderr is
     captured to {home}/driver_stage_<ID>.log (otherwise scorer output would
     be lost), and the launcher mirrors the driver's stdout to
     {home}/driver_nohup.log (required by nohup redirection). driver.log and
     driver_state.json remain the spec's record; the spec's monitor command
     `tail -n 5 .../driver.log` shows transitions, guard readings and
     heartbeats.
D11  Resume granularity: steps are individually marked completed; on relaunch
     completed steps are skipped, so a stage whose steps are all completed is
     skipped entirely ("stages already completed are skipped"), while failed,
     guard-skipped, timeout and dependency-skipped stages are re-evaluated
     (interpretation; the spec only pins the completed-skip case).
D12  Stage status vocabulary beyond the spec's prose: completed, failed,
     gate_failed, timeout, skipped_guard, skipped_dependency, skipped_cap,
     interrupted, terminated. Exit code 0 from the driver = "run finished",
     not "all stages succeeded".
D13  S5 runs as a child of the driver (self --integrity) so timeout/signal/
     retry apply uniformly; sha256 MISMATCH vs STATE_FOR_LAUNCH.md exits 3
     (prominent FLAG, gate, no retry) while file-count/manifest discrepancies
     are findings, not failures; ABSENT STATE_FOR_LAUNCH.md is logged and
     skipped (it does not exist yet). The sha parser accepts any line with a
     64-hex digest and a scripts/*.py path because the file's format does not
     exist yet -- session 3b (task C0) re-verifies, this is not a substitute.
D14  Kill semantics: on timeout or driver TERM the driver sends TERM to the
     child PROCESS GROUP (children are started with start_new_session),
     waits --kill-grace (default 5 s), then SIGKILLs the group.
D15  The conflict check ('phase3_driver|124_phase2') excludes the driver's own
     PID and its ancestor chain; without that exclusion the check would be
     circular (the test harness and the launcher both legitimately match the
     pattern). pgrep missing -> logged UNGUARDED and skipped (spec's
     missing-tool rule).
D16  Redirectability: --home / PHASE3_HOME (and --plan / PHASE3_PLAN) exist
     so tests never touch data/processed/phase3; the production plan embeds
     {home} in every --out-dir, so a redirected home would redirect the
     scorers too. Production defaults are the real paths.
D17  The two-sequence subset in S1 is `154 --sequence project --out-dir
     data/processed/phase3/gb1_project --limit-roster 20` (154's decision S1
     pins the separate project out-dir; roster order = draw order, so
     --limit-roster 20 = the first 20 of the draw recorded in the A4b log).
D18  Launcher additions for testability: --dry-run (runs the driver's dry-run
     in the foreground) and --force passthrough; both are disclosed in the
     launcher header. The launcher also refuses live locks and conflicting
     processes itself, per spec line 224.
D19  Tests use tempfile.mkdtemp (Python's `mktemp -d`), 22 tests, and the
     disclosed test-only overrides listed in the harness docstring; no real
     stage, git command, or network access is involved. Production values
     (retry 30 s, heartbeats 60 s, windows 600/1800 s, grace 5 s) are NOT
     exercised at full length -- only their overridden equivalents (a
     10-minute-window test would take 10 minutes); the override path is the
     same code path.
D20  Out of scope for this deliverable (not implemented here, per the
     session brief): writing STATE_FOR_LAUNCH.md, appending [A7] and the 3a
     SUMMARY to PHASE3A_BUILD_LOG.md, and the known pending 157 6h-mode fix
     mentioned in STATE.md -- another owner/process handles those; this
     harness created none of them.
================================================================================
"""


def main():
    if "venv" not in sys.executable:
        print(f"REFUSING: run with venv/bin/python3, not {sys.executable}",
              file=sys.stderr)
        return 2
    print(HEADER % (sys.executable, sys.version.replace("\n", " ")), flush=True)
    before = real_home_sentinels()
    results = []
    t0 = time.time()
    for fn in TESTS:
        name = fn.__name__
        ts = time.time()
        status, detail = "PASS", ""
        with tempfile.TemporaryDirectory(prefix="phase3_a7_") as sb:
            try:
                fn(sb)
            except AssertionError as e:
                status, detail = "FAIL", str(e)
            except Exception as e:  # noqa: BLE001 -- record, keep going
                status, detail = "ERROR", repr(e)
        dur = time.time() - ts
        results.append((name, status, detail, dur))
        print(f"[{status}] {name} ({dur:.1f}s)"
              + (f"  {detail}" if detail else ""), flush=True)
    total = time.time() - t0

    after = real_home_sentinels()
    sentinel_ok = before == after
    print("\nsentinel check (real data/processed/phase3 must gain no driver "
          "artifacts): " + ("OK" if sentinel_ok else "FAILED " + str(after)))

    n = len(results)
    n_pass = sum(1 for r in results if r[1] == "PASS")
    print(f"\nSUMMARY: {n} tests, {n_pass} passed, {n - n_pass} failed, "
          f"wall time {total:.1f} s")
    for name, status, detail, dur in results:
        if status != "PASS":
            print(f"  FAILED {name}: {detail}")

    print("\n" + DEVIATIONS, end="", flush=True)
    return 0 if (n_pass == n and sentinel_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
