#!/bin/bash
# SessionStart hook: print the shared Claude rules into context, for sessions that
# have no ~/.claude/rules of their own (cloud sessions, fresh containers).
#
# Must never block or fail the session: every network step is bounded and every
# failure falls through to exit 0.

REPO_URL="${SHARED_RULES_REPO:-https://github.com/bogheorghiu/claude-rules}"
CACHE="${CLAUDE_PLUGIN_DATA:-$HOME/.cache/shared-rules}/claude-rules"

# The local install already makes Claude Code load these rules natively;
# printing them again would put every rule in context twice.
[ -d "$HOME/.claude/rules/shared/.git" ] && exit 0

# Bound a network command where `timeout` exists (absent on stock macOS).
bounded() {
    if command -v timeout >/dev/null 2>&1; then timeout 15 "$@"; else "$@"; fi
}

if [ -d "$CACHE/.git" ]; then
    bounded git -C "$CACHE" pull --ff-only -q >/dev/null 2>&1
else
    mkdir -p "$(dirname "$CACHE")" 2>/dev/null
    # git removes a failed clone itself, but not one killed by `timeout`; a half-made
    # .git would send every later session down the pull branch and never recover.
    bounded git clone --depth 1 -q "$REPO_URL" "$CACHE" >/dev/null 2>&1 || rm -rf "$CACHE"
fi

shopt -s nullglob
files=("$CACHE"/rules/*.md)
if [ ${#files[@]} -eq 0 ]; then
    # Silence would read the same as "there are no rules"; say which it is.
    echo "[shared-rules] No shared rules loaded this session: could not fetch $REPO_URL and nothing is cached."
    exit 0
fi

# Frontmatter = lines between a leading '---' and the next '---'.
frontmatter() { awk 'NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit} NR>1 {print}' "$1"; }

scoped=()
echo "<shared-rules source=\"$REPO_URL\">"
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
