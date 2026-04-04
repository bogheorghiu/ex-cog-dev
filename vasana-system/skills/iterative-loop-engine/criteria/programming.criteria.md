# Programming Criteria

**Domain:** Code quality and correctness verification
**Promise:** `ALL PROGRAMMING CRITERIA PASS`

## Completion Criteria

### Test Requirements

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| Tests pass | 100% green | Run test suite, check exit code |
| No regressions | 0 new failures | Compare with baseline |
| Coverage maintained | ≥ baseline | Check coverage report |
| New code tested | All new functions | Verify test existence |

### Build Requirements

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| Build succeeds | Exit code 0 | Run build command |
| No build warnings | 0 new warnings | Compare warning count |
| Type checks pass | 0 errors | Run type checker |

### Quality Requirements

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| Linting clean | 0 errors | Run linter |
| No security issues | 0 high/critical | Run security scanner if available |
| Code review ready | Self-reviewed | Check diff, verify intent |

### Integration Requirements

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| Existing tests pass | 100% | Run full test suite |
| No breaking changes | Or documented | Check API compatibility |
| Dependencies resolved | All installed | Check package manager |

## Severity Tiers

| Tier | Definition | Action |
|------|------------|--------|
| **BLOCKING** | Must fix before completion | Iterate until resolved |
| **WARNING** | Should fix, may defer | Document if not fixed |
| **INFO** | Nice to fix | Optional |

## Per-Pass Output Format

```markdown
## Programming Pass [N]

### Work Completed
[Code changes made this pass]

### Test Results
- Total: [X] tests
- Passing: [X]
- Failing: [X]
- Skipped: [X]

### Build Status
- Build: [PASS/FAIL]
- Type check: [PASS/FAIL]
- Lint: [X] errors, [X] warnings

### Criteria Check
- [ ] Tests pass: [X]% (threshold: 100%) [✅/❌]
- [ ] Build succeeds: [status] [✅/❌]
- [ ] Type checks: [status] [✅/❌]
- [ ] Lint clean: [status] [✅/❌]
- [ ] No regressions: [status] [✅/❌]

### Issues Found
- BLOCKING: [list]
- WARNING: [list]
- INFO: [list]

### Next Iteration Plan
[What to fix/improve next]
```

## Completion Output

```markdown
## Final Programming Status

All programming criteria satisfied:
- ✅ Tests: [X]/[X] passing (100%)
- ✅ Build: Succeeds
- ✅ Type check: Clean
- ✅ Lint: Clean
- ✅ No regressions

<promise>ALL PROGRAMMING CRITERIA PASS</promise>
```

## Commands Reference

**IMPORTANT:** These are example commands showing common patterns per language/framework. Adapt to your project's actual tooling - the loop engine is tool-agnostic.

```bash
# Tests
npm test / pytest / cargo test / go test ./...

# Build
npm run build / python -m build / cargo build / go build

# Type check
npx tsc --noEmit / mypy . / cargo check

# Lint
npm run lint / ruff check . / cargo clippy / golangci-lint run
```

**Project-specific guidance:**
- Check `package.json` scripts, `Makefile`, or project README for actual commands
- If project has a `coding-standard.md`, it may specify exact commands
- When in doubt, run `npm run` (Node) or `make help` to discover available commands

## TDD Integration

When used with TDD workflow:

1. **RED phase:** Write failing test → criteria: test exists, fails correctly
2. **GREEN phase:** Minimal implementation → criteria: test passes
3. **REFACTOR phase:** Clean up → criteria: all tests still pass, code quality

Each TDD cycle is one iteration of the loop.

---

## 🔴 ENHANCED TDD LOOP (ENFORCED for Development)

**Source:** Nvidia paper on CUDA kernel generation (via Replit/VentureBeat interview)

> "One-shot: ~50% success. Add verifier in loop: autonomous execution for hours."
> "Failures are DATA, not failures - they inform the next iteration."

### When to Use Enhanced vs Basic Loop

