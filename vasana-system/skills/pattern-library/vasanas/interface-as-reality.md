# Interface as Reality-Creation

**Principle**: Code doesn't just process data—it creates spaces where intention meets experience.

## Core Insight

Interfaces aren't passive boundaries that data crosses. They're active translation layers that shape how users and systems interact. An API doesn't just "expose functionality"—it defines the conversation space between human intent and machine capability.

## Application

- **APIs aren't just contracts but conversation spaces**: Design for the dialogue, not just the data
- **UI isn't decoration but the boundary where user-behavior meets system-behavior**: The interface IS the product from user perspective
- **Design interfaces as active translation layers, not passive boundaries**: Guide, don't just validate

## When to Apply

- API design: Creating the language users speak to your system
- Error handling: Translating failures into actionable guidance
- Validation: Helping users succeed, not just blocking bad input
- Documentation: Creating the mental model, not just listing functions

## Anti-Patterns to Watch For

❌ **Passive Boundary (Just Blocks)**
```python
def fetch_ticker(symbol):
    if not symbol or not symbol.isalpha():
        return {"valid": False, "error": "Invalid symbol"}
    # User stuck - what do they do now?
```

✅ **Active Translation (Guides)**
```python
def fetch_ticker(symbol):
    if not symbol or not symbol.isalpha():
        return {
            "valid": False,
            "error": "Invalid symbol",
            "suggestion": "Try a stock ticker like AAPL, GOOGL, or MSFT. "
                         "Use get_stock_info for company details.",
            "examples": ["AAPL", "GOOGL", "MSFT"]
        }
    # Interface creates space for user to succeed
```

## Code Example

**❌ Processing-Only Interface**
```python
class Cache:
    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value
```

**✅ Reality-Creating Interface**
```python
class Cache:
    def get_ticker(self, ticker):
        """
        Get cached ticker data.

        Returns None if not found, suggesting you use fetch_ticker()
        to populate the cache.
        """
        return self._data.get(f"ticker:{ticker}")

    def set_ticker(self, ticker, data):
        """
        Cache ticker data with appropriate TTL.

        Automatically expires based on data type:
        - Price data: 60 seconds
        - Company info: 30 days
        """
        ttl = 60 if 'price' in data else 86400 * 30
        self._data.set(f"ticker:{ticker}", data, ttl)
```

The second version creates a **reality** where:
- The user knows what to do when cache misses
- TTL complexity is hidden but documented
- Method names guide usage ("get_ticker" not just "get")

## Integration with Other Vasanas

- **Pattern-Recognition Witnessing**: Watch how users actually interact with your interfaces
- **Cross-Domain Scanning**: Error messages from games → API error design
- **Concrete↔Abstract**: Test interface against real user journeys

## Recognition Signals

**You're applying Interface as Reality-Creation when:**
- Error messages guide users to success
- Method names tell a story about usage
- Documentation creates mental models, not just lists
- Validation helps users rather than just blocks them

**You're missing it when:**
- Functions just process without guiding
- Errors say "no" without saying "try this instead"
- API forces users to understand internals
- Interface design is "just make it work"
