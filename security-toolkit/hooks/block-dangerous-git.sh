#!/bin/bash
# PreToolUse hook: Block dangerous git operations
# Matcher: Bash
#
# SECURITY RATIONALE:
# - Claude cannot merge PRs (requires user review + approval)
# - Claude cannot push directly to main/master
# - Claude cannot force push (destructive)
#
# Location: .claude/hooks/scripts/block-dangerous-git.sh
# Registered in: .claude/settings.local.json under PreToolUse
#
# FIX 2025-12-28: Extract BASE_CMD to prevent false positives from
# matching content inside --body or other string arguments.

# Hooks receive JSON stdin with tool_name and tool_input
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Extract base command (first 7 tokens) to avoid matching inside quoted strings
# This prevents false positives like: gh pr comment --body "text about push to main"
# Using 7 tokens to handle: command git -C /some/path push origin main
# Also normalize "command git" to "git" for matching
BASE_CMD=$(echo "$COMMAND" | sed -E 's/^command[[:space:]]+git/git/' | awk '{print $1, $2, $3, $4, $5, $6, $7}')

# Audit log helper: logs blocked attempts for security monitoring
# Usage: log_blocked_attempt "rule-name" "$COMMAND"
log_blocked_attempt() {
    local rule="$1"
    local cmd="$2"
    local log_dir="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/logs"
    mkdir -p "$log_dir" 2>/dev/null
    # Log rotation: This log grows slowly (only on blocked attempts). For cleanup:
    #   truncate -s 0 .claude/hooks/logs/blocked-attempts.log  # or delete; recreated on next block
    echo "[$(date -Iseconds)] BLOCKED $rule: $cmd" >> "$log_dir/blocked-attempts.log" 2>/dev/null
}

# Block PR merge (using BASE_CMD)
# Matches: gh pr merge, gh pr merge 123, etc.
if [[ "$BASE_CMD" =~ ^gh[[:space:]]+pr[[:space:]]+merge ]]; then
    log_blocked_attempt "pr-merge" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 Claude cannot merge PRs.\n\nThis requires user review and approval.\nPlease merge manually: gh pr merge <PR#>"
}
EOF
    exit 2
fi

# Block push to main/master (using BASE_CMD)
# Matches: git push origin main, git push main, git push -u origin main,
# git push origin refs/heads/main (full refspec form some tooling generates)
# Branch-name check uses full $COMMAND (not BASE_CMD) because the branch
# name may sit beyond BASE_CMD's 7-token window for long git -C paths.
if [[ "$BASE_CMD" =~ ^git[[:space:]]+push[[:space:]] ]]; then
    # Check if main/master appears in the push target (full command for accuracy)
    if [[ "$COMMAND" =~ [[:space:]](main|master)([[:space:]]|$) ]] || \
       [[ "$COMMAND" =~ [[:space:]]origin[[:space:]]+(main|master) ]] || \
       [[ "$COMMAND" =~ refs/heads/(main|master) ]]; then
        log_blocked_attempt "push-main" "$COMMAND"
        cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 Claude cannot push to main/master.\n\nUse a feature branch and create a PR instead."
}
EOF
        exit 2
    fi
fi

# Block force push (including --force-with-lease)
# Using BASE_CMD to confirm it's a git push, then check full command for force flags
if [[ "$BASE_CMD" =~ ^git[[:space:]]+push ]]; then
    if [[ "$COMMAND" =~ --force ]] || \
       [[ "$COMMAND" =~ [[:space:]]-f([[:space:]]|$) ]]; then
        log_blocked_attempt "force-push" "$COMMAND"
        cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 Claude cannot force push.\n\nThis is a destructive operation that rewrites history.\n(Includes --force, --force-with-lease, -f)"
}
EOF
        exit 2
    fi
fi

# Block git worktree remove (may delete unmerged work)
# Safe alternative: check conditions, user rm -rf, then git worktree prune + git branch -d
if [[ "$BASE_CMD" =~ ^git[[:space:]]+worktree[[:space:]]+remove ]]; then
    log_blocked_attempt "worktree-remove" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 git worktree remove blocked (may delete unmerged work).\n\nUse /worktree-cleanup for safe removal:\n1. Checks if merged, no uncommitted changes, no unpushed\n2. User: rm -rf .worktrees/wt-name\n3. git worktree prune && git branch -d <branch>"
}
EOF
    exit 2
fi

# Block git branch -D (force delete skips merge check)
# Only git branch -d (lowercase) is safe
if [[ "$BASE_CMD" =~ ^git[[:space:]]+branch[[:space:]]+-D ]]; then
    log_blocked_attempt "branch-force-delete" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 git branch -D blocked (force-deletes unmerged branches).\n\nUse: git branch -d <branch> (lowercase -d, fails if not merged)\n\nSee: .claude/rules/discard-safety.md"
}
EOF
    exit 2
fi

# Block --no-verify on git commit/push (bypasses hooks)
# This is CRITICAL - hooks are the enforcement mechanism
# Only block on actual git commands, and only as a flag (space before, space/EOL after)
if [[ "$BASE_CMD" =~ ^git[[:space:]]+(commit|push) ]] && [[ "$COMMAND" =~ [[:space:]]--no-verify([[:space:]]|$) ]]; then
    log_blocked_attempt "no-verify" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 --no-verify is BLOCKED.\n\nThis bypasses pre-commit/pre-push hooks which enforce workflow discipline.\n\nIf hooks are blocking your commit, fix the underlying issue:\n- Wrong branch? Create a worktree\n- Test failures? Fix the tests\n\nSee: .claude/rules/git-workflow.md"
}
EOF
    exit 2
fi

