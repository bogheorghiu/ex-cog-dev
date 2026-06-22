---
name: iterative-verification
description: >-
  "Is this ACTUALLY verified, or did I just say it is?" - An iterative
  verification loop for factual accuracy: re-check claims against the evidence
  every pass, and don't stop at the first plausible answer. Use when (1) claims require
  evidence not assumption, (2) verification must be demonstrable, (3)
  single-pass investigation insufficient, (4) factual accuracy is critical.
  Provides the loop logic: iterate until verification thresholds met. Does NOT
  trigger for: opinions, preferences, how-to instructions, or when user
  explicitly wants quick answer.
---

# Iterative Verification

**Seed question:** *Is this ACTUALLY verified, or did I just say it is?*

> *Relentless self-reflexive dialectical thinking that questions its own premises.*

## Core Principle

An iterative workflow keeps going until genuinely complete.
For facts: keep verifying until claims meet evidence thresholds.

**The anti-pattern this counters:**
```
❌ "I searched once, found something, called it verified"
❌ "The claim sounds right, I'll present it as fact"
❌ "I'm confident, so I don't need to check"
```

**The pattern this enforces:**
```
✅ Search → Label evidence tier → Check threshold → Iterate if gaps
✅ Claim is VERIFIED only when evidence supports it
✅ Keep iterating until criteria actually pass
```

## When This Applies

**TRIGGER:**
- Any claim that must be factually accurate
- Investigation outputs with evidence requirements
- Trust/reliability assessments
- Decisions based on facts, not preferences
- User asks "is this actually true?" or "can you verify?"

**DO NOT TRIGGER:**
- Opinion requests
- Preference questions
- How-to instructions
- User says "quick answer" or "don't need sources"
- Creative/generative tasks

## The Verification Loop

```
1. INVESTIGATE
   - Gather information
   - Make claims

2. LABEL
   - Assign evidence tier to each claim:
     * VERIFIED: Primary sources, court docs, regulatory filings
     * CREDIBLE: Multiple independent sources
     * ALLEGED: Single source, unverified
     * SPECULATIVE: Inference, theoretical

3. CHECK THRESHOLDS
   - ≥80% claims labeled?
   - ≥2 independent sources?
   - Flow traced ≥3 steps?
   - Evidence fresh (<2 years for reliability data)?

4. IF GAPS → ITERATE
   - Identify what's missing
   - Search for specific evidence
   - Return to step 1

5. IF ALL PASS → COMPLETE
   - Output with confidence
   - All claims have evidence basis
```

## Evidence Tier Definitions

| Tier | Definition | Examples |
|------|------------|----------|
| **VERIFIED** | Primary sources directly confirm | Regulatory filings, court documents, lab test results, official statements |
| **CREDIBLE** | Multiple independent sources agree | 3+ news outlets, consistent professional reports, corroborated accounts |
| **ALLEGED** | Single source, no corroboration | One article, one whistleblower, one study |
| **SPECULATIVE** | Inference from patterns | "If X then probably Y", theoretical risk |

## Threshold Requirements

For factual accuracy tasks, iterate until:

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Claims labeled | ≥80% | Most claims should have explicit evidence basis |
| Independent sources | ≥2 | Reduces single-point-of-failure |
| Evidence freshness | <2 years | Prevents stale information in dynamic domains |
| Flow depth | ≥3 steps | Surface claims hide deeper realities |

## Iteration Examples

**Pass 1: Initial Investigation**
```
Claim: "Company X has good privacy practices"
Evidence tier: ALLEGED (marketing claims only)
Gap: No independent verification
→ ITERATE
```

**Pass 2: Targeted Search**
```
Search: "Company X privacy audit independent"
Found: Third-party security audit report
Claim upgraded: CREDIBLE (audit + marketing = 2 sources)
Remaining gaps: Ownership chain unclear
→ ITERATE
```

