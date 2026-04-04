# Corpus Analysis Criteria

Domain-specific criteria for iterative corpus analysis (Substack, YouTube transcripts, RSS feeds).

## Completion Criteria

### 1. Theme Saturation
**Condition:** 2+ consecutive passes find no new themes

**Assessment:** After each pass, count:
- New patterns/themes discovered
- Previously identified patterns reinforced with new evidence

**Quality Threshold:** Pass is HIGH if (new + reinforced) >= 2, else LOW

**Saturation Detection:** 2+ consecutive LOW passes = saturated

### 2. Representative Coverage
**Condition:** >= 70% of articles clustered into identified themes

**Assessment:**
- Count articles assigned to at least one theme
- Calculate: `coverage = assigned / total`
- Target: coverage >= 0.70

**Note:** Some outliers are expected and valuable.

### 3. Outlier Examination
**Condition:** Unclustered articles explicitly examined for unique insights

**Assessment:**
- List all articles not fitting major themes
- For each outlier, note what makes it unique
- Document if outlier represents emerging pattern or true one-off

## Assessment Method

After each parsing pass:

```
1. Count new themes discovered this pass
2. Count themes reinforced with new evidence
3. Mark pass as HIGH (>= 2 patterns) or LOW (< 2 patterns)
4. If 2+ consecutive LOW passes: STOP (saturated)
5. Calculate coverage percentage
6. If coverage >= 70% AND saturated: COMPLETE
```

## Pattern Taxonomy

When analyzing corpus, categorize patterns by type:

| Type | Description | Example |
|------|-------------|---------|
| **Concepts** | Key terms, mental models, frameworks | "Second brain", "Zettelkasten" |
| **Workflows** | Step-by-step processes | "Morning writing routine" |
| **Anti-patterns** | What NOT to do | "Never write in isolation" |
| **Tips/Tricks** | Shortcuts, hacks | "Use voice memos for capture" |
| **Tools** | Ecosystem components | "Obsidian", "Notion", "Roam" |
| **Relationships** | Connections between concepts | "GTD integrates with Zettelkasten" |

## Completion Promise

When all criteria pass:

```
<promise>ALL CORPUS ANALYSIS CRITERIA PASS</promise>
```

## Integration with Ralph-Plus

This criteria file works with `saturation_detector.py`:

```python
from scripts.saturation_detector import SaturationTracker

tracker = SaturationTracker(
    consecutive_low_threshold=2,  # Matches criteria
    high_pattern_threshold=2,     # Matches criteria
)

while not tracker.is_saturated:
    # Run analysis pass
    new, reinforced = analyze_corpus_pass()

    if not tracker.should_continue(new, reinforced):
        break

    tracker.record_pass(new, reinforced)
```

## Cross-Corpus Application

This criteria applies to:
- **Substack articles** - Text-based content analysis
- **YouTube transcripts** - Video content themes
- **RSS feeds** - Blog/news aggregation
- **Research papers** - Academic corpus

Adjust pattern taxonomy to domain. Core saturation algorithm remains constant.
