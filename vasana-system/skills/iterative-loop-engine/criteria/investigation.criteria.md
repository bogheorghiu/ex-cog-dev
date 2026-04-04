# Investigation Criteria

**Domain:** Factual accuracy verification
**Promise:** `ALL FALSIFICATION CRITERIA PASS`

## Completion Criteria

### Structural Requirements

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| Flow depth | ≥3 steps traced | Count investigation layers |
| Ownership chain | Reaches beneficial owners | Verify terminal ownership |
| Evidence labeling | ≥80% claims labeled | Count labeled / total claims |
| Category usage | Non-binary assessment | Check for nuanced tiers |
| Red flags | All addressed | Review flagged items |

### Process Requirements

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| Marketing claims | Independently verified | Cross-reference with non-marketing sources |
| Single-source claims | Not presented as verified | Check tier labels |
| Systemic analysis | Present | Review for flow/role analysis |
| Purpose vs reality | Distinguished | Check for gap analysis |
| Brand saturation | Detected and corrected | Review for over-representation |

### Source Requirements

| Criterion | Threshold | Assessment Method |
|-----------|-----------|-------------------|
| Independent sources | ≥2 non-affiliate | Count unique, independent sources |
| Performance data | Sustained, not peak | Check for trend data |
| Evidence freshness | <2 years (flag if older) | Check publication dates |

## Evidence Tier Definitions

| Tier | Definition | Examples |
|------|------------|----------|
| **VERIFIED** | Primary sources directly confirm | Regulatory filings, court documents, lab test results |
| **CREDIBLE** | Multiple independent sources agree | 3+ news outlets, consistent reports |
| **ALLEGED** | Single source, no corroboration | One article, one whistleblower |
| **SPECULATIVE** | Inference from patterns | "If X then probably Y" |

## Per-Pass Output Format

```markdown
## Investigation Pass [N]

### Claims Made
1. [Claim] - [TIER] - [Source]
2. [Claim] - [TIER] - [Source]
...

### Criteria Check
- [ ] Flow depth: [X] steps (threshold: ≥3) [✅/❌]
- [ ] Evidence labeling: [X]% (threshold: ≥80%) [✅/❌]
- [ ] Independent sources: [X] (threshold: ≥2) [✅/❌]
- [ ] Evidence freshness: [status] [✅/❌]
- [ ] Marketing claims verified: [status] [✅/❌]
...

### Gaps Identified
[What needs more evidence]

### Next Iteration Plan
[What to search/verify next]
```

## Completion Output

```markdown
## Final Verification

All falsification criteria satisfied:
- ✅ Flow depth: [X] steps
- ✅ Evidence labeling: [X]%
- ✅ Independent sources: [X]
- ✅ [All other criteria...]

<promise>ALL FALSIFICATION CRITERIA PASS</promise>
```

## Integration

- **Primary skill:** `deep-investigation-protocol`
- **Loop skill:** `iterative-loop-engine`
- **Agent:** `iterative-investigator`

## Source

Criteria derived from `deep-investigation-protocol/FALSIFICATION-CRITERIA.md`
