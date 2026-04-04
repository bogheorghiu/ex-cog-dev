---
name: portfolio-reader
description: >-
  What does my portfolio actually look like right now? Reads local portfolio
  snapshots (Tradeville + IBKR) and provides unified analysis. Use when
  (1) user asks about portfolio, (2) before making investment decisions,
  (3) when macro indicators change significantly, (4) cross-referencing
  positions with cui-bono/stonk or macro-monitor analysis.
---

# Portfolio Reader

## Purpose

Read and analyze local portfolio snapshots from Tradeville (Romanian broker)
and IBKR (Interactive Brokers). Provides a unified view across both accounts.

## Where Data Lives

All portfolio data is local-only (gitignored):

```
.claude/local/portfolio/snapshots/
├── tradeville-YYYY-MM-DD-HHMM.json     # Tradeville positions
├── tradeville-YYYY-MM-DD-HHMM.png      # Tradeville screenshot
├── ibkr-positions-YYYY-MM-DD-HHMM.json # IBKR positions (from API)
├── ibkr-summary-YYYY-MM-DD-HHMM.json   # IBKR account summary (NAV, cash)
├── ibkr-web-YYYY-MM-DD-HHMM.png        # IBKR screenshot (visual verification)
```

## How to Read Snapshots

### Step 1: Find Latest Files

```bash
ls -t .claude/local/portfolio/snapshots/*.json 2>/dev/null | head -5
```

Or use glob to find the most recent by timestamp pattern:
- Tradeville: `tradeville-*.json` (positions array)
- IBKR positions: `ibkr-positions-*.json` (positions with market values)
- IBKR summary: `ibkr-summary-*.json` (NAV, cash, margin, buying power)

### Step 2: Read JSON Data

**Tradeville JSON** contains a positions array with:
- Symbol, quantity, average price, current price
- P&L (realized and unrealized), market value
- Currency (RON-denominated)

**IBKR positions JSON** contains:
- Contract details (symbol, exchange, currency, asset class)
- Position size, market price, market value
- Average cost, unrealized P&L
- Multi-currency (USD, EUR, etc.)

**IBKR summary JSON** contains:
- Net asset value (NAV)
- Cash balances by currency
- Buying power, margin requirements
- Total account value

### Step 3: View Screenshots (Optional)

Read `.png` files for visual verification. Useful when JSON extraction
may have missed data or when the user wants visual confirmation.

## Analysis Capabilities

### Unified Portfolio View

Combine Tradeville + IBKR data into one view:
1. Read latest JSON from both brokers
2. Normalize currencies (RON positions from Tradeville, multi-currency from IBKR)
3. Present total portfolio value, position-level detail, allocation breakdown

### Sector Allocation

Group positions by sector/geography:
- Romanian equities (Tradeville)
- International equities (IBKR)
- Energy sector exposure (cross-reference with oil prices from macro-monitor)
- Geographic concentration risk

### P&L Analysis

- Per-position unrealized P&L
- Total portfolio P&L
- Best/worst performers
- Cost basis vs current value

### Historical Comparison

Compare snapshots across dates:
```bash
# Find snapshots from different dates
ls .claude/local/portfolio/snapshots/tradeville-*.json
```
- Diff positions between dates (new/closed positions, quantity changes)
- Track portfolio value over time
- Identify trends in allocation shifts

## Cross-References

### With macro-monitor

- **Oil prices (Brent):** Affect energy sector positions (Romgaz, OMV Petrom)
- **EUR/RON rate:** Affects Romanian stock values when comparing to EUR/USD portfolio
- **Interest rates:** Impact bank stocks and bond positions
- **VIX:** High VIX may warrant defensive rebalancing

Run macro-monitor's crisis check for context:
```bash
python3 projects/ex-cog-dev/research-toolkit/skills/macro-monitor/scripts/fred_fetcher.py crisis
```

### With stonk agent / cui-bono

Before making investment decisions, use the stonk agent (or cui-bono directly) for:
- Power structure analysis of potential new positions
- Ethical constraint evaluation
- Multi-polar dynamics assessment

### With deep-investigation-protocol

For in-depth analysis of specific holdings or sectors:
- Use DIP for company-specific deep dives
- Combine with portfolio data to assess concentration risk

## How to Update Data

Portfolio data is now collected via the `portfolio-mcp` MCP server
(`projects/ex-cog-dev/research-toolkit/mcp-servers/portfolio-mcp/`).

### Tradeville (4-step workflow)

1. **`tradeville_login`** — Instructions to run login script in a terminal (MCP stdin is reserved for JSON-RPC; login must happen outside MCP).
2. **`tradeville_discover`** — Opens browser with CDP port for Claude to navigate. Claude calls `tradeville_save_sub_account` for each sub-account found, then calls `tradeville_finish_discover` to close the browser.
3. **`tradeville_set_active_account`** — Set which sub-account to use for routine snapshots.
4. **`tradeville_snapshot`** — Auto-approvable. Navigates to portfolio page; if the sub-account URL uses the `click:` prefix (e.g. `click:Subcont PERSONAL`), clicks through the dropdown to switch sub-accounts. Saves screenshot + JSON.

### IBKR

1. **`ibkr_login`** — Opens visible browser for Client Portal Gateway auth (requires gateway at localhost:5000).
2. **`ibkr_snapshot`** — Auto-approvable. Calls REST API, saves positions + NAV to JSON.

### Status check

```
portfolio_status  — shows auth state, discovered URL, recent snapshots
```

Data dir: `~/.claude/local/portfolio/` (or `$PORTFOLIO_DATA_DIR`).

## When to Use This Skill

| Trigger | Action |
|---------|--------|
| User asks "what's in my portfolio?" | Read latest snapshots, present unified view |
| Before investment decision (task #36, #39) | Read current positions to avoid duplication/overconcentration |
| Macro indicator changes significantly | Cross-reference positions with macro-monitor data |
| User asks about specific position | Find it across both brokers, show details |
| User asks about allocation/exposure | Calculate sector/geography breakdown |

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.
