# Financial MCP Server - Demo Guide

## Showcasing the Deployed MCP Server

This guide demonstrates how to showcase the Financial MCP Server working with Claude Code/Desktop after deployment.

## Approach: Claude Desktop Integration Demo

This follows **Approach C** from ANTHROPIC_UX_INTEGRATION.md - showcasing the MCP server through actual Claude integration rather than building a separate UI.

### Benefits of This Approach

- Zero additional development time
- Shows real MCP functionality in action
- Demonstrates the server's actual integration with Claude
- More impressive than screenshots - shows live interaction
- Highlights backend quality and caching performance

## Demo Scenarios

### Scenario 1: Stock Price Lookup

**User Request:**
"What's the current stock price for Apple?"

**Expected Claude Response:**
```
I'll get the current stock price for Apple (AAPL).

[Uses get_stock_price tool]

Current price for AAPL: $150.23
Change: +2.34 (+1.58%)
Last updated: 2025-11-22 14:30:00 EST

The stock is currently trading at $150.23, up $2.34 from the previous close.
```

**What to Highlight:**
- Fast response time (cache working)
- Clean, formatted output
- Real-time data from yfinance

---

### Scenario 2: Historical Data Analysis

**User Request:**
"Show me the stock history for Microsoft over the last month"

**Expected Claude Response:**
```
I'll fetch the historical data for Microsoft (MSFT) over the last month.

[Uses get_stock_history tool]

Historical Data for MSFT (1 month):

Summary Statistics:
- Current Price: $380.45
- Period High: $385.20 (2025-11-15)
- Period Low: $365.10 (2025-10-25)
- Average Price: $375.30
- Total Volume: 125,450,000

Recent Trend: Upward (+4.2% over period)

[Dataset includes 22 trading days with full OHLCV data]
```

**What to Highlight:**
- Rich dataset with statistics
- Summary calculations performed by server
- Cache speeds up subsequent requests

---

### Scenario 3: Comprehensive Stock Info

**User Request:**
"Give me detailed information about Tesla"

**Expected Claude Response:**
```
I'll get comprehensive information about Tesla (TSLA).

[Uses get_stock_info tool]

Company Information for TSLA:
- Name: Tesla, Inc.
- Sector: Consumer Cyclical
- Industry: Auto Manufacturers
- Market Cap: $780.5B
- P/E Ratio: 65.3
- 52-Week Range: $138.80 - $299.29

Fundamentals:
- EPS: $4.12
- Dividend Yield: N/A (No dividend)
- Beta: 2.01
- Average Volume: 125.4M

Recent Splits: 3-for-1 stock split on 2022-08-25
```

**What to Highlight:**
- Comprehensive data from yfinance
- Fallback mechanism (fast_info → history)
- Error handling for edge cases

---

### Scenario 4: Technical Indicators

**User Request:**
"What are the technical indicators for NVIDIA?"

**Expected Claude Response:**
```
I'll analyze the technical indicators for NVIDIA (NVDA).

[Uses get_technical_indicators tool]

Technical Indicators for NVDA (1 year period):

Moving Averages:
- SMA 20: $485.30
- SMA 50: $475.60
- SMA 200: $425.10

Current price ($492.15) is:
- Above SMA 20: Bullish short-term
- Above SMA 50: Bullish medium-term
- Above SMA 200: Bullish long-term

RSI (14-day): 62.5
- Status: Neutral (between 30-70)
- Not overbought or oversold

Volume Analysis:
- Average Volume: 48.5M
- Recent Volume: 52.3M
- Volume Trend: Slightly elevated
```

**What to Highlight:**
- Complex calculations performed server-side
- Technical analysis expertise
- Clear buy/sell/neutral signals

---

### Scenario 5: Comprehensive Stock Analysis

**User Request:**
"Analyze Amazon's stock performance"

**Expected Claude Response:**
```
I'll perform a comprehensive analysis of Amazon (AMZN).

[Uses get_stock_analysis tool]

Comprehensive Analysis for AMZN (6 months):

Price Action:
- Current: $145.60
- 6-Month Change: +12.5%
- Volatility: Medium (σ = 2.8%)

Pattern Detection:
- Trend: Upward channel
- Support Level: $138.50
- Resistance Level: $152.30

Anomalies Detected:
- Volume spike on 2025-10-27 (earnings day)
- Gap up on 2025-11-01 (+3.2%)

Trading Signals:
- MACD: Bullish crossover
- Moving Average: Above 50-day MA
- Volume: Confirming uptrend

Overall Sentiment: Bullish
```

**What to Highlight:**
- Advanced pattern detection
- Anomaly identification
- Multiple indicator synthesis

---

### Scenario 6: Force Refresh Demonstration

**User Request:**
"Force refresh the ticker for Google"

