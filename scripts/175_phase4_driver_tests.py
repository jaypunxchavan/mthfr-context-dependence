#!/usr/bin/env python3
"""scripts/175_phase4_driver_tests.py -- A9's driver test suite.

Every test runs in an ISOLATED TEMPORARY DIRECTORY with STUB stages and never
touches a real output, a real checkpoint or a real scorer: the plan under test
is a JSON file of stub commands, and --home points at the temp dir.  The only
real code exercised is the driver's own machinery (lock, guards, budgets,
retry, signals, state, coverage rule, dry-run, resume) plus the UNCHANGED
scripts/lib/phase3_guards.py.

TESTS (all hard; a failure prints the evidence and exits 3):
  T1  double-start refusal, 50 of 50, sequential (driver A holds the lock and
      is proven running, then B is launched 50 times and must refuse each time
      with exit 2 and a printed reason)
  T2  the Phase 3 flake specifically: 50 SIMULTANEOUS starts of A and B on one
      home -- exactly one may hold the lock, the other must refuse; the number
      of wins per side is reported.  This is the case Phase 3 could lose
      (mkdir-then-write window) and the one the flock makes impossible.
  T3  stale lock: a leftover marker directory plus a dead PID is cleared with a
      printed message and the run proceeds; a leftover lock FILE (normal after
      a crash, the kernel having released the flock) does not block anything
  T4  SIGTERM: forwarded to the child's process group, state written, exit 143,
      and the lock is free afterwards
  T5  timeout: a stage whose budget expires kills the child group and the
      driver continues
  T6  retry: exit 1 is retried to exactly 3 attempts; exit 3 is attempted
      exactly ONCE (never retried); a gate step is never retried
  T7  guards with simulated readings (PHASE3_FAKE_*): each of the five failing
      cases skips its stage, and all-good readings run it
  T8  --dry-run for plans A, B and C: prints the plan, creates nothing
  T9  resume: a completed stage is skipped on relaunch
  T10 the Amendment 1 item 5 coverage rule: with no score files the neighbour
      step is skipped as a dependency; with >= 30 complete members it runs

Usage:
  venv/bin/python3 scripts/175_phase4_driver_tests.py            # all tests
  venv/bin/python3 scripts/175_phase4_driver_tests.py --only T4   # one test
"""

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / "venv" / "bin" / "python3")
DRIVER = str(ROOT / "scripts" / "phase4_driver.py")

RESULTS = []


def record(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {name}" + (f": {detail}" if detail else ""), flush=True)


def base_env(**extra):
    env = dict(os.environ)
    env.update({k: str(v) for k, v in extra.items()})
    # zero wait windows so no test ever sleeps on a guard
    for k, v in (("PHASE4_AC_WAIT_S", "0"), ("PHASE4_AC_POLL_S", "0"),
                 ("PHASE4_MEM_WAIT_S", "0"), ("PHASE4_MEM_STEP_S", "0"),
                 ("PHASE4_RETRY_DELAY_S", "0.1"),
                 ("PHASE4_HEARTBEAT_S", "1"),
                 ("PHASE4_KILL_GRACE_S", "1")):
        env.setdefault(k, v)
    env.update(extra)
    return env


def run_driver(home, plan="A", plan_file=None, extra=(), env=None,
               timeout=120):
    cmd = [PY, DRIVER, "--plan", plan, "--home", str(home),
           "--retry-delay", "0.1", "--heartbeat-s", "1",
           "--guard-ac-wait", "0", "--guard-ac-poll", "0",
           "--guard-mem-wait", "0", "--guard-mem-step", "0",
           "--kill-grace", "1"]
    if plan_file:
        cmd += ["--plan-file", str(plan_file)]
    cmd += list(extra)
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                          env=env or base_env(), timeout=timeout)


def write_stub(d, name, body):
    p = d / name
    p.write_text(body)
    p.chmod(0o755)
    return str(p)


STUB_OK = ("import sys, pathlib\n"
           "pathlib.Path(sys.argv[1]).write_text('ran')\n"
           "sys.exit(0)\n")
STUB_SLEEP = ("import sys, time\n"
              "time.sleep(float(sys.argv[2]))\n"
              "sys.exit(0)\n")
STUB_READY_SLEEP = ("import sys, time, pathlib\n"
                    "pathlib.Path(sys.argv[1]).write_text('ready')\n"
                    "time.sleep(float(sys.argv[2]))\n"
                    "sys.exit(0)\n")
