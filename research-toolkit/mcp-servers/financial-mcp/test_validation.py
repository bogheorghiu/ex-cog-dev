#!/usr/bin/env python3
"""Unit tests for financial-mcp input validation (implementations/utils.py).

These are the pure, dependency-free validators (re + datetime only) used to
sanitize tool arguments before any yfinance/network call. test_units.py already
covers the cache layer; this covers the argument gatekeepers. Exits non-zero on
failure.
"""

import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "fin_utils", _HERE / "implementations" / "utils.py"
)
u = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(u)

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


try:
    print("\n1. Testing validate_symbol()...")
    ok, cleaned, err = u.validate_symbol("aapl")
    check("lowercase is accepted and upper-cased", ok and cleaned == "AAPL" and err is None)
    ok, cleaned, _ = u.validate_symbol("  msft  ")
    check("surrounding whitespace is stripped", ok and cleaned == "MSFT")
    check("dotted class shares parse (BRK.B)", u.validate_symbol("BRK.B")[:2] == (True, "BRK.B"))
    check("hyphenated ticker accepted (BRK-B)", u.validate_symbol("BRK-B")[:2] == (True, "BRK-B"))
    check("digits accepted (8035 / RY)", u.validate_symbol("8035")[0] is True)

    ok, cleaned, err = u.validate_symbol("")
    check("empty string rejected with empty-message", ok is False and cleaned is None and "empty" in err.lower())
    ok, cleaned, err = u.validate_symbol(None)
    check("None rejected as empty", ok is False and cleaned is None)
    ok, cleaned, err = u.validate_symbol("   ")
    check("whitespace-only fails format (not empty branch)", ok is False and "format" in err.lower())
    check("internal space rejected", u.validate_symbol("AA PL")[0] is False)
    check("special chars rejected", u.validate_symbol("AAPL!")[0] is False)
    check("over-length (11 chars) rejected", u.validate_symbol("ABCDEFGHIJK")[0] is False)
    check("max-length (10 chars) accepted", u.validate_symbol("ABCDEFGHIJ")[0] is True)

    print("\n2. Testing validate_date()...")
    check("empty date is valid (optional param)", u.validate_date("") == (True, None))
    check("None date is valid (optional param)", u.validate_date(None) == (True, None))
    check("well-formed date accepted", u.validate_date("2026-01-15") == (True, None))
    ok, err = u.validate_date("2026-13-01")
    check("impossible month rejected", ok is False and "YYYY-MM-DD" in err)
    check("US-order date rejected", u.validate_date("01-15-2026")[0] is False)
    check("slash separators rejected", u.validate_date("2026/01/15")[0] is False)
    check("non-date string rejected", u.validate_date("yesterday")[0] is False)

    print("\n3. Testing validate_period()...")
    for p in ["1d", "5d", "1mo", "1y", "ytd", "max"]:
        check(f"valid period {p!r} accepted", u.validate_period(p) == (True, None))
    ok, err = u.validate_period("1w")
    check("unknown period rejected with guidance", ok is False and "Invalid period" in err)
    check("empty period rejected", u.validate_period("")[0] is False)
    check("period matching is case-sensitive (1D)", u.validate_period("1D")[0] is False)

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    pass

raise SystemExit(1 if failures else 0)
