# Review Criteria

**Domain:** PR/Code review iteration completion
**Promise:** `ALL REVIEW CRITERIA PASS`

## Completion Criteria

### Comment Resolution

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| Blocking comments | 0 unresolved | Check review status |
| Requested changes | All addressed | Verify each change request |
| Questions answered | All responded | Check for unanswered threads |
| Suggestions evaluated | All considered | Document decisions |

### CI/CD Status

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| All checks pass | 100% green | Check CI status |
| No new failures | 0 regressions | Compare with base |
| Required checks | All complete | Check required status |

### Review Status

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| Approvals | ≥ required count | Check approval status |
| No blocking reviews | 0 "changes requested" active | Check review state |
| Stale reviews | Re-requested if needed | Check after new commits |

### Content Quality

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| PR description | Complete and accurate | Verify describes changes |
| Test plan | Present if required | Check for testing notes |
| Breaking changes | Documented | Check for migration notes |

## Comment Categories

| Category | Action Required | Resolution |
|----------|-----------------|------------|
| **BLOCKING** | Must fix | Code change required |
| **SUGGESTION** | Should consider | Implement or explain why not |
| **QUESTION** | Must answer | Respond in thread |
| **NIT** | Optional | Fix or acknowledge |
| **PRAISE** | None | Appreciate! |

## Per-Pass Output Format

```markdown
## Review Pass [N]

### Comments Addressed
1. [Comment summary] - [Resolution: fixed/responded/acknowledged]
2. [Comment summary] - [Resolution]
...

### CI Status
- [Check 1]: [PASS/FAIL/PENDING]
- [Check 2]: [PASS/FAIL/PENDING]
...

### Review Status
- Approvals: [X]/[required]
- Changes requested: [X] active
- Pending reviews: [X]

### Criteria Check
- [ ] Blocking comments: [X] (threshold: 0) [✅/❌]
- [ ] CI checks: [X]% passing (threshold: 100%) [✅/❌]
- [ ] Approvals: [X] (threshold: [required]) [✅/❌]
- [ ] No active change requests: [status] [✅/❌]

### Unresolved Items
- BLOCKING: [list]
- PENDING: [list]

### Next Iteration Plan
[What to address next]
```

## Completion Output

```markdown
## Final Review Status

All review criteria satisfied:
- ✅ Blocking comments: 0
- ✅ CI checks: All passing
- ✅ Approvals: [X]/[required]
- ✅ No active change requests

<promise>ALL REVIEW CRITERIA PASS</promise>
```

## GitHub CLI Commands

```bash
# View PR status
gh pr view [number] --json state,reviews,statusCheckRollup

# List comments
gh pr view [number] --comments

# Check CI status
gh pr checks [number]

# View review status
gh pr view [number] --json reviews --jq '.reviews[] | {author: .author.login, state: .state}'
```

## Addressing Comments Pattern

For each comment:

1. **Read:** Understand the feedback
2. **Categorize:** BLOCKING/SUGGESTION/QUESTION/NIT
3. **Act:**
   - BLOCKING → Fix code, commit, push
   - SUGGESTION → Implement or explain rationale
   - QUESTION → Respond with answer
   - NIT → Fix or "acknowledged, will fix in follow-up"
4. **Verify:** Ensure action addresses the comment

## Integration

- **Loop skill:** `iterative-loop-engine`
- **Related:** `.claude/rules/git-workflow.md` - "PR Review Iteration Workflow (ENFORCED)" section
- **Note:** This criteria file operationalizes the PR iteration rules from git-workflow.md into measurable completion criteria
- **Agent:** Can be used by any PR-focused agent

## Max Iterations Handling

If max iterations reached without approval:

1. Stop iteration loop
2. Document unresolved blockers in PR comment
3. Notify user with summary
4. **Do NOT force merge** - wait for human decision

Non-blocking suggestions may be deferred:
- Document as "acknowledged, will address in follow-up PR"
- Create tracking issue if needed
