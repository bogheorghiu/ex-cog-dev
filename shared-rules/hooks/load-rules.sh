#!/bin/bash
# SessionStart hook: print the shared Claude rules into context, for sessions that
# have no ~/.claude/rules of their own (cloud sessions, fresh containers).
#
# Must never block or fail the session: every failure falls through to exit 0.

# Settings come from the plugin's userConfig (plugin.json), which Claude Code exports
# to hooks as CLAUDE_PLUGIN_OPTION_<KEY>.
REPO_URL="${CLAUDE_PLUGIN_OPTION_RULES_REPO:-https://github.com/bogheorghiu/claude-rules}"
# Anything but "auto" means ask: an unrecognised value must fail toward consent.
MODE=ask; [ "${CLAUDE_PLUGIN_OPTION_UPDATE_MODE:-}" = auto ] && MODE=auto
CACHE="${CLAUDE_PLUGIN_DATA:-$HOME/.cache/shared-rules}/claude-rules"
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

# `load-rules.sh approve <sha>`: the user said yes to a pending update. Takes the sha
# the notice showed, not "latest", so a push landing after the notice can't ride
# along on an approval given for something else.
if [ "${1:-}" = approve ]; then
    if [ -n "${2:-}" ] && git -C "$CACHE" reset -q --hard "$2" 2>/dev/null; then
        echo "[shared-rules] Approved $2; these rules load from the next session on."
        exit 0
    fi
    echo "[shared-rules] Could not approve '${2:-}': not a version fetched into $CACHE." >&2
    exit 1
fi

# The local install already makes Claude Code load these rules natively;
# printing them again would put every rule in context twice. (-e, not -d: a
# submodule or worktree checkout has a .git *file*.)
[ -e "$HOME/.claude/rules/shared/.git" ] && exit 0

# A private or mistyped URL must fail, not wait at a credential prompt; a stalled
# transfer must end even where `timeout` is absent (stock macOS).
export GIT_TERMINAL_PROMPT=0
git_net() {
    local t=()
    command -v timeout >/dev/null 2>&1 && t=(timeout 15)
    "${t[@]}" git -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=10 "$@" >/dev/null 2>&1
}

# A cache cloned from a different URL (SHARED_RULES_REPO changed) is not this repo.
if [ -d "$CACHE/.git" ] && [ "$(git -C "$CACHE" remote get-url origin 2>/dev/null)" != "$REPO_URL" ]; then
    rm -rf "$CACHE"
fi

stale=""
pending=""
if [ -d "$CACHE/.git" ]; then
    # fetch + reset rather than pull: a force-pushed upstream would make
    # `pull --ff-only` fail on every session and freeze the cache for good.
    # The cache's checkout is the approved version; in ask mode a newer fetch waits.
    if ! git_net -C "$CACHE" fetch --depth 1 -q origin HEAD; then
        stale=1
    elif [ "$(git -C "$CACHE" rev-parse FETCH_HEAD)" != "$(git -C "$CACHE" rev-parse HEAD)" ]; then
        # Nothing to ask about when no rule changed (a README edit, say).
        if [ "$MODE" = auto ] || [ -z "$(git -C "$CACHE" diff --name-only HEAD FETCH_HEAD -- rules/)" ]; then
            git -C "$CACHE" reset -q --hard FETCH_HEAD >/dev/null 2>&1 || stale=1
        else
            pending=$(git -C "$CACHE" rev-parse FETCH_HEAD)
        fi
    fi
else
    # A first clone is loaded in either mode: installing the plugin is consent to
    # the rules it points at today; ask mode governs what changes after that.
    # Clone beside the cache and move it in only when complete, so a clone killed
    # mid-way can never leave a half-made .git that every later session trips on.
    mkdir -p "$(dirname "$CACHE")" 2>/dev/null
    tmp="$CACHE.tmp.$$"
    if git_net clone --depth 1 -q "$REPO_URL" "$tmp"; then
        mv "$tmp" "$CACHE"
    fi
    rm -rf "$tmp"
fi

# Rules may sit in subfolders of rules/, as Claude Code allows locally. `find`, not
# globstar: macOS ships bash 3.2, where ** silently means * and top-level rules vanish.
files=()
while IFS= read -r f; do files+=("$f"); done < <(find "$CACHE/rules" -type f -name '*.md' 2>/dev/null | LC_ALL=C sort)
if [ ${#files[@]} -eq 0 ]; then
    # Silence would read the same as "there are no rules"; say which it is.
    if [ -d "$CACHE/.git" ]; then
        echo "[shared-rules] No shared rules loaded this session: $REPO_URL was fetched but has no .md files under rules/."
    else
        echo "[shared-rules] No shared rules loaded this session: could not fetch $REPO_URL and nothing is cached."
    fi
    exit 0
fi

# The \r strip matters: a rule committed from Windows has CRLF endings, its
# '---\r' would never match the delimiter, and a path-scoped rule would load in full.
frontmatter() {
    awk '{sub(/\r$/, "")} NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit} NR>1 {print}' "$1"
}

scoped=()
echo "<shared-rules source=\"$REPO_URL\">"
[ -n "$stale" ] && echo "Could not refresh from the source this session; these are the last cached copies and may be out of date."
if [ -n "$pending" ]; then
    echo
    echo "=== rule updates awaiting the user's approval ==="
    echo "Update mode is 'ask'. The rules below are the approved version $(git -C "$CACHE" rev-parse --short HEAD)."
    echo "The source has a newer version $pending changing:"
    git -C "$CACHE" diff --name-status HEAD "$pending" -- rules/ | sed 's/^/    /'
    echo "Tell the user about this pending update before other work. To show them the changes:"
    echo "    git -C '$CACHE' diff HEAD $pending -- rules/"
    echo "Only if the user explicitly approves, run:"
    echo "    CLAUDE_PLUGIN_DATA='${CLAUDE_PLUGIN_DATA:-}' bash '$SELF' approve $pending"
fi
for f in "${files[@]}"; do
    if frontmatter "$f" | grep -q '^paths:'; then
        scoped+=("$f")
        continue
    fi
    echo
    echo "=== rule: ${f#"$CACHE/rules/"} ==="
    cat "$f"
done

if [ ${#scoped[@]} -gt 0 ]; then
    echo
    echo "=== path-scoped rules ==="
    echo "Not loaded here. Before working on files matching a rule's paths, read that rule's file."
    for f in "${scoped[@]}"; do
        echo
        echo "- $f"
        frontmatter "$f" | sed 's/^/    /'
    done
fi
echo "</shared-rules>"
exit 0
