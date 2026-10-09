#!/usr/bin/env bash
# rebuild_headlines.sh -- rebuild the Phase 4 headline numbers from the CACHED files
# and print a PASS/FAIL table against the values recorded in the logs.
#
# Written for Task C5 of docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md.
# This script is ADDITIVE: it writes only under reproduce/runs/ and reads
# everything else.  It never writes to data/processed/phase4/ and never launches
# the driver.
#
# USAGE
#   bash reproduce/rebuild_headlines.sh [--quick] [--only MODULE[,MODULE...]]
#
#   --quick     reduced draws (N_BOOT=300, N_SIM=100, N_STAB=200).  Bootstrap CIs
#               will NOT match the logged ones; point estimates and words must.
#   --only      run a subset of: inputs,S,N,L,M,U,G,indep
#
# EXIT CODE 0 iff every requested check passes.
#
# WHAT IT DOES, IN ORDER
#   1. environment: venv interpreter, package versions vs reproduce/requirements.lock
#   2. inputs:      every file the headline numbers depend on, PRESENT/ABSENT
#   3. indep:       scripts/176_phase4b_independent_recompute.py -- the second,
#                   independent implementation; its own PASS/FAIL table
#   4. N, L:        scripts/172_neigh_analysis.py and 174_ladder_analysis.py,
#                   whose printed headline numbers are compared to
#                   reproduce/headline_expectations.tsv
#   5. S:           scripts/166_sign_convention.py (no model, seconds)
#   6. M, U, G:     reported as NOT-RUN here by default, because 167/168/169 each
#                   need inputs this archive may not carry; run them with --only.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/venv/bin/python3"
RUNS="$REPO/reproduce/runs"
EXPECT="$REPO/reproduce/headline_expectations.tsv"
mkdir -p "$RUNS"

QUICK=0
ONLY="inputs,indep,S,N,L"
for a in "$@"; do
  case "$a" in
    --quick) QUICK=1 ;;
    --only=*) ONLY="${a#--only=}" ;;
    --only) shift; ONLY="${1:-}" ;;
  esac
done
if [ "$QUICK" = "1" ]; then
  export N_BOOT=300 N_SIM=100 N_STAB=200
else
  export N_BOOT="${N_BOOT:-10000}" N_SIM="${N_SIM:-1000}" N_STAB="${N_STAB:-2000}"
fi
export SEED="${SEED:-0}"

FAILED=0
step() { printf '\n=== %s ===\n' "$1"; }
want() { case ",$ONLY," in *,"$1",*) return 0 ;; *) return 1 ;; esac; }
note_fail() { FAILED=$((FAILED+1)); printf '  [FAIL] %s\n' "$1"; }
note_pass() { printf '  [PASS] %s\n' "$1"; }

printf '########################################################################\n'
printf '# rebuild_headlines.sh   started %s\n' "$(date)"
printf '# repo=%s\n# N_BOOT=%s N_SIM=%s N_STAB=%s SEED=%s   modules=%s\n' \
  "$REPO" "$N_BOOT" "$N_SIM" "$N_STAB" "$SEED" "$ONLY"
printf '########################################################################\n'

# ---------------------------------------------------------------- 1. environment
step "1. ENVIRONMENT"
if [ ! -x "$PY" ]; then
  note_fail "venv/bin/python3 missing -- the project interpreter (AGENTS 1)"
  printf 'FATAL: cannot continue without %s\n' "$PY"; exit 1
fi
note_pass "venv/bin/python3 present: $("$PY" -c 'import sys;print(sys.version.split()[0])')"
if [ -f reproduce/requirements.lock ]; then
  "$PY" -m pip freeze > "$RUNS/requirements.now.lock" 2>/dev/null
  if diff -q reproduce/requirements.lock "$RUNS/requirements.now.lock" >/dev/null; then
    note_pass "pip freeze matches reproduce/requirements.lock exactly"
  else
    printf '  [WARN] pip freeze DIFFERS from reproduce/requirements.lock:\n'
    diff reproduce/requirements.lock "$RUNS/requirements.now.lock" | head -20 | sed 's/^/    /'
  fi
fi
"$PY" - << 'PYEOF'
import importlib
for m in ("numpy", "pandas", "scipy", "sklearn", "patsy", "statsmodels", "openpyxl"):
    try:
        mod = importlib.import_module(m)
        print(f"  [ok]   {m} {getattr(mod, '__version__', '?')}")
    except Exception as e:
        print(f"  [MISS] {m}: {type(e).__name__}")
PYEOF

