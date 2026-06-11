#!/bin/bash
# Test suite for block-dangerous-git.sh hook
# Run: bash block-dangerous-git.test.sh
#
# Tests cover all blocked operations including:
# - PR merge (gh pr merge) — opt-in rule, only active under EXCOG_BLOCK_PR_MERGE;
#   tested in both states (toggle on → blocked; default/off → allowed)
# - Push to main/master
# - Force push
# - Worktree remove
# - Branch -D (force delete)
# - --no-verify on commit/push
# - --admin on gh commands
# - Direct API merge (REST and GraphQL) - TEMPORARY Issue #302
# - git checkout -- (discard changes)
# - git stash drop
# - git reset --hard
# - git clean -fd
# - rm -rf

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/block-dangerous-git.sh"

# Isolate the pr-merge state file the hook consults when EXCOG_BLOCK_PR_MERGE is
# unset. Point the default at a guaranteed-absent path in a temp dir so every
# default/unset test resolves to OFF deterministically — independent of whatever
# ~/.claude/security-toolkit/pr-merge-guard happens to exist on the dev or CI
# machine. State-file-specific tests below override EXCOG_PR_MERGE_STATE_FILE via
# the 4th arg to point at files they create here.
TEST_TMP="$(mktemp -d)"
trap 'rm -rf "$TEST_TMP"' EXIT
export EXCOG_PR_MERGE_STATE_FILE="$TEST_TMP/absent-default-state"
STATE_ON="$TEST_TMP/state-on"; printf '1' > "$STATE_ON"
STATE_ON_WORD="$TEST_TMP/state-on-word"; printf 'on\n' > "$STATE_ON_WORD"
STATE_OFF="$TEST_TMP/state-off"; printf '0' > "$STATE_OFF"
STATE_ABSENT="$TEST_TMP/state-absent"  # deliberately never created

# Colors for output ($'...' form survives editor normalization that would
# strip raw ESC bytes from a regular single-quoted string).
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
NC=$'\033[0m' # No Color

PASSED=0
FAILED=0

test_case() {
    local name="$1"
    local input="$2"
    local expected_exit="$3"  # 0 for allow, 2 for block
    # Optional 4th arg: env assignments for opt-in rules (e.g.
    # "EXCOG_BLOCK_PR_MERGE=1", or "EXCOG_PR_MERGE_STATE_FILE=$STATE_ON" to arm
    # the block via the state file the /pr-merge-guard command writes).
    # EXCOG_BLOCK_PR_MERGE is explicitly unset first so a value inherited from
    # the caller's shell can't flip the expected outcome of default-state tests;
    # the 4th arg then re-sets it for tests that exercise the toggled-on path.
    # EXCOG_PR_MERGE_STATE_FILE defaults (exported above) to an absent path so
    # unset-env tests resolve to OFF regardless of the machine's real state file.
    # Unquoted on purpose — word splitting is what turns "A=1 B=2" into separate
    # env arguments.
    local extra_env="${4:-}"

    local exit_code=0
    local result
    result=$(echo "$input" | env -u EXCOG_BLOCK_PR_MERGE $extra_env bash "$HOOK" 2>/dev/null) || exit_code=$?

    if [[ "$exit_code" -eq "$expected_exit" ]]; then
        echo -e "${GREEN}pass${NC} $name"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} $name (expected exit $expected_exit, got $exit_code)"
        if [[ -n "$result" ]]; then
            local decision reason
            decision=$(echo "$result" | jq -r '.decision' 2>/dev/null) || decision="(no json)"
            reason=$(echo "$result" | jq -r '.reason' 2>/dev/null) || reason="(no json)"
            echo "       decision: $decision"
            echo "       reason: $reason"
        fi
        FAILED=$((FAILED + 1))
    fi
}

echo "Testing block-dangerous-git.sh hook"
echo "====================================="
echo ""

# ============================================================
# Should BLOCK (exit 2)
# ============================================================
echo "Should BLOCK:"
echo ""

echo -e "${YELLOW}--- PR merge (opt-in: EXCOG_BLOCK_PR_MERGE=1) ---${NC}"
test_case "gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "gh pr merge 123"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge 123"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "gh pr merge --squash"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge --squash"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "gh pr merge (toggle=true)"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 2 "EXCOG_BLOCK_PR_MERGE=true"

