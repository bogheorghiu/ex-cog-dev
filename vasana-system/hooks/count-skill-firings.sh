#!/bin/bash
# PreToolUse hook: count skill activations ("firings").
#
# A skill firing is the model invoking the `Skill` tool. This hook records
# each one as a JSONL line so activation can be measured across sessions —
# e.g. A/B testing whether a skill's description reliably auto-fires, which
# is exactly the question the intrinsic-prompt-design rewrite is trying to
# answer. A hook is the only vantage point that sees the decision the
# moment the model makes it.
#
# Why PreToolUse (not Post): the firing *decision* is the event of interest,
# and we want it recorded even if the skill body later errors. The hook is
# strictly an observer — it always exits 0 and emits empty JSON, never gates
# the tool.
#
# Scope note (honest): this counts firings (the numerator). It cannot see the
# turns where a skill *should* have fired and didn't — that denominator comes
# from running N controlled turns and comparing. And it counts both autonomous
# activations and explicit `/skill` invocations; distinguish them by not
# invoking explicitly during a measured run.
#
# Logs to ~/.claude/logs/skill-firings.log as JSONL:
#   {timestamp, session_id, skill, cwd}
# Override the path with SKILL_FIRINGS_LOG (the test uses this).

set -u

LOG_FILE="${SKILL_FIRINGS_LOG:-${HOME}/.claude/logs/skill-firings.log}"
mkdir -p "$(dirname "$LOG_FILE")"

input=$(cat)
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

emit_passthrough() { printf '{}'; }

if ! command -v jq &> /dev/null; then
    # No-jq fallback: can't attribute the skill, but still count the firing
    # with a valid JSON line so the numerator stays correct. jq is a hard
    # requirement for this hook ecosystem in practice (see security-toolkit).
    printf '{"timestamp":"%s","skill":"unknown","note":"jq unavailable"}\n' \
        "$timestamp" >> "$LOG_FILE"
    emit_passthrough
    exit 0
fi

tool_name=$(printf '%s' "$input" | jq -r '.tool_name // ""')

# Only record Skill-tool invocations. The hooks.json matcher should already
# scope this to "Skill", but double-checking means a mis-scoped matcher can't
# silently pollute the firing log with unrelated tool calls.
if [ "$tool_name" != "Skill" ]; then
    emit_passthrough
    exit 0
fi

session_id=$(printf '%s' "$input" | jq -r '.session_id // ""')
cwd=$(printf '%s' "$input" | jq -r '.cwd // ""')
# The skill-identifier field name has drifted across harness versions; check
# the known candidates in order and fall back to "unknown" rather than dropping
# the firing entirely.
skill=$(printf '%s' "$input" | jq -r '
    .tool_input.skill // .tool_input.command // .tool_input.name //
    .tool_input.skill_name // "unknown"')

# Build the log line with jq so the dynamic values are always correctly
# escaped (skill names and cwd can contain characters that would break a
# hand-rolled printf JSON line).
jq -cn \
    --arg ts "$timestamp" \
    --arg sid "$session_id" \
    --arg skill "$skill" \
    --arg cwd "$cwd" \
    '{timestamp:$ts, session_id:$sid, skill:$skill, cwd:$cwd}' \
    >> "$LOG_FILE"

emit_passthrough
exit 0
