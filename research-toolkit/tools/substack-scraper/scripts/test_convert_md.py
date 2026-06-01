#!/usr/bin/env python3
"""Unit tests for convert_md_to_single.py pure-logic functions.

Covers the markdown-consolidation helpers: metadata extraction (with the
filename-date and fallback-title paths), per-article section formatting, and a
directory→single-file round-trip backed by a tempdir. The argparse main() is
out of scope. Exits non-zero on failure.
"""

import importlib.util
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("convert_md", _HERE / "convert_md_to_single.py")
cm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cm)

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


try:
    print("\n1. Testing extract_metadata_from_content()...")
    md = cm.extract_metadata_from_content(
        "# Real Title\n\nSource: https://x.substack.com/p/post\n\nBody text.",
        "2024-01-15-real-title.md",
    )
    check("title pulled from first H1", md["title"] == "Real Title")
    check("source URL pulled from content", md["url"] == "https://x.substack.com/p/post")
    check("date pulled from filename prefix", md["date"] == "2024-01-15")

    md2 = cm.extract_metadata_from_content("Body only, no heading.", "2024-03-09-my-cool-post.md")
    check("title falls back from filename", md2["title"] == "My Cool Post")
    check("fallback strips date + titlecases", "2024" not in md2["title"])

    md3 = cm.extract_metadata_from_content("no h1 here", "undated-slug.md")
    check("no filename date -> date is None", md3["date"] is None)
    check("undated filename still yields a title", md3["title"] == "Undated Slug")

    md4 = cm.extract_metadata_from_content("body", "2024-01-15-.md")
    check("empty fallback title becomes 'Untitled'", md4["title"] == "Untitled")

    print("\n2. Testing format_article_section()...")
    section = cm.format_article_section(
        "# Dupe Title\n\nSource: https://x/p/1\n\nThe actual body.",
        {"title": "Dupe Title", "date": "2024-01-15", "url": "https://x/p/1"},
    )
    check("header carries the title as H1", section.startswith("# Dupe Title"))
    check("date line rendered", "**Date:** 2024-01-15" in section)
    check("source line rendered", "**Source:** https://x/p/1" in section)
    check("body retained", "The actual body." in section)
    check("original H1 stripped from body (title appears once)", section.count("# Dupe Title") == 1)
    check("original Source: line stripped from body", "Source: https://x/p/1" not in section)

    bare = cm.format_article_section("body", {"title": "T", "date": None, "url": None})
    check("date line omitted when no date", "**Date:**" not in bare)
    check("source line omitted when no url", "**Source:**" not in bare)

    print("\n3. Testing convert_directory_to_single_file() round-trip...")
    check("missing input dir returns 0", cm.convert_directory_to_single_file(Path("/no/such/dir"), Path("/tmp/x.md")) == 0)
    with tempfile.TemporaryDirectory() as d:
        ddir = Path(d)
        empty = ddir / "empty"
        empty.mkdir()
        check("empty dir returns 0", cm.convert_directory_to_single_file(empty, ddir / "out0.md") == 0)

        src = ddir / "src"
        src.mkdir()
        (src / "2024-01-01-alpha.md").write_text("# Alpha\n\nFirst body.", encoding="utf-8")
        (src / "2024-02-01-beta.md").write_text("# Beta\n\nSecond body.", encoding="utf-8")
        out = ddir / "nested" / "all_articles.md"
        n = cm.convert_directory_to_single_file(src, out)
        check("processes both articles", n == 2)
        check("creates missing output parent dir", out.exists())
        body = out.read_text(encoding="utf-8")
        check("uses --- separator between articles", "\n\n---\n\n" in body)
        check("articles ordered by (date-prefixed) filename", body.index("Alpha") < body.index("Beta"))

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    pass

raise SystemExit(1 if failures else 0)