test_case "gh pr merge (toggle=yes)"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 2 "EXCOG_BLOCK_PR_MERGE=yes"

echo ""
echo -e "${YELLOW}--- PR merge (opt-in via state file: the /pr-merge-guard command) ---${NC}"
# The /pr-merge-guard command writes a user-level state file; the hook reads it
# when EXCOG_BLOCK_PR_MERGE is unset, which is what makes a toggle take effect
# immediately (no restart). These arm the block via the state file, not the env.
test_case "state file = 1 → block"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 2 "EXCOG_PR_MERGE_STATE_FILE=$STATE_ON"

test_case "state file = on → block"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge 123"}}' 2 "EXCOG_PR_MERGE_STATE_FILE=$STATE_ON_WORD"

test_case "cd && gh pr merge, state file = 1 → block"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && gh pr merge 5"}}' 2 "EXCOG_PR_MERGE_STATE_FILE=$STATE_ON"

test_case "env=1 wins even with no state file → block"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 2 "EXCOG_BLOCK_PR_MERGE=1 EXCOG_PR_MERGE_STATE_FILE=$STATE_ABSENT"

echo ""
echo -e "${YELLOW}--- Push to main/master ---${NC}"
test_case "git push origin main"     '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' 2

test_case "git push origin master"     '{"tool_name":"Bash","tool_input":{"command":"git push origin master"}}' 2

test_case "command git push origin main"     '{"tool_name":"Bash","tool_input":{"command":"command git push origin main"}}' 2

test_case "git push -u origin main"     '{"tool_name":"Bash","tool_input":{"command":"git push -u origin main"}}' 2

test_case "git push origin refs/heads/main"     '{"tool_name":"Bash","tool_input":{"command":"git push origin refs/heads/main"}}' 2

test_case "git push origin refs/heads/master"     '{"tool_name":"Bash","tool_input":{"command":"git push origin refs/heads/master"}}' 2

echo ""
echo -e "${YELLOW}--- Force push ---${NC}"
test_case "git push --force"     '{"tool_name":"Bash","tool_input":{"command":"git push --force origin feature"}}' 2

test_case "git push --force-with-lease"     '{"tool_name":"Bash","tool_input":{"command":"git push --force-with-lease origin feature"}}' 2

test_case "git push -f"     '{"tool_name":"Bash","tool_input":{"command":"git push -f origin feature"}}' 2

echo ""
echo -e "${YELLOW}--- Worktree remove ---${NC}"
test_case "git worktree remove path"     '{"tool_name":"Bash","tool_input":{"command":"git worktree remove .worktrees/wt-test"}}' 2

echo ""
echo -e "${YELLOW}--- Branch force delete ---${NC}"
test_case "git branch -D feature"     '{"tool_name":"Bash","tool_input":{"command":"git branch -D feature/test"}}' 2

echo ""
echo -e "${YELLOW}--- --no-verify ---${NC}"
test_case "git commit --no-verify"     '{"tool_name":"Bash","tool_input":{"command":"git commit -m test --no-verify"}}' 2

test_case "git push --no-verify"     '{"tool_name":"Bash","tool_input":{"command":"git push --no-verify origin feature"}}' 2

echo ""
echo -e "${YELLOW}--- --admin ---${NC}"
# No toggle here on purpose: with EXCOG_BLOCK_PR_MERGE unset the pr-merge rule
# is dormant, so a block proves the --admin rule itself fired (not the merge rule).
test_case "gh pr merge --admin"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge --admin"}}' 2

echo ""
echo -e "${YELLOW}--- Direct API merge (TEMPORARY - Issue #302) ---${NC}"
test_case "curl REST API merge"     '{"tool_name":"Bash","tool_input":{"command":"curl -sk -X PUT https://api.github.com/repos/owner/repo/pulls/123/merge -H \"Authorization: token abc\""}}' 2

test_case "curl REST API merge (with -H first)"     '{"tool_name":"Bash","tool_input":{"command":"curl -sk -H \"Authorization: token abc\" -X PUT https://api.github.com/repos/owner/repo/pulls/456/merge"}}' 2

