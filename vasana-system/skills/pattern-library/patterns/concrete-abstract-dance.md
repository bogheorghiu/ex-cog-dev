# Concrete↔Abstract Dance

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

**Principle**: Abstractions without grounding fail; implementations without patterns sprawl.

## Core Insight

The path to good abstractions isn't "think hard about the general case." It's "build working examples, notice the pattern, extract it." Then test that extraction against new concrete cases. Abstractions and implementations inform each other in a continuous dance.

## Application

- **Start with working examples, extract patterns**: Don't abstract until you have 2-3 concrete cases
- **Test abstractions against multiple concrete cases**: If it doesn't simplify real usage, it's wrong
- **Let implementation details reveal design patterns**: The pattern lives in the code, not your head
- **Ground architectural decisions in actual use cases**: "Flexible" without concrete use cases = over-engineered

## When to Apply

- Designing reusable components: Build specific first, generalize after
- Creating libraries/frameworks: Start with real usage, extract common patterns
- Refactoring: Look for actual repetition, not hypothetical reuse
- Architecture decisions: Ground in concrete requirements, not abstract "flexibility"

## Anti-Patterns to Watch For

❌ **Abstract-First Approach (Fails)**
```python
class DataFetcher:
    """Generic data fetcher with caching"""
    def fetch(self, resource_id, provider):
        # Too abstract - what's a resource? what's a provider?
        # No grounding in actual use cases
        pass
```

✅ **Concrete-First Approach (Works)**
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
# Now you know what needs to be generic
```

## Code Example: The Dance in Action

**Step 1: Concrete**
```python
# Fetch stock price (first use case)
def get_stock(ticker):
    return yfinance.Ticker(ticker).info['currentPrice']

# Fetch crypto price (second use case)
def get_crypto(symbol):
    return requests.get(f'crypto-api/{symbol}').json()['price']
```

**Step 2: Notice Pattern**
```
Both:
- Take identifier (ticker/symbol)
- Call external API
- Extract price from response
- Need error handling
- Need caching
```

**Step 3: Abstract (Test Against Concrete)**
```python
class MarketDataFetcher:
    def __init__(self, cache_manager):
        self.cache = cache_manager

    def get_price(self, symbol, asset_type='stock'):
        # Abstraction grounded in concrete cases
        cache_key = f"{asset_type}:{symbol}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        if asset_type == 'stock':
            price = yfinance.Ticker(symbol).info['currentPrice']
        elif asset_type == 'crypto':
            price = requests.get(f'crypto-api/{symbol}').json()['price']

        self.cache.set(cache_key, price, ttl=60)
        return price
```

**Step 4: Test Against Concrete**
```python
# Does it simplify the original use cases?
fetcher = MarketDataFetcher(cache)

# Stock case:
stock_price = fetcher.get_price('AAPL', 'stock')  # ✓ Simpler

# Crypto case:
crypto_price = fetcher.get_price('BTC', 'crypto')  # ✓ Simpler

# If abstraction makes concrete cases HARDER, it's wrong
```

## The Dance Continues

After using the abstraction in real code, you might notice:
- "asset_type parameter is annoying" → Maybe two methods better?
- "Always passing cache_manager" → Maybe singleton pattern?
- "Error handling repeated" → Extract to decorator?

Each concrete usage informs the next abstraction refinement.

## Integration with Other Vasanas

- **Rooted Flight**: Grounding enables meaningful abstraction
- **Groove-Deepening**: Habits push toward premature abstraction
- **Framework Dissolution**: Bad abstractions become constraining frameworks

## Recognition Signals

**You're in the dance when:**
- Building working code before extracting patterns
- Testing abstractions against real use cases
- Refactoring only when pattern is clear (2-3 instances)
- Abstractions simplify concrete code, not complicate it

**You've stopped dancing when:**
- Designing abstractions before writing concrete code
- Creating "flexible" systems for hypothetical use cases
- Abstractions make simple cases complex
- Justifying abstraction with "we might need it later"
