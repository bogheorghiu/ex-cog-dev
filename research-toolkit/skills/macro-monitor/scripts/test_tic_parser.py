#!/usr/bin/env python3
"""Unit tests for tic_parser.py pure-logic functions.

Covers parse_tic_data() and analyze_holdings() with synthetic fixtures — no
network (fetch_tic_data() is the only networked function and is not exercised).
Exits non-zero on failure.
"""

import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("tic_parser", _HERE / "tic_parser.py")
tic = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tic)

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


# A minimal stand-in for the Treasury mfh.txt layout: a header line ending in a
# year, then country rows with the most-recent month first.
SAMPLE = """Foreign Holdings of U.S. Treasury Securities
Country                    2026   2025   2024
Japan                     1100   1150   1200
China, Mainland            580    640    700
United Kingdom             750    740    730
Grand Total               7000   7100   7200
"""

try:
    print("\n1. Testing parse_tic_data()...")
    parsed = tic.parse_tic_data(SAMPLE)
    check("no error key on valid input", "error" not in parsed)
    check("Japan parsed into countries", "Japan" in parsed["countries"])
    check("Japan latest value is most-recent month", parsed["countries"]["Japan"]["latest_holdings_billions"] == 1100.0)
    check("Grand Total row excluded", not any("Grand Total" in c for c in parsed["countries"]))
    check("key_countries picks up China, Mainland", any("China" in c for c in parsed["key_countries"]))
    check("recent_values preserved in order", parsed["countries"]["Japan"]["recent_values"] == [1100.0, 1150.0, 1200.0])

    print("\n2. Testing parse_tic_data() with no header...")
    bad = tic.parse_tic_data("no dates here\njust text\n")
    check("missing date header returns error", bad.get("error") == "Could not find date header")

    print("\n3. Testing analyze_holdings() — China below threshold...")
    analysis = tic.analyze_holdings(parsed)
    china_alert = any("China holdings below $600B" in w for w in analysis["warnings"])
    check("China <$600B raises an alert", china_alert)
    check("observations recorded for key countries", len(analysis["observations"]) >= 1)

    print("\n4. Testing analyze_holdings() — coordinated selling...")
    # Both China and Japan dropping >$20B month-over-month should be CRITICAL.
    coordinated = {
        "key_countries": {
            "China, Mainland": {"latest_holdings_billions": 550.0, "recent_values": [550.0, 640.0]},
            "Japan": {"latest_holdings_billions": 1100.0, "recent_values": [1100.0, 1160.0]},
        }
    }
    coord_analysis = tic.analyze_holdings(coordinated)
    check("coordinated selling flagged CRITICAL first", coord_analysis["warnings"] and "CRITICAL: Coordinated selling" in coord_analysis["warnings"][0])

    print("\n5. Testing analyze_holdings() — stable holdings, no warnings...")
    stable = {
        "key_countries": {
            "United Kingdom": {"latest_holdings_billions": 750.0, "recent_values": [750.0, 748.0]},
        }
    }
    stable_analysis = tic.analyze_holdings(stable)
    check("stable holdings produce no warnings", stable_analysis["warnings"] == [])

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    pass

raise SystemExit(1 if failures else 0)
