#!/usr/bin/env python3
"""
FRED Data Fetcher - Free public data from Federal Reserve Economic Data

No API key required for basic CSV downloads.

Commonly used series:
- DGS10: 10-Year Treasury Constant Maturity Rate
- DTWEXBGS: Nominal Broad U.S. Dollar Index
- DCOILBRENTEU: Brent Crude Oil Price
- DEXUSEU: USD per EUR Exchange Rate
- T10Y2Y: 10-Year Treasury Minus 2-Year Treasury (yield curve)
- VIXCLS: CBOE Volatility Index
- FEDFUNDS: Federal Funds Effective Rate
"""

from __future__ import annotations
import urllib.request
import csv
from datetime import datetime, timedelta
from io import StringIO
from typing import Optional


# Common macro series for quick reference
MACRO_SERIES = {
    "DGS10": "10-Year Treasury Yield",
    "DTWEXBGS": "Broad Dollar Index",
    "T10Y2Y": "10Y-2Y Yield Spread",
    "VIXCLS": "VIX Volatility Index",
    "FEDFUNDS": "Federal Funds Rate",
    "DCOILBRENTEU": "Brent Crude Oil ($/barrel)",
    "DEXUSEU": "USD/EUR Exchange Rate",
}



def _build_fred_url(
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    last_n_days: int = 30,
) -> str:
    """Build the FRED CSV download URL (pure — no I/O)."""
    base_url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

    if start_date:
        base_url += f"&cosd={start_date}"
    else:
        # Default to last N days
        start = (datetime.now() - timedelta(days=last_n_days)).strftime("%Y-%m-%d")
        base_url += f"&cosd={start}"

    if end_date:
        base_url += f"&coed={end_date}"

    return base_url


def _parse_fred_csv(data: str, series_id: str) -> list[dict]:
    """
    Parse FRED CSV text into a list of {date, value} dicts (pure — no I/O).

    Skips FRED's '.' missing-value marker and any non-numeric values.
    """
    results = []
    reader = csv.DictReader(StringIO(data))
    for row in reader:
        date = row.get('DATE', row.get('date', ''))
        value = row.get(series_id, row.get('value', ''))

        # Skip missing values (FRED uses '.' for missing)
        if value and value != '.':
            try:
                results.append({
                    'date': date,
                    'value': float(value)
                })
            except ValueError:
                pass

    return results


def fetch_fred_series(
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    last_n_days: int = 30,
) -> list[dict]:
    """
    Fetch data from FRED for a given series.

    Thin I/O wrapper: builds the URL, downloads, and delegates parsing to the
    pure helpers (_build_fred_url / _parse_fred_csv) so the logic is testable
    without network access.

    Args:
        series_id: FRED series identifier (e.g., 'DGS10')
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        last_n_days: If no dates provided, fetch last N days (default 30)

    Returns:
        List of dicts with 'date' and 'value' keys
    """
    base_url = _build_fred_url(series_id, start_date, end_date, last_n_days)

    try:
        with urllib.request.urlopen(base_url, timeout=10) as response:
            data = response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error fetching {series_id}: {e}")
        return []

    return _parse_fred_csv(data, series_id)


def get_latest(series_id: str) -> Optional[dict]:
    """Get the most recent value for a series."""
    data = fetch_fred_series(series_id, last_n_days=14)
    return data[-1] if data else None


def analyze_divergence(yields_data: list[dict], dollar_data: list[dict], days: int = 5) -> dict:
    """
    Classify a yield-dollar divergence pattern from already-fetched series
    (pure — no I/O, so it can be tested with fixtures).

    Normal: Yields up → Dollar up
    Red flag: Yields up + Dollar down (or vice versa)

    Args:
        yields_data: list of {date, value} for the yield series (oldest first)
        dollar_data: list of {date, value} for the dollar series (oldest first)
        days: nominal comparison window, echoed back in the result

    Returns dict with analysis, or {"error": ...} if there's too little data.
    """
    if len(yields_data) < 2 or len(dollar_data) < 2:
        return {"error": "Insufficient data"}

    # Use first and last available points. Window is approximate since
    # trading days != calendar days (fetches days+14 calendar days of data,
    # actual comparison span depends on market holidays).
    yield_change = yields_data[-1]['value'] - yields_data[0]['value']
    dollar_change = dollar_data[-1]['value'] - dollar_data[0]['value']

    # Determine pattern
    yield_direction = "up" if yield_change > 0.05 else ("down" if yield_change < -0.05 else "flat")
    dollar_direction = "up" if dollar_change > 0.5 else ("down" if dollar_change < -0.5 else "flat")

    # Check for divergence
    divergence = False
    if yield_direction == "up" and dollar_direction == "down":
        divergence = True
        interpretation = "RED FLAG: Yields rising but dollar falling - potential foreign selling / confidence crisis"
    elif yield_direction == "down" and dollar_direction == "down":
        divergence = True
        interpretation = "WARNING: Both falling - flight from US assets"
    elif yield_direction == "up" and dollar_direction == "up":
        interpretation = "Normal: Higher rates attracting capital"
    else:
        interpretation = "Stable or mixed signals"

    return {
        "period_days": days,
        "yield_latest": yields_data[-1]['value'],
        "yield_change": round(yield_change, 3),
        "yield_direction": yield_direction,
        "dollar_latest": dollar_data[-1]['value'],
        "dollar_change": round(dollar_change, 2),
        "dollar_direction": dollar_direction,
        "divergence_detected": divergence,
        "interpretation": interpretation,
        "as_of": yields_data[-1]['date']
    }