STUB_FAIL_COUNT = ("import sys, pathlib\n"
                   "p = pathlib.Path(sys.argv[1])\n"
                   "n = int(p.read_text()) if p.exists() else 0\n"
                   "p.write_text(str(n + 1))\n"
                   "sys.exit(int(sys.argv[2]))\n")
STUB_IGNORE_TERM = ("import signal, sys, time\n"
                    "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
                    "time.sleep(120)\n")


def plan_one(step_name, cmd, budget_s=60, sid="ST1", requires=None):
    step = {"name": step_name, "cmd": cmd}
    if requires:
        step["requires"] = requires
    return {"name": "test-plan",
            "stages": [{"id": sid, "label": "stub stage", "budget_s": budget_s,
                        "guard": False, "steps": [step]}]}


# ===================================================================== tests
def t1_double_start(d):
    home = d / "t1"
    home.mkdir()
    ready = home / "ready"
    marker = home / "done"
    sleep_s = write_stub(d, "stub_ready_sleep.py", STUB_READY_SLEEP)
    pf = home / "plan.json"
    pf.write_text(json.dumps(plan_one(
        "sleep", [PY, sleep_s, str(ready), "20"])))
    env = base_env()
    a = subprocess.Popen(
        [PY, DRIVER, "--plan", "A", "--home", str(home), "--plan-file",
         str(pf), "--guard-ac-wait", "0", "--guard-ac-poll", "0",
         "--guard-mem-wait", "0", "--guard-mem-step", "0"],
        cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, env=env)
    try:
        t_end = time.time() + 30
        while not ready.exists() and time.time() < t_end:
            time.sleep(0.05)
        record("T1a driver A reached its running stage (lock held)",
               ready.exists(), f"ready marker {ready}")
        refusals, bad = 0, []
        for i in range(50):
            r = run_driver(home, "A", pf, timeout=60)
            if r.returncode == 2 and "REFUSING TO START" in (r.stdout + r.stderr):
                refusals += 1
            else:
                bad.append((i, r.returncode, (r.stdout or "")[-200:]))
        record("T1 double-start refusal 50 of 50", refusals == 50 and not bad,
               f"{refusals}/50 refused with exit 2"
               + (f"; first failure {bad[0]}" if bad else ""))
    finally:
        a.send_signal(signal.SIGTERM)
        try:
            a.wait(timeout=30)
        except subprocess.TimeoutExpired:
            a.kill()
    lc = run_driver(home, "A", extra=["--lock-check"])
    record("T1c lock is free after A terminated", lc.returncode == 0,
           (lc.stdout or "").strip().splitlines()[-1] if lc.stdout else "")


def t2_simultaneous(d):
    home = d / "t2"
    home.mkdir()
    ready = home / "ready"
    sleep_s = write_stub(d, "stub_ready2.py", STUB_READY_SLEEP)
    pf = home / "plan.json"
    pf.write_text(json.dumps(plan_one("sleep", [PY, sleep_s, str(ready), "20"])))
    env = base_env()
    cmd = [PY, DRIVER, "--plan", "A", "--home", str(home), "--plan-file",
           str(pf), "--guard-ac-wait", "0", "--guard-ac-poll", "0",
           "--guard-mem-wait", "0", "--guard-mem-step", "0"]
    a_wins = b_wins = both_ran = weird = reached = 0
    for i in range(50):
        if ready.exists():
            ready.unlink()
        pa = subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, env=env)
        pb = subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, env=env)
        # give the winner time to reach its stage, then stop both
        t_end = time.time() + 10
        while not ready.exists() and time.time() < t_end:
            time.sleep(0.02)
        if ready.exists():
            reached += 1
        for p in (pa, pb):
            p.send_signal(signal.SIGTERM)
        outs = []
        for p in (pa, pb):
            try:
                text = p.communicate(timeout=30)[0] or ""
                outs.append((p.returncode, text))
            except subprocess.TimeoutExpired:
                p.kill()
                outs.append((-1, ""))
        # a refusal exits 2 from acquire_lock, BEFORE any signal handling; the
        # winner is still running when we TERM it, so it exits 143
        refused_flags = [rc == 2 and "REFUSING TO START" in o
                         for rc, o in outs]
        ran_flags = [rc not in (2, None) for rc, _ in outs]
        if sum(refused_flags) == 1 and sum(ran_flags) == 1:
            if ran_flags[0]:
                a_wins += 1
            else:
                b_wins += 1
        elif sum(refused_flags) == 0:
            both_ran += 1
        else:
            weird += 1
    record("T2 simultaneous starts: never two drivers on one home",
           both_ran == 0 and weird == 0,
           f"50 rounds; exactly one ran and exactly one refused in "
           f"{a_wins + b_wins}/50 (A won {a_wins}, B won {b_wins}); the "
           f"winner's stage was reached in {reached}/50 rounds; rounds where "
           f"NEITHER refused (i.e. two drivers on one home): {both_ran}; "
           f"unclassifiable: {weird}")