# ---------------------------------------------------------------- 2. inputs
step "2. INPUTS (every headline number depends on these)"
if want inputs; then
  MISSING=0
  while IFS='|' read -r path why extra; do
    case "$path" in \#*|"") continue ;; esac
    if [ -e "$path" ]; then
      printf '  [ok]   %s\n' "$path"
      # OPTIONAL third field "bg_files=N" (added for the night-B ladder columns): a
      # COUNT check, because "[ -e dir ]" alone would still pass with 96 of 97
      # background files present.  Two-field lines are unaffected -- extra is empty
      # and this block is skipped for them.
      case "$extra" in
        bg_files=*)
          want_n="${extra#bg_files=}"
          got_n=$(ls "$path"/bg_*.csv 2>/dev/null | wc -l | tr -d ' ')
          if [ "$got_n" -eq "$want_n" ]; then
            printf '  [ok]   %s: %s bg_*.csv (expected %s)\n' "$path" "$got_n" "$want_n"
          else
            printf '  [MISS] %s: %s bg_*.csv, expected %s\n' "$path" "$got_n" "$want_n"
            MISSING=$((MISSING+1))
          fi ;;
      esac
    else
      printf '  [MISS] %s   <- %s\n' "$path" "$why"; MISSING=$((MISSING+1))
    fi
  done < reproduce/required_inputs.tsv
  printf '  %s required input(s) missing\n' "$MISSING"
  [ "$MISSING" -gt 0 ] && printf '  [NOTE] the checks that need a missing input will report\n' \
     '         NOT-COMPUTABLE rather than a wrong number. Restore it from\n' \
     '         data/processed/DATA_SHA256_MANIFEST.txt-listed copies.\n'
fi

# ---------------------------------------------------------------- 3. independent recompute
step "3. INDEPENDENT RECOMPUTE (scripts/176, no staged Phase-4 script called)"
if want indep; then
  if [ -f scripts/176_phase4b_independent_recompute.py ]; then
    "$PY" scripts/176_phase4b_independent_recompute.py --modules S,N,L,M,U,G \
        > "$RUNS/independent_recompute.txt" 2>&1
    echo "  output: reproduce/runs/independent_recompute.txt"
    grep -E "comparisons gated" "$RUNS/independent_recompute.txt" | sed 's/^/  /'
    ND=$(grep -c "^    \[DIFF\]" "$RUNS/independent_recompute.txt")
    NK=$(grep -c "^    \[DIFF\] M-2 " "$RUNS/independent_recompute.txt")
    NEW=$((ND-NK))
    if [ "$ND" -eq 0 ]; then
      note_pass "independent recompute: no disagreements with the staged outputs"
    elif [ "$NEW" -eq 0 ]; then
      note_pass "independent recompute: $ND disagreement(s), all of them the ONE documented \
exception (M-2 stratified rho, 3.198e-05, unresolved; see PHASE4B_MORNING_LOG.md [C2] Finding 3)"
    else
      note_fail "independent recompute: $NEW NEW disagreement(s) beyond the documented M-2 one"
      grep "^    \[DIFF\]" "$RUNS/independent_recompute.txt" | grep -v "M-2 " | sed 's/^/        /'
    fi
  else
    note_fail "scripts/176_phase4b_independent_recompute.py is missing"
  fi
fi

# ---------------------------------------------------------------- 4/5. staged analyses
run_and_check () {   # $1 = label, $2 = script, $3 = log-file; expectations on stdin
  local label="$1"; shift
  local script="$1"; shift
  local out="$1"; shift
  if ! want "$label"; then return; fi
  if [ ! -f "$script" ]; then note_fail "$label: $script missing"; return; fi
  "$PY" "$script" > "$out" 2>&1
  local rc=$?
  printf '  %s -> %s (exit %s)\n' "$script" "${out#$REPO/}" "$rc"
  # Each expectation line: NAME ; SED-REGEX-with-one-group ; EXPECTED
  # sed is used (not grep -o) because only sed can return a CAPTURE GROUP, and the
  # field separator is ';' because these regexes contain '|' themselves.
  while IFS=';\' read -r name rex exp; do
    case "$name" in \#*|"") continue ;; esac
    local got
    got=$(sed -nE "s#.*${rex}.*#\\1#p" "$out" | head -1)
    got=${got%% *}
    if [ -z "$got" ]; then
      note_fail "$label / $name: pattern not found in the output (regex: $rex)"
    elif [ "$got" = "$exp" ]; then
      note_pass "$label / $name = $got"
    else
      note_fail "$label / $name: got '$got', expected '$exp'"
    fi
  done
}

