#!/bin/bash
# Test suite for the pre-push PII guard
# Run: bash pre-push.test.sh
#
# The gate's whole job is to stop a denylisted personal name reaching a remote, so every test
# here asks one question: does a name get through, or does a clean push get blocked? The hook is
# driven exactly as git drives it — ref lines on stdin, remote name in $1.
#
# Tests cover:
# - Baseline: a name in the outgoing commits blocks; clean commits pass
# - Log safety: the matched term is NEVER echoed, including when it is in the ref name
# - Fail-closed on an errored scan (grep's own status, not the pipeline's, under pipefail)
# - Fail-closed when git cannot determine the push range
# - Fail-closed when the denylist exists but cannot be read
# - Binary/NUL bytes in one commit must not blind the scan of another
# - Merge commits: a name added only in a conflict resolution
# - Annotated tags: a name in the tag's own message
# - Push-range scoping: already-pushed history is not re-scanned
# - Second remote: commits already on origin still get scanned
# - Denylist normalization: CRLF, '|' separators, comment-only and blank-only files
# - An empty PII_DENYLIST must not mask a valid local denylist
# - Linked worktrees resolve the denylist to the main clone's root
# - Staleness: a private copy that has drifted from the tracked hook warns
#
# A synthetic term is used throughout — this suite contains no personal data.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/pre-push"

# Every scratch repo lives here and dies with the run. Git is isolated from the developer's and
# CI's own config so an inherited hooksPath, template dir, or signing key cannot change a result.
TEST_TMP="$(mktemp -d)"
trap 'chmod -R u+rwX "$TEST_TMP" 2>/dev/null; rm -rf "$TEST_TMP"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
# The hook's own staleness warning is about the developer's install, not about these scratch
# repos; individual staleness tests re-enable it.
export EXCOG_PREPUSH_NO_STALE_CHECK=1

TERM_STR="ACME-TESTPERSON"          # synthetic denylist term; never a real name
Z=0000000000000000000000000000000000000000

# Colors for output ($'...' form survives editor normalization that would
# strip raw ESC bytes from a regular single-quoted string).
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
NC=$'\033[0m' # No Color

PASSED=0
FAILED=0

pass() { PASSED=$((PASSED+1)); printf "${GREEN}PASS${NC}  %s\n" "$1"; }
fail() { FAILED=$((FAILED+1)); printf "${RED}FAIL${NC}  %s\n      %s\n" "$1" "$2"; }

# newrepo <name> — creates and enters a scratch repo with a one-term denylist.
# Must NOT be called inside $( ): the cd has to persist for the commits that follow.
newrepo() {
    R="$TEST_TMP/$1"
    mkdir -p "$R"
    cd "$R"
    git -c init.defaultBranch=main init -q .
    git config user.email test@example.invalid
    git config user.name "Test Runner"
    git config commit.gpgsign false
    # Without this, `git add .` commits the denylist itself and the hook matches its own patterns.
    printf 'pii-denylist.local\n' > "$R/.gitignore"
    printf '%s\n' "$TERM_STR" > "$R/pii-denylist.local"
}

# run_hook <repo> <remote-name> <stdin-line> [env-assignment ...] — sets RC and OUT.
run_hook() {
    local repo="$1" rem="$2" line="$3"
    shift 3
    set +e
    OUT="$(cd "$repo" && printf '%s\n' "$line" | env "$@" bash "$HOOK" "$rem" 2>&1)"
    RC=$?
    set -e
}

# A block is rc!=0 AND a BLOCKED message — rc alone could come from any other failure.
expect_block() {
    if [ "$RC" -ne 0 ] && printf '%s' "$OUT" | grep -q BLOCKED; then
        pass "$1"
    else
        fail "$1" "expected block; rc=$RC out=$(printf '%s' "$OUT" | head -1)"
    fi
}
expect_allow() {
    if [ "$RC" -eq 0 ] && ! printf '%s' "$OUT" | grep -q BLOCKED; then
        pass "$1"
    else
        fail "$1" "expected allow; rc=$RC out=$(printf '%s' "$OUT" | head -1)"
    fi
}
expect_out() {   # name, needle
    if printf '%s' "$OUT" | grep -q "$2"; then
        pass "$1"
    else
        fail "$1" "expected output to contain '$2'; got: $(printf '%s' "$OUT" | head -1)"
    fi
}
expect_not_out() {
    if printf '%s' "$OUT" | grep -q "$2"; then
        fail "$1" "output should not contain '$2'"
    else
        pass "$1"
    fi
}
# The denylisted term must never reach the terminal or a CI log.
expect_no_leak() {
    if printf '%s' "$OUT" | grep -qi "$TERM_STR"; then
        fail "$1" "denylisted term leaked into output"
    else
        pass "$1"
    fi
}