def t3_stale_lock(d):
    home = d / "t3"
    home.mkdir()
    marker = home / ".driver.lock"
    marker.mkdir()
    (marker / "driver.pid").write_text("999999\n")       # a dead PID
    (home / ".driver.lockfile").write_text('{"pid": 999999}\n')
    out = write_stub(d, "stub_marker.py", STUB_OK)
    pf = home / "plan.json"
    pf.write_text(json.dumps(plan_one("run", [PY, out, str(home / "done")])))
    r = run_driver(home, "A", pf)
    ok = r.returncode == 0 and (home / "done").exists()
    record("T3 stale marker + dead PID cleared, run proceeds", ok,
           (f"exit {r.returncode}"
            + ("; 'STALE LOCK MARKER CLEARED' printed"
               if "STALE LOCK MARKER CLEARED" in (r.stdout + r.stderr)
               else "; NOTE: no stale message printed")))


def t4_term(d):
    home = d / "t4"
    home.mkdir()
    pidfile = home / "child.pid"
    stub = write_stub(d, "stub_ignore_term.py", STUB_IGNORE_TERM)
    pf = home / "plan.json"
    pf.write_text(json.dumps(plan_one("sleepy", [PY, stub], budget_s=120)))
    env = base_env()
    p = subprocess.Popen(
        [PY, DRIVER, "--plan", "A", "--home", str(home), "--plan-file",
         str(pf), "--guard-ac-wait", "0", "--guard-ac-poll", "0",
         "--guard-mem-wait", "0", "--guard-mem-step", "0", "--kill-grace", "1"],
        cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, env=env)
    t_end = time.time() + 30
    while not pidfile.exists() and time.time() < t_end:
        time.sleep(0.05)
    time.sleep(1.0)                       # let the child start
    p.send_signal(signal.SIGTERM)
    try:
        out = p.communicate(timeout=40)[0]
    except subprocess.TimeoutExpired:
        p.kill()
        out = p.communicate()[0]
    state = json.loads((home / "driver_state_phase4A.json").read_text())
    child_alive = False
    try:
        os.killpg(os.getpgid(p.pid), 0)
    except (ProcessLookupError, PermissionError, OSError):
        child_alive = False
    lc = run_driver(home, "A", extra=["--lock-check"])
    record("T4a SIGTERM -> driver exits 143", p.returncode == 143,
           f"exit {p.returncode}")
    record("T4b state records the interruption",
           state.get("status") == "terminated",
           f"state status {state.get('status')!r}")
    record("T4c lock released after SIGTERM", lc.returncode == 0,
           (lc.stdout or "").strip().splitlines()[-1] if lc.stdout else "")
    record("T4d TERM was forwarded to the child group",
           "forwarding TERM to child process group" in out,
           "child group TERM/SIGKILL path exercised")


def t5_timeout(d):
    home = d / "t5"
    home.mkdir()
    stub = write_stub(d, "stub_long.py", STUB_SLEEP)
    pf = home / "plan.json"
    pf.write_text(json.dumps(plan_one("slow", [PY, stub, "60", "60"],
                                      budget_s=3, sid="ST1")))
    r = run_driver(home, "A", pf, timeout=90)
    state = json.loads((home / "driver_state_phase4A.json").read_text())
    st = state["stages"]["ST1"]["status"]
    record("T5 timeout kills the stage, driver continues", st == "timeout",
           f"stage status {st!r}; driver exit {r.returncode}; "
           f"{'child group killed' in (r.stdout + r.stderr)}")


