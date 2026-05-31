#!/bin/bash
# Test suite for block-dc-config.sh and block-dc-execute.sh hooks.
# Run: bash block-dc.test.sh
#
# These PreToolUse hooks block Desktop Commander's config-mutation and
# command-execution tools (both the "desktop-commander" and "desktopcommander"
# server-name spellings). A blocked call exits 2 and prints a JSON decision;
# any other tool exits 0 silently.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_HOOK="$SCRIPT_DIR/block-dc-config.sh"
EXECUTE_HOOK="$SCRIPT_DIR/block-dc-execute.sh"

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
NC=$'\033[0m'

PASSED=0
FAILED=0

# Assert the hook exits with the expected code (0 allow, 2 block).
test_exit() {
    local name="$1" hook="$2" input="$3" expected_exit="$4"
    local exit_code=0
    echo "$input" | bash "$hook" >/dev/null 2>&1 || exit_code=$?
    if [[ "$exit_code" -eq "$expected_exit" ]]; then
        echo -e "${GREEN}pass${NC} $name"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} $name (expected exit $expected_exit, got $exit_code)"
        FAILED=$((FAILED + 1))
    fi
}

# Assert that a blocked call emits a JSON block decision.
test_blocks_with_reason() {
    local name="$1" hook="$2" input="$3"
    local out
    out=$(echo "$input" | bash "$hook" 2>/dev/null)
    if [[ "$out" == *'"decision": "block"'* ]]; then
        echo -e "${GREEN}pass${NC} $name"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} $name (no block decision in output)"
        FAILED=$((FAILED + 1))
    fi
}

echo "--- block-dc-config.sh ---"
test_exit "config: set_config_value (desktop-commander) blocked" "$CONFIG_HOOK" \
    '{"tool_name":"mcp__desktop-commander__set_config_value"}' 2
test_exit "config: set_config_value (desktopcommander) blocked" "$CONFIG_HOOK" \
    '{"tool_name":"mcp__desktopcommander__set_config_value"}' 2
test_blocks_with_reason "config: emits block decision JSON" "$CONFIG_HOOK" \
    '{"tool_name":"mcp__desktop-commander__set_config_value"}'
test_exit "config: get_config_value allowed" "$CONFIG_HOOK" \
    '{"tool_name":"mcp__desktop-commander__get_config_value"}' 0
test_exit "config: unrelated DC read tool allowed" "$CONFIG_HOOK" \
    '{"tool_name":"mcp__desktop-commander__read_file"}' 0
test_exit "config: non-DC tool allowed" "$CONFIG_HOOK" \
    '{"tool_name":"Bash"}' 0
test_exit "config: empty input allowed" "$CONFIG_HOOK" '{}' 0

echo ""
echo "--- block-dc-execute.sh ---"
test_exit "execute: start_process (desktop-commander) blocked" "$EXECUTE_HOOK" \
    '{"tool_name":"mcp__desktop-commander__start_process"}' 2
test_exit "execute: execute_command (desktop-commander) blocked" "$EXECUTE_HOOK" \
    '{"tool_name":"mcp__desktop-commander__execute_command"}' 2
test_exit "execute: start_process (desktopcommander) blocked" "$EXECUTE_HOOK" \
    '{"tool_name":"mcp__desktopcommander__start_process"}' 2
test_exit "execute: execute_command (desktopcommander) blocked" "$EXECUTE_HOOK" \
    '{"tool_name":"mcp__desktopcommander__execute_command"}' 2
test_blocks_with_reason "execute: emits block decision JSON" "$EXECUTE_HOOK" \
    '{"tool_name":"mcp__desktop-commander__start_process"}'
test_exit "execute: read_file (DC, non-exec) allowed" "$EXECUTE_HOOK" \
    '{"tool_name":"mcp__desktop-commander__read_file"}' 0
test_exit "execute: non-DC tool allowed" "$EXECUTE_HOOK" \
    '{"tool_name":"Bash"}' 0
test_exit "execute: empty input allowed" "$EXECUTE_HOOK" '{}' 0

echo ""
echo "====================================="
echo -e "Results: ${GREEN}${PASSED} passed${NC}, ${RED}${FAILED} failed${NC}"
[[ "$FAILED" -eq 0 ]] || exit 1
