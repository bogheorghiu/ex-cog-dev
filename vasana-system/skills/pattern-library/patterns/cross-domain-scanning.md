# Cross-Domain Pattern Scanning

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

**Principle**: Similar dynamics appear across seemingly unrelated systems.

## Core Insight

The problem you're stuck on in web development might have been solved elegantly in game design, or biology, or music composition. Patterns transcend domains. When direct approaches fail, scan for analogous problems in completely different fields.

## Application

- **Game mechanics in state management**: Lives/respawns → retry policies, power-ups → temporary state
- **Biological patterns in system architecture**: Immune systems → anomaly detection, evolution → versioning
- **Musical composition in code rhythm**: Themes/variations → DRY principle, harmony → API consistency
- **Economic systems in resource management**: Supply/demand → caching strategies, markets → load balancing

When stuck, ask: **"Where else have I seen this pattern?"**

## When to Apply

- Cache strategy decisions (game entity lifespans)
- Error handling patterns (biological immune responses)
- State management (musical themes and variations)
- System resilience (ecosystem adaptation)
- Resource allocation (economic markets)

## Anti-Patterns to Watch For

❌ **No Pattern Recognition (Domain Tunnel Vision)**
```python
# Just expire everything after 24 hours
CACHE_TTL = 86400  # Why 24 hours? Because... reasons?
# Not seeing the pattern from other domains
```

✅ **Game Mechanic → State Management**
```python
# Recognized pattern from game design:
# Different entity types have different lifespans
# - Power-ups: short TTL (seconds)
# - Map state: medium TTL (minutes)
# - Player stats: long TTL (days)
# - Enemy AI: no cache (always fresh)

# Applied to stock data:
VALID_TICKER_TTL_DAYS = 30      # Company info changes rarely (like player stats)
FAILED_TICKER_TTL_DAYS = 7      # Failed lookups retry sooner (like respawn timer)
STOCK_PRICE_TTL_SECONDS = 60    # Price changes frequently (like power-up spawns)

# Pattern from one domain solves problem in another
```

## Code Examples

### Example 1: Immune System → Anomaly Detection

**Pattern in Biology:**
- Normal cells: ignored
- Abnormal cells: attacked
- Previously seen threats: remembered
- Unknown threats: investigated

**Applied to Error Handling:**
```python
class ErrorHandler:
    def __init__(self):
        self.known_errors = {}  # "Immune memory"
        self.anomaly_threshold = 3

    def handle(self, error):
        error_signature = str(type(error))

        if error_signature in self.known_errors:
            # Known error → fast response (immune memory)
            return self.known_errors[error_signature]['response']

        # Unknown error → investigate (immune response)
        if self.is_anomaly(error):
            self.alert_team(error)  # "Attack" unknown threat

        # Learn from error (build immunity)
        self.known_errors[error_signature] = {
            'response': self.default_response(error),
            'first_seen': datetime.now()
        }
```

### Example 2: Musical Composition → Code Structure

**Pattern in Music:**
- Theme: Main melody
- Variations: Theme with modifications
- Harmony: Complementary patterns
- Rhythm: Consistent timing

**Applied to API Design:**
```python
# Theme: Base operation
def get_ticker(symbol):
    return fetch_ticker(symbol)

# Variation 1: With caching
def get_ticker_cached(symbol, cache):
    # Same theme, different orchestration
    return cache.get_or_fetch(symbol, fetch_ticker)

# Variation 2: With validation
def get_ticker_validated(symbol):
    # Same theme, validation harmony
    validate_symbol(symbol)
    return fetch_ticker(symbol)

# All variations follow same "melody" (core operation)
# With different "instrumentation" (added features)
```

### Example 3: Economics → Caching Strategy

**Pattern in Markets:**
- High demand goods: Keep well-stocked
- Perishable goods: Short shelf life
- Rare goods: Fetch on demand
- Seasonal goods: Predictable patterns

**Applied to Cache Design:**
```python
class MarketBasedCache:
    def set(self, key, value, access_pattern='rare'):
        if access_pattern == 'high_demand':
            # Like grocery stores stocking bread
            ttl = 3600
            priority = 'high'

        elif access_pattern == 'perishable':
            # Like fresh fish at market
            ttl = 60
            priority = 'low'

        elif access_pattern == 'rare':
            # Like specialty items
            ttl = 86400
            priority = 'medium'

        self._store(key, value, ttl, priority)
```

## Cross-Domain Scanning Checklist

When stuck on a problem:
1. **Name the core dynamic**: "Things with different change rates need different policies"
2. **Scan domains**: Where else do systems handle different change rates?
   - Games: Entity lifespans
   - Biology: Cell regeneration cycles
   - Economics: Inventory turnover
3. **Map the pattern**: How did they solve it there?
4. **Adapt to your domain**: Apply the principle, not the literal solution

## Integration with Other Vasanas

- **Concrete↔Abstract Dance**: Patterns from other domains = abstract templates to test concretely
- **Pattern-Recognition Witnessing**: Notice when you're stuck using only one domain's patterns
- **Interface as Reality-Creation**: UI patterns from games → web interface design

## Recognition Signals

**You're scanning across domains when:**
- Asking "where else does this problem appear?"
- Finding solutions in unexpected places
- Noticing "this is just like [different domain]"
- Borrowing metaphors from other fields

**You're domain-locked when:**
- Only looking at similar code/projects
- Reinventing solutions that exist elsewhere
- Stuck because "standard patterns don't fit"
- Not seeing obvious analogies from other fields