**Pass 3: Ownership Verification**
```
Search: "Company X beneficial ownership SEC filings"
Found: SEC filing showing parent company
Claim: Ownership chain now VERIFIED
All thresholds pass
→ COMPLETE
```

## Fact-Verification Examples

### China: TikTok Algorithm Ownership Error (March 2026)

A report claimed the consortium "controls the algorithm" after TikTok's sale. Iterative verification revealed the opposite.

> **Report claimed:** "The consortium controls the algorithm, meaning it's no longer under ByteDance/Chinese government potential influence."
> **Verified against primary sources:** "This is factually wrong. ByteDance retains ownership of the recommendation algorithm. The US entity operates it under license but cannot own, independently transfer, or unilaterally modify the core IP." — Adversarial Critique, China tech/trade assessment
>
> **Verification gap:** Single-pass investigation accepted the "clean break" narrative. Iterative verification against NBC News, TechPolicy.Press, and Rest of World revealed the deal was "in direct tension with the explicit text of the divestment law." *Source: china-critique.md, ERROR 3*

### Iran: Beit Shemesh Casualty Count (March 2026)

A report stating "8 killed" in a missile strike was corrected through cross-source verification.

> **Report stated:** "8 killed" in Beit Shemesh strike.
> **Actual:** "9 killed (including three teenage siblings: Yaakov 16, Avigail 15, Sarah 13 Bitton). Multiple sources confirm: Al Jazeera, Jerusalem Post, Times of Israel, Euronews." — Adversarial Critique, Iran assessment
>
> **Lesson:** In a report claiming VERIFIED evidence tiers, even minor numerical errors undermine the tier system. Cross-referencing against 4 independent sources caught the discrepancy. *Source: iran-critique.md, Challenge 6*

### Iran: Russia's Role Understated (March 2026)

A report characterized Russia/China support as "muted criticism only," which iterative verification contradicted.

> **Report claimed:** Russia showed "limited actual support to Iran" with "muted criticism only."
> **Counter-evidence found:** "Russia IS providing satellite intelligence on US troop positions (CNN, March 6, confirmed by US officials). Russia delivered Su-35 fighter jets ($6.5B order) and $590M in air defense systems before the war." — Adversarial Critique, Iran assessment
>
> **Result:** Evidence tier downgraded from CREDIBLE to ALLEGED/INCOMPLETE. A single pass accepted the "muted" characterization; the verification loop surfaced active intelligence sharing and substantial pre-war arms deliveries. *Source: iran-critique.md, Challenge 4*

## Convergence Warning Protocol

When all sources agree quickly, this is a signal, not a conclusion. Flag it explicitly:

```
WARNING: All sources converge on [X]. This may be correct, but rapid
convergence can indicate:
  (a) genuine consensus,
  (b) groupthink,
  (c) manufactured consensus (same original source),
  (d) our own confirmation bias.
Testing with adversarial search.
```

After flagging, actively search for dissent. If dissent exists: investigate it. If no dissent exists after adversarial search: convergence is likely genuine, but note the flag in your output.

## Probability Distribution Requirement

Never present a single scenario as the outcome. Present a probability distribution:

```
Scenario A (50%): [Most likely outcome] because [evidence]
Scenario B (30%): [Second most likely] because [evidence]
Scenario C (15%): [Contrarian case] because [evidence]
Scenario D (5%):  [Tail risk] because [structural possibility]
```