**Expected Claude Response:**
```
I'll force a fresh validation of Google's ticker (GOOGL).

[Uses force_fetch_ticker tool]

Ticker Validation for GOOGL:
- Status: Valid and active
- Exchange: NASDAQ
- Currency: USD
- Fresh data retrieved bypassing cache
- Timestamp: 2025-11-22 14:32:15

This ticker is confirmed valid and ready for use with other tools.
```

**What to Highlight:**
- Cache bypass mechanism
- Validation functionality
- Use case: verifying ticker before bulk operations

---

## Demo Format Options

### Option A: Screen Recording

**Tools Needed:**
- Screen recording software (OBS, QuickTime, Loom)
- Claude Desktop or Claude Code
- Microphone (optional for narration)

**Steps:**
1. Open Claude Desktop/Code
2. Ensure MCP server is configured and connected
3. Record screen
4. Run through 2-3 demo scenarios
5. Highlight:
   - Tool discovery in Claude
   - Real-time responses
   - Cache performance (second request faster)
   - Error handling (try invalid ticker)
6. Edit and export video

**Duration:** 3-5 minutes

---

### Option B: Written Walkthrough with Screenshots

**Steps:**
1. Configure Claude Code with deployed server
2. Take screenshots of:
   - MCP configuration in Claude
   - Each tool being used
   - Responses with formatted data
3. Create Markdown document with:
   - Setup instructions
   - Screenshot + explanation for each tool
   - Performance notes
   - Integration benefits

**Format:** Markdown or blog post

---

### Option C: Interactive GIF Demo

**Tools Needed:**
- Terminalizer, asciinema, or LICEcap
- Claude Code CLI

**Steps:**
1. Record terminal session
2. Show Claude Code commands
3. Demonstrate tool usage
4. Export as GIF or embeddable player

**Benefit:** Lightweight, embeddable in README

---

## Demo Script

### Opening (30 seconds)

"This is the Financial MCP Server deployed on Railway, integrated with Claude Code. It provides 6 financial data tools with intelligent caching and error handling."

### Tool Demonstrations (2-3 minutes)

Walk through 3-4 scenarios above, showing:
1. Fast response times
2. Rich data formatting
3. Cache performance
4. Error handling

### Technical Highlights (30 seconds)

"Behind the scenes, this server features:
- 3-layer caching architecture
- Intelligent validation (format → cache → API)
- Context-aware error messages
- Graceful fallbacks
- Production-ready design"

### Closing (30 seconds)

"The server is deployed via Docker on Railway, accessible remotely via HTTP/SSE transport. All code is on GitHub."

---

## What Makes This Demo Effective

1. **Real Integration**: Shows actual Claude using your tools, not mockups
2. **Performance Proof**: Cache benefits are visible (first vs second request)
3. **Error Handling**: Try invalid tickers to show graceful failures
4. **Zero UI Development**: No frontend needed, Claude IS the UI
5. **Differentiation**: Most MCP demos are code walkthroughs; this shows live usage

---

## Configuration for Demo

### Claude Code Configuration

```bash
# Add deployed MCP server
claude mcp add --transport sse financial-server https://your-app.railway.app/sse

# Verify connection
claude mcp list

# Test a tool
claude "Get stock price for AAPL"
```

### Claude Desktop Configuration

Edit `~/.claude/config.json` (macOS/Linux) or `%APPDATA%\Claude\config.json` (Windows):

```json
{
  "mcpServers": {
    "financial-server": {
      "transport": "sse",
      "url": "https://your-app.railway.app/sse"
    }
  }
}
```

---

## Recording Best Practices

1. **Clean Terminal**: Clear scrollback before recording
2. **Font Size**: Increase terminal font for readability
3. **Slow Down**: Type slower than normal or use prepared commands
4. **Show Delays**: Let viewers see response times
5. **Highlight Cache**: Run same query twice to show speed difference
6. **Error Handling**: Intentionally try invalid ticker to show error messages

---

## Publishing the Demo

### Where to Share

1. **GitHub README**: Embed GIF or link to video
2. **YouTube/Vimeo**: Full walkthrough video
3. **Twitter/LinkedIn**: Short clips highlighting key features
4. **Dev.to/Medium**: Written walkthrough with screenshots
5. **MCP Community**: Share in MCP server showcases

### Demo Repository Structure

```
README.md
├── Link to demo video
├── Screenshot gallery
├── Quick start guide
└── Link to deployed instance

DEMO.md (this file)
├── Detailed demo scenarios
├── Recording guide
└── Configuration instructions
```

---

## Next Steps

1. Deploy MVP to Railway
2. Test all 6 tools work remotely
3. Record demo following one of the formats above
4. Publish demo materials
5. Share with MCP community

---

## References

- **ANTHROPIC_UX_INTEGRATION.md**: Approach C rationale
- **DEPLOY.md**: Deployment instructions
- **DEPLOYMENT_PLAN.md**: Technical architecture
- **Claude Desktop Docs**: https://docs.claude.com/en/docs/claude-desktop
