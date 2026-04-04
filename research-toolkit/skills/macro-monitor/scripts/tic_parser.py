#!/usr/bin/env python3
"""
TIC Data Parser - Treasury International Capital (Foreign Holdings of US Securities)

Source: https://ticdata.treasury.gov/Publish/mfh.txt

This data shows how much US Treasury securities are held by foreign countries.
Updated monthly (mid-month for prior month data).

Key countries to monitor:
- Japan: Largest holder (~$1.1-1.3T)
- China: Second/Third largest (~$700B-1T, declining from $1.3T peak)
- UK: Major holder (~$700-900B)
"""

from __future__ import annotations
import urllib.request
import re
from datetime import datetime
from typing import Optional


TIC_URL = "https://ticdata.treasury.gov/Publish/mfh.txt"

# Countries of particular geopolitical interest
KEY_COUNTRIES = ["Japan", "China, Mainland", "United Kingdom", "Belgium", "Luxembourg", "Cayman Islands"]


def fetch_tic_data() -> Optional[str]:
    """Fetch raw TIC data from Treasury."""
    try:
        with urllib.request.urlopen(TIC_URL, timeout=30) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Error fetching TIC data: {e}")
        return None


def parse_tic_data(raw_data: str) -> dict:
    """
    Parse the TIC mfh.txt file.

    The file format is fixed-width with country names and monthly values.
    Returns structured data with holdings by country.
    """
    lines = raw_data.strip().split('\n')

    # Find the header line with dates
    date_line_idx = None
    for i, line in enumerate(lines):
        if re.search(r'\d{4}$', line.strip()):  # Line ending with a year
            date_line_idx = i
            break

    if date_line_idx is None:
        return {"error": "Could not find date header"}

    # Parse dates from header (they appear as months/years)
    date_header = lines[date_line_idx]

    # Extract data lines (countries with their holdings)
    results = {
        "source": TIC_URL,
        "fetched_at": datetime.now().isoformat(),
        "countries": {},
        "key_countries": {}
    }

    # Simple pattern matching for country data lines
    # Format: Country name followed by numbers (in billions)
    for line in lines[date_line_idx + 1:]:
        # Skip empty lines and headers
        if not line.strip() or line.startswith('---') or 'Grand Total' in line:
            continue

        # Try to extract country and latest value
        # TIC format has country name at start, then values
        parts = line.split()
        if len(parts) < 2:
            continue

        # Find where numbers start
        country_parts = []
        values = []
        for part in parts:
            # Check if part looks like a number
            clean_part = part.replace(',', '').replace('*', '').strip()
            try:
                val = float(clean_part)
                values.append(val)
            except ValueError:
                if not values:  # Still in country name
                    country_parts.append(part)

        if country_parts and values:
            country = ' '.join(country_parts)
            latest_value = values[0]  # Most recent month

            # Store all countries
            results["countries"][country] = {
                "latest_holdings_billions": latest_value,
                "recent_values": values[:6] if len(values) >= 6 else values
            }

            # Highlight key countries
            for key_country in KEY_COUNTRIES:
                if key_country.lower() in country.lower():
                    results["key_countries"][country] = {
                        "latest_holdings_billions": latest_value,
                        "recent_values": values[:6] if len(values) >= 6 else values
                    }

    return results


def analyze_holdings(data: dict) -> dict:
    """Analyze TIC data for warning signs."""
    analysis = {
        "warnings": [],
        "observations": []
    }

    key_countries = data.get("key_countries", {})

    for country, info in key_countries.items():
        values = info.get("recent_values", [])
        latest = info.get("latest_holdings_billions", 0)

        if len(values) >= 2:
            # Check month-over-month change
            mom_change = values[0] - values[1]

            if "China" in country:
                analysis["observations"].append(
                    f"China: ${latest:.1f}B (change: ${mom_change:+.1f}B)"
                )
                if latest < 600:
                    analysis["warnings"].append(
                        f"ALERT: China holdings below $600B threshold (${latest:.1f}B)"
                    )
                if mom_change < -50:
                    analysis["warnings"].append(
                        f"ALERT: China sold >${abs(mom_change):.1f}B in single month"
                    )

            elif "Japan" in country:
                analysis["observations"].append(
                    f"Japan: ${latest:.1f}B (change: ${mom_change:+.1f}B)"
                )
                if mom_change < -30:
                    analysis["warnings"].append(
                        f"WARNING: Japan sold >${abs(mom_change):.1f}B in single month"
                    )

            elif "United Kingdom" in country:
                analysis["observations"].append(
                    f"UK: ${latest:.1f}B (change: ${mom_change:+.1f}B)"
                )

    # Check for coordinated selling
    china_selling = False
    japan_selling = False
    for country, info in key_countries.items():
        values = info.get("recent_values", [])
        if len(values) >= 2:
            change = values[0] - values[1]
            if "China" in country and change < -20:
                china_selling = True
            if "Japan" in country and change < -20:
                japan_selling = True

    if china_selling and japan_selling:
        analysis["warnings"].insert(0,
            "CRITICAL: Coordinated selling - both China and Japan reducing holdings"
        )

    return analysis


def get_summary() -> dict:
    """Get a summary of current TIC data with analysis."""
    raw_data = fetch_tic_data()
    if not raw_data:
        return {"error": "Failed to fetch TIC data"}

    parsed = parse_tic_data(raw_data)
    analysis = analyze_holdings(parsed)

    return {
        "key_countries": parsed.get("key_countries", {}),
        "analysis": analysis,
        "source": TIC_URL,
        "fetched_at": parsed.get("fetched_at")
    }


def main():
    """CLI interface."""
    import sys
    import json

    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("TIC Data Parser - Foreign Holdings of US Treasury Securities")
        print("\nUsage:")
        print("  python tic_parser.py           # Get summary with analysis")
        print("  python tic_parser.py full      # Get all countries")
        print("  python tic_parser.py raw       # Get raw parsed data")
        return

    if len(sys.argv) > 1 and sys.argv[1] == "raw":
        raw = fetch_tic_data()
        if raw:
            parsed = parse_tic_data(raw)
            print(json.dumps(parsed, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "full":
        raw = fetch_tic_data()
        if raw:
            parsed = parse_tic_data(raw)
            print(json.dumps(parsed["countries"], indent=2))
    else:
        summary = get_summary()
        print(json.dumps(summary, indent=2))

        # Print human-readable analysis
        if "analysis" in summary:
            print("\n" + "="*50)
            print("ANALYSIS")
            print("="*50)

            for obs in summary["analysis"].get("observations", []):
                print(f"  {obs}")

            warnings = summary["analysis"].get("warnings", [])
            if warnings:
                print("\nWARNINGS:")
                for warn in warnings:
                    print(f"  !! {warn}")
            else:
                print("\n  No warnings - holdings appear stable")


if __name__ == "__main__":
    main()
