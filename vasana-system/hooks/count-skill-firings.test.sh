#!/bin/bash
# Tests for count-skill-firings.sh — the skill-firing counter hook.
#
# These prove the *measurement* works end to end on a known event: given a
# synthetic Skill PreToolUse envelope, the hook appends exactly one correctly
# attributed JSONL line; given a non-Skill envelope, it appends nothing. This
# is the "explicit call to verify it works" check, made deterministic.
#
# What it does NOT prove: that the live harness actually emits PreToolUse
# events for the Skill tool. That can only be confirmed in a real installed
# session — it's the one load-bearing assumption this hook rests on.

set -u

HOOK="$(dirname "$0")/count-skill-firings.sh"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
export SKILL_FIRINGS_LOG="$TMP_DIR/skill-firings.log"

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

reset_log() { rm -f "$SKILL_FIRINGS_LOG"; }
log_lines() { [ -f "$SKILL_FIRINGS_LOG" ] && wc -l < "$SKILL_FIRINGS_LOG" | tr -d ' ' || echo 0; }

# --- 1. A Skill firing is recorded, with the skill name attributed ---------
reset_log
echo '{"tool_name":"Skill","session_id":"sess-123","cwd":"/repo","tool_input":{"command":"intrinsic-prompt-design","args":""}}' \
    | bash "$HOOK" > /dev/null
lines=$(log_lines)
check "Skill firing writes exactly one line" "$([ "$lines" = "1" ] && echo 1 || echo 0)"
line=$(cat "$SKILL_FIRINGS_LOG" 2>/dev/null)
check "line attributes the skill name" \
    "$(echo "$line" | grep -q '"skill":"intrinsic-prompt-design"' && echo 1 || echo 0)"
check "line records the session id" \
    "$(echo "$line" | grep -q '"session_id":"sess-123"' && echo 1 || echo 0)"
check "line is valid JSON" \
    "$(echo "$line" | jq -e . > /dev/null 2>&1 && echo 1 || echo 0)"

# --- 2. The 'skill' field name variant is also handled ---------------------
reset_log
echo '{"tool_name":"Skill","tool_input":{"skill":"deep-research"}}' | bash "$HOOK" > /dev/null
check "alternate .tool_input.skill field is read" \
    "$(grep -q '"skill":"deep-research"' "$SKILL_FIRINGS_LOG" && echo 1 || echo 0)"

# --- 3. Non-Skill tool calls are ignored (no false counts) -----------------
reset_log
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | bash "$HOOK" > /dev/null
check "Bash call writes no firing line" "$([ "$(log_lines)" = "0" ] && echo 1 || echo 0)"

reset_log
echo '{"tool_name":"Edit","tool_input":{"file_path":"/x"}}' | bash "$HOOK" > /dev/null
check "Edit call writes no firing line" "$([ "$(log_lines)" = "0" ] && echo 1 || echo 0)"

# --- 4. The hook is a pass-through observer (emits {} , exits 0) ------------
out=$(echo '{"tool_name":"Skill","tool_input":{"command":"x"}}' | bash "$HOOK"; echo "rc=$?")
check "emits empty-JSON passthrough and exits 0" \
    "$(echo "$out" | grep -q '{}rc=0' && echo 1 || echo 0)"

# --- 5. Two firings accumulate (counter, not overwrite) --------------------
reset_log
echo '{"tool_name":"Skill","tool_input":{"command":"a"}}' | bash "$HOOK" > /dev/null
echo '{"tool_name":"Skill","tool_input":{"command":"b"}}' | bash "$HOOK" > /dev/null
check "firings append (2 lines)" "$([ "$(log_lines)" = "2" ] && echo 1 || echo 0)"

echo
echo "count-skill-firings: $pass passed, $fail failed"
[ "$fail" = "0" ]
