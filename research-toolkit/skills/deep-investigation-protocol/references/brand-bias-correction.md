# Brand Saturation Bias Correction

## The Problem

Brand reputation operates on lag. Training data captures past consensus, not present reality. Advertising volume shapes "common knowledge" independent of current performance.

Result: Dominant brands get recommended even when evidence no longer supports dominance.

## Quality Information Flow

Each step introduces distortion:

```
Manufacturer testing (selection bias)
    ↓
Marketing claims (peak performance, ideal conditions)
    ↓
Affiliate review sites (revenue optimization)
    ↓
Aggregated "consensus" (repetition creates authority)
    ↓
AI training data (frequency-weighted, no methodology weighting)
    ↓
Initial recommendation (bias embedded)
```

The protocol interrupts this flow by seeking information upstream of distortion.

## Detection Triggers

Brand saturation is present when:

- Same brand appears 80%+ of "best of" recommendations
- Multiple sources use near-identical phrasing (indicates PR origin)
- Recommendations lack differentiated reasoning ("it's just better")
- "Best" claims unsupported by disclosed methodology
- Review focuses on features rather than performance verification
- No failure mode discussion
- No mention of professional defection patterns

## Correction Techniques

### 1. Defection Search

**Query:** "switched from [brand] to" OR "why I stopped using [brand]" OR "[brand] problems [year]"

**Why it works:** Professional users document switches more rigorously than purchases. Switching has costs, so defection signals genuine issues. Consumer reviews capture satisfaction; defection captures deal-breakers.

**Look for:**
- Patterns in defection reasons (recurring failure modes)
- Professional vs consumer defection (different issues)
- Timing clusters (manufacturing or firmware changes)
- Manufacturer response to documented issues

### 2. Sustained vs Peak Performance

**Query:** "sustained write test" OR "post-cache performance" OR "stress test" OR "thermal throttling"

**Why it works:** Marketing specs show peak performance under ideal conditions. Real workloads exhaust favorable conditions (cache, thermal headroom). Sustained performance reveals true capability.

**Key concepts:**
- SLC cache: Fast burst mode, then dramatic slowdown when full
- Thermal throttling: Performance drops under sustained load
- Post-cache numbers often 50-80% lower than marketed

### 3. Warranty as Confidence Signal

**Compare:** Warranty periods at equivalent price/capacity.

**Why it works:** Warranty is manufacturer betting on longevity with own money. Longer warranty at same price = higher confidence. Structural signal, not marketing claim.

**Look for:**
- Duration difference (3-year vs 5-year is significant)
- Warranty reductions over time (quality concerns)
- Claim process reputation

### 4. Vertical Integration Check

**Research:** Who fabricates core components vs who assembles?

**Why it works:** Fabricators control quality fundamentally. Assemblers depend on suppliers. Vertical integration means aligned incentives—fabricator's reputation rides on product.

**Questions:**
- Does company manufacture core components?
- What's their history in component manufacturing?
- Do they control full stack or final assembly only?

### 5. Affiliate Revenue Detection

**Red flags:**
- "Best X of [Year]" from sites with affiliate links on every product
- Identical rankings across multiple "review" sites
- No methodology disclosure
- High-commission products at top
- Recommendations change when affiliate programs change

**Trust signals:**
- Methodology disclosed
- Products purchased, not provided
- Negative findings included
- Long-term follow-up
- Author has expertise and reputation

### 6. Independent Failure Documentation

**Query:** "[product] failure reddit" OR "[product] class action" OR "iFixit [brand]"

**Why it works:** Failure modes reveal what marketing hides. Repair communities see patterns invisible to individual users.

**Sources:**
- Reddit repair/tech communities
- iFixit teardowns
- Class action filings
- Professional photographer/videographer forums

## Red Flag Combinations (Products)

| Combination | Concern Level |
|-------------|---------------|
| Brand dominance + No independent sustained testing | HIGH |
| Marketing volume + Warranty shorter than competitors | HIGH |
| "Best" ranking + Affiliate links + No methodology | HIGH |
| Recent reliability issues + Unchanged marketing claims | CRITICAL |
| Professional defection pattern + Unchanged consumer consensus | HIGH |

## Output Pattern

**Instead of:**
"Samsung T7 is the best external SSD—it's fast, reliable, and widely recommended."

**Prefer:**
"Samsung T7 Shield has dominant market position [VERIFIED]. Independent sustained-write testing shows post-cache performance of 380-420 MB/s vs marketed 1,050 MB/s [VERIFIED: AnandTech, EverythingUSB]. Crucial X9 Pro sustained 875 MB/s through entire transfer [VERIFIED]. Warranty: Samsung 3-year vs Crucial 5-year [VERIFIED]. For continuous backup workloads, Crucial's sustained performance advantage outweighs Samsung's brand recognition."

## Domain Notes

### Storage Products
- Sustained write performance critical
- NAND type matters (TLC vs QLC)
- Warranty period strongly predictive
- Defection patterns highly informative

### Electronics
- Repair community documentation valuable
- Long-term reliability data often missing at launch
- Affiliate revenue especially distorting

### Software/Services
- Use surveillance/privacy analysis instead
- Ownership chains matter more than benchmarks

## Principles

1. **Trace the flow**: Where does "knowledge" come from? Each step introduces distortion.
2. **Structural signals over claims**: Warranty, vertical integration, defection reveal more than marketing.
3. **Sustained over peak**: Real workloads stress differently than benchmarks.
4. **Professional defection is diagnostic**: When pros switch, reasons reveal hidden failure modes.
5. **Reputation operates on lag**: Past dominance ≠ current performance.
