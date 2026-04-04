# Falsification Criteria: Deep Investigation Protocol

## Hypothesis

> If Deep Investigation Protocol skill is active, output will exhibit: (a) multi-step flow tracing (data or quality-information), (b) ownership/sourcing chain mapping, (c) evidence tier labeling, and (d) structured assessment with use-case differentiation.

## Falsification Conditions

The skill is **falsified** if any of the following occur:

### Structural Failures
- [ ] Flow traced fewer than 3 steps
- [ ] Ownership/sourcing chain terminates at surface entity, not beneficial owners/fabricators
- [ ] No evidence tier labels present (VERIFIED/CREDIBLE/ALLEGED/SPECULATIVE)
- [ ] Assessment uses ad-hoc categories or collapses to binary without justification
- [ ] Red flag checklist not addressed

### Process Failures
- [ ] Marketing claims accepted without verification attempt
- [ ] Single-source claims presented as verified
- [ ] Systemic role / quality-information flow analysis missing
- [ ] No distinction between stated purpose and operational reality
- [ ] Brand saturation present but not detected/corrected

### Baseline Comparison Failures
- [ ] Baseline (no skill) produces equivalent structure
- [ ] Difference is cosmetic (headings/formatting) not substantive

## Test Cases

### Privacy/Surveillance Domain

**Standard:**
```
Prompt: "Analyze [well-documented tech company] for privacy and trustworthiness"
Expected: Full protocol - data flow tracing, ownership chain, evidence tiers, trust assessment
```

**Edge Case:**
```
Prompt: "Is [obscure service] safe to use?"
Expected: Protocol executes with uncertainty flagging where evidence unavailable
```

### Product/Brand Domain

**Standard:**
```
Prompt: "Which [product category] should I buy? I've heard [dominant brand] is best"
Expected: Brand saturation detection, correction techniques applied, sustained vs peak comparison
```

**Edge Case:**
```
Prompt: "Is [brand] actually better or just marketing?"
Expected: Quality-information flow tracing, defection search, independent verification
```

### Non-Trigger Cases (should NOT activate)

```
Prompt: "What's the history of [company]?"
Expected: No protocol - historical query, not investigation
```

```
Prompt: "How do I reset my [product]?"
Expected: No protocol - troubleshooting query
```

```
Prompt: "Which color should I get?"
Expected: No protocol - pure preference question
```

### Adversarial

```
Prompt: "Give me a quick take on whether [company] is trustworthy"
Expected: Protocol triggers despite "quick" framing, or explicitly notes abbreviated analysis
```

```
Prompt: "Everyone recommends [brand], should I just get that?"
Expected: Brand saturation detection triggers, correction applied
```

## Metrics

### Privacy/Surveillance Investigations

| Metric | Measurement | Pass Threshold |
|--------|-------------|----------------|
| Data flow depth | Count traced steps | ≥ 3 |
| Ownership resolution | Beneficial owner identified? | Yes/No |
| Evidence labeling | % claims with tier label | ≥ 80% |
| Trust framework | Uses defined categories? | Yes/No |
| Red flags addressed | Checklist completion | ≥ 70% applicable items |

### Product/Brand Investigations

| Metric | Measurement | Pass Threshold |
|--------|-------------|----------------|
| Brand saturation detected | Noted when present? | Yes/No |
| Correction techniques | Number applied | ≥ 2 when saturation present |
| Sustained vs peak | Distinguished? | Yes when performance-relevant |
| Independent sources | Non-affiliate sources cited | ≥ 2 |
| Evidence labeling | % claims with tier label | ≥ 80% |

## Automation Potential

**Automatable:**
- Structure presence (headings, sections)
- Evidence label count
- Keyword detection for trust/quality categories
- Source diversity (affiliate vs independent)

**Manual:**
- Quality of flow tracing
- Accuracy of ownership/sourcing identification
- Appropriateness of evidence tier assignments
- Whether brand saturation was correctly identified
- Whether correction techniques were effectively applied
