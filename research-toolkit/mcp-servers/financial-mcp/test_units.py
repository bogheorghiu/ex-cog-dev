#!/usr/bin/env python3
"""Unit tests for financial-mcp stdlib-only logic.

Covers:
  - implementations/utils.py: validate_symbol / validate_date / validate_period
  - cache/manager.py: CacheManager store/get/expiry/cleanup/force_refresh/stats

No network and no yfinance: the yfinance-coupled paths (ticker_validator) are
intentionally out of scope. The cache is pointed at a temp dir via CACHE_DIR,
which cache/config.py reads at import time, so we set it before importing.
"""

import importlib.util
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

_HERE = Path(__file__).resolve().parent

# Point the cache at a throwaway dir BEFORE importing the cache package, since
# cache/config.py snapshots CACHE_DIR / CACHE_DB_PATH at import time.
_cache_dir = Path(tempfile.mkdtemp(prefix="financial-mcp-cache-test-"))
os.environ["CACHE_DIR"] = str(_cache_dir)

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


# --- Load utils.py directly by path (avoids importing the implementations pkg) ---
_uspec = importlib.util.spec_from_file_location(
    "fmcp_utils", _HERE / "implementations" / "utils.py"
)
utils = importlib.util.module_from_spec(_uspec)
_uspec.loader.exec_module(utils)

# --- Import the cache package normally so its relative imports resolve ---
sys.path.insert(0, str(_HERE))
from cache.manager import CacheManager  # noqa: E402

try:
    print("\n1. Testing validate_symbol()...")
    ok, cleaned, err = utils.validate_symbol("  aapl ")
    check("valid symbol accepted", ok is True and err is None)
    check("symbol cleaned and upper-cased", cleaned == "AAPL")
    check("empty symbol rejected", utils.validate_symbol("")[0] is False)
    check("illegal characters rejected", utils.validate_symbol("AA$PL")[0] is False)
    check("over-long symbol rejected", utils.validate_symbol("ABCDEFGHIJK")[0] is False)
    check("dotted/hyphenated symbol accepted", utils.validate_symbol("BRK.B")[0] is True)

    print("\n2. Testing validate_date()...")
    check("valid date accepted", utils.validate_date("2026-05-31") == (True, None))
    check("empty date treated as optional/valid", utils.validate_date("") == (True, None))
    check("malformed date rejected", utils.validate_date("31-05-2026")[0] is False)

    print("\n3. Testing validate_period()...")
    check("known period accepted", utils.validate_period("1mo") == (True, None))
    check("unknown period rejected", utils.validate_period("13mo")[0] is False)

    print("\n4. Testing CacheManager store/get round-trip...")
    cache = CacheManager()
    cache.store_ticker("aapl", valid=True, company_name="Apple Inc.",
                       sector="Technology", cache_type="success")
    got = cache.get_ticker("AAPL")
    check("stored ticker retrievable", got is not None)
    check("symbol normalized to upper-case", got and got["symbol"] == "AAPL")
    check("company_name persisted", got and got["company_name"] == "Apple Inc.")
    check("valid flag is a real bool", got and got["valid"] is True)
    check("unknown symbol returns None", cache.get_ticker("ZZZZ") is None)

    print("\n5. Testing TTL expiry behavior...")
    # Write a row that is already expired, directly via sqlite, then confirm
    # get_ticker treats it as a miss and cleanup_expired removes it.
    import sqlite3
    from cache.config import CACHE_DB_PATH
    past = (datetime.now() - timedelta(days=1)).isoformat()
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO ticker_cache "
            "(symbol, valid, cache_type, created_at, expires_at) "
            "VALUES (?, ?, ?, ?, ?)",
            ("EXPIRED", True, "success", past, past),
        )
        conn.commit()
    check("expired entry is not returned", cache.get_ticker("EXPIRED") is None)
    removed = cache.cleanup_expired()
    check("cleanup_expired removes the stale row", removed >= 1)

    print("\n6. Testing force_refresh() and stats...")
    cache.store_ticker("MSFT", valid=True, company_name="Microsoft", cache_type="success")
    cache.force_refresh("MSFT")
    check("force_refresh evicts the entry", cache.get_ticker("MSFT") is None)
    stats = cache.get_cache_stats()
    check("stats report total_entries", "total_entries" in stats)
    check("stats report the cache file path", stats["cache_file"] == CACHE_DB_PATH)

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    shutil.rmtree(_cache_dir, ignore_errors=True)
    print("✓ Cleanup complete")

raise SystemExit(1 if failures else 0)
