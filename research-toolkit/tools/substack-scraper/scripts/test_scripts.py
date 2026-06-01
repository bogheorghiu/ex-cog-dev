#!/usr/bin/env python3
"""Unit tests for the substack-scraper pure-logic helpers.

Covers two stdlib-only, dependency-free modules:
  - saturation_detector.py — the Ralph-Plus SaturationTracker + simple helpers
  - utils.py — slugify + progress checkpoint round-trip

No network, no browser, no mocks: every function takes data in and returns data
out (utils' file helpers use a tempdir). The scraper's Playwright-driven scripts
are intentionally out of scope. Exits non-zero on failure.
"""

import importlib.util
import json
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, _HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sat = _load("saturation_detector")
utils = _load("utils")

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


try:
    print("\n1. Testing SaturationTracker.assess_quality()...")
    t = sat.SaturationTracker()
    check("total >= threshold (2) is HIGH", t.assess_quality(2, 0) == sat.PassQuality.HIGH)
    check("new+reinforced summed for threshold", t.assess_quality(1, 1) == sat.PassQuality.HIGH)
    check("below threshold is LOW", t.assess_quality(1, 0) == sat.PassQuality.LOW)
    check("zero activity is LOW", t.assess_quality(0, 0) == sat.PassQuality.LOW)

    print("\n2. Testing record_pass() + get_summary()...")
    t = sat.SaturationTracker()
    r = t.record_pass(5, 2, "first")
    check("record_pass returns the pass result", isinstance(r, sat.PassResult))
    check("recorded quality reflects counts", r.quality == sat.PassQuality.HIGH)
    check("history grows", len(t.history) == 1)
    t.record_pass(0, 1, "second")  # LOW
    summ = t.get_summary()
    check("summary counts total passes", summ["total_passes"] == 2)
    check("summary counts high-value passes", summ["high_value_passes"] == 1)
    check("summary counts low-value passes", summ["low_value_passes"] == 1)
    check("summary sums new patterns", summ["total_new_patterns"] == 5)
    check("summary sums reinforced", summ["total_reinforced"] == 3)

    print("\n3. Testing should_continue() consecutive-LOW stop...")
    t = sat.SaturationTracker()
    check("empty history continues", t.should_continue() is True)
    t.record_pass(0, 0)  # LOW #1
    check("one recorded LOW still continues (threshold 2)", t.should_continue() is True)
    check("  ...and did not flag saturation yet", t.is_saturated is False)
    t.record_pass(0, 1)  # LOW #2
    check("two recorded LOWs stop", t.should_continue() is False)
    check("real (non-preview) stop sets is_saturated", t.is_saturated is True)
    check("stop_reason mentions consecutive low", "consecutive low" in t.stop_reason.lower())

    print("\n4. Testing a HIGH pass resets the LOW streak...")
    t = sat.SaturationTracker()
    t.record_pass(0, 0)   # LOW
    t.record_pass(5, 5)   # HIGH — resets streak
    t.record_pass(0, 0)   # LOW (only 1 trailing)
    check("single trailing LOW after a HIGH continues", t.should_continue() is True)

    print("\n5. Testing preview semantics (must NOT mutate state)...")
    t = sat.SaturationTracker()
    t.record_pass(0, 0)  # one real LOW recorded
    # Preview of a 2nd LOW: reaches the threshold and returns False...
    check("preview reaching threshold returns False", t.should_continue(0, 0) is False)
    # ...but because it's a preview, saturation state must stay untouched.
    check("preview does NOT set is_saturated", t.is_saturated is False)
    check("preview does NOT set stop_reason", t.stop_reason == "")
    # A preview of a HIGH pass should let it continue.
    check("preview of HIGH pass continues", t.should_continue(5, 5) is True)
    # Only one of the two preview args provided => preview ignored entirely.
    check("partial preview (reinforced=None) is ignored", t.should_continue(0, None) is True)

    print("\n6. Testing module-level simple helpers...")
    check("assess_pass_quality_simple HIGH at 2", sat.assess_pass_quality_simple(2, 0) == "HIGH")
    check("assess_pass_quality_simple sums args", sat.assess_pass_quality_simple(0, 2) == "HIGH")
    check("assess_pass_quality_simple LOW below 2", sat.assess_pass_quality_simple(1, 0) == "LOW")
    cont, reason = sat.should_continue_simple(["HIGH", "LOW", "LOW"])
    check("two trailing LOWs stop", cont is False and reason != "")
    cont, reason = sat.should_continue_simple(["LOW", "HIGH"])
    check("trailing HIGH continues", cont is True and reason == "")
    cont, _ = sat.should_continue_simple(["LOW"])
    check("single LOW continues", cont is True)
    cont, _ = sat.should_continue_simple(["low", "low"])
    check("case-insensitive LOW matching", cont is False)

    print("\n7. Testing utils.slugify()...")
    check("spaces become single dashes", utils.slugify("Hello World") == "hello-world")
    check("apostrophes are dropped, not dashed", utils.slugify("What's Up?") == "whats-up")
    check("unicode is normalized to ascii", utils.slugify("Café Olé") == "cafe-ole")
    check("runs of separators collapse", utils.slugify("  Multiple   Spaces  ") == "multiple-spaces")
    check("leading/trailing dashes stripped", utils.slugify("--Trim--Me--") == "trim-me")
    check("already-slug is stable", utils.slugify("already-slug-123") == "already-slug-123")
    check("empty string stays empty", utils.slugify("") == "")
    check("all-punctuation collapses to empty", utils.slugify("!!!???") == "")

    print("\n8. Testing utils progress checkpoint round-trip...")
    with tempfile.TemporaryDirectory() as d:
        missing = str(Path(d) / "nope.json")
        check("missing checkpoint loads as empty set", utils.load_progress(missing) == set())

        bad = Path(d) / "bad.json"
        bad.write_text("{not valid json")
        check("invalid JSON loads as empty set", utils.load_progress(str(bad)) == set())

        cp = str(Path(d) / "progress.json")
        done = {"https://a.example/1", "https://a.example/2"}
        utils.save_progress(cp, done)
        check("save→load round-trips the set", utils.load_progress(cp) == done)
        check("saved file is valid JSON list", isinstance(json.loads(Path(cp).read_text()), list))

        nested = str(Path(d) / "x" / "y" / "z")
        check("ensure_dir returns the path", utils.ensure_dir(nested) == nested)
        check("ensure_dir created the directory", Path(nested).is_dir())
        check("ensure_dir is idempotent", utils.ensure_dir(nested) == nested)

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    pass

raise SystemExit(1 if failures else 0)
