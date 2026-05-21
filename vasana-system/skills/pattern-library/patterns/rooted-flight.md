# Rooted Flight

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

**Principle**: Constraints create possibilities. Deep grounding enables creative transcendence.

## Core Insight

The best innovations don't come from ignoring fundamentals - they come from mastering them so deeply you can see beyond them. Constraints aren't limitations to work around; they're the launch pad for creativity.

## Application

- **Master fundamentals to innovate effectively**: You can't transcend rules you don't understand
- **Best abstractions emerge from concrete implementations**: Build working code first, extract patterns after
- **Know the rules to transcend them meaningfully**: Breaking conventions works when you understand why they exist

## When to Apply

- Starting new projects: Learn the domain deeply before trying to "innovate"
- Choosing technologies: Understand the constraints before engineering around them
- Creating abstractions: Ground them in real use cases, not theoretical possibilities

## Anti-Patterns to Watch For

❌ **Premature Innovation**
```python
# Trying to build "better" abstraction without understanding problem
class GenericDataProcessor:
    """Revolutionary new pattern!"""
    # But... what problem does this solve?
```

✅ **Grounded Innovation**
```python
# First: Understand the actual pattern
def process_stock_data(ticker):
    # Concrete implementation that works

def process_crypto_data(symbol):
    # Another concrete implementation

# Then: Extract abstraction from real patterns
class MarketDataProcessor:
    # Now we know what needs to be generic
```

## Code Example

**❌ Ungrounded "Clever" Code**
```python
# Trying to be clever without understanding constraints
def fetch(resource, **kwargs):
    # What's a resource? What kwargs are valid?
    # No grounding in actual use cases
```

**✅ Rooted Flight**
```python
# Start grounded:
def fetch_stock_price(ticker):
    """Get current price for stock ticker"""
    return yf.Ticker(ticker).info['currentPrice']

# Use it, understand constraints:
# - Tickers are strings
# - API has rate limits
# - Prices change frequently
# - Need caching

# Now transcend with understanding:
def fetch_market_data(symbol, asset_type='stock', cache_ttl=60):
    """
    Generic fetcher grounded in actual constraints:
    - Rate limits → caching
    - Asset types → explicit parameter
    - Price volatility → configurable TTL
    """
```

The second version is "clever" but **grounded in understanding the problem space**.

## Integration with Other Vasanas

- **Concrete↔Abstract Dance**: Implements the movement from grounded to transcendent
- **Framework Dissolution**: Knowing rules enables meaningful transcendence
- **Groove-Deepening**: Mastery without calcification

## Recognition Signals

**You're applying Rooted Flight when:**
- Learning domain thoroughly before architecting
- Testing abstractions against real use cases
- Building working examples before generalizing

**You're missing it when:**
- Designing "flexible" systems with no concrete requirements
- Creating abstractions that handle hypothetical cases
- Choosing "interesting" patterns over proven solutions
