#!/usr/bin/env python3
"""Unit tests for parse_content.py pure-logic functions.

Covers the corpus-size adaptation algorithm (get_adaptive_detail_level and its
100/50/20 boundaries), ParseConfig validation + category mapping, the
directory loader (tempdir-backed), and the prompt builder's mode/category
branches. The AI-call-driven parse_articles() is out of scope. Exits non-zero
on failure.
"""

import importlib.util
import json
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("parse_content", _HERE / "parse_content.py")
pc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pc)

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


try:
    print("\n1. Testing get_adaptive_detail_level() tiers + boundaries...")
    eff, clust, reason = pc.get_adaptive_detail_level(150, 8)
    check("bulk (>100) caps to 2 + clustering", eff == 2 and clust is True)
    check("bulk over-request explains the reduction", "auto-reduced" in reason)
    eff, clust, reason = pc.get_adaptive_detail_level(150, 1)
    check("bulk under cap keeps requested level", eff == 1 and clust is True)
    check("bulk under cap: no 'auto-reduced'", "auto-reduced" not in reason)

    eff, clust, _ = pc.get_adaptive_detail_level(80, 8)
    check("large (>50) caps to 3 + clustering", eff == 3 and clust is True)
    eff, clust, reason = pc.get_adaptive_detail_level(30, 8)
    check("medium (>20) caps to 5, no clustering", eff == 5 and clust is False)
    check("medium reports auto-capped", "auto-capped" in reason)
    eff, clust, reason = pc.get_adaptive_detail_level(30, 4)
    check("medium under cap: untouched, empty reason", eff == 4 and clust is False and reason == "")
    eff, clust, reason = pc.get_adaptive_detail_level(10, 9)
    check("small (<=20) uses requested level verbatim", eff == 9 and clust is False and reason == "")

    # Boundary exactness: thresholds are strict > comparisons.
    check("exactly 100 falls in the >50 tier (cap 3)", pc.get_adaptive_detail_level(100, 9)[0] == 3)
    check("exactly 50 falls in the >20 tier (cap 5)", pc.get_adaptive_detail_level(50, 9)[0] == 5)
    check("exactly 20 falls in the small tier (verbatim)", pc.get_adaptive_detail_level(20, 9)[0] == 9)

    print("\n2. Testing ParseConfig validation + category...")
    check("default level 5 -> balanced", pc.ParseConfig().category == "balanced")
    check("level 0 -> quick", pc.ParseConfig(detail_level=0).category == "quick")
    check("level 3 -> quick (boundary)", pc.ParseConfig(detail_level=3).category == "quick")
    check("level 6 -> balanced (boundary)", pc.ParseConfig(detail_level=6).category == "balanced")
    check("level 7 -> comprehensive (boundary)", pc.ParseConfig(detail_level=7).category == "comprehensive")
    check("level 10 -> comprehensive", pc.ParseConfig(detail_level=10).category == "comprehensive")
    for bad in (-1, 11):
        try:
            pc.ParseConfig(detail_level=bad)
            check(f"out-of-range {bad} raises", False)
        except ValueError:
            check(f"out-of-range {bad} raises ValueError", True)

    print("\n3. Testing load_articles_from_dir() (tempdir)...")
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        check("empty/absent dir -> ([], '')", pc.load_articles_from_dir(base) == ([], ""))
        (base / "json").mkdir()
        (base / "json" / "a.json").write_text(json.dumps({"title": "A"}), encoding="utf-8")
        (base / "json" / "b.json").write_text(json.dumps({"title": "B"}), encoding="utf-8")
        (base / "json" / "bad.json").write_text("{not json", encoding="utf-8")
        (base / "all_articles.md").write_text("FULL CONTENT", encoding="utf-8")
        arts, content = pc.load_articles_from_dir(base)
        check("valid json metadata loaded, bad skipped", len(arts) == 2)
        check("json files read in sorted order", [a["title"] for a in arts] == ["A", "B"])
        check("markdown content loaded", content == "FULL CONTENT")

    print("\n4. Testing generate_parsing_prompt() branches...")
    arts = [{"title": "First", "date": "2024-01-01", "url": "https://x/1"}, {"url": "https://x/2"}]
    quick = pc.generate_parsing_prompt(pc.ParseConfig(detail_level=2), arts)
    check("prompt states the article count", "following 2 Substack articles" in quick)
    check("quick category instruction present", "under 500 words" in quick)
    check("article title listed", "1. First" in quick)
    check("date annotated when present", "(2024-01-01)" in quick)
    check("missing title -> 'Untitled'", "Untitled" in quick)

    comp = pc.generate_parsing_prompt(pc.ParseConfig(detail_level=9), arts)
    check("comprehensive category instruction present", "comprehensive analysis" in comp)

    clustered = pc.generate_parsing_prompt(
        pc.ParseConfig(detail_level=2, use_clustering=True, adaptive_reason="Bulk corpus"), arts
    )
    check("clustering mode emits THEME CLUSTERING", "THEME CLUSTERING" in clustered)
    check("adaptive reason surfaced with warning", "⚠️ Bulk corpus" in clustered)

    custom = pc.generate_parsing_prompt(pc.ParseConfig(detail_level=5, custom_prompt="Focus on X"), arts)
    check("custom prompt appended", "Additional Instructions:\nFocus on X" in custom)

    withbody = pc.generate_parsing_prompt(pc.ParseConfig(), arts, content="BODY TEXT")
    check("full content appended when provided", "## Full Article Content" in withbody and "BODY TEXT" in withbody)
    check("content section omitted when empty", "Full Article Content" not in quick)

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    pass

raise SystemExit(1 if failures else 0)
