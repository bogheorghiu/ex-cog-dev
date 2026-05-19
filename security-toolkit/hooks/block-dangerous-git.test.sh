#!/bin/bash
# Test suite for block-dangerous-git.sh hook
# Run: bash block-dangerous-git.test.sh
#
# Tests cover all blocked operations including:
# - PR merge (gh pr merge)
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

    local exit_code=0
    local result
    result=$(echo "$input" | bash "$HOOK" 2>/dev/null) || exit_code=$?

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

echo -e "${YELLOW}--- PR merge ---${NC}"
test_case "gh pr merge"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge"}}' 2

test_case "gh pr merge 123"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge 123"}}' 2

test_case "gh pr merge --squash"     '{"tool_name":"Bash","tool_input":{"command":"gh pr merge --squash"}}' 2

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

echo ""
echo -e "${YELLOW}--- Normal gh operations ---${NC}"
test_case "gh pr create"     '{"tool_name":"Bash","tool_input":{"command":"gh pr create --title test"}}' 0

test_case "gh pr view"     '{"tool_name":"Bash","tool_input":{"command":"gh pr view 311"}}' 0

test_case "gh pr comment"     '{"tool_name":"Bash","tool_input":{"command":"gh pr comment 311 --body \"looks good\""}}' 0

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
