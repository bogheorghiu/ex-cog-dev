#!/usr/bin/env python3
"""Unit tests for fred_fetcher.py pure-logic functions.

Covers the I/O-free helpers extracted from the networked entry points:
  _build_fred_url, _parse_fred_csv, analyze_divergence, evaluate_crisis.

No network and no mocks — each function takes data in and returns data out, so
fixtures are enough. The networked wrappers (fetch_fred_series / get_latest /
macro_snapshot) are intentionally not exercised here. Exits non-zero on failure.
"""

import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("fred_fetcher", _HERE / "fred_fetcher.py")
fred = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fred)

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


try:
    print("\n1. Testing _build_fred_url()...")
    url = fred._build_fred_url("DGS10", start_date="2026-01-01", end_date="2026-02-01")
    check("includes series id", "id=DGS10" in url)
    check("includes explicit start date", "cosd=2026-01-01" in url)
    check("includes explicit end date", "coed=2026-02-01" in url)
    default_url = fred._build_fred_url("VIXCLS", last_n_days=30)
    check("supplies a default cosd when no start date", "cosd=" in default_url)
    check("omits coed when no end date", "coed=" not in default_url)

    print("\n2. Testing _parse_fred_csv()...")
    csv_text = "DATE,DGS10\n2026-05-01,4.25\n2026-05-02,.\n2026-05-03,4.30\n"
    parsed = fred._parse_fred_csv(csv_text, "DGS10")
    check("two valid rows parsed", len(parsed) == 2)
    check("missing-value '.' row skipped", all(r["value"] != "." for r in parsed))
    check("values cast to float", parsed[0]["value"] == 4.25 and isinstance(parsed[0]["value"], float))
    check("date preserved", parsed[0]["date"] == "2026-05-01")
    check("non-numeric junk ignored", fred._parse_fred_csv("DATE,DGS10\n2026-05-01,oops\n", "DGS10") == [])
    check("empty CSV yields empty list", fred._parse_fred_csv("DATE,DGS10\n", "DGS10") == [])

    print("\n3. Testing analyze_divergence()...")
    check("insufficient data returns error",
          fred.analyze_divergence([{"date": "d", "value": 1.0}], [], days=5).get("error") == "Insufficient data")

    # Yields up + dollar down → RED FLAG divergence.
    yields_up = [{"date": "2026-05-01", "value": 4.0}, {"date": "2026-05-06", "value": 4.3}]
    dollar_down = [{"date": "2026-05-01", "value": 105.0}, {"date": "2026-05-06", "value": 103.0}]
    div = fred.analyze_divergence(yields_up, dollar_down, days=5)
    check("yields-up/dollar-down flagged as divergence", div["divergence_detected"] is True)
    check("yield_direction up", div["yield_direction"] == "up")
    check("dollar_direction down", div["dollar_direction"] == "down")
    check("RED FLAG interpretation", "RED FLAG" in div["interpretation"])
    check("as_of is the latest yield date", div["as_of"] == "2026-05-06")

    # Yields up + dollar up → normal, no divergence.
    dollar_up = [{"date": "2026-05-01", "value": 103.0}, {"date": "2026-05-06", "value": 105.0}]
    normal = fred.analyze_divergence(yields_up, dollar_up, days=5)
    check("yields-up/dollar-up is not divergence", normal["divergence_detected"] is False)
    check("normal interpretation", "Normal" in normal["interpretation"])

    # Both flat (changes under thresholds) → stable/mixed, no divergence.
    flat_y = [{"date": "2026-05-01", "value": 4.00}, {"date": "2026-05-06", "value": 4.01}]
    flat_d = [{"date": "2026-05-01", "value": 105.0}, {"date": "2026-05-06", "value": 105.1}]
    flat = fred.analyze_divergence(flat_y, flat_d, days=5)
    check("sub-threshold moves read as flat", flat["yield_direction"] == "flat" and flat["dollar_direction"] == "flat")
    check("flat is not divergence", flat["divergence_detected"] is False)

    print("\n4. Testing evaluate_crisis()...")
    # VIX critical (>45) and yield curve inverted (<0) should both alert.
    snapshot = {
        "VIXCLS": {"name": "VIX", "value": 50.0},
        "T10Y2Y": {"name": "Yield Curve", "value": -0.5},
        "DGS10": {"name": "10Y Yield", "value": 4.2},          # under 5.0 high → no alert
        "DCOILBRENTEU": {"name": "Brent Crude", "value": 90.0},  # within 70-120 → no alert
        "divergence_analysis": {"divergence_detected": True, "interpretation": "RED FLAG: test"},
    }
    crisis = fred.evaluate_crisis(snapshot)
    check("VIX critical raises an alert", any("CRITICAL" in a for a in crisis["alerts"]))
    check("yield curve inversion raises an alert", any("INVERTED" in a for a in crisis["alerts"]))
    check("divergence surfaced as an alert", any("DIVERGENCE" in a for a in crisis["alerts"]))
    check("alert_count matches alert list length", crisis["alert_count"] == len(crisis["alerts"]))
    check("divergence_analysis stripped from snapshot copy", "divergence_analysis" not in crisis["snapshot"])

    # All-normal snapshot → zero alerts.
    calm = {
        "VIXCLS": {"name": "VIX", "value": 15.0},
        "T10Y2Y": {"name": "Yield Curve", "value": 0.5},
        "DGS10": {"name": "10Y Yield", "value": 4.0},
        "DCOILBRENTEU": {"name": "Brent Crude", "value": 85.0},
        "divergence_analysis": {"divergence_detected": False},
    }
    calm_result = fred.evaluate_crisis(calm)
    check("calm market produces zero alerts", calm_result["alert_count"] == 0)

    # Series missing a value should be skipped, not crash.
    sparse = fred.evaluate_crisis({"VIXCLS": {"name": "VIX"}})
    check("missing value handled gracefully", sparse["alert_count"] == 0)

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    pass

raise SystemExit(1 if failures else 0)