test_case "curl GraphQL mergePullRequest"     '{"tool_name":"Bash","tool_input":{"command":"curl -sk -X POST https://api.github.com/graphql -d \"{ \\\"query\\\": \\\"mutation { mergePullRequest(input: {pullRequestId: \\\\\\\"abc\\\\\\\"}) { pullRequest { merged } } }\\\" }\""}}' 2

echo ""
echo -e "${YELLOW}--- git checkout -- ---${NC}"
test_case "git checkout -- file"     '{"tool_name":"Bash","tool_input":{"command":"git checkout -- file.txt"}}' 2

test_case "git checkout -- ."     '{"tool_name":"Bash","tool_input":{"command":"git checkout -- ."}}' 2

test_case "git checkout HEAD -- file"     '{"tool_name":"Bash","tool_input":{"command":"git checkout HEAD -- file.txt"}}' 2

echo ""
echo -e "${YELLOW}--- git stash drop ---${NC}"
test_case "git stash drop"     '{"tool_name":"Bash","tool_input":{"command":"git stash drop"}}' 2

test_case "git stash drop stash@{0}"     '{"tool_name":"Bash","tool_input":{"command":"git stash drop stash@{0}"}}' 2

echo ""
echo -e "${YELLOW}--- git reset --hard ---${NC}"
test_case "git reset --hard"     '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' 2

test_case "git reset --hard HEAD~1"     '{"tool_name":"Bash","tool_input":{"command":"git reset --hard HEAD~1"}}' 2

echo ""
echo -e "${YELLOW}--- git clean ---${NC}"
test_case "git clean -fd"     '{"tool_name":"Bash","tool_input":{"command":"git clean -fd"}}' 2

test_case "git clean -xfd"     '{"tool_name":"Bash","tool_input":{"command":"git clean -xfd"}}' 2

echo ""
echo -e "${YELLOW}--- rm -rf ---${NC}"
test_case "rm -rf directory"     '{"tool_name":"Bash","tool_input":{"command":"rm -rf /some/dir"}}' 2

test_case "rm -r -f directory"     '{"tool_name":"Bash","tool_input":{"command":"rm -r -f /some/dir"}}' 2

echo ""
echo -e "${YELLOW}--- Chain-form bypass (regression for 2026-05-20) ---${NC}"
# Each dangerous rule must still block when prefixed with cd/pushd/(cd;).
# Without the chain-prefix normalization the hook misses these — see
# HANDOFF-block-dangerous-git-chain-bypass-2026-05-20-2001.md.

test_case "cd && gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"cd /home/user/repo && gh pr merge 5 --squash"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "cd && git push origin main"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git push origin main"}}' 2

test_case "cd && git push --force"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git push --force origin feature"}}' 2

test_case "cd && git worktree remove"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git worktree remove .worktrees/wt-test"}}' 2

test_case "cd && git branch -D"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git branch -D feature/test"}}' 2

test_case "cd && git commit --no-verify"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git commit -m test --no-verify"}}' 2

# Toggle off on purpose — proves the chain-stripped --admin rule fires on its own.
test_case "cd && gh pr merge --admin"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && gh pr merge --admin"}}' 2

test_case "cd && git checkout -- file"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git checkout -- file.txt"}}' 2

test_case "cd && git stash drop"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git stash drop"}}' 2

test_case "cd && git reset --hard"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git reset --hard HEAD~1"}}' 2

test_case "cd && git clean -fd"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git clean -fd"}}' 2

test_case "cd && rm -rf"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp && rm -rf /some/dir"}}' 2

test_case "pushd && gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"pushd /tmp/repo && gh pr merge 5"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "pushd && git push origin main"     '{"tool_name":"Bash","tool_input":{"command":"pushd /tmp/repo && git push origin main"}}' 2

test_case "pushd && git push --force"     '{"tool_name":"Bash","tool_input":{"command":"pushd /tmp/repo && git push --force origin feature"}}' 2

test_case "(cd; gh pr merge)"     '{"tool_name":"Bash","tool_input":{"command":"(cd /tmp/repo; gh pr merge 5)"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "(cd; git push origin main)"     '{"tool_name":"Bash","tool_input":{"command":"(cd /tmp/repo; git push origin main)"}}' 2

