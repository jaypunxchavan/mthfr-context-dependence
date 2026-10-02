#!/usr/bin/env bash
# scripts/launch_phase3_overnight.sh -- Phase 3 overnight launcher (task A7).
#
# BEHAVIOR (PHASE3_OVERNIGHT.md A7 / Part B; this header was written before
# the first run; every deviation is disclosed in
# docs/tasks/phase3-overnight/PHASE3_A7_TEST_OUTPUT.txt):
#
#   bash scripts/launch_phase3_overnight.sh              -> launch the detached run
#   bash scripts/launch_phase3_overnight.sh --dry-run    -> print the driver's full
#                                                           plan, run nothing, exit 0
#   bash scripts/launch_phase3_overnight.sh --force      -> pass --force to the driver
#                                                           (guards overridden, logged)
#   PHASE3_HOME=/path bash scripts/launch_phase3_overnight.sh
#                                                        -> redirect state/lock/log
#                                                           (tests use this; default is
#                                                           data/processed/phase3)
#
#   * Lock check: refuse if data/processed/phase3/.driver.lock exists and its
#     PID is alive; clear a stale lock (dead PID) with a printed message.
#   * Refuse if any process matching 'phase3_driver|124_phase2' is alive
#     (excluding this launcher and its ancestors), via scripts/lib/phase3_guards.py.
#   * Guards: AC power + battery >= 30%, swap < 3.0 GB, free memory >= 35%
#     (the launcher's stricter floor; the stage floor is 25%), disk >= 5 GiB.
#     No wait windows here -- the launcher refuses immediately and says what
#     to quit (OpenCode window, browsers, Spotify, Claude, ChatGPT).
#   * Launches the driver detached: nohup + caffeinate -ims -w <pid>, stdout
#     mirrored to data/processed/phase3/driver_nohup.log, then prints the PID,
#     the monitor command `tail -n 5 data/processed/phase3/driver.log` and the
#     stop command `kill $(cat .../.driver.lock/driver.pid)`.
#   * If interrupted, re-running this script resumes (completed stages skip).

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

DRY=0
FORCE=0
FORCE_ARGS=()
usage() { sed -n '2,30p' "$0"; }
for arg in "$@"; do
  case "$arg" in
    --dry-run)  DRY=1 ;;
    --force)    FORCE=1; FORCE_ARGS=(--force) ;;
    -h|--help)  usage; exit 0 ;;
    *)          echo "usage: bash scripts/launch_phase3_overnight.sh [--dry-run] [--force]" >&2; exit 2 ;;
  esac
done

PY="venv/bin/python3"
DRIVER="scripts/phase3_driver.py"
GUARDS="scripts/lib/phase3_guards.py"
HOMEDIR="${PHASE3_HOME:-$ROOT/data/processed/phase3}"
LOCK="$HOMEDIR/.driver.lock"
PIDF="$LOCK/driver.pid"
LOG="$HOMEDIR/driver.log"
NOHUP_LOG="$HOMEDIR/driver_nohup.log"

if [ ! -f "$PY" ]; then
  echo "REFUSING: $PY not found (run from the repo; venv must exist)" >&2
  exit 1
fi

# ---- 1. lock check (spec: refuse live, clear stale with a message) --------
if [ -d "$LOCK" ]; then
  pid="$(cat "$PIDF" 2>/dev/null || true)"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    echo "REFUSING: driver lock $LOCK is held by PID $pid (alive)."
    echo "  A driver is already running. Monitor: tail -n 5 $LOG"
    echo "  Stop it first with: kill \$(cat $PIDF)"
    exit 1
  fi
  echo "STALE LOCK CLEARED: $LOCK (driver.pid=${pid:-missing} not alive) -> removing it"
  rm -rf "$LOCK"
fi

# ---- 2. conflicting live processes (phase3_driver|124_phase2) -------------
conflicts="$("$PY" "$GUARDS" --conflicts)"
conflicts_rc=$?
if [ "$conflicts_rc" -ne 0 ]; then
  echo "REFUSING: conflicting process(es) alive (PID(s): $conflicts)"
  echo "  pattern 'phase3_driver|124_phase2' -- a driver or the phase-2 scorer"
  echo "  is already running. Stop it first."
  exit 1
fi

# ---- 3. guards + the 35% launcher memory floor (no waits; refuse now) -----
guard_out="$("$PY" "$GUARDS" --launch-check ${FORCE_ARGS[@]+"${FORCE_ARGS[@]}"})"
guard_rc=$?
if [ "$guard_rc" -ne 0 ]; then
  echo "$guard_out"
  echo ""
  echo "REFUSING TO LAUNCH: environment guard(s) failed (readings above)."
  echo "Plug in AC power if not already, and QUIT FIRST:"
  echo "  - the OpenCode window"
  echo "  - browsers (Safari, Chrome, ...)"
  echo "  - Spotify"
  echo "  - Claude"
  echo "  - ChatGPT"
  echo "  - anything else heavy (Low Power Mode off, lid open)"
  echo "Then re-run: bash scripts/launch_phase3_overnight.sh"
  echo "(override the guards for one run only with: --force, logged)"
  exit 1
fi
echo "$guard_out"

# ---- 4. dry run: print the plan, create nothing ---------------------------
if [ "$DRY" = 1 ]; then
  "$PY" "$DRIVER" --home "$HOMEDIR" ${FORCE_ARGS[@]+"${FORCE_ARGS[@]}"} --dry-run
  exit $?
fi

# ---- 5. launch detached ----------------------------------------------------
mkdir -p "$HOMEDIR" || { echo "REFUSING: cannot create $HOMEDIR" >&2; exit 1; }
nohup "$PY" "$DRIVER" --home "$HOMEDIR" ${FORCE_ARGS[@]+"${FORCE_ARGS[@]}"} \
  >> "$NOHUP_LOG" 2>&1 &
DRIVER_PID=$!
if command -v caffeinate >/dev/null 2>&1; then
  caffeinate -ims -w "$DRIVER_PID" >/dev/null 2>&1 &
  echo "caffeinate -ims -w $DRIVER_PID started (Mac stays awake on AC)"
else
  echo "WARNING: caffeinate not found -> no wake lock (the Mac may sleep!)"
fi
sleep 1
if ! kill -0 "$DRIVER_PID" 2>/dev/null; then
  echo "FAILED: the driver exited immediately. Last lines of $NOHUP_LOG:"
  tail -n 10 "$NOHUP_LOG" 2>/dev/null
  echo "(a live lock or a conflicting process is the usual cause)"
  exit 1
fi
echo ""
echo "Phase 3 overnight driver LAUNCHED."
echo "  PID:       $DRIVER_PID   (also written to $PIDF)"
echo "  monitor:   tail -n 5 $LOG"
echo "  stop:      kill \$(cat $PIDF)"
echo "  resume:    re-run this script (completed stages are skipped)"
echo "Do not tail -f, do not open OpenCode, do not run anything heavy."
