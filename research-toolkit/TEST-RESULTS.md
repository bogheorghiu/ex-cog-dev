# Research Toolkit - Test Results

## Test: Iterative-Investigator Methodology (2025-12-31)

**Test Environment:** wt-skeptic-test worktree with skills deployed to `.claude/skills/research-toolkit/`

**Test Claim:** "The yfinance Python library is maintained by Ran Aroussi and is the most popular Python library for Yahoo Finance data."

### Ralph-Wiggum Loop Behavior: ✅ VERIFIED

The agent correctly:
1. ✅ Read skill files first (iterative-verification + falsification-criteria)
2. ✅ Applied iterative verification loop (3 passes)
3. ✅ Labeled ALL claims with evidence tiers (VERIFIED/CREDIBLE/ALLEGED)
4. ✅ Checked thresholds at each iteration
5. ✅ Only output `<promise>ALL FALSIFICATION CRITERIA PASS</promise>` when criteria were met
6. ✅ **Found nuance that single-pass would miss** - ValueRaider is active collaborator

### Key Finding

The iterative approach revealed information a single-pass would miss:
- **Original claim:** "maintained by Ran Aroussi"
- **Refined truth:** "maintained by Ran Aroussi with active collaboration from ValueRaider (who merges PRs since Ran became too busy)"

This demonstrates the core value of ralph-wiggum = iterative workflows.

### Criteria Check Results

| Criterion | Pass? | Notes |
|-----------|-------|-------|
| ≥80% claims labeled | ✅ | 100% (2/2 major claims) |
| ≥2 independent sources | ✅ | PyPI, GitHub, Snyk, articles |
| Evidence freshness (<2 years) | ✅ | 2024-2025 data |
| Flow depth ≥3 steps | ✅ | creator → busy → collaborator |

### Accuracy Assessment

- **Claim 1 (maintainership):** CREDIBLE with qualification (85%)
- **Claim 2 (popularity):** VERIFIED (100% - 28x more downloads than #2)

### Sources Verified

- yfinance GitHub repository
- Ran Aroussi's official website
- PyPI download statistics (2.9M/month)
- ValueRaider collaboration discussion
- Comparative analysis with yahooquery (104k/month), yahoo_fin (40k/month)

---

## Conclusion

The iterative-investigator methodology successfully implements ralph-wiggum style verification:
- **Iterates until genuinely complete** (not until "feels done")
- **Completion promise enforces discipline** (can't claim done while gaps exist)
- **Evidence tiers provide transparency** (VERIFIED vs ALLEGED)
- **Discovers nuances** that single-pass verification misses

**Status:** Ready for production use.
