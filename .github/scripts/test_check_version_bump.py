#!/usr/bin/env python3
"""Unit tests for the version-bump guard decision logic (Appendix C).

Pure-function tests — no git, no filesystem. Run directly:
    python3 .github/scripts/test_check_version_bump.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_version_bump import evaluate, version_tuple  # noqa: E402

DIRS = {"alpha": "alpha/", "beta": "beta/"}
failures = []


def check(name, cond):
    if cond:
        print(f"   ✓ {name}")
    else:
        print(f"   ✗ {name}")
        failures.append(name)


def test_version_tuple():
    print("\n1. version_tuple() comparison")
    check("1.10 > 1.9 numerically (not string)", version_tuple("1.10") > version_tuple("1.9"))
    check("2.0 > 1.99", version_tuple("2.0") > version_tuple("1.99"))
    check("equal versions compare equal", version_tuple("1.2.3") == version_tuple("1.2.3"))
    check("None -> (0,) fallback", version_tuple(None) == (0,))
    check("garbage -> (0,) fallback", version_tuple("x.y") == (0,))


def test_no_plugin_touched():
    print("\n2. changes outside any plugin dir -> pass")
    out = evaluate(
        [".github/workflows/ci.yml", "README.md"],
        {"alpha": "1.0.0", "beta": "1.0.0"},
        {"alpha": "1.0.0", "beta": "1.0.0"},
        DIRS,
    )
    check("no failures", out == [])


def test_bumped_passes():
    print("\n3. plugin changed + version bumped -> pass")
    out = evaluate(
        ["alpha/skills/x.md"],
        {"alpha": "1.0.0"},
        {"alpha": "1.0.1"},
        DIRS,
    )
    check("no failures", out == [])


def test_not_bumped_fails():
    print("\n4. plugin changed + version unchanged -> fail")
    out = evaluate(["alpha/skills/x.md"], {"alpha": "1.0.0"}, {"alpha": "1.0.0"}, DIRS)
    check("one failure", len(out) == 1)
    check("names the plugin", out and "alpha" in out[0])


def test_decreased_fails():
    print("\n5. plugin changed + version decreased -> fail")
    out = evaluate(["alpha/x"], {"alpha": "2.0.0"}, {"alpha": "1.9.0"}, DIRS)
    check("one failure", len(out) == 1)


def test_minor_vs_patch_ordering():
    print("\n6. 1.9 -> 1.10 counts as an increase (numeric, not string)")
    out = evaluate(["alpha/x"], {"alpha": "1.9"}, {"alpha": "1.10"}, DIRS)
    check("no failures (1.10 > 1.9)", out == [])


def test_missing_head_manifest_fails():
    print("\n7. plugin changed + manifest missing/unparseable at head -> fail")
    out = evaluate(["alpha/x"], {"alpha": "1.0.0"}, {"alpha": None}, DIRS)
    check("one failure", len(out) == 1)
    check("mentions missing/unparseable", out and "missing or unparseable" in out[0])


def test_new_plugin_passes():
    print("\n8. new plugin (absent at base) -> pass at any version")
    out = evaluate(["beta/x"], {"alpha": "1.0.0", "beta": None}, {"alpha": "1.0.0", "beta": "0.1.0"}, DIRS)
    check("no failures", out == [])


def test_multiple_plugins_independent():
    print("\n9. two plugins changed, only one bumped -> exactly one failure")
    out = evaluate(
        ["alpha/x", "beta/y"],
        {"alpha": "1.0.0", "beta": "1.0.0"},
        {"alpha": "1.0.1", "beta": "1.0.0"},  # alpha bumped, beta not
        DIRS,
    )
    check("exactly one failure", len(out) == 1)
    check("the failure is beta", out and "beta" in out[0] and "alpha" not in out[0])


def test_prefix_not_substring_matched():
    print("\n10. prefix matching is dir-anchored (alpha/ does not match alphabet/)")
    dirs = {"alpha": "alpha/"}
    out = evaluate(["alphabet/x.md"], {"alpha": "1.0.0"}, {"alpha": "1.0.0"}, dirs)
    check("no failures (alphabet/ is not under alpha/)", out == [])


if __name__ == "__main__":
    print("Testing version-bump guard logic (Appendix C)...")
    test_version_tuple()
    test_no_plugin_touched()
    test_bumped_passes()
    test_not_bumped_fails()
    test_decreased_fails()
    test_minor_vs_patch_ordering()
    test_missing_head_manifest_fails()
    test_new_plugin_passes()
    test_multiple_plugins_independent()
    test_prefix_not_substring_matched()
    if failures:
        print(f"\n❌ {len(failures)} check(s) failed: {failures}")
        raise SystemExit(1)
    print("\n✅ All version-bump-guard logic tests passed!")
