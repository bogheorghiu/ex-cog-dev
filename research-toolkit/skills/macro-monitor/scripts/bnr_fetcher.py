#!/usr/bin/env python3
"""
BNR (National Bank of Romania) Exchange Rate Fetcher

Fetches EUR/RON and other exchange rates from BNR's public XML feed.

Sources:
- https://www.bnr.ro/nbrfxrates.xml (current day)
- https://www.bnr.ro/nbrfxrates10days.xml (last 10 business days)
"""

from __future__ import annotations
import sys
import urllib.request
import xml.etree.ElementTree as ET
from typing import Optional


BNR_URL_CURRENT = "https://www.bnr.ro/nbrfxrates.xml"
BNR_URL_10DAYS = "https://www.bnr.ro/nbrfxrates10days.xml"

# BNR XML namespace
BNR_NS = {"bnr": "http://www.bnr.ro/xsd"}

# Alert thresholds for EUR/RON
EURRON_THRESHOLDS = {
    "warning": 5.05,
    "critical": 5.10,
}


def parse_bnr_xml(xml_text: str) -> list[dict]:
    """
    Parse BNR XML into a list of rate dicts.

    Each dict has 'date' key plus currency keys (e.g., 'EUR', 'USD').

    Returns empty list on parse error.
    """
    if not xml_text or not xml_text.strip():
        return []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    results = []
    # Find all Cube elements (each represents one day)
    for cube in root.findall('.//bnr:Cube', BNR_NS):
        date = cube.get('date')
        if not date:
            continue

        entry = {'date': date}
        for rate_el in cube.findall('bnr:Rate', BNR_NS):
            currency = rate_el.get('currency')
            if currency and rate_el.text:
                try:
                    entry[currency] = float(rate_el.text)
                except ValueError:
                    pass

        results.append(entry)

    results.sort(key=lambda r: r['date'])
    return results


def fetch_bnr_rates(days: int = 10) -> list[dict]:
    """
    Fetch exchange rates from BNR.

    Args:
        days: 1 for current day, 10 for last 10 business days

    Returns:
        List of rate dicts sorted by date, or empty list on error.
    """
    url = BNR_URL_10DAYS if days > 1 else BNR_URL_CURRENT

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            xml_text = response.read().decode('utf-8')
    except (urllib.error.URLError, OSError) as e:
        print(f"Error fetching BNR data: {e}", file=sys.stderr)
        return []

    return parse_bnr_xml(xml_text)


def get_latest_eurron() -> Optional[dict]:
    """
    Get today's EUR/RON rate.

    Returns:
        Dict with 'rate' and 'date' keys, or None on error.
    """
    rates = fetch_bnr_rates(days=1)
    if not rates:
        return None

    latest = rates[-1]
    if 'EUR' not in latest:
        return None

    return {
        'rate': latest['EUR'],
        'date': latest['date'],
    }


def check_eurron_alert(
    threshold_high: float = EURRON_THRESHOLDS["warning"],
    threshold_critical: float = EURRON_THRESHOLDS["critical"],
) -> Optional[dict]:
    """
    Check EUR/RON against alert thresholds.

    Returns:
        Dict with 'level' ('NORMAL', 'WARNING', 'CRITICAL'), 'rate', 'date'.
        None if data unavailable.
    """
    latest = get_latest_eurron()
    if latest is None:
        return None

    rate = latest['rate']

    if rate >= threshold_critical:
        level = 'CRITICAL'
    elif rate >= threshold_high:
        level = 'WARNING'
    else:
        level = 'NORMAL'

    return {
        'level': level,
        'rate': rate,
        'date': latest['date'],
        'threshold_high': threshold_high,
        'threshold_critical': threshold_critical,
    }


def eurron_trend(days: int = 10) -> Optional[dict]:
    """
    Compute EUR/RON trend over the given period.

    Returns:
        Dict with 'direction' ('up'/'down'/'flat'), 'change', 'start_rate',
        'end_rate', 'start_date', 'end_date'. None if insufficient data.
    """
    rates = fetch_bnr_rates(days=days)
    eur_rates = [r for r in rates if 'EUR' in r]

    if len(eur_rates) < 2:
        return None

    first = eur_rates[0]
    last = eur_rates[-1]
    change = last['EUR'] - first['EUR']

    # Flat threshold: less than 0.005 RON change over the period
    if abs(change) < 0.005:
        direction = 'flat'
    elif change > 0:
        direction = 'up'
    else:
        direction = 'down'

    return {
        'direction': direction,
        'change': round(change, 4),
        'start_rate': first['EUR'],
        'end_rate': last['EUR'],
        'start_date': first['date'],
        'end_date': last['date'],
        'days': len(eur_rates),
    }


def main():
    """CLI interface."""
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else 'latest'

    if cmd not in ('latest', 'trend', 'alert'):
        print(f"Unknown command: {cmd}. Use: latest | trend | alert", file=sys.stderr)
        sys.exit(1)

    if cmd == 'latest':
        result = get_latest_eurron()
        if result:
            print(f"EUR/RON: {result['rate']:.4f}")
            print(f"Date:    {result['date']}")
        else:
            print("Failed to fetch EUR/RON rate from BNR")

    elif cmd == 'trend':
        result = eurron_trend(days=10)
        if result:
            arrow = {'up': '^', 'down': 'v', 'flat': '='}[result['direction']]
            print(f"EUR/RON Trend ({result['days']} days): {result['direction'].upper()} {arrow}")
            print(f"  {result['start_date']}: {result['start_rate']:.4f}")
            print(f"  {result['end_date']}: {result['end_rate']:.4f}")
            print(f"  Change: {result['change']:+.4f}")
        else:
            print("Failed to compute EUR/RON trend")

    elif cmd == 'alert':
        result = check_eurron_alert()
        if result:
            if result['level'] == 'CRITICAL':
                print(f"CRITICAL: EUR/RON {result['rate']:.4f} >= {result['threshold_critical']}")
            elif result['level'] == 'WARNING':
                print(f"WARNING: EUR/RON {result['rate']:.4f} >= {result['threshold_high']}")
            else:
                print(f"NORMAL: EUR/RON {result['rate']:.4f} (below {result['threshold_high']})")
            print(f"Date: {result['date']}")
        else:
            print("Failed to check EUR/RON alert")


if __name__ == "__main__":
    main()