step "4. MODULE N (scripts/172, neighbour arm) and MODULE L (scripts/174, ladder)"
run_and_check N scripts/172_neigh_analysis.py "$RUNS/172_neigh_analysis.txt" << 'EOF'
rho_A222V on H;rho_A222V = (-?[0-9.]+);-0.090021683
p_NB(neg);p_NB[(]neg[)] = ([0-9.]+);0.127660
count at or below;p_NB[(]neg[)] = [0-9.]+ *[(]1 [+] ([0-9]+)[)]/[(]1 [+] 46[)];5
section-5 word;WORD: (REGION-LIKE[POSITION-SPECIFIC]*|UNRESOLVED|UNDERPOWERED);REGION-LIKE
d3 flexible partial;partial rho_b ~ d3 *[|] *spline[(]dseq[)]: *([+-][0-9.]+);+0.192294
dseq flexible partial;partial rho_b ~ dseq *[|] *spline[(]d3[)] *: *([+-][0-9.]+);-0.053758
section-6 word;WORD: (BOTH-LOCAL|3D-LOCAL|SEQUENCE-LOCAL|NEITHER-RESOLVED);NEITHER-RESOLVED
cell mean C2;C2: n=[0-9]+ mean=([+-][0-9.]+);-0.035857
EOF
run_and_check L scripts/174_ladder_analysis.py "$RUNS/174_ladder_analysis.txt" << 'EOF'
650M rho_A222V on H;[(]i[)] *rho_A222V on H = (-?[0-9.]+);-0.090021683
650M p_spec_H(neg);p_spec_H[(]neg[)] = ([0-9.]+);0.050633
650M gradient;gradient Spearman.* = ([+-][0-9.]+);+0.713319
650M confound;shift confound.* = ([+-][0-9.]+);-0.612697
650M word;WORD [(]650M[)]: ([A-Z-]+);MODEL-REPLICATES
150M word;WORD [(]150M[)]: ([A-Z-]+);MODEL-DOES-NOT-REPLICATE
35M word;WORD [(]35M[)]: ([A-Z-]+);MODEL-DOES-NOT-REPLICATE
650-150M per-background median;650M vs 150M:.*median ([+-][0-9.]+);+0.086725
650-150M across-background rho;650M vs 150M:.*between rho_b: ([+-][0-9.]+);-0.145645
650-35M per-background median;650M vs 35M:.*median ([+-][0-9.]+);+0.071303
650-35M across-background rho;650M vs 35M:.*between rho_b: ([+-][0-9.]+);+0.381036
EOF

step "5. MODULE S (scripts/166, sign convention)"
run_and_check S scripts/166_sign_convention.py "$RUNS/166_sign_convention.txt" << 'EOF'
checks PASS;A3 SUMMARY: ([0-9]+) checks PASS;49
EOF

step "6. MODULES M, U, G -- not run by default"
for m in M U G; do
  if want "$m"; then
    case "$m" in
      M) s=scripts/167_mech_anchor.py ;;
      U) s=scripts/168_utility.py ;;
      G) s=scripts/169_gb1_locality.py ;;
    esac
    if [ -f "$s" ]; then
      printf '  running %s (this is the long one; N_BOOT=%s)\n' "$s" "$N_BOOT"
      "$PY" "$s" > "$RUNS/$(basename "$s" .py).txt" 2>&1
      printf '  -> reproduce/runs/%s.txt (exit %s); its own PASS/FAIL table is in the file\n' \
        "$(basename "$s" .py)" "$?"
      grep -E "GATE (PASS|FAIL)|RESULT" "$RUNS/$(basename "$s" .py).txt" | tail -3 | sed 's/^/    /'
    else
      note_fail "$m: $s missing"
    fi
  else
    printf '  module %s: skipped (not in --only). Its frozen words are in the logs:\n' "$m"
    printf '    M-1 PARTIAL-SURVIVES, M-3 EXCESS-OVER-ARTIFACT, M-5 WITHIN-CARRIED, M-6 MODERATE\n'
    printf '    U-1 CONDITIONING-HURTS, U-2 UNVERIFIED-LABELS (no word)\n'
    printf '    G-1 MODEL-DECAYS + LOCALITY-DIFFERS fire, DATA-DECAYS does not; G-2 SEPARATION-MATTERS; G-3 SKIPPED\n'
  fi
done

# ---------------------------------------------------------------- summary
step "SUMMARY"
printf '  checks failed: %s\n' "$FAILED"
printf '  logs: %s\n' "${RUNS#$REPO/}/"
printf '  finished %s\n' "$(date)"
if [ "$FAILED" -eq 0 ]; then
  printf '\nRESULT: PASS -- every requested check reproduced its logged value.\n'
  exit 0
fi
printf '\nRESULT: FAIL -- %s check(s) did not reproduce. Read the [FAIL] lines above;\n' "$FAILED"
printf '        do NOT adjust the expectations to make them pass (AGENTS 0).\n'
exit 1