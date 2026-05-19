#!/bin/bash
# PreToolUse hook: Block Desktop Commander config changes
# Matcher: mcp__desktop-commander.*|mcp__desktopcommander.*
#
# SECURITY RATIONALE:
# Prevents autonomous modification of DC settings.
# Config changes should require explicit user request.

# Read tool name from stdin JSON (CC hooks protocol)
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)

# MCP tools use pattern: mcp__servername__toolname
if [[ "$TOOL_NAME" == "mcp__desktop-commander__set_config_value" ]] || \
   [[ "$TOOL_NAME" == "mcp__desktopcommander__set_config_value" ]]; then
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 Desktop Commander config changes require explicit user request.\n\nThis prevents autonomous modification of security settings."
}
EOF
    exit 2
fi

exit 0
