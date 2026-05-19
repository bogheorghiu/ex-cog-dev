#!/bin/bash
# PreToolUse hook: Block Desktop Commander execute_command/start_process
# Matcher: mcp__desktop-commander.*|mcp__desktopcommander.*
#
# SECURITY RATIONALE:
# Desktop Commander's start_process bypasses all directory restrictions.
# Claude Code already has Bash tool which properly respects permissions.

# Read tool name from stdin JSON (CC hooks protocol)
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)

# Check if this is Desktop Commander's execution tool
# MCP tools use pattern: mcp__servername__toolname
if [[ "$TOOL_NAME" == "mcp__desktop-commander__start_process" ]] || \
   [[ "$TOOL_NAME" == "mcp__desktop-commander__execute_command" ]] || \
   [[ "$TOOL_NAME" == "mcp__desktopcommander__start_process" ]] || \
   [[ "$TOOL_NAME" == "mcp__desktopcommander__execute_command" ]]; then

    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 Desktop Commander execution tools are disabled for security.\n\nReason: start_process bypasses Claude Code's directory restrictions.\n\nPlease use Claude Code's Bash tool instead, which properly respects:\n- Allowed directories\n- Command permissions\n- Security policies"
}
EOF
    exit 2
fi

# Allow all other tools
exit 0