| Loop Type | Use When | Key Difference |
|-----------|----------|----------------|
| **Basic Ralph** | Research, info gathering, exploration | No "failures" to analyze |
| **Enhanced TDD** | Code development, bug fixing, implementation | Failures are cumulative data |

**Rule:** If there's a TEST/VERIFICATION STEP with PASS/FAIL outcome → use Enhanced loop.

### Enhanced Loop Structure

```
BASIC RALPH:
EXECUTE → ASSESS → CHECK → ITERATE → EXIT

ENHANCED TDD (ENFORCED):
EXECUTE → TEST → CAPTURE FAILURES → ANALYZE PATTERNS → ITERATE with context → EXIT
                ↑                    ↑
                |                    |
           Failure Accumulator   Pattern Detector
```

### Failure-Feedback Components

#### 1. Failure Accumulator

Collect across iterations:
- Error messages (verbatim)
- Stack traces (relevant portions)
- Test output (full context)
- Failure timestamps

```markdown
## Failure History

### Iteration 1
- ERROR: `TypeError: Cannot read property 'map' of undefined`
- LOCATION: `src/utils/transform.js:42`
- CONTEXT: data was null, not array

### Iteration 2
- ERROR: Same as #1, different input path
- NEW CONTEXT: null check added but missed edge case
```

#### 2. Pattern Detector

Ask after each failure:
- Same failure type recurring? → **Root cause not addressed**
- New failure type? → **Progress made, new issue discovered**
- Regression? → **Fix broke something else**

```markdown
## Pattern Analysis

### Recurring Patterns
- 3x: Null reference on data array → SYSTEMATIC: Add null guards everywhere
- 2x: Type mismatch on API response → SYSTEMATIC: Add response validation

### Pattern Shift (Progress Indicators)
- Iteration 1-2: Null errors
- Iteration 3-4: Type errors (null fixed!)
- Iteration 5: Edge case (types fixed!)
```

#### 3. Context Injection

Feed previous failures into next iteration:

```markdown
## Iteration 4 Context

### Previous Failures Summary
- Iterations 1-2 failed due to null data (FIXED: added null checks)
- Iteration 3 failed due to type mismatch (FIXED: added type coercion)

### Current Failure
- Test: "should handle empty arrays"
- Error: Assertion failed - expected [] got null

### Informed Approach
Previous fixes addressed null-to-defined and type issues.
This failure is about empty-array-vs-null distinction.
TRY: Separate empty check from null check.
```

#### 4. Failure History Persistence

For multi-session work:
- Store failure patterns in episodic memory
- Reference in future sessions on same codebase
- Build project-specific failure vocabulary

### Enhanced Per-Pass Output Format

```markdown
## TDD Pass [N]

### Work Completed
[Code changes made this pass]

### Test Results
- Total: [X] tests | Passing: [X] | Failing: [X]

### Failure Analysis (if any failures)

#### New Failures This Iteration
- [failure 1]
- [failure 2]

#### Recurring Failures (from previous iterations)
- [failure that persisted] - NEEDS DIFFERENT APPROACH

#### Resolved Failures (were failing, now passing)
- [previously failing test] - FIXED by [change]

#### Pattern Assessment
- [ ] Same failure type recurring: [YES/NO]
- [ ] Root cause identified: [YES/NO - description]
- [ ] New approach needed: [YES/NO - what]

### Next Iteration Plan (Informed by Failures)
Previous attempts failed because: [X]
This iteration will try: [Y] (different approach)
```

### Exit Condition (Enhanced)

Only exit when:
1. ✅ All tests pass (standard)
2. ✅ No recurring failure patterns (enhanced)
3. ✅ Failure history shows progression (not cycling)

**Anti-pattern:** Trying same fix repeatedly. If same failure 3+ times → STOP, ask human or change approach fundamentally.

## Integration

- **Primary skill:** `test-driven-development` (if available)
- **Loop skill:** `iterative-loop-engine`
- **Agent:** `iterative-programmer`