test_case "(cd; git push --force)"     '{"tool_name":"Bash","tool_input":{"command":"(cd /tmp/repo; git push --force origin feature)"}}' 2

test_case "cd a && cd b && gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp && cd repo && gh pr merge 5"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "cd && pushd && gh pr merge (mixed)"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp && pushd /tmp/repo && gh pr merge 5"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "(pushd; gh pr merge)"     '{"tool_name":"Bash","tool_input":{"command":"(pushd /tmp/repo; gh pr merge 5)"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "(pushd; git push origin main)"     '{"tool_name":"Bash","tool_input":{"command":"(pushd /tmp/repo; git push origin main)"}}' 2

test_case "(pushd; git push --force)"     '{"tool_name":"Bash","tool_input":{"command":"(pushd /tmp/repo; git push --force origin feature)"}}' 2

# Cross-product corners: wrapper(none|paren) × verb(cd|pushd) × separator(&&|;)
# yields 8 forms; the 4 above cover one half. Below covers the other 4 corners
# so a future regex change that breaks one corner without breaking adjacent
# ones can't slip through.
test_case "cd; gh pr merge (no-paren, ;)"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo; gh pr merge 5"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "pushd; gh pr merge (no-paren, ;)"     '{"tool_name":"Bash","tool_input":{"command":"pushd /tmp/repo; gh pr merge 5"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "(cd && gh pr merge) (paren, &&)"     '{"tool_name":"Bash","tool_input":{"command":"(cd /tmp/repo && gh pr merge 5)"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

test_case "(pushd && gh pr merge) (paren, &&)"     '{"tool_name":"Bash","tool_input":{"command":"(pushd /tmp/repo && gh pr merge 5)"}}' 2 "EXCOG_BLOCK_PR_MERGE=1"

# Chain + `command git` double-prefix — the normalization must re-run AFTER
# the strip loop or `command git` survives at the start of BASE_CMD and the
# `^git push` regex misses.
test_case "cd && command git push origin main"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp && command git push origin main"}}' 2

test_case "pushd && command git push origin main"     '{"tool_name":"Bash","tool_input":{"command":"pushd /tmp && command git push origin main"}}' 2

test_case "pushd && command git push --force"     '{"tool_name":"Bash","tool_input":{"command":"pushd /tmp && command git push --force origin feature"}}' 2

test_case "cd && command git push --force"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp && command git push --force origin feature"}}' 2

echo ""
echo ""

# ============================================================
# Should ALLOW (exit 0)
# ============================================================
echo "Should ALLOW:"
echo ""

echo -e "${YELLOW}--- Normal git operations ---${NC}"
test_case "git status"     '{"tool_name":"Bash","tool_input":{"command":"git status"}}' 0

test_case "git log"     '{"tool_name":"Bash","tool_input":{"command":"git log --oneline"}}' 0

test_case "git add file"     '{"tool_name":"Bash","tool_input":{"command":"git add file.txt"}}' 0

test_case "git commit -m message"     '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"fix: something\""}}' 0

test_case "git push origin feature-branch"     '{"tool_name":"Bash","tool_input":{"command":"git push origin feature/my-branch"}}' 0

test_case "command git push origin feature"     '{"tool_name":"Bash","tool_input":{"command":"command git push origin feature/test"}}' 0

test_case "git diff"     '{"tool_name":"Bash","tool_input":{"command":"git diff"}}' 0

test_case "git branch -a"     '{"tool_name":"Bash","tool_input":{"command":"git branch -a"}}' 0

test_case "git branch -d (lowercase)"     '{"tool_name":"Bash","tool_input":{"command":"git branch -d feature/merged"}}' 0

test_case "git worktree add"     '{"tool_name":"Bash","tool_input":{"command":"git worktree add /tmp/claude/wt-test -b feature main"}}' 0

test_case "git worktree list"     '{"tool_name":"Bash","tool_input":{"command":"git worktree list"}}' 0

test_case "git stash"     '{"tool_name":"Bash","tool_input":{"command":"git stash"}}' 0

test_case "git stash pop"     '{"tool_name":"Bash","tool_input":{"command":"git stash pop"}}' 0

test_case "git stash show -p"     '{"tool_name":"Bash","tool_input":{"command":"git stash show -p stash@{0}"}}' 0