def check_divergence(yields_series: str = "DGS10", dollar_series: str = "DTWEXBGS", days: int = 5) -> dict:
    """
    Fetch the two series and classify their divergence.

    Thin I/O wrapper around analyze_divergence().
    """
    yields_data = fetch_fred_series(yields_series, last_n_days=days + 14)
    dollar_data = fetch_fred_series(dollar_series, last_n_days=days + 14)
    return analyze_divergence(yields_data, dollar_data, days=days)


def macro_snapshot() -> dict:
    """Get a quick snapshot of key macro indicators."""
    snapshot = {}

    for series_id, name in MACRO_SERIES.items():
        latest = get_latest(series_id)
        if latest:
            snapshot[series_id] = {
                "name": name,
                "value": latest['value'],
                "date": latest['date']
            }
        else:
            snapshot[series_id] = {"name": name, "error": "Failed to fetch"}

    # Add divergence check
    snapshot["divergence_analysis"] = check_divergence()

    return snapshot


RED_FLAGS = {
    "DCOILBRENTEU": {"name": "Brent Crude", "high": 120, "low": 70},
    "VIXCLS": {"name": "VIX", "high": 35, "critical": 45},
    "T10Y2Y": {"name": "Yield Curve", "inversion": 0},
    "DGS10": {"name": "10Y Yield", "high": 5.0},
    "DEXUSEU": {"name": "USD/EUR (dollar weakening)", "high": 1.20},
}


def evaluate_crisis(snapshot: dict) -> dict:
    """
    Apply RED_FLAGS thresholds to an already-built snapshot (pure — no I/O,
    so it can be tested with fixtures).

    Expects a snapshot shaped like macro_snapshot() output: each series maps to
    a dict with a "value" key, plus an optional "divergence_analysis" entry.
    """
    alerts = []

    for series_id, thresholds in RED_FLAGS.items():
        data = snapshot.get(series_id, {})
        value = data.get("value")
        if value is None:
            continue

        name = thresholds["name"]
        if "critical" in thresholds and value > thresholds["critical"]:
            alerts.append(f"🚨 {name}: {value} CRITICAL (above {thresholds['critical']})")
        elif "high" in thresholds and value > thresholds["high"]:
            alerts.append(f"🔴 {name}: {value} (above {thresholds['high']})")
        if "low" in thresholds and value < thresholds["low"]:
            alerts.append(f"🔴 {name}: {value} (below {thresholds['low']})")
        if "inversion" in thresholds and value < thresholds["inversion"]:
            alerts.append(f"🔴 {name}: {value} INVERTED (recession signal)")

    div = snapshot.get("divergence_analysis", {})
    if div.get("divergence_detected"):
        alerts.append(f"🔴 DIVERGENCE: {div['interpretation']}")

    return {
        "alerts": alerts,
        "alert_count": len(alerts),
        "snapshot": {k: v for k, v in snapshot.items() if k != "divergence_analysis"},
        "divergence": div,
    }


def crisis_check() -> dict:
    """Run all checks and return only alerts. Thin I/O wrapper around evaluate_crisis()."""
    return evaluate_crisis(macro_snapshot())


def main():
    """CLI interface for quick checks."""
    import sys
    import json

    if len(sys.argv) < 2:
        print("FRED Data Fetcher - Free macro data")
        print("\nUsage:")
        print("  python fred_fetcher.py <series_id>     # Get latest value")
        print("  python fred_fetcher.py snapshot        # Quick macro snapshot")
        print("  python fred_fetcher.py divergence      # Check yield-dollar divergence")
        print("  python fred_fetcher.py crisis          # Red flag alert check")
        print("\nCommon series:")
        for sid, name in MACRO_SERIES.items():
            print(f"  {sid}: {name}")
        return

    cmd = sys.argv[1].upper()

    if cmd == "SNAPSHOT":
        result = macro_snapshot()
        print(json.dumps(result, indent=2))
    elif cmd == "DIVERGENCE":
        result = check_divergence()
        print(json.dumps(result, indent=2))
    elif cmd == "CRISIS":
        result = crisis_check()
        if result["alert_count"] == 0:
            print("✅ No red flags. All indicators within normal range.")
        else:
            print(f"⚠️  {result['alert_count']} ALERT(S):")
            for alert in result["alerts"]:
                print(f"  {alert}")
        print()
        for series_id, thresholds in RED_FLAGS.items():
            data = result['snapshot'].get(series_id, {})
            val = data.get('value', '?')
            print(f"  {thresholds['name']}: {val}")
    else:
        # Treat as series ID
        latest = get_latest(cmd)
        if latest:
            name = MACRO_SERIES.get(cmd, cmd)
            print(f"{name}")
            print(f"  Value: {latest['value']}")
            print(f"  Date:  {latest['date']}")
        else:
            print(f"No data found for series: {cmd}")


if __name__ == "__main__":
    main()