The contrarian case MUST receive non-zero allocation unless genuinely impossible. Binary framing (X will/won't happen) almost always collapses a spectrum into a false dichotomy.

For actionable investigations: never recommend 100% allocation to any single scenario. A 50/30/20 split is almost always better than 100/0/0.

## Steel-Man Obligation

After reaching any conclusion in the verification loop, steel-man the strongest possible contrarian argument:

- If the investigation leans toward crisis: What is the strongest case for quick resolution? Quantify it.
- If the investigation leans toward stability: What is the strongest case for escalation? Quantify it.
- If the investigation identifies a villain: What is the most charitable interpretation of their actions?

This is not about fairness — it is about testing whether the conclusion survives its best counter-argument. If you cannot articulate the contrarian case with genuine force, your verification is incomplete.

### Verdict-Tier Check

Completion requires: verdict tier matches evidence tier. "No mainstream confirmation" = UNVERIFIED, not FALSE. Escalate to DISCONFIRMED only with specific counter-evidence.

## Self-Check Questions

Before claiming completion, ask:

1. **"Did I label this claim, or did I assume it?"**
   - Every factual claim needs an evidence tier

2. **"Is my source independent?"**
   - Affiliate content, marketing, and SEO-gamed reviews don't count

3. **"When was this verified?"**
   - Old evidence may not reflect current reality

4. **"Did I search for counter-evidence?"**
   - Confirmation bias finds what you expect; search adversarially

5. **"Would this pass falsification criteria?"**
   - Check against `FALSIFICATION-CRITERIA.md` if available

6. **"Did I steel-man the contrarian case?"**
   - The strongest counter-argument must be articulated and tested

7. **"Am I presenting a distribution or a single scenario?"**
   - Binary conclusions are almost always wrong; present probabilities

8. **"Is this skill's framework limiting what I can verify?"**
   - These evidence tiers, thresholds, and protocols are tools, not truths — if they're channeling you away from something real, override them and say why

## The "One More" Sweep Rule

After believing verification is complete and all thresholds pass, do ONE MORE sweep:

1. Pick the perspective you are **least sympathetic to**
2. Search that perspective's sources for your topic
3. If this changes nothing: you are genuinely done
4. If this changes something: you are not done — return to the verification loop

This catches the blind spot that all previous passes share: your own position. The perspective you instinctively dismiss is the one most likely to contain what you missed.

## Dialectic Spiral for Contested Claims

When claims are contested (sources disagree, evidence tiers conflict), apply the dialectic spiral within the verification loop:

```
Round 1: THESIS — Present the claim with evidence tier
Round 2: ANTITHESIS — Search for counter-evidence.
         The original claim must REBUT with evidence, not assertion.
Round 3: RESOLUTION — What survives the test? Note what was abandoned.
Round 4+: GENERATE the exact opposite of the resolution.
         Don't look for an existing counterpoint — produce one.
         Then search: does anyone anywhere articulate it?
         Does reality support it?
         Continue until generating the opposite yields nothing meaningful.
```

**The key move is generative, not classificatory.** Pre-mapped "opposing views" limit the dialectic to existing positions. Generating the opposite of a synthesis can produce positions that don't exist in any source category — that's where novel insight comes from. "Who bears costs / who captures benefits" is one useful lens for generation, not the only one.

Exit when generating the next antithesis produces nothing that changes the synthesis. Minimum 4 rounds for contested claims.

Reference: `METHODOLOGY-comprehensive-investigation.md` Section 6 for extended protocol with agent team structure.

## Integration with Ralph-Wiggum

This skill provides the verification loop logic that ralph-loop enforces through persistence.

**Without ralph-loop:** User invokes this skill, follows methodology manually
**With ralph-loop:** Agent runs in loop until completion promise satisfied

Both achieve the same goal: iterate until genuinely verified.

## Output Pattern

```markdown
## Verification Status

### Claims Assessed
1. [Claim] - [TIER] - [Source]
2. [Claim] - [TIER] - [Source]
...

### Threshold Check
- Evidence labeling: [X]% (threshold: 80%) [✅/❌]
- Independent sources: [X] (threshold: 2) [✅/❌]
- Evidence freshness: [status] [✅/❌]
- [Other criteria...]

### Verification Status
[COMPLETE: All thresholds met] or [INCOMPLETE: Gaps identified]

### If Incomplete: Next Iteration
- Gap: [what's missing]
- Search: [what to look for]
```

---

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

**Integration:** Use the `/ralph-loop` command from the ralph-loop plugin for automated iteration.