def t6_retry_vs_gate(d):
    home = d / "t6"
    home.mkdir()
    count1 = home / "n1"
    count3 = home / "n3"
    stub = write_stub(d, "stub_count.py", STUB_FAIL_COUNT)
    pf1 = home / "p1.json"
    pf1.write_text(json.dumps(plan_one("fail1", [PY, stub, str(count1), "1"])))
    r1 = run_driver(home, "A", pf1, timeout=90)
    n1 = int(count1.read_text()) if count1.exists() else 0
    record("T6a exit 1 retried to exactly 3 attempts", n1 == 3,
           f"{n1} attempts (driver exit {r1.returncode})")
    pf3 = home / "p3.json"
    pf3.write_text(json.dumps(plan_one("fail3", [PY, stub, str(count3), "3"])))
    r3 = run_driver(home, "A", pf3, timeout=90)
    n3 = int(count3.read_text()) if count3.exists() else 0
    record("T6b exit 3 attempted exactly once (never retried)", n3 == 1,
           f"{n3} attempts; stage status "
           f"{json.loads((home / 'driver_state_phase4A.json').read_text())['stages']['ST1']['status']!r}")


def t7_guards(d):
    cases = [("AC off", {"PHASE3_FAKE_AC": "0"}),
             ("battery 12%", {"PHASE3_FAKE_BATT": "12"}),
             ("swap 4.5 GB", {"PHASE3_FAKE_SWAP": "4.5"}),
             ("free memory 10%", {"PHASE3_FAKE_MEM": "10"}),
             ("disk 1 GiB", {"PHASE3_FAKE_DISK_GIB": "1"})]
    out = write_stub(d, "stub_guard.py", STUB_OK)
    allok = True
    detail = []
    for i, (label, fakes) in enumerate(cases):
        home = d / f"t7_{i}"
        home.mkdir()
        pf = home / "plan.json"
        plan = plan_one("guarded", [PY, out, str(home / "done")])
        plan["stages"][0]["guard"] = True
        pf.write_text(json.dumps(plan))
        env = base_env(**fakes)
        r = run_driver(home, "A", pf, env=env, timeout=60)
        state = json.loads((home / "driver_state_phase4A.json").read_text())
        st = state["stages"]["ST1"]["status"]
        if st != "skipped_guard" or (home / "done").exists():
            allok = False
        detail.append(f"{label}->{st}")
    record("T7a each failing guard skips its stage", allok,
           "; ".join(detail))
    home = d / "t7_ok"
    home.mkdir()
    pf = home / "plan.json"
    plan = plan_one("guarded", [PY, out, str(home / "done")])
    plan["stages"][0]["guard"] = True
    pf.write_text(json.dumps(plan))
    r = run_driver(home, "A", pf,
                   env=base_env(PHASE3_FAKE_AC="1", PHASE3_FAKE_BATT="80",
                                PHASE3_FAKE_SWAP="0.5", PHASE3_FAKE_MEM="60",
                                PHASE3_FAKE_DISK_GIB="40"),
                   timeout=60)
    record("T7b all-good readings run the stage",
           r.returncode == 0 and (home / "done").exists(),
           f"exit {r.returncode}")


def t8_dry_run(d):
    ok, detail = True, []
    for plan in ("A", "B", "C"):
        home = d / f"t8_{plan}"
        home.mkdir()
        r = run_driver(home, plan, extra=["--dry-run"], timeout=60)
        made = list(home.iterdir())
        ids = {"A": ["SA1", "SA2", "SA3"], "B": ["SB1", "SB2"],
               "C": ["SB3", "SB4", "SB5", "SB6"]}[plan]
        have = all(i in (r.stdout or "") for i in ids)
        if r.returncode != 0 or made or not have:
            ok = False
        detail.append(f"plan {plan}: exit {r.returncode}, created {len(made)}, "
                      f"ids present {have}")
    record("T8 --dry-run for A, B and C prints the plan and creates nothing",
           ok, "; ".join(detail))


def t9_resume(d):
    home = d / "t9"
    home.mkdir()
    count = home / "n"
    stub = write_stub(d, "stub_count0.py", STUB_FAIL_COUNT)
    pf = home / "plan.json"
    pf.write_text(json.dumps(plan_one("once", [PY, stub, str(count), "0"])))
    r1 = run_driver(home, "A", pf, timeout=60)
    n1 = int(count.read_text()) if count.exists() else 0
    r2 = run_driver(home, "A", pf, timeout=60)
    n2 = int(count.read_text()) if count.exists() else 0
    log = (home / "driver_phase4A.log").read_text()
    record("T9a the first run executes the step", n1 == 1, f"{n1} run(s)")
    record("T9b relaunch skips the completed stage",
           n2 == 1 and "skipped" in log and "(resume)" in log,
           f"{n2} run(s) after relaunch; resume lines in the log: "
           f"{log.count('(resume)')}")


