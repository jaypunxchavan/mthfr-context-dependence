#!/usr/bin/env bash
# scripts/launch_phase4_overnight.sh -- Phase 4 overnight launcher (task A9).
#
# BEHAVIOUR (PHASE4_STRENGTHENING.md A9 + Part B; this header was written
# before the first launch, and nothing here has been run against real data --
# A9 stops at READY-TO-LAUNCH):
#
#   bash scripts/launch_phase4_overnight.sh --plan A     -> night A
#   bash scripts/launch_phase4_overnight.sh --plan B     -> night B
#   bash scripts/launch_phase4_overnight.sh --plan C     -> night C (the stages
#                                                            that did not fit
#                                                            night B)
#   bash scripts/launch_phase4_overnight.sh --plan A --dry-run
#                                                    -> print the driver's full
#                                                       plan, run nothing
#   bash scripts/launch_phase4_overnight.sh --plan A --force
#                                                    -> pass --force to the
#                                                       driver (guards
#                                                       overridden, logged)
#   PHASE4_HOME=/path bash scripts/launch_phase4_overnight.sh --plan A
#                                                    -> redirect state/lock/log
#                                                       (tests use this;
#                                                       default
#                                                       data/processed/phase4)
#
#   1. LOCK: refuses if the driver lock is HELD, tested by trying to take
#      fcntl.flock(LOCK_EX|LOCK_NB) on data/processed/phase4/.driver.lockfile
#      (the driver does this check too, immediately before it starts work).
#      This launcher does NOT delete a lock it does not understand: the kernel
#      releases a flock when its holder dies, so a leftover FILE is normal and
#      harmless, and a leftover marker directory is cleaned up by the driver
#      itself with a printed message.
#   2. CONFLICTS: refuses if a process matching
#      'phase4_driver|171_neigh_score|173_ladder_score' is alive (this
#      launcher and its ancestors excluded), via the driver's --conflicts,
#      which calls scripts/lib/phase3_guards.py UNCHANGED.
#   3. GUARDS: one immediate reading of every guard with the launcher's
#      stricter 35% free-memory floor and NO wait windows -- it refuses now and
#      says what to quit.  (The stage floor inside the driver is 25%, with the
#      spec's 10-minute AC and 30-minute memory wait windows.)
#   4. DRY RUN prints the plan and creates nothing.
#   5. LAUNCH detached: nohup + caffeinate -ims -w <pid>, stdout mirrored to
#      driver_phase4<PLAN>_nohup.log, then prints the PID, the monitor
#      command, the stop command and the resume command.
#
#   If interrupted, re-running this script resumes: steps already recorded
#   `completed` in driver_state_phase4<PLAN>.json are skipped.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

PLAN=""
DRY=0
FORCE=0
FORCE_ARGS=()
usage() { sed -n '2,45p' "$0"; }
for arg in "$@"; do
  case "$arg" in
    --plan) next=1 ;;
    --plan=*) PLAN="${arg#--plan=}" ;;
    --dry-run) DRY=1 ;;
    --force) FORCE=1; FORCE_ARGS=(--force) ;;
    -h|--help) usage; exit 0 ;;
    *) echo "usage: bash scripts/launch_phase4_overnight.sh --plan {A|B|C} [--dry-run] [--force]" >&2; exit 2 ;;
  esac
  if [ "${next:-0}" = "1" ]; then PLAN="$arg"; next=0; fi
done
case "$PLAN" in
  A|B|C) ;;
  *) echo "REFUSING: --plan must be A, B or C (got '${PLAN:-<none>}')" >&2; exit 2 ;;
esac

PY="venv/bin/python3"
DRIVER="scripts/phase4_driver.py"
GUARDS="scripts/lib/phase3_guards.py"
HOMEDIR="${PHASE4_HOME:-$ROOT/data/processed/phase4}"
LOG="$HOMEDIR/driver_phase4${PLAN}.log"
STATE="$HOMEDIR/driver_state_phase4${PLAN}.json"
LOCKF="$HOMEDIR/.driver.lockfile"
NOHUP_LOG="$HOMEDIR/driver_phase4${PLAN}_nohup.log"