# Block --admin on gh commands (bypasses branch protection)
if [[ "$BASE_CMD" =~ ^gh[[:space:]] ]] && [[ "$COMMAND" =~ --admin ]]; then
    log_blocked_attempt "admin-bypass" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 --admin is BLOCKED.\n\nThis bypasses ALL branch protection rules (required reviews, status checks, etc.).\n\nNever use administrative bypass. Wait for proper review and approval.\n\nSee: .claude/rules/git-workflow.md"
}
EOF
    exit 2
fi

# TEMPORARY: Block direct GitHub API merge calls (until bot account - Issue #302)
# Owner tokens bypass branch protection rulesets via both REST and GraphQL APIs.
# Rulesets DO block normal `gh pr merge` but not direct API calls.
# REST: /repos/{owner}/{repo}/pulls/{number}/merge
# GraphQL: mutation { mergePullRequest(...) }
# Note: GraphQL pattern requires 'mutation' keyword to avoid matching query-only requests
if [[ "$COMMAND" =~ curl.*api\.github\.com/repos/[^/]+/[^/]+/pulls/[0-9]+/merge ]] || \
   [[ "$COMMAND" =~ curl.*api\.github\.com/graphql.*mutation.*mergePullRequest ]]; then
    log_blocked_attempt "api-merge" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 Direct API merge calls are BLOCKED (TEMPORARY - Issue #302).\n\nOwner tokens bypass branch protection rulesets via API calls (both REST and GraphQL).\nRulesets DO block `gh pr merge` but not direct API calls.\n\nLong-term fix: Use bot account with non-owner permissions.\n\nDo NOT use: curl .../pulls/N/merge or GraphQL mergePullRequest"
}
EOF
    exit 2
fi

# Block git checkout -- (discards uncommitted changes to specific files)
# Matches: git checkout -- file, git checkout -- ., git checkout HEAD -- file
# Note: Uses full COMMAND for -- check because file path after -- may be beyond BASE_CMD's 7 tokens
# This intentionally matches -- anywhere in the command, not just in BASE_CMD
if [[ "$BASE_CMD" =~ ^git[[:space:]]+checkout[[:space:]] ]] && [[ "$COMMAND" =~ [[:space:]]--[[:space:]] ]]; then
    log_blocked_attempt "checkout-discard" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 git checkout -- blocked.\n\nThis discards uncommitted changes permanently.\n\nFirst check what would be lost:\n  git diff <file>\n\nSee: .claude/rules/discard-safety.md"
}
EOF
    exit 2
fi

# Block git stash drop (permanent loss of stashed work)
if [[ "$BASE_CMD" =~ ^git[[:space:]]+stash[[:space:]]+drop ]]; then
    log_blocked_attempt "stash-drop" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 git stash drop blocked.\n\nBefore dropping, verify stash contents:\n  git stash show -p stash@{N}\n\nCheck if work is from another session/project.\n\nSee: .claude/rules/discard-safety.md"
}
EOF
    exit 2
fi

# Block git reset --hard (loses all uncommitted changes)
# Pattern matches --hard as standalone word to avoid false positives like --hardcoded-value
if [[ "$BASE_CMD" =~ ^git[[:space:]]+reset[[:space:]] ]] && [[ "$COMMAND" =~ (^|[[:space:]])--hard([[:space:]]|$) ]]; then
    log_blocked_attempt "reset-hard" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 git reset --hard blocked.\n\nThis loses ALL uncommitted changes permanently.\n\nFirst check what would be lost:\n  git status\n  git diff\n\nSee: .claude/rules/discard-safety.md"
}
EOF
    exit 2
fi

# Block git clean -fd (deletes untracked files)
# Pattern matches flags containing f or d (e.g., -f, -d, -fd, -df, -xfd)
# BUT allows dry-run in either form:
#   - short bundle containing n: -n, -nfd, -fn, etc.
#   - long form: --dry-run (separate check; [a-zA-Z]* doesn't include
#     '-', so the short-form regex can't catch '--dry-run' even after
#     backtracking).
if [[ "$BASE_CMD" =~ ^git[[:space:]]+clean[[:space:]] ]] && \
   [[ "$COMMAND" =~ [[:space:]]-[a-zA-Z]*[fd] ]] && \
   ! [[ "$COMMAND" =~ [[:space:]]-[a-zA-Z]*n ]] && \
   ! [[ "$COMMAND" =~ [[:space:]]--dry-run([[:space:]]|$) ]]; then
    log_blocked_attempt "clean" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 git clean blocked.\n\nThis deletes untracked files permanently.\n\nFirst check what would be deleted:\n  git clean -n\n\nSee: .claude/rules/discard-safety.md"
}
EOF
    exit 2
fi

# Block rm -rf on directories (too dangerous without review)
# Matches rm with both -r and -f flags in any order (-rf, -fr, -r -f, etc.)
# Note: Allows 'rm -r' or 'rm -f' alone - only blocks the dangerous combination
# KNOWN GAP: long-form flags (rm --recursive --force) are not caught.
# Low risk in practice (rare phrasing). If it bites, extend the regex.
if [[ "$BASE_CMD" =~ ^rm[[:space:]] ]] && [[ "$COMMAND" =~ [[:space:]]-[a-zA-Z]*r ]] && [[ "$COMMAND" =~ [[:space:]]-[a-zA-Z]*f ]]; then
    log_blocked_attempt "rm-rf" "$COMMAND"
    cat <<'EOF'
{
  "decision": "block",
  "reason": "🚫 rm -rf blocked.\n\nList contents first, confirm what will be deleted.\nConsider: rm -ri (interactive) for safety.\n\nSee: .claude/rules/discard-safety.md"
}
EOF
    exit 2
fi

# Allow all other commands
exit 0
