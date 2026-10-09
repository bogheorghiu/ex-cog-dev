#!/bin/bash
# Tests for load-rules.sh, run against a local fixture repo served over file://.
#
# What they do NOT prove: that the live harness injects SessionStart stdout into
# context, or that github.com is reachable from a given cloud environment.

set -u

HOOK="$(cd "$(dirname "$0")" && pwd)/load-rules.sh"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

# Pin ambient git config so a developer's settings can't change results.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

pass=0
fail=0
check() {
    if [ "$2" = "1" ]; then echo "  ok   - $1"; pass=$((pass + 1))
    else echo "  FAIL - $1"; fail=$((fail + 1)); fi
}
has() { case "$1" in *"$2"*) echo 1 ;; *) echo 0 ;; esac; }

# Fixture source repo: one always-on rule, one path-scoped rule, one non-rule file.
SRC="$TMP_DIR/src"
mkdir -p "$SRC/rules"
printf '# Always rule\nALWAYS_BODY\n' > "$SRC/rules/always.md"
printf -- '---\npaths:\n  - "src/**"\n---\n# Scoped rule\nSCOPED_BODY\n' > "$SRC/rules/scoped.md"
printf 'README_BODY\n' > "$SRC/README.md"
git -C "$SRC" init -q && git -C "$SRC" add -A && git -C "$SRC" commit -qm init

run_hook() { # args: HOME dir, repo url
    env -i HOME="$1" PATH="$PATH" GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
        CLAUDE_PLUGIN_DATA="$1/data" SHARED_RULES_REPO="$2" bash "$HOOK" </dev/null
}

echo "Testing load-rules.sh"
echo "====================="

# --- First run: clones and prints ---
H1="$TMP_DIR/h1"; mkdir -p "$H1"
out=$(run_hook "$H1" "file://$SRC"); rc=$?
check "first run exits 0" "$([ $rc -eq 0 ] && echo 1 || echo 0)"
check "always-on rule printed in full" "$(has "$out" ALWAYS_BODY)"
check "path-scoped rule body NOT printed" "$([ "$(has "$out" SCOPED_BODY)" = 0 ] && echo 1 || echo 0)"
check "path-scoped rule listed with its paths" "$(has "$out" 'src/**')"
check "path-scoped rule listed with its file location" "$(has "$out" "$H1/data/claude-rules/rules/scoped.md")"
check "non-rule README not printed" "$([ "$(has "$out" README_BODY)" = 0 ] && echo 1 || echo 0)"

# --- A rule added upstream reaches the next session (one-file drop) ---
printf '# New rule\nNEW_BODY\n' > "$SRC/rules/new.md"
git -C "$SRC" add -A && git -C "$SRC" commit -qm add
out=$(run_hook "$H1" "file://$SRC")
check "rule dropped upstream appears after pull" "$(has "$out" NEW_BODY)"

# --- Source unreachable, cache present: falls back to cache ---
# Move the source away: the cache pulls from its own recorded origin, not the URL.
mv "$SRC" "$SRC.gone"
out=$(run_hook "$H1" "file://$SRC"); rc=$?
mv "$SRC.gone" "$SRC"
check "unreachable source with cache exits 0" "$([ $rc -eq 0 ] && echo 1 || echo 0)"
check "unreachable source with cache still prints cached rules" "$(has "$out" ALWAYS_BODY)"
check "unreachable source with cache says copies may be stale" "$(has "$out" 'may be out of date')"

# --- Upstream history rewritten (force-push): cache follows it, no freeze ---
git -C "$SRC" checkout -q --orphan rewritten
printf '# Rewritten\nREWRITTEN_BODY\n' > "$SRC/rules/always.md"
git -C "$SRC" add -A && git -C "$SRC" commit -qm rewritten
git -C "$SRC" branch -q -M rewritten master 2>/dev/null || git -C "$SRC" branch -q -M rewritten main
out=$(run_hook "$H1" "file://$SRC")
check "force-pushed upstream content reaches the cache" "$(has "$out" REWRITTEN_BODY)"
check "force-pushed upstream: no stale notice" "$([ "$(has "$out" 'may be out of date')" = 0 ] && echo 1 || echo 0)"

# --- Configured URL changes: the cache is re-cloned from the new source ---
SRC2="$TMP_DIR/src2"; mkdir -p "$SRC2/rules"
printf '# Other\nOTHER_BODY\n' > "$SRC2/rules/other.md"
git -C "$SRC2" init -q && git -C "$SRC2" add -A && git -C "$SRC2" commit -qm init
out=$(run_hook "$H1" "file://$SRC2")
check "changed repo URL: new source's rules printed" "$(has "$out" OTHER_BODY)"
check "changed repo URL: old source's rules gone" "$([ "$(has "$out" REWRITTEN_BODY)" = 0 ] && echo 1 || echo 0)"

# --- CRLF frontmatter is still recognised as path-scoped ---
printf -- '---\r\npaths:\r\n  - "x/**"\r\n---\r\nCRLF_BODY\r\n' > "$SRC2/rules/crlf.md"
git -C "$SRC2" add -A && git -C "$SRC2" commit -qm crlf
out=$(run_hook "$H1" "file://$SRC2")
check "CRLF path-scoped rule body NOT printed" "$([ "$(has "$out" CRLF_BODY)" = 0 ] && echo 1 || echo 0)"

# --- Source unreachable, no cache: one-line notice, exit 0 ---
H2="$TMP_DIR/h2"; mkdir -p "$H2"
out=$(run_hook "$H2" "file://$TMP_DIR/missing"); rc=$?
check "offline with no cache exits 0" "$([ $rc -eq 0 ] && echo 1 || echo 0)"
check "offline with no cache says nothing was loaded" "$(has "$out" 'No shared rules loaded')"
check "failed clone leaves no half-made cache" "$([ ! -e "$H2/data/claude-rules" ] && echo 1 || echo 0)"

# --- Local install present: silent, to avoid loading every rule twice ---
H3="$TMP_DIR/h3"; mkdir -p "$H3/.claude/rules/shared/.git"
out=$(run_hook "$H3" "file://$SRC"); rc=$?
check "local install present: exits 0" "$([ $rc -eq 0 ] && echo 1 || echo 0)"
check "local install present: prints nothing" "$([ -z "$out" ] && echo 1 || echo 0)"

H4="$TMP_DIR/h4"; mkdir -p "$H4/.claude/rules/shared"; echo "gitdir: elsewhere" > "$H4/.claude/rules/shared/.git"
out=$(run_hook "$H4" "file://$SRC")
check "local install as submodule/worktree (.git file): prints nothing" "$([ -z "$out" ] && echo 1 || echo 0)"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