echo ""
echo -e "${YELLOW}--- Baseline and log safety ---${NC}"

newrepo baseline
echo clean > a.txt; git add .; git commit -qm c1
BASE=$(git rev-parse HEAD)
echo "written by $TERM_STR" > b.txt; git add .; git commit -qm c2
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE"
expect_block   "name in outgoing commits blocks the push"
expect_no_leak "matched term is not echoed"

newrepo clean
echo x > a.txt; git add .; git commit -qm c1; BASE=$(git rev-parse HEAD)
echo y > b.txt; git add .; git commit -qm c2
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE"
expect_allow "clean commits are allowed through"

newrepo refdelete
echo x > a.txt; git add .; git commit -qm c1
run_hook "$R" origin "refs/heads/gone $Z refs/heads/gone $(git rev-parse HEAD)"
expect_allow "a ref deletion is not scanned"

echo ""
echo -e "${YELLOW}--- Fail closed: a scan that could not run must never read as clean ---${NC}"

# git cannot resolve the range (the remote advertised a SHA this clone does not have — an
# ordinary force-push-after-someone-else-advanced-the-branch, with no intervening fetch).
newrepo gitfail
echo x > a.txt; git add .; git commit -qm c1
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
expect_block "an undeterminable push range blocks"

# grep's own error (exit 2) must not be mistaken for its no-match (exit 1).
newrepo unreadable
echo x > a.txt; git add .; git commit -qm c1; BASE=$(git rev-parse HEAD)
echo "has $TERM_STR" > b.txt; git add .; git commit -qm c2
chmod 000 "$R/pii-denylist.local"
if [ -r "$R/pii-denylist.local" ]; then
    # Running as root: chmod cannot make a file unreadable, so the case is unreachable here.
    printf "${YELLOW}SKIP${NC}  unreadable denylist blocks (running as root)\n"
else
    run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE"
    expect_block "an unreadable denylist blocks"
fi
chmod 644 "$R/pii-denylist.local"

echo ""
echo -e "${YELLOW}--- Content the scan used to miss ---${NC}"

# grep -I declares the WHOLE stream binary at the first NUL and abandons it. git log -p is
# reverse-chronological, so a NUL in a NEWER commit would hide a name in an older one.
newrepo nulbyte
echo x > a.txt; git add .; git commit -qm c0; BASE=$(git rev-parse HEAD)
echo "note about $TERM_STR" > notes.md; git add .; git commit -qm "adds the name"
{ head -c 9000 /dev/zero | tr '\0' 'a'; printf 'tail\0\0binary'; } > gen.log
git add .; git commit -qm "adds a file with a NUL byte"
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE"
expect_block "a NUL byte in another commit does not blind the scan"

# git log -p prints no diff body for a merge commit without -m.
newrepo mergecommit
echo base > f.txt; git add .; git commit -qm c0; BASE=$(git rev-parse HEAD)
git checkout -q -b side; echo side > f.txt; git commit -qam cs
git checkout -q -; echo main > f.txt; git commit -qam cm
git merge side -q >/dev/null 2>&1 || true
echo "resolved by $TERM_STR" > f.txt; git add f.txt; git commit -qm "merge resolve" >/dev/null
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE"
expect_block "a name added only in a merge resolution blocks"

# A tag object's message never appears in git log output.
newrepo tagmsg
echo x > a.txt; git add .; git commit -qm c1
git tag -a v1 -m "release by $TERM_STR"
run_hook "$R" origin "refs/tags/v1 $(git rev-parse v1) refs/tags/v1 $Z"
expect_block   "a name in an annotated tag message blocks"
expect_no_leak "tag-message match is not echoed"

echo ""
echo -e "${YELLOW}--- Push-range scoping ---${NC}"

# Positional revs mean "reachable from", which would scan the whole history and block on terms
# already in pushed commits — telling the operator to rewrite published history.
newrepo rangescope
echo "old $TERM_STR" > old.txt; git add .; git commit -qm "already-pushed commit with the name"
PUSHED=$(git rev-parse HEAD)
echo newfile > new.txt; git add .; git commit -qm "clean new commit"
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $PUSHED"
expect_allow "already-pushed history is not re-scanned"

# A new branch on a SECOND remote: its commits are on origin but not on the target.
newrepo secondremote
echo "has $TERM_STR" > a.txt; git add .; git commit -qm "name commit"
SHA=$(git rev-parse HEAD)
git update-ref refs/remotes/origin/main "$SHA"      # already on origin
git remote add mirror /dev/null
run_hook "$R" mirror "refs/heads/main $SHA refs/heads/main $Z"
expect_block "pushing to a second remote scans commits already on origin"

