#!/bin/bash
# Twin: vasana-system/hooks/count-skill-firings.test.sh — keep logic-identical (repo convention on twin copies).
# Tests for count-skill-firings.sh — the skill-firing counter hook.
#
# These prove the *measurement* works end to end on a known event: given a
# synthetic Skill PreToolUse envelope, the hook appends exactly one correctly
# attributed JSONL line; given a non-Skill envelope, it appends nothing. This
# is the "explicit call to verify it works" check, made deterministic.
#
# Section 6 covers the writer election: this hook ships in more than one
# plugin, each registering it on the same PreToolUse/Skill event, so before
# the election a single firing wrote one line per installed copy and every
# count read off the log was doubled. Those tests stand a second plugin up
# via SKILL_FIRINGS_PLUGIN and assert one line per firing regardless.
#
# Sections 7 and 8 pin the election's two hard edges: it must never trade a
# doubled count for a silent one (an unusable claim degrades to counting), and
# two installs of the same plugin must be two candidates rather than one name
# matching itself.
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
# The election persists a claim per session beside the log; a test that wants a
# clean slate has to drop that too, or it inherits the previous test's winner.
reset_all() { rm -f "$SKILL_FIRINGS_LOG"; rm -rf "$(dirname "$SKILL_FIRINGS_LOG")/.skill-firings-writer"; }
fire() { echo "$2" | SKILL_FIRINGS_PLUGIN="$1" bash "$HOOK" > /dev/null; }
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

# --- 6. One writer per session, however many plugins are installed ---------
# Two copies of this hook, both matching PreToolUse/Skill, both handed the
# same event. Before the election this wrote two lines and doubled the count.
reset_all
ev='{"tool_name":"Skill","session_id":"sess-collide","cwd":"/repo","tool_input":{"command":"cui-bono"}}'
fire "plugin-a" "$ev"
fire "plugin-b" "$ev"
check "two plugins, one firing writes exactly one line" \
    "$([ "$(log_lines)" = "1" ] && echo 1 || echo 0)"
check "the surviving line names the plugin that won" \
    "$(grep -q '"plugin":"plugin-a"' "$SKILL_FIRINGS_LOG" && echo 1 || echo 0)"
check "the losing plugin wrote nothing" \
    "$(grep -q '"plugin":"plugin-b"' "$SKILL_FIRINGS_LOG" && echo 0 || echo 1)"

# Order must not matter: whoever arrives first owns the session.
reset_all
fire "plugin-b" "$ev"
fire "plugin-a" "$ev"
check "election is first-come, not alphabetical" \
    "$(grep -q '"plugin":"plugin-b"' "$SKILL_FIRINGS_LOG" && echo 1 || echo 0)"

# The winner keeps counting; the loser stays silent for the whole session.
reset_all
ev2='{"tool_name":"Skill","session_id":"sess-collide","tool_input":{"command":"dialectic-spiral"}}'
fire "plugin-a" "$ev"
fire "plugin-b" "$ev"
fire "plugin-a" "$ev2"
fire "plugin-b" "$ev2"
check "two firings x two plugins still yields two lines" \
    "$([ "$(log_lines)" = "2" ] && echo 1 || echo 0)"

# A claim is scoped to its session, so a later session can elect anyone. A
# permanent claim would mean uninstalling the winner silently ends all
# counting, which is indistinguishable from "no skills fired".
reset_all
fire "plugin-a" "$ev"
other='{"tool_name":"Skill","session_id":"sess-other","tool_input":{"command":"kernel-shell"}}'
fire "plugin-b" "$other"
check "a different session elects independently" \
    "$([ "$(log_lines)" = "2" ] && echo 1 || echo 0)"
check "the second session's winner is recorded" \
    "$(grep -q '"plugin":"plugin-b"' "$SKILL_FIRINGS_LOG" && echo 1 || echo 0)"

# A session id arrives as untrusted JSON and becomes part of a claim path.
reset_all
evil='{"tool_name":"Skill","session_id":"../../escape","tool_input":{"command":"x"}}'
fire "plugin-a" "$evil"
check "a traversal-shaped session id still logs one line" \
    "$([ "$(log_lines)" = "1" ] && echo 1 || echo 0)"
