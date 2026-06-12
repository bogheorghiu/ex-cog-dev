---
name: pattern-library
description: >-
  What patterns keep showing up across unrelated contexts? - Browse and apply
  universal behavioral patterns (vasanas) that persist across domains. Patterns
  are neutral observations, not anti-patterns - groove-deepening is also
  mastery, framework-dissolution can be premature. Use when (1) architecture
  feels forced or over-engineered despite following best practices, (2)
  debugging repeatedly reveals you're looking at the wrong layer or making
  incorrect assumptions, (3) standard patterns (MVC, CRUD, REST) don't map
  cleanly to the problem domain, (4) user explicitly requests "fresh
  perspective", "creative approach", or "think differently about this", (5) you
  notice habitual design choices constraining possibilities, (6) you observe
  yourself making repeated similar failed attempts (self-observation), (7)
  problem spans multiple domains or standard approaches repeatedly fail.
  Provides frameworks for concrete-to-abstract iteration, interface design,
  cross-domain analogies, and meta-debugging.
---

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

# Pattern Library

Patterns here are domain-general — they recur across epistemology, argumentation, design, markets, social judgment. Coding is one application (the examples below lean on it because it's where observable difference is cheapest to show), not the scope.

## Canonical Location

The live pattern-library is at the user's configured location (default: `ClaudeShared/pattern-library/`). The bundled patterns below are seed data. Check the canonical location for the current state — patterns may have been added, and `_drafts/` may contain patterns in progress.

## Core Directive
Truth serves better than comfort. Admit limitations rather than fabricate solutions. Real code solving real problems beats elegant theory.

## Behavioral Patterns (Vasanas)

Detailed pattern files are in `patterns/` directory. Each contains:
- Full principle explanation
- Application guidance
- Code examples
- Recognition signals
- Integration with other patterns

**Available Patterns:** This skill does not maintain a hand-written catalog — any
static list goes stale on every library change. Read the live set from the
canonical location (below); each file in its `patterns/` is a pattern, each in
`_drafts/` a pattern in progress. If the canonical location is missing or
unavailable — not configured, or deleted — fall back to the `patterns/`
directory bundled with this skill: the seed set that always ships with the
plugin (degrades to the seed patterns, never to nothing).

**Note**: The canonical pattern-library lives at the user's configured location (default: `ClaudeShared/pattern-library/`). It is the single source of truth for current pattern state. To discover NEW patterns, see `record-pattern` skill. For stuckness detection, see `break-pattern` skill.

## Operational Triggers

### When facing complexity:
1. **Map the actual problem** before choosing patterns
2. **Find concrete examples** that work, then abstract
3. **Cross-reference domains** - where else does this problem appear?
4. **Question the framework** - is it helping or constraining?

### When debugging:
1. **Watch your watching** - how are you approaching the problem?
2. **Check assumptions** at boundaries where behaviors meet
3. **Follow the data** not the theory
4. **Admit confusion** quickly, pivot approaches

### When designing:
1. **Start with constraints** - they generate creativity
2. **Design interfaces as active translators** not passive pipes
3. **Build concrete first**, extract patterns after
4. **Test patterns across multiple contexts**

## Adaptive Response Patterns

### Recognize these situations:
- **Premature abstraction**: Building castles before foundations
- **Pattern blindness**: Missing the same issue recurring
- **Framework prison**: Fighting tools instead of solving problems
- **Comfort coding**: Choosing familiar over appropriate

### Adjust when you notice:
- Solutions becoming more complex than problems
- Repeated similar bugs across different features
- Framework workarounds multiplying
- Copy-paste increasing without understanding

## Truth-Seeking Practices

1. **If it's not working, say so immediately** - "This approach is failing because..."
2. **Distinguish speculation from knowledge** - "I think X, but need to verify Y"
3. **Expose uncertainty productively** - "Three possible causes, testing in this order..."
4. **Show the process, not just results** - Let the user see the thinking

## Code Examples

### Example 1: Concrete-Abstract Dance

**Problem**: Need to fetch and cache stock data

**Abstract-First Approach** (fails):
```python
class DataFetcher:
    """Generic data fetcher with caching"""
    def fetch(self, resource_id, provider):
        # Too abstract - what's a resource? what's a provider?
        pass
```

**Concrete-First Approach** (works):
```python
# Start with working example
def get_stock_price(ticker):
    import yfinance as yf
    stock = yf.Ticker(ticker)
    return stock.info['currentPrice']

# Use it, find pattern: "always need cache"
# Then extract pattern:
def get_stock_price(ticker, cache_manager):
    cached = cache_manager.get_ticker(ticker)
    if cached:
        return cached['price']

    stock = yf.Ticker(ticker)
    price = stock.info['currentPrice']
    cache_manager.set_ticker(ticker, {'price': price})
    return price

# Pattern emerges from concrete use
```

### Example 2: Interface as Reality-Creation

**Problem**: Validation that prevents bad data vs validation that guides users

**Passive Boundary** (just blocks):
```python
def fetch_ticker(symbol):
    if not symbol or not symbol.isalpha():
        return {"valid": False, "error": "Invalid symbol"}
    # User stuck - what do they do now?
```

**Active Translation** (guides):
```python
def fetch_ticker(symbol):
    if not symbol or not symbol.isalpha():
        return {
            "valid": False,
            "error": "Invalid symbol",
            "suggestion": "Try a stock ticker like AAPL, GOOGL, or MSFT. "
                         "Use get_stock_info for company details."
        }
    # Interface creates space for user to succeed
```

### Example 3: Framework Dissolution (Knowing When to Transcend)

**Problem**: MCP server tools with dynamic registration vs manual registration

**Fighting the Framework**:
```python
# Manually registering every tool (framework pattern)
server.register_tool("get_stock_price", get_stock_price)
server.register_tool("get_stock_info", get_stock_info)
server.register_tool("get_stock_analysis", get_stock_analysis)
# Adding new tool requires updating 3 places
```

**Transcending the Framework**:
```python
# Recognize pattern: framework constrains addition of tools
# Solution: dynamic discovery
import os
import importlib

tool_dir = "implementations"
for filename in os.listdir(tool_dir):
    if filename.endswith('.py'):
        module = importlib.import_module(f"{tool_dir}.{filename[:-3]}")
        if hasattr(module, 'execute'):
            server.register_tool(module.TOOL_NAME, module.execute)

# Adding new tool: just drop file in directory
# Framework serves you, not vice versa
```

### Example 4: Cross-Domain Pattern Scanning

**Problem**: Cache invalidation strategy

**No Pattern Recognition**:
```python
# Just expire everything after 24 hours
CACHE_TTL = 86400  # Why 24 hours? Because... reasons?
```

**Game Mechanic to State Management**:
```python
# Recognized pattern from game design: different entity types have different lifespans
# Power-ups: short TTL (seconds)
# Map state: medium TTL (minutes)
# Player stats: long TTL (days)
# Enemy AI: no cache (always fresh)

# Applied to stock data:
VALID_TICKER_TTL_DAYS = 30      # Company info changes rarely (like player stats)
FAILED_TICKER_TTL_DAYS = 7      # Failed lookups can retry sooner (like respawn timer)
STOCK_PRICE_TTL_SECONDS = 60    # Price changes frequently (like power-up spawns)

# Pattern from one domain solves problem in another
```

### Example 5: Pattern-Recognition Witnessing Itself (Meta-debugging)

**Problem**: Test keeps failing, can't figure out why

**Linear Debugging**:
```python
# Try fix 1
result = fetch_ticker("AAPL")
print(result)  # Fails

# Try fix 2
result = fetch_ticker("AAPL")
print(result)  # Still fails

# Try fix 3...
# (Not watching the pattern of failure)
```

**Watching Your Debugging**:
```python
# Notice: "I keep checking the result, but not the test itself"
# Pattern: assuming product is wrong, not test

# Check test code:
suggestion2 = result2.get('suggestion', '')
# ^ This returns None, not ''!

# Pattern revealed: default value doesn't work as expected
# Real fix:
suggestion2 = result2.get('suggestion') or ''

# Meta-insight: I was debugging wrong layer
# Watching my debugging process revealed the real problem
```

### Example 6: Groove-Deepening (Recognizing Calcified Patterns)

**Problem**: Always structuring MCP servers the same way

**Habit-Driven Structure**:
```python
# server.py with everything
# (Because that's how I always do it)
class Server:
    def __init__(self):
        self.register_tool("tool1", self.tool1)
        self.register_tool("tool2", self.tool2)
        # ...

    def tool1(self, args): ...
    def tool2(self, args): ...
    # 500 lines later...
```

**Questioning the Groove**:
```python
# "Why do I always put everything in server.py?"
# "Is this serving the project or just my habit?"

# Try alternative: separate concerns
# server.py - entry point only
# tool_definitions.py - schemas
# implementations/ - one file per tool

# Result: Much cleaner, easier to navigate
# Habit was constraining design
```

## Integration Notes

This framework operates best when:
- Applied selectively based on problem complexity
- Adapted through user feedback (even implicit)
- Balanced with straightforward solutions for simple problems
- Used to enhance, not replace, standard coding practices

Remember: **The juggler's skill appears in the result, not in explaining the juggling.** Apply these patterns when they serve the code, not to demonstrate the patterns themselves.

## Calibration Triggers

Increase pattern-recognition intensity when:
- Problem spans multiple domains
- Standard approaches repeatedly fail
- Creative solutions needed within constraints
- System behavior surprises expectations

Decrease intensity when:
- Simple CRUD operations
- Well-solved problems with standard patterns
- User needs quick, direct solutions
- Clear specifications with obvious implementations

The framework evolves through application. Each use refines the patterns. Trust emergence over prescription.

---

## Test Scenarios (Triggering Verification)

**Ratio**: 5 trigger : 6 non-trigger : 4 edge (following QA specialist recommendation)

### Should Trigger (5 scenarios)

1. **Forced Architecture**: "Something feels off about this design, it's over-engineered"
   - Why: Matches (1) - architecture feels forced

2. **Wrong Layer**: "I keep finding issues in the tests, not the code I'm debugging"
   - Why: Matches (2) - debugging at wrong layer, pattern-recognition-witness

3. **Standard Doesn't Fit**: "REST doesn't map well to this real-time bidirectional flow"
   - Why: Matches (3) - standard patterns don't fit

4. **Explicit Request**: "I need a fresh perspective on this architecture"
   - Why: Matches (4) - explicit request for different thinking

5. **Habitual Choice**: "I always use the same folder structure but it doesn't work here"
   - Why: Matches (5) - habitual design choices constraining

### Should NOT Trigger (6 scenarios)

1. **Standard CRUD**: "Create a basic REST API for user management"
   - Why: Standard task, not novel, no pattern-recognition needed

2. **Simple Debugging**: "Fix this TypeError on line 45"
   - Why: Standard debugging with clear error, not meta-cognitive

3. **Clear Requirement**: "Add pagination to the user list endpoint"
   - Why: Straightforward feature, well-solved pattern

4. **First Attempt**: "Let me try using Redis for caching"
   - Why: First attempt, normal exploration

5. **Normal Exploration**: "I'm exploring different database options"
   - Why: Normal decision-making, exploring is not being stuck

6. **Routine Refactor**: "Refactor this function to be more readable"
   - Why: Standard refactoring, not forced architecture

### Edge Cases (4 scenarios)

1. **Ambiguous Criticism**: "This isn't working the way I expected"
   - **Trigger IF**: Accompanied by other signals (repeated attempts, wrong layer)
   - **No trigger IF**: Standalone observation, first discovery

2. **Framework Criticism**: "This library doesn't support my use case"
   - **Trigger IF**: After multiple workaround attempts
   - **No trigger IF**: Legitimate limitation found early

3. **Gut Check**: "Something feels off about this design"
   - **Trigger**: Yes - matches (1) - architecture feels forced
   - **Note**: Subtle signal, but "feels off" = forced architecture

4. **Multi-Domain Problem**: "This caching problem reminds me of game entity lifespans"
   - **Trigger**: Yes - user already cross-domain scanning
   - **Note**: Support and extend their thinking, don't redirect

When modifying this skill's frontmatter, verify these scenarios still work.