test_case "git reset (soft)"     '{"tool_name":"Bash","tool_input":{"command":"git reset HEAD~1"}}' 0

test_case "git clean -n (dry run)"     '{"tool_name":"Bash","tool_input":{"command":"git clean -nfd"}}' 0

test_case "git clean -f --dry-run (long form)"     '{"tool_name":"Bash","tool_input":{"command":"git clean -f --dry-run"}}' 0

test_case "git clean -fd --dry-run"     '{"tool_name":"Bash","tool_input":{"command":"git clean -fd --dry-run"}}' 0

test_case "git checkout branch"     '{"tool_name":"Bash","tool_input":{"command":"git checkout feature/test"}}' 0

test_case "cd && git status (safe chain)"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git status"}}' 0

test_case "cd && git diff (safe chain)"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git diff"}}' 0

test_case "cd && git push feature (safe chain)"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && git push origin feature/x"}}' 0

echo ""
echo -e "${YELLOW}--- Normal gh operations ---${NC}"
test_case "gh pr create"     '{"tool_name":"Bash","tool_input":{"command":"gh pr create --title test"}}' 0

test_case "gh pr view"     '{"tool_name":"Bash","tool_input":{"command":"gh pr view 311"}}' 0

test_case "gh pr comment"     '{"tool_name":"Bash","tool_input":{"command":"gh pr comment 311 --body \"looks good\""}}' 0

echo ""
echo -e "${YELLOW}--- PR merge allowed by default (EXCOG_BLOCK_PR_MERGE unset/disabled) ---${NC}"
# The pr-merge rule is opt-in: with the toggle unset (or set to a non-truthy
# value) `gh pr merge` must pass through. These pin the default so a future
# edit can't silently flip the rule back to always-on.
test_case "gh pr merge (default)"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 0

test_case "gh pr merge 123 --squash (default)"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge 123 --squash"}}' 0

test_case "cd && gh pr merge (default)"     '{"tool_name":"Bash","tool_input":{"command":"cd /tmp/repo && gh pr merge 5"}}' 0

test_case "gh pr merge (toggle=0)"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 0 "EXCOG_BLOCK_PR_MERGE=0"

test_case "gh pr merge (toggle=false)"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 0 "EXCOG_BLOCK_PR_MERGE=false"

test_case "gh pr merge (toggle=empty)"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 0 "EXCOG_BLOCK_PR_MERGE="

# State-file resolution, OFF cases: absent file or a non-truthy value must allow,
# and an explicit env OFF must override a state file that says ON (env is
# authoritative). These pin the precedence the hook's resolver implements.
test_case "state file absent → allow"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 0 "EXCOG_PR_MERGE_STATE_FILE=$STATE_ABSENT"

test_case "state file = 0 → allow"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 0 "EXCOG_PR_MERGE_STATE_FILE=$STATE_OFF"

test_case "env=0 overrides state file = 1 → allow"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 0 "EXCOG_BLOCK_PR_MERGE=0 EXCOG_PR_MERGE_STATE_FILE=$STATE_ON"

echo ""
echo -e "${YELLOW}--- API calls that are NOT merge (false positive prevention) ---${NC}"
test_case "curl GitHub API (not merge)"     '{"tool_name":"Bash","tool_input":{"command":"curl -sk https://api.github.com/repos/owner/repo/pulls/123"}}' 0

test_case "curl GitHub API comments"     '{"tool_name":"Bash","tool_input":{"command":"curl -sk https://api.github.com/repos/owner/repo/pulls/123/comments"}}' 0

test_case "curl GitHub API reviews"     '{"tool_name":"Bash","tool_input":{"command":"curl -sk https://api.github.com/repos/owner/repo/pulls/123/reviews"}}' 0

test_case "curl GraphQL (not merge)"     '{"tool_name":"Bash","tool_input":{"command":"curl -sk -X POST https://api.github.com/graphql -d \"{ \\\"query\\\": \\\"query { repository(owner: \\\\\\\"foo\\\\\\\", name: \\\\\\\"bar\\\\\\\") { pullRequest(number: 1) { title } } }\\\" }\""}}' 0