if [ ! -f "$PY" ]; then
  echo "REFUSING: $PY not found (run from the repo; venv must exist)" >&2
  exit 1
fi
if [ ! -f "$DRIVER" ]; then
  echo "REFUSING: $DRIVER not found" >&2
  exit 1
fi

# ---- 1. lock check (flock; no deletion of anything we do not own) ---------
lock_out="$("$PY" "$DRIVER" --plan "$PLAN" --home "$HOMEDIR" --lock-check)"
lock_rc=$?
echo "$lock_out"
if [ "$lock_rc" -ne 0 ]; then
  echo "  A Phase 4 driver is already running. Monitor: tail -n 5 $LOG"
  echo "  Stop it first with: kill \$(cat $STATE | venv/bin/python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))[\"driver_pid\"])' $STATE)"
  exit 1
fi

# ---- 2. conflicting live processes ----------------------------------------
conflicts="$("$PY" "$DRIVER" --plan "$PLAN" --home "$HOMEDIR" --conflicts)"
conflicts_rc=$?
if [ "$conflicts_rc" -ne 0 ]; then
  echo "REFUSING: conflicting process(es) alive (PID(s): $conflicts)"
  echo "  pattern 'phase4_driver|171_neigh_score|173_ladder_score' -- a"
  echo "  driver or one of the Phase 4 scorers is already running. Stop it"
  echo "  first."
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
  echo "  - this OpenCode window"
  echo "  - browsers (Safari, Chrome, ...)"
  echo "  - Spotify"
  echo "  - Claude / ChatGPT"
  echo "  - anything else heavy (Low Power Mode off, lid open)"
  echo "If swap was above 2 GB since the last reboot, RESTART the Mac first"
  echo "(swap is not released by closing apps)."
  echo "Then re-run: bash scripts/launch_phase4_overnight.sh --plan $PLAN"
  echo "(override the guards for one run only with: --force, logged)"
  exit 1
fi
echo "$guard_out"

# ---- 4. dry run: print the plan, create nothing ---------------------------
if [ "$DRY" = 1 ]; then
  "$PY" "$DRIVER" --plan "$PLAN" --home "$HOMEDIR" \
      ${FORCE_ARGS[@]+"${FORCE_ARGS[@]}"} --dry-run
  exit $?
fi

# ---- 5. launch detached ----------------------------------------------------
mkdir -p "$HOMEDIR" || { echo "REFUSING: cannot create $HOMEDIR" >&2; exit 1; }
nohup "$PY" "$DRIVER" --plan "$PLAN" --home "$HOMEDIR" \
    ${FORCE_ARGS[@]+"${FORCE_ARGS[@]}"} >> "$NOHUP_LOG" 2>&1 &
DRIVER_PID=$!
if command -v caffeinate >/dev/null 2>&1; then
  caffeinate -ims -w "$DRIVER_PID" >/dev/null 2>&1 &
  echo "caffeinate -ims -w $DRIVER_PID started (the Mac stays awake on AC)"
else
  echo "WARNING: caffeinate not found -> no wake lock (the Mac may sleep!)"
fi
sleep 1
if ! kill -0 "$DRIVER_PID" 2>/dev/null; then
  echo "FAILED: the driver exited immediately. Last lines of $NOHUP_LOG:"
  tail -n 10 "$NOHUP_LOG" 2>/dev/null
  echo "(a held lock or a conflicting process is the usual cause)"
  exit 1
fi
echo ""
echo "Phase 4 overnight driver LAUNCHED (plan $PLAN)."
echo "  PID:       $DRIVER_PID   (also recorded in $STATE)"
echo "  monitor:   tail -n 5 $LOG"
echo "  state:     cat $STATE"
echo "  stop:      kill $DRIVER_PID"
echo "  resume:    re-run this script with the same --plan (completed steps"
echo "             are skipped; do NOT delete $STATE)"
echo "Do not tail -f, do not open OpenCode, do not run anything heavy."