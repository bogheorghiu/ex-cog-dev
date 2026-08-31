#!/bin/bash
# Twin: vasana-system/hooks/count-skill-firings.sh — keep logic-identical (repo convention on twin copies).
# The one intended difference is the PLUGIN constant below, exactly as the twin skill linters differ only in a banner.
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
#   {timestamp, session_id, skill, cwd, plugin}
# Override the path with SKILL_FIRINGS_LOG (the test uses this).
#
# ONE WRITER PER SESSION, and why it exists:
# This hook ships in more than one plugin, and each registers it on
# PreToolUse with matcher "Skill". With two of them installed, a single
# firing produced two near-identical lines — so every count read off this log
# was doubled, and the tail-bounded readers (firing_filter.py reads the last
# 4000 lines) saw half the history they believed they had. Neither plugin can
# see the other's hooks, so the fix is a claim rather than coordination: the
# first hook to run in a session atomically creates a claim file naming
# itself, and only that named owner writes for the rest of the session. Both
# hooks match exactly the same event, so a single writer yields one line per
# firing however many copies are installed.
#
# The claim is per session, not permanent, because a permanent one would fail
# silently: uninstall the winning plugin and counting would simply stop, which
# is indistinguishable from "no skills fired". Per session, that costs at most
# the remainder of one session.
#
# Two cases deliberately fall back to counting twice rather than risk counting
# nothing, both marked at the code below: an event carrying no session id (no
# session to scope a claim to), and a claim that cannot be created or read at
# all. Doubling is visible in the log and can be divided out; silence reads
# exactly like a skill that never fired, which is the reading this hook exists
# to make impossible.
#
# The `plugin` field is what makes the election observable. Without it a
# reader cannot tell which copy produced a line, and "only one of them logs"
# becomes invisible behaviour — the fail-silent shape this hook exists to
# avoid. It is additive: existing readers key on the fields they already know.

set -u

# The single intended divergence between the twin copies.
PLUGIN="research-toolkit"

LOG_FILE="${SKILL_FIRINGS_LOG:-${HOME}/.claude/logs/skill-firings.log}"
LOG_DIR="$(dirname "$LOG_FILE")"
mkdir -p "$LOG_DIR"

input=$(cat)
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

emit_passthrough() { printf '{}'; }

if ! command -v jq &> /dev/null; then
    # No-jq fallback: can't attribute the skill, but still count the firing
    # with a valid JSON line so the numerator stays correct. jq is a hard
    # requirement for this hook ecosystem in practice (see security-toolkit).
    #
    # Honest limit: this path cannot run the election, because the session id
    # it would key on is inside the JSON we have no parser for. So with two
    # plugins installed AND jq missing, firings double here as they did
    # everywhere before. Left rather than papered over with regex JSON
    # parsing: this is already a degraded path that cannot name the skill,
    # and a wrong session id would mis-elect on the healthy path too.
    printf '{"timestamp":"%s","skill":"unknown","plugin":"%s","note":"jq unavailable"}\n' \
        "$timestamp" "$PLUGIN" >> "$LOG_FILE"
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

# --- Writer election (see header) ------------------------------------------
# SKILL_FIRINGS_PLUGIN lets a test stand in as a second plugin without needing
# the sibling plugin on disk, mirroring what SKILL_FIRINGS_LOG already does for
# the log path. Production never sets it.
me="${SKILL_FIRINGS_PLUGIN:-$PLUGIN}"
# Elect on the install location as well as the name. Two installs of the SAME
# plugin — a marketplace copy and a local checkout, say — would otherwise both
# match a claim naming that plugin and both write, reproducing the very
# doubling this election exists to remove, and invisibly, because the two lines
# would be identical. Where the harness exports no root, this degrades to the
# name and behaves as it would have anyway.
me_id="$me|${CLAUDE_PLUGIN_ROOT:-}"

# The session id reaches us as untrusted JSON and is about to become part of a
# path, so reduce it to characters that cannot traverse or escape a directory.
claim_key=$(printf '%s' "$session_id" | tr -c 'A-Za-z0-9._-' '_')
# "." and ".." survive that filter but name the claim directory itself rather
# than a file inside it, so no claim could ever be created.
case "$claim_key" in
    "." | "..") claim_key="" ;;
esac

# Default to writing. Every branch below can only take that away, and only on
# positive evidence that another copy owns this session.
write=1

if [ -n "$claim_key" ]; then
    claim_dir="$LOG_DIR/.skill-firings-writer"
    mkdir -p "$claim_dir" 2>/dev/null
    claim="$claim_dir/$claim_key"
    tmp="$claim.tmp.$$"

    # Write the owner's name FIRST, then link it into place. `ln` fails if the
    # target exists, and the link is atomic, so the claim becomes visible only
    # once it already names its owner. Creating the file empty and filling it
    # afterwards would leave a window in which a rival reads an unowned claim.
    # The subshell is what silences a FAILED redirect: `> "$tmp" 2>/dev/null`
    # would only cover printf's own output, while the shell reports a path it
    # cannot open (name too long, disk full) on its own stderr before printf
    # runs at all. This hook must stay quiet on stderr — it is an observer.
    if ( printf '%s\n' "$me_id" > "$tmp" ) 2>/dev/null && ln "$tmp" "$claim" 2>/dev/null; then
        # Won it. Bound the directory's growth once per session, not per
        # firing. These are our own files in our own directory.
        find "$claim_dir" -maxdepth 1 -type f -mtime +7 -delete 2>/dev/null
    else
        owner=$(head -n 1 "$claim" 2>/dev/null || printf '')
        # ONLY a readable claim naming somebody else silences this copy. Every
        # other state — no claim at all (the create failed for its own reasons:
        # a name too long for the filesystem, a full or read-only disk), or a
        # claim left empty by an older version or a process killed mid-write —
        # falls through to writing. A duplicated line is visible in the log and
        # can be divided back out; silence is indistinguishable from "no skills
        # fired", which is the one reading this hook exists to make impossible.
        if [ -n "$owner" ] && [ "$owner" != "$me_id" ]; then
            write=0
        fi
    fi
    rm -f "$tmp" 2>/dev/null
fi
# No usable session id means there is no session to scope a claim to. Electing
# on a fixed stand-in key would make the claim permanent rather than per
# session: the first copy ever to run would own the log for good, and
# uninstalling it would end counting with nothing to show why. Counting a
# firing twice is the lesser fault, so this path does not elect at all.

if [ "$write" != "1" ]; then
    emit_passthrough
    exit 0
fi

# Build the log line with jq so the dynamic values are always correctly
# escaped (skill names and cwd can contain characters that would break a
# hand-rolled printf JSON line).
jq -cn \
    --arg ts "$timestamp" \
    --arg sid "$session_id" \
    --arg skill "$skill" \
    --arg cwd "$cwd" \
    --arg plugin "$me" \
    '{timestamp:$ts, session_id:$sid, skill:$skill, cwd:$cwd, plugin:$plugin}' \
    >> "$LOG_FILE"

emit_passthrough
exit 0