echo ""
echo -e "${YELLOW}--- Ref names ---${NC}"

newrepo refname
echo x > a.txt; git add .; git commit -qm c1
git checkout -q -b "feature/$TERM_STR-fixes"
run_hook "$R" origin "refs/heads/feature/$TERM_STR-fixes $(git rev-parse HEAD) refs/heads/feature/$TERM_STR-fixes $Z"
expect_block   "a denylisted term in the ref NAME blocks"
expect_no_leak "the offending ref name is not echoed"

echo ""
echo -e "${YELLOW}--- Denylist normalization ---${NC}"

newrepo crlf
printf '%s\r\n' "$TERM_STR" > "$R/pii-denylist.local"      # Windows-side editor under WSL
echo x > a.txt; git add .; git commit -qm c1; BASE=$(git rev-parse HEAD)
echo "has $TERM_STR here" > b.txt; git add .; git commit -qm c2
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE"
expect_block "a CRLF-saved denylist still matches"

newrepo pipesep
printf 'OTHER-TERM|%s\n' "$TERM_STR" > "$R/pii-denylist.local"   # the CI secret's own format
echo x > a.txt; git add .; git commit -qm c1; BASE=$(git rev-parse HEAD)
echo "has $TERM_STR" > b.txt; git add .; git commit -qm c2
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE"
expect_block "a '|'-separated denylist file is normalized"

newrepo blankline
printf '\n%s\n\n' "$TERM_STR" > "$R/pii-denylist.local"
echo x > a.txt; git add .; git commit -qm c1; BASE=$(git rev-parse HEAD)
echo "nothing to see" > b.txt; git add .; git commit -qm c2
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE"
expect_allow "a blank line is not an empty pattern that matches everything"

newrepo commentsonly
printf '# add names below\n\n' > "$R/pii-denylist.local"
echo x > a.txt; git add .; git commit -qm c1
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $Z"
expect_out "a comments-only denylist reports itself INACTIVE" "INACTIVE"

newrepo envmask
echo x > a.txt; git add .; git commit -qm c1; BASE=$(git rev-parse HEAD)
echo "has $TERM_STR" > b.txt; git add .; git commit -qm c2
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE" "PII_DENYLIST=|"
expect_block "an empty PII_DENYLIST does not mask a valid local denylist"

newrepo envwins
echo x > a.txt; git add .; git commit -qm c1; BASE=$(git rev-parse HEAD)
echo "has OTHER-ENV-TERM" > b.txt; git add .; git commit -qm c2
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $BASE" "PII_DENYLIST=OTHER-ENV-TERM"
expect_block "PII_DENYLIST terms are used when set"

echo ""
echo -e "${YELLOW}--- Linked worktrees ---${NC}"

# The denylist is gitignored and untracked, so it does not exist at a linked worktree's own root;
# resolving only --show-toplevel there would silently report the guard INACTIVE.
newrepo worktree
echo x > a.txt; git add .; git commit -qm c1; BASE=$(git rev-parse HEAD)
echo "has $TERM_STR" > b.txt; git add .; git commit -qm c2
git worktree add -q "$TEST_TMP/wt-linked" -b feat >/dev/null 2>&1
run_hook "$TEST_TMP/wt-linked" origin "refs/heads/feat $(git -C "$TEST_TMP/wt-linked" rev-parse HEAD) refs/heads/feat $BASE"
expect_block "a linked worktree finds the main clone's denylist"

echo ""
echo -e "${YELLOW}--- Staleness of a cp-installed copy ---${NC}"

# A private copy under .git/hooks/ is never updated by a pull. The running script is compared
# against the repo's tracked .githooks/pre-push, so drift is reported rather than silent.
newrepo stale
mkdir -p "$R/.githooks"
printf '#!/usr/bin/env bash\n# a DIFFERENT (older) tracked hook\nexit 0\n' > "$R/.githooks/pre-push"
echo x > a.txt; git add .; git commit -qm c1
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $Z" "EXCOG_PREPUSH_NO_STALE_CHECK="
expect_out "a drifted private copy warns" "WARNING"

newrepo notstale
mkdir -p "$R/.githooks"
cp "$HOOK" "$R/.githooks/pre-push"
echo x > a.txt; git add .; git commit -qm c1
run_hook "$R" origin "refs/heads/main $(git rev-parse HEAD) refs/heads/main $Z" "EXCOG_PREPUSH_NO_STALE_CHECK="
expect_not_out "an up-to-date copy does not warn" "WARNING"

echo ""
echo ""

# ============================================================
# Results
# ============================================================
echo "====================================="
echo -e "Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo ""

if [[ $FAILED -gt 0 ]]; then
    exit 1
fi