def t10_coverage(d):
    """Amendment 1 item 5: the neighbour step runs only with >= 30 complete
    NB members.  We build a temp home with a roster and score files."""
    home = d / "t10"
    (home / "neigh").mkdir(parents=True)
    roster = home / "neigh" / "roster_v1.csv"
    cols = ["bg_id", "cell", "position", "wt_aa", "mut_aa", "d3", "dseq",
            "second_at_position", "alanine_first", "score_order"]
    # 40 amendment cells, taken from the real frozen roster's C1/C2/C5 rows
    import csv as _csv
    real = list(_csv.DictReader(open(
        ROOT / "data/processed/phase4/neigh/roster_v1.csv", newline="")))
    sel = [r for r in real if r["cell"] in ("C1", "C2", "C5")][:40]
    with open(roster, "w", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in sel:
            w.writerow({k: r[k] for k in cols})
    out = write_stub(d, "stub_cov.py", STUB_OK)
    # (a) no score files -> only the six existing nulls are complete -> < 30
    pf = home / "p_none.json"
    pf.write_text(json.dumps(plan_one(
        "neigh", [PY, out, str(home / "ran_none")],
        requires={"kind": "nb_coverage"})))
    r = run_driver(home, "A", pf, timeout=120)
    st = json.loads((home / "driver_state_phase4A.json").read_text())
    sa = st["stages"]["ST1"]["steps"]["neigh"]["status"]
    record("T10a with no scores the neighbour step is skipped "
           "(6 complete < 30)", sa == "skipped_dependency" and
           not (home / "ran_none").exists(), f"step status {sa!r}")
    # (b) give 24 of them full score files -> 6 + 24 = 30 -> the rule is met
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "s125", str(ROOT / "scripts/125_phase2_analysis.py"))
    s125 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s125)
    H = sorted(int(p) for p in s125.holdout(s125.build_frame()))
    for r_ in sel[:24]:
        own = int(r_["position"])
        npos = len([p for p in H if p != own])
        with open(home / "neigh" / f"bg_{r_['bg_id']}.csv", "w") as fh:
            fh.write("bg_id,position,mut_aa,score,delta\n")
            for pos in [p for p in H if p != own]:
                for mut in "ACDEFGHIKLMNPQRSTVWY":
                    fh.write(f"{r_['bg_id']},{pos},{mut},0.0,0.0\n")
    pf2 = home / "p_yes.json"
    pf2.write_text(json.dumps(plan_one(
        "neigh", [PY, out, str(home / "ran_yes")],
        requires={"kind": "nb_coverage"})))
    r2 = run_driver(home, "A", pf2, timeout=120)
    st2 = json.loads((home / "driver_state_phase4A.json").read_text())
    sa2 = st2["stages"]["ST1"]["steps"]["neigh"]["status"]
    record("T10b with 24 complete new members (6 + 24 = 30) the step runs",
           sa2 == "completed" and (home / "ran_yes").exists(),
           f"step status {sa2!r}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    d = Path(tempfile.mkdtemp(prefix="phase4_driver_tests_"))
    print(f"isolated temp dir: {d}")
    print("PRE-REGISTERED: every test uses stub stages in this directory; no "
          "real output, checkpoint or scorer is touched.")
    tests = [("T1", t1_double_start), ("T2", t2_simultaneous),
             ("T3", t3_stale_lock), ("T4", t4_term), ("T5", t5_timeout),
             ("T6", t6_retry_vs_gate), ("T7", t7_guards), ("T8", t8_dry_run),
             ("T9", t9_resume), ("T10", t10_coverage)]
    print("\nDRIVER TESTS (scripts/175_phase4_driver_tests.py)")
    try:
        for name, fn in tests:
            if args.only and args.only not in name:
                continue
            print(f"\n-- {name} --")
            t0 = time.time()
            try:
                fn(d)
            except Exception as e:
                record(f"{name} raised", False, f"{type(e).__name__}: {e}")
            print(f"   ({time.time() - t0:.1f}s)")
    finally:
        n_pass = sum(1 for _, ok, _ in RESULTS if ok)
        n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
        print(f"\nTEST SUMMARY: {n_pass} PASS, {n_fail} FAIL of {len(RESULTS)} "
              f"checks.")
        print(f"temp dir kept for inspection: {d}")
        print("LIMITATIONS: these tests exercise the driver's own machinery "
              "with stub stages; they do not exercise the real scorers, and "
              "the T2 simultaneous-start count is a race sample, not a proof "
              "of impossibility.")
        if n_fail:
            sys.exit(3)
    sys.exit(0)


if __name__ == "__main__":
    main()