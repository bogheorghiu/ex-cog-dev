#!/usr/bin/env python3
"""Functional tests for the technical-indicator math (implementations/
get_technical_indicators.py: calculate_rsi / calculate_moving_averages /
calculate_volume_analysis).

These operate on pandas objects, so they need the financial-mcp dependency env
(pandas/numpy arrive transitively via yfinance) — run through uvx, not the
plain-stdlib step:

    uvx --from research-toolkit/mcp-servers/financial-mcp \
        python research-toolkit/mcp-servers/financial-mcp/test_indicators.py

We assert known closed-form behavior (a pure uptrend pins RSI at 100, a pure
downtrend at 0, rolling windows leave a NaN warm-up, OBV follows price
direction) rather than re-deriving the formulas — so the checks would catch a
real regression, not just mirror the implementation. Exits non-zero on failure.
"""

import os
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent

# fetch_ticker (pulled in transitively) imports the cache, which snapshots its
# directory at import time — point it at a throwaway dir first.
os.environ.setdefault("CACHE_DIR", tempfile.mkdtemp(prefix="fmcp-indicators-test-"))

# Import the functions through the package so the relative import in
# get_technical_indicators (`from .fetch_ticker import fetch_ticker`) resolves.
sys.path.insert(0, str(_HERE))
import pandas as pd  # noqa: E402  (provided by the uvx env)
import numpy as np  # noqa: E402
from implementations.get_technical_indicators import (  # noqa: E402
    calculate_rsi,
    calculate_moving_averages,
    calculate_volume_analysis,
)

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


try:
    print("\n1. Testing calculate_rsi()...")
    up = pd.Series([float(i) for i in range(1, 41)])  # strictly increasing
    rsi_up = calculate_rsi(up, period=14)
    check("uptrend pins RSI at 100", round(float(rsi_up.iloc[-1]), 6) == 100.0)
    # where(delta > 0, 0) turns the leading diff() NaN into 0 (NaN > 0 is False),
    # so the rolling mean becomes valid one step early: warm-up is period-1 NaNs.
    check("warm-up is period-1 (13) NaNs", rsi_up.iloc[:13].isna().all())
    check("RSI defined from index period-1", not np.isnan(rsi_up.iloc[13]))

    down = pd.Series([float(i) for i in range(40, 0, -1)])  # strictly decreasing
    rsi_down = calculate_rsi(down, period=14)
    check("downtrend pins RSI at 0", round(float(rsi_down.iloc[-1]), 6) == 0.0)

    rsi_p5 = calculate_rsi(up, period=5)
    check("custom period shifts warm-up (4 NaNs, defined at 4)", rsi_p5.iloc[:4].isna().all() and not np.isnan(rsi_p5.iloc[4]))
    check("RSI stays within [0, 100]", float(rsi_up.dropna().min()) >= 0.0 and float(rsi_up.dropna().max()) <= 100.0)

    print("\n2. Testing calculate_moving_averages()...")
    const = pd.Series([5.0] * 60)
    ma = calculate_moving_averages(const)
    check("returns MA_20 / MA_50 / MA_200 keys", set(ma.keys()) == {"MA_20", "MA_50", "MA_200"})
    check("MA of a constant series equals the constant", float(ma["MA_20"].iloc[-1]) == 5.0)
    check("MA_20 warm-up is 19 NaNs then a value", ma["MA_20"].iloc[:19].isna().all() and not np.isnan(ma["MA_20"].iloc[19]))
    check("window longer than the series stays all-NaN (MA_200 on len 60)", ma["MA_200"].isna().all())
    ramp = pd.Series([float(i) for i in range(20)])  # 0..19
    check("MA_20 over 0..19 is their mean (9.5)", float(calculate_moving_averages(ramp)["MA_20"].iloc[-1]) == 9.5)

    print("\n3. Testing calculate_volume_analysis()...")
    n = 30
    rising = pd.DataFrame({"Close": [float(i) for i in range(1, n + 1)], "Volume": [100.0] * n})
    va = calculate_volume_analysis(rising)
    check(
        "returns the expected indicator keys",
        set(va.keys()) == {"volume_ma_20", "volume_ma_50", "volume_ratio_20", "volume_ratio_50", "obv"},
    )
    check("constant volume => ratio_20 ~ 1.0 after warm-up", abs(float(va["volume_ratio_20"].iloc[-1]) - 1.0) < 1e-9)
    check("OBV rises with a rising price (positive at the end)", float(va["obv"].iloc[-1]) > 0)

    falling = pd.DataFrame({"Close": [float(i) for i in range(n, 0, -1)], "Volume": [100.0] * n})
    obv_down = calculate_volume_analysis(falling)["obv"]
    check("OBV falls with a falling price (negative at the end)", float(obv_down.iloc[-1]) < 0)

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    pass

raise SystemExit(1 if failures else 0)
