---
name: macro-monitor
description: What is moving in the macro picture? Geopolitical/macro market indicators. Use when (1) China/US Treasury dynamics, (2) dollar-yield divergence, (3) Brent crude oil / energy price spikes, (4) geopolitical market risk, (5) one-command crisis check, (6) EUR/RON exchange rate monitoring. NOT for stock analysis or fundamentals.
---

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

# Macro Monitor - Geopolitical Financial Checklist

## Purpose

Structured monitoring of macro/geopolitical financial indicators using **free public data sources**.

## Quick Checklist

### 1. Foreign Treasury Holdings (Monthly)

**Source:** Treasury TIC Data (https://ticdata.treasury.gov/Publish/mfh.txt)

**What to check:**
- China holdings level (normal: $700B-$1.3T)
- Japan holdings level (normal: $1.0T-$1.3T)
- Month-over-month change
- Trend direction over 6 months

**Red flags:**
- Drop >$50B in single month
- China drops below $600B
- Coordinated selling (China + Japan both selling)

### 2. Dollar Index vs 10Y Yield (Daily)

**Sources:**
- DXY: FRED series DTWEXBGS (https://fred.stlouisfed.org/series/DTWEXBGS)
- 10Y: FRED series DGS10 (https://fred.stlouisfed.org/series/DGS10)

**Normal behavior:** Higher yields → stronger dollar

**Red flag patterns:**
| Yields | Dollar | Interpretation |
|--------|--------|----------------|
| Up | Down | Confidence crisis - foreign selling |
| Down | Down | Flight from US assets |
| Up | Up | Normal - higher rates attract capital |

**Critical divergence:** Yields rising + Dollar falling = investigate immediately

### 3. Central Bank Gold (Monthly)

**Source:** World Gold Council or PBOC announcements

**What to check:**
- PBOC monthly gold purchases
- Cumulative central bank buying
- Gold price trend vs dollar

**Red flags:**
- PBOC buying >20 tonnes/month sustained
- Multiple central banks buying simultaneously
- Gold rising despite dollar strength

### 4. Yield Curve (Daily)

**Source:** FRED series T10Y2Y (https://fred.stlouisfed.org/series/T10Y2Y)

**What to check:**
- 10Y-2Y spread
- Inversion status
- Duration of inversion

**Warning levels:**
| Spread | Status |
|--------|--------|
| >100bp | Normal, healthy |
| 0-50bp | Flattening, watch closely |
| <0bp | Inverted - recession signal |

### 5. EUR/RON Exchange Rate (Daily)

**Source:** BNR (National Bank of Romania) XML feed
- Current day: https://www.bnr.ro/nbrfxrates.xml
- Last 10 days: https://www.bnr.ro/nbrfxrates10days.xml

**What to check:**
- Current EUR/RON rate
- 10-day trend direction and magnitude
- Proximity to alert thresholds

**Red flags:**
| EUR/RON | Level | Interpretation |
|---------|-------|----------------|
| < 5.05 | Normal | Stable, within historical range |
| >= 5.05 | WARNING | RON weakening, monitor inflation impact on savings |
| >= 5.10 | CRITICAL | Significant depreciation, consider hedging |

**Why it matters:** EUR/RON directly impacts purchasing power for EUR-denominated goods/services and savings held in RON. A weakening RON erodes real value of RON savings and increases import costs.

## Data Retrieval

### Automated Scripts

**FRED data:** `python3 scripts/fred_fetcher.py [series_id|snapshot|divergence|crisis]`
- `snapshot` — all 7 macro series (Treasury, dollar, VIX, Fed funds, Brent, EUR, yield curve)
- `divergence` — yield-dollar divergence check with interpretation
- `crisis` — red flag alert check (Brent >$120, VIX >35, 10Y >5%, yield curve inverted, USD/EUR >1.20)
- `[SERIES_ID]` — latest value for any FRED series

**BNR data:** `python3 scripts/bnr_fetcher.py [latest|trend|alert]`
- `latest` (default) — current EUR/RON rate from BNR
- `trend` — 10-day EUR/RON trend with direction and magnitude
- `alert` — check EUR/RON against warning (5.05) and critical (5.10) thresholds

**TIC data:** `python3 scripts/tic_parser.py`

### Manual Quick Check

```bash
# Get latest 10Y yield
curl -s "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10" | tail -5

# Get latest dollar index
curl -s "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS" | tail -5
```

## Interpretation Framework

### Growth vs Value Sensitivity

**Growth stocks** (tech, high P/E):
- More sensitive to rate increases
- Future cash flows discounted at higher rates
- Sell on yield spikes

**Value stocks** (utilities, banks):
- Less rate-sensitive
- Banks may benefit from higher rates
- More defensive in rate environment

### Sector Impact Matrix

| Indicator | Tech Impact | Bank Impact | Utility Impact |
|-----------|-------------|-------------|----------------|
| Yields up | Negative | Positive | Negative |
| Dollar up | Mixed (int'l) | Positive | Neutral |
| Gold up | Neutral | Neutral | Defensive signal |
| TIC selling | Negative | Negative | Defensive demand |

## When to Escalate

**Immediate attention required if:**
1. Dollar-yield divergence >3 days
2. China TIC drop >$50B in month
3. Multiple indicators red simultaneously
4. Pattern resembles April 2025 event

## Reference Materials

See `reference/` subdirectory for:
- Historical divergence patterns
- Detailed indicator documentation
- Source URLs and update schedules

---

**Update frequency:** Check TIC monthly (mid-month release), FRED daily for divergence monitoring, BNR daily for EUR/RON.
