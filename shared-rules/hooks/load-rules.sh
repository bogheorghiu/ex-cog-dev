#!/bin/bash
# SessionStart hook: print the shared Claude rules into context, for sessions that
# have no ~/.claude/rules of their own (cloud sessions, fresh containers).
#
# Must never block or fail the session: every failure falls through to exit 0.

REPO_URL="${SHARED_RULES_REPO:-https://github.com/bogheorghiu/claude-rules}"
CACHE="${CLAUDE_PLUGIN_DATA:-$HOME/.cache/shared-rules}/claude-rules"

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
if [ -d "$CACHE/.git" ]; then
    # fetch + reset rather than pull: a force-pushed upstream would make
    # `pull --ff-only` fail on every session and freeze the cache for good.
    if ! { git_net -C "$CACHE" fetch --depth 1 -q origin HEAD && \
           git -C "$CACHE" reset -q --hard FETCH_HEAD >/dev/null 2>&1; }; then
        stale=1
    fi
else
    # Clone beside the cache and move it in only when complete, so a clone killed
    # mid-way can never leave a half-made .git that every later session trips on.
    mkdir -p "$(dirname "$CACHE")" 2>/dev/null
    tmp="$CACHE.tmp.$$"
    if git_net clone --depth 1 -q "$REPO_URL" "$tmp"; then
        mv "$tmp" "$CACHE"
    fi
    rm -rf "$tmp"
fi

shopt -s nullglob
files=("$CACHE"/rules/*.md)
if [ ${#files[@]} -eq 0 ]; then
    # Silence would read the same as "there are no rules"; say which it is.
    echo "[shared-rules] No shared rules loaded this session: could not fetch $REPO_URL and nothing is cached."
    exit 0
fi

# Frontmatter = lines between a leading '---' and the next '---' (CRLF-tolerant).
frontmatter() {
    awk '{sub(/\r$/, "")} NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit} NR>1 {print}' "$1"
}

scoped=()
echo "<shared-rules source=\"$REPO_URL\">"
[ -n "$stale" ] && echo "Could not refresh from the source this session; these are the last cached copies and may be out of date."
for f in "${files[@]}"; do
    if frontmatter "$f" | grep -q '^paths:'; then
        scoped+=("$f")
        continue
    fi
    echo
    echo "=== rule: $(basename "$f") ==="
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
