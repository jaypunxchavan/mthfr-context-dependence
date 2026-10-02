#!/usr/bin/env bash
# scripts/launch_phase2.sh -- Phase 2 overnight background scorer launcher (task G4).
#
# BEHAVIOR FIXED HERE (execution doc G4; do not change after session 2a logging):
#   bash scripts/launch_phase2.sh              -> launches the detached run (NEVER run in session 2a)
#   bash scripts/launch_phase2.sh --dry-run    -> prints exactly what would run; creates NOTHING; exit 0
#
#   * Runs from the repo root: nohup runs `venv/bin/python3
#     scripts/124_phase2_score_backgrounds.py` in a loop of up to 5 attempts
#     (30 s sleep between attempts; a nonzero exit retries; completed
#     backgrounds are skipped by script 124's own resume logic on every attempt)
#   * stdout+stderr append to data/processed/phase2/run.log
#   * wrapper PID written to data/processed/phase2/run.pid; the wrapper traps
#     TERM/INT/QUIT and forwards the signal to the running python child, so the
#     prescribed stop command `kill $(cat data/processed/phase2/run.pid)`
#     actually stops scoring
#   * wrapped with `caffeinate -ims -w <pid>` so the Mac stays awake on AC power
#
# Session 2a tested ONLY `--dry-run`. The real launch is hand-run by Arnav after
# reading the log.
#
# PROJECTION (fixed numbers, G4): 96 backgrounds; 62,706 passes = 18x654 + 78x653
# (Arm S includes position 222; each V/G background skips its own position) vs
# Q1's 62,784 = 96x654 before those skips; at the recorded 511-647 ms/pass
# ~= 8.9-11.3 h; at this session's measured G1 pace 0.530 s/pass ~= 9.2 h.

set -uo pipefail

DRY=0
case "${1:-}" in
  "")        ;;
  --dry-run) DRY=1 ;;
  -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
  *)         echo "usage: bash scripts/launch_phase2.sh [--dry-run]" >&2; exit 2 ;;
esac

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

PY="venv/bin/python3"
SCORER="scripts/124_phase2_score_backgrounds.py"
OUTDIR="data/processed/phase2"
LOG="$OUTDIR/run.log"
PIDF="$OUTDIR/run.pid"
MAX_ATTEMPTS=5
RETRY_SLEEP=30

# The detached worker: attempt loop + signal forwarding. Defined once so the
# dry-run prints the very same bytes that the real launch executes.
read -r -d '' WRAPPER <<'WRAP_EOF' || true
log="$1"; py="$2"; scorer="$3"; attempts="$4"; nap="$5"; pidf="$6"
child=""
on_term() {
  echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) received TERM/INT -- stopping current scorer" >> "$log"
  if [ -n "$child" ]; then kill -TERM "$child" 2>/dev/null; fi
  exit 130
}
trap on_term TERM INT QUIT
i=1
while [ "$i" -le "$attempts" ]; do
  echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) attempt $i/$attempts started" >> "$log"
  "$py" "$scorer" >> "$log" 2>&1 &
  child=$!
  wait "$child"; rc=$?
  child=""
  echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) attempt $i/$attempts exited rc=$rc" >> "$log"
  if [ "$rc" -eq 0 ]; then
    echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) SUCCESS on attempt $i (scorer exit 0)" >> "$log"
    exit 0
  fi
  if [ "$i" -lt "$attempts" ]; then
    echo "[launcher] nonzero exit -> sleeping ${nap}s before retry" >> "$log"
    sleep "$nap"
  fi
  i=$((i + 1))
done
echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) GAVE UP after $attempts attempts" >> "$log"
exit 1
WRAP_EOF

PROJECTION="projection: 96 backgrounds; 62,706 passes = 18x654 + 78x653
  (vs Q1's 62,784 = 96x654 before each V/G background's own position is skipped);
  511-647 ms/pass (execution doc record) ~= 8.9-11.3 h;
  measured G1 pace 0.530 s/pass (530 ms) -> 62,706 x 0.530 ~= 9.2 h"

if [ "$DRY" -eq 1 ]; then
  echo "DRY RUN -- nothing below this line was executed or created."
  echo "repo root: $ROOT"
  echo
  echo "1) mkdir -p $OUTDIR"
  echo
  echo "2) the detached attempt loop, launched as:"
  echo "   nohup bash -c '<attempt loop below>' _ \\"
  echo "     '$LOG' '$PY' '$SCORER' $MAX_ATTEMPTS $RETRY_SLEEP '$PIDF' >> '$LOG' 2>&1 &"
  echo "   with the wrapper PID written to $PIDF; attempt loop body:"
  echo "   -----------------------------------------------------------------"
  printf '%s\n' "$WRAPPER" | sed 's/^/   /'
  echo "   -----------------------------------------------------------------"
  echo "   (each attempt runs exactly: $PY $SCORER, appending to $LOG;"
  echo "    script 124 skips completed backgrounds on every attempt,"
  echo "    writes scores atomically to $OUTDIR/bg_<id>.csv + manifest.csv)"
  echo
  echo "3) caffeinate -ims -w \$PID &   (keeps the Mac awake on AC until the run ends)"
  echo
  echo "MONITOR:"
  echo "  tail -f $LOG"
  echo "  ls $OUTDIR/bg_*.csv | wc -l"
  echo "RESUME after an interruption: rerun this same launch script --"
  echo "  bash scripts/launch_phase2.sh"
  echo "  (attempt 1 skips every background that already has a complete file)"
  echo "STOP:"
  echo "  kill \$(cat $PIDF)"
  echo "$PROJECTION"
  exit 0
fi

# ---------------------------------------------------------------- real path
mkdir -p "$OUTDIR"
{
  echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) launch_phase2.sh starting:"
  echo "[launcher]   attempts=$MAX_ATTEMPTS retry_sleep=${RETRY_SLEEP}s scorer=$PY $SCORER"
  echo "[launcher]   repo root: $ROOT"
} >> "$LOG"

nohup bash -c "$WRAPPER" _ \
  "$LOG" "$PY" "$SCORER" "$MAX_ATTEMPTS" "$RETRY_SLEEP" "$PIDF" >> "$LOG" 2>&1 &
PID=$!
echo "$PID" > "$PIDF"

if command -v caffeinate >/dev/null 2>&1; then
  caffeinate -ims -w "$PID" >/dev/null 2>&1 &
else
  echo "[launcher] WARNING: caffeinate not found; the Mac may sleep mid-run" >> "$LOG"
fi

echo "launched detached scorer: PID $PID (written to $PIDF)"
echo "MONITOR:   tail -f $LOG"
echo "           ls $OUTDIR/bg_*.csv | wc -l"
echo "RESUME:    bash scripts/launch_phase2.sh   (reruns this script; completed skipped)"
echo "STOP:      kill \$(cat $PIDF)"
echo "$PROJECTION"