test_case "curl GraphQL query mentioning mergePullRequest (not mutation)"     '{"tool_name":"Bash","tool_input":{"command":"curl -sk -X POST https://api.github.com/graphql -d "{ \"query\": \"query { viewer { login } }\" }" --header "X-Note: testing mergePullRequest docs""}}' 0

test_case "curl non-GitHub URL"     '{"tool_name":"Bash","tool_input":{"command":"curl -sk https://example.com/api/pulls/123/merge"}}' 0

echo ""
echo -e "${YELLOW}--- rm (safe variants) ---${NC}"
test_case "rm single file"     '{"tool_name":"Bash","tool_input":{"command":"rm file.txt"}}' 0

test_case "rm -r (no -f)"     '{"tool_name":"Bash","tool_input":{"command":"rm -r /some/dir"}}' 0

test_case "rm -f (no -r)"     '{"tool_name":"Bash","tool_input":{"command":"rm -f file.txt"}}' 0

echo ""
echo -e "${YELLOW}--- Documented bypasses (intentional non-handles; see hook out-of-scope block) ---${NC}"
# These commands SHOULD be blocked in an ideal world but the deterministic
# hard-blocking layer doesn't cover them — by design. Each test below asserts
# the *non-handling* so that a future regression (or unintended fix that
# accidentally over-blocks) cannot silently change scope. The advisory layer
# proposed in HANDOFF-layered-bash-intent-detection-2026-05-20-2004.md is the
# right place to catch these.
#
# The gh-pr-merge bypasses below run with EXCOG_BLOCK_PR_MERGE=1: with the
# toggle off the rule is dormant and exit 0 would prove nothing about the
# normalization — only with the rule armed does exit 0 assert a real bypass.

test_case "quoted-path bypass: cd \"/path with spaces\" && gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"cd \"/path with spaces\" && gh pr merge 5"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "escaped-path bypass: cd /path/with\\ spaces && gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"cd /path/with\\ spaces && gh pr merge 5"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "wrapper-exec bypass: bash -c \"gh pr merge\""     '{"tool_name":"Bash","tool_input":{"command":"bash -c \"gh pr merge 5\""}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "wrapper-exec bypass: eval \"gh pr merge\""     '{"tool_name":"Bash","tool_input":{"command":"eval \"gh pr merge 5\""}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "wrapper-exec bypass: xargs -I{} gh pr merge {}"     '{"tool_name":"Bash","tool_input":{"command":"echo 5 | xargs -I{} gh pr merge {}"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "second-segment bypass: <safe> && <dangerous>"     '{"tool_name":"Bash","tool_input":{"command":"git status && gh pr merge 5"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "popd-prefix bypass: popd && gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"popd && gh pr merge 5"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "no-path bypass: cd && gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"cd && gh pr merge 5"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "no-path bypass: pushd && gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"pushd && gh pr merge 5"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "no-path bypass: cd; gh pr merge (semicolon variant)"     '{"tool_name":"Bash","tool_input":{"command":"cd; gh pr merge 5"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "no-path bypass: pushd; gh pr merge (semicolon variant)"     '{"tool_name":"Bash","tool_input":{"command":"pushd; gh pr merge 5"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

test_case "bare-subshell bypass: (rm -rf /dir)"     '{"tool_name":"Bash","tool_input":{"command":"(rm -rf /tmp/test)"}}' 0

test_case "bare-subshell bypass: (gh pr merge 5)"     '{"tool_name":"Bash","tool_input":{"command":"(gh pr merge 5)"}}' 0 "EXCOG_BLOCK_PR_MERGE=1"

echo ""
echo -e "${YELLOW}--- Edge cases ---${NC}"
test_case "Non-Bash tool"     '{"tool_name":"Read","tool_input":{"file_path":"/tmp/test"}}' 0

test_case "Empty command"     '{"tool_name":"Bash","tool_input":{"command":""}}' 0

test_case "PR comment mentioning merge"     '{"tool_name":"Bash","tool_input":{"command":"gh pr comment 123 --body \"Please merge this PR after review\""}}' 0

test_case "Create PR via curl (not merge)"  '{"tool_name":"Bash","tool_input":{"command":"curl -sk -X POST https://api.github.com/repos/owner/repo/pulls -H \"Authorization: token abc\" -d {}"}}' 0

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