claim_dir="$TMP_DIR/.skill-firings-writer"
check "the claim stayed inside its own directory" \
    "$([ "$(find "$claim_dir" -mindepth 1 | wc -l | tr -d ' ')" = "1" ] && echo 1 || echo 0)"
check "no path component escaped into the log directory" \
    "$([ ! -e "$TMP_DIR/escape" ] && echo 1 || echo 0)"

# "." and ".." survive filename sanitisation but would name the claim directory
# itself, so the claim could never be created and counting would stop silently.
reset_all
dotdot='{"tool_name":"Skill","session_id":"..","tool_input":{"command":"x"}}'
fire "plugin-a" "$dotdot"
check "a dot-dot session id still logs its firing" \
    "$([ "$(log_lines)" = "1" ] && echo 1 || echo 0)"

# Single-plugin installs must be untouched by any of this.
reset_all
fire "solo-plugin" "$ev"
fire "solo-plugin" "$ev2"
check "one plugin alone still counts every firing" \
    "$([ "$(log_lines)" = "2" ] && echo 1 || echo 0)"

# --- 7. The election never trades a doubled count for a silent one ---------
# Every failure below used to silence the hook for a whole session, which is
# indistinguishable from "no skills fired" — the one reading this log exists
# to rule out. Each must degrade to writing instead.

# A claim left empty: an older version's file, or a winner killed mid-write.
reset_all
mkdir -p "$TMP_DIR/.skill-firings-writer"
: > "$TMP_DIR/.skill-firings-writer/sess-empty"
empty='{"tool_name":"Skill","session_id":"sess-empty","tool_input":{"command":"x"}}'
fire "plugin-a" "$empty"
fire "plugin-a" "$empty"
check "an empty claim degrades to counting, not to silence" \
    "$([ "$(log_lines)" = "2" ] && echo 1 || echo 0)"

# A session id too long to be a filename: the claim cannot be created at all.
reset_all
longid=$(printf 'x%.0s' $(seq 1 900))
long="{\"tool_name\":\"Skill\",\"session_id\":\"$longid\",\"tool_input\":{\"command\":\"x\"}}"
fire "plugin-a" "$long"
check "an unusable claim key still records the firing" \
    "$([ "$(log_lines)" = "1" ] && echo 1 || echo 0)"

# No session id at all. There is no session to scope a claim to, so this path
# deliberately does not elect: it counts twice rather than create a permanent
# claim that would end all counting the day its owner is uninstalled.
reset_all
none='{"tool_name":"Skill","tool_input":{"command":"x"}}'
fire "plugin-a" "$none"
fire "plugin-b" "$none"
check "a session-less firing counts rather than electing" \
    "$([ "$(log_lines)" = "2" ] && echo 1 || echo 0)"
check "a session-less firing leaves no permanent claim behind" \
    "$([ ! -d "$TMP_DIR/.skill-firings-writer" ] || [ -z "$(ls -A "$TMP_DIR/.skill-firings-writer")" ] && echo 1 || echo 0)"

# --- 8. Two installs of the SAME plugin are two candidates, not one --------
# A marketplace copy and a local checkout share a name, so a name-only claim
# matched itself and both wrote — the original bug, back and invisible,
# because both lines would read identically.
reset_all
CLAUDE_PLUGIN_ROOT=/install/a fire "same-name" "$ev"
CLAUDE_PLUGIN_ROOT=/install/b fire "same-name" "$ev"
check "same plugin at two install roots writes one line" \
    "$([ "$(log_lines)" = "1" ] && echo 1 || echo 0)"

# The converse: one install firing twice is two firings, not a rival.
reset_all
CLAUDE_PLUGIN_ROOT=/install/a fire "same-name" "$ev"
CLAUDE_PLUGIN_ROOT=/install/a fire "same-name" "$ev2"
check "one install firing twice still counts twice" \
    "$([ "$(log_lines)" = "2" ] && echo 1 || echo 0)"

echo
echo "count-skill-firings: $pass passed, $fail failed"
[ "$fail" = "0" ]
