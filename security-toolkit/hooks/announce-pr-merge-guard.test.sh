#!/bin/bash
# Tests for announce-pr-merge-guard.sh — the one-time SessionStart notice.
#
# These prove two things deterministically:
#   1. The context gate: the notice fires only on a recognized Claude Code
#      surface (CLAUDECODE=1 + an allowlisted CLAUDE_CODE_ENTRYPOINT) and stays
#      silent — without consuming the one-time sentinel — everywhere else
#      (Cowork / Dispatch / headless SDK).
#   2. The once-ever behavior: first Code run emits the notice AND writes the
#      sentinel; later runs (sentinel present) emit nothing; all exit 0.
#
# What they do NOT prove is that the live harness actually injects a SessionStart
# hook's stdout into the model context — that is the same load-bearing assumption
# vasana-system/hooks/vasana.sh rests on, confirmable only in a real installed
# session.

set -u

HOOK="$(dirname "$0")/announce-pr-merge-guard.sh"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
SENTINEL="$TMP_DIR/.introduced"

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

# Run the hook with a clean, explicit environment so the test controls every
# signal the gate reads. Args: KEY=VALUE ... ; reads SessionStart JSON on stdin.
run_hook() {
    rm -f "$SENTINEL"
    echo '{"hook_event_name":"SessionStart"}' | \
        env -i HOME="$TMP_DIR" PATH="$PATH" \
            EXCOG_PR_MERGE_INTRO_SENTINEL="$SENTINEL" \
            "$@" \
            bash "$HOOK"
}

echo "Testing announce-pr-merge-guard.sh"
echo "===================================="

# --- Context gate: silent on non-Code surfaces, sentinel untouched ---

# Cowork / generic SDK: CLAUDECODE unset entirely.
out=$(run_hook); rc=$?
check "non-Code (no CLAUDECODE) is silent" "$([ -z "$out" ] && echo 1 || echo 0)"
check "non-Code exits 0" "$([ "$rc" -eq 0 ] && echo 1 || echo 0)"
check "non-Code does NOT write the sentinel" "$([ ! -f "$SENTINEL" ] && echo 1 || echo 0)"

# CLAUDECODE=1 but an unrecognized entrypoint (e.g. a future SDK value).
out=$(run_hook CLAUDECODE=1 CLAUDE_CODE_ENTRYPOINT=sdk); rc=$?
check "unrecognized entrypoint is silent" "$([ -z "$out" ] && echo 1 || echo 0)"
check "unrecognized entrypoint no sentinel" "$([ ! -f "$SENTINEL" ] && echo 1 || echo 0)"

# CLAUDECODE=1 but no entrypoint at all → not recognized → silent.
out=$(run_hook CLAUDECODE=1); rc=$?
check "missing entrypoint is silent" "$([ -z "$out" ] && echo 1 || echo 0)"

# Cowork: CLAUDE_CODE_IS_COWORK=1 forces silence even with CLAUDECODE=1 and an
# otherwise-allowlisted entrypoint (proves the explicit exclusion wins over the
# allowlist, so the gate holds if Cowork's entrypoint ever drifts).
out=$(run_hook CLAUDECODE=1 CLAUDE_CODE_ENTRYPOINT=cli CLAUDE_CODE_IS_COWORK=1); rc=$?
check "Cowork (CLAUDE_CODE_IS_COWORK set) is silent" "$([ -z "$out" ] && echo 1 || echo 0)"
check "Cowork does NOT write the sentinel" "$([ ! -f "$SENTINEL" ] && echo 1 || echo 0)"

# Dispatch: even with an otherwise-allowlisted entrypoint, CLAUDE_CODE_BRIEF
# forces silence (Dispatch is the autonomous Desktop agent, never interactive).
out=$(run_hook CLAUDECODE=1 CLAUDE_CODE_ENTRYPOINT=cli CLAUDE_CODE_BRIEF=1); rc=$?
check "Dispatch (CLAUDE_CODE_BRIEF set) is silent" "$([ -z "$out" ] && echo 1 || echo 0)"
check "Dispatch does NOT write the sentinel" "$([ ! -f "$SENTINEL" ] && echo 1 || echo 0)"

# The real Dispatch signature (from a live env dump): CLAUDECODE=1,
# entrypoint=local-agent, plus BRIEF and IS_COWORK both set.
out=$(run_hook CLAUDECODE=1 CLAUDE_CODE_ENTRYPOINT=local-agent CLAUDE_CODE_BRIEF=1 CLAUDE_CODE_IS_COWORK=1); rc=$?
check "real Dispatch signature is silent" "$([ -z "$out" ] && echo 1 || echo 0)"

# --- Recognized Code surfaces announce ---

# Terminal CLI.
out=$(run_hook CLAUDECODE=1 CLAUDE_CODE_ENTRYPOINT=cli); rc=$?
check "cli entrypoint exits 0" "$([ "$rc" -eq 0 ] && echo 1 || echo 0)"
check "cli entrypoint emits the notice" "$(echo "$out" | grep -q 'PR-merge guard' && echo 1 || echo 0)"
check "cli entrypoint mentions /pr-merge-guard on" "$(echo "$out" | grep -q '/pr-merge-guard on' && echo 1 || echo 0)"
check "cli entrypoint creates the sentinel" "$([ -f "$SENTINEL" ] && echo 1 || echo 0)"

# Claude Code on the web / mobile (remote execution).
out=$(run_hook CLAUDECODE=1 CLAUDE_CODE_ENTRYPOINT=remote_mobile); rc=$?
check "remote_* entrypoint emits the notice" "$(echo "$out" | grep -q 'PR-merge guard' && echo 1 || echo 0)"

# --- Once-ever: a second Code run with the sentinel present stays silent ---
# (run_hook clears the sentinel, so drive this case by hand to keep it across runs.)
rm -f "$SENTINEL"
base_env=(env -i HOME="$TMP_DIR" PATH="$PATH" EXCOG_PR_MERGE_INTRO_SENTINEL="$SENTINEL" CLAUDECODE=1 CLAUDE_CODE_ENTRYPOINT=cli)
out1=$(echo '{"hook_event_name":"SessionStart"}' | "${base_env[@]}" bash "$HOOK"); rc1=$?
out2=$(echo '{"hook_event_name":"SessionStart"}' | "${base_env[@]}" bash "$HOOK"); rc2=$?
out3=$(echo '{"hook_event_name":"SessionStart"}' | "${base_env[@]}" bash "$HOOK"); rc3=$?
check "first Code run emits the notice" "$(echo "$out1" | grep -q 'PR-merge guard' && echo 1 || echo 0)"
check "first Code run creates the sentinel" "$([ -f "$SENTINEL" ] && echo 1 || echo 0)"
check "second Code run emits nothing" "$([ -z "$out2" ] && [ "$rc2" -eq 0 ] && echo 1 || echo 0)"
check "third Code run still silent" "$([ -z "$out3" ] && [ "$rc3" -eq 0 ] && echo 1 || echo 0)"

echo "===================================="
echo "Results: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
