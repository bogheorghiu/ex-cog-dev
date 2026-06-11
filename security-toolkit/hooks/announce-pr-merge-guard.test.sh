#!/bin/bash
# Tests for announce-pr-merge-guard.sh — the one-time SessionStart notice.
#
# These prove the once-ever behavior deterministically: first run emits the
# notice AND writes the sentinel; second run (sentinel present) emits nothing;
# both exit 0. What they do NOT prove is that the live harness actually injects
# a SessionStart hook's stdout into the model context — that is the same
# load-bearing assumption vasana-system/hooks/vasana.sh rests on, confirmable
# only in a real installed session.

set -u

HOOK="$(dirname "$0")/announce-pr-merge-guard.sh"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
export EXCOG_PR_MERGE_INTRO_SENTINEL="$TMP_DIR/.introduced"

pass=0
fail=0
check() {
    local name="$1" cond="$2"
    if [ "$cond" = "1" ]; then
        echo "  ok   - $name"; pass=$((pass + 1))
    else
        echo "  FAIL - $name"; fail=$((fail + 1))
    fi
}

echo "Testing announce-pr-merge-guard.sh"
echo "===================================="

# --- First run: no sentinel yet ---
out1=$(echo '{"hook_event_name":"SessionStart"}' | bash "$HOOK"); rc1=$?
check "first run exits 0" "$([ "$rc1" -eq 0 ] && echo 1 || echo 0)"
check "first run emits the notice" "$(echo "$out1" | grep -q 'PR-merge guard' && echo 1 || echo 0)"
check "first run mentions /pr-merge-guard on" "$(echo "$out1" | grep -q '/pr-merge-guard on' && echo 1 || echo 0)"
check "first run creates the sentinel" "$([ -f "$EXCOG_PR_MERGE_INTRO_SENTINEL" ] && echo 1 || echo 0)"

# --- Second run: sentinel now present ---
out2=$(echo '{"hook_event_name":"SessionStart"}' | bash "$HOOK"); rc2=$?
check "second run exits 0" "$([ "$rc2" -eq 0 ] && echo 1 || echo 0)"
check "second run emits nothing" "$([ -z "$out2" ] && echo 1 || echo 0)"

# --- Third run, still silent (idempotent) ---
out3=$(echo '{"hook_event_name":"SessionStart"}' | bash "$HOOK"); rc3=$?
check "third run still silent" "$([ -z "$out3" ] && [ "$rc3" -eq 0 ] && echo 1 || echo 0)"

echo "===================================="
echo "Results: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
