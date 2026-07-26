#!/usr/bin/env python3
"""Unit tests for the prose-review validator's parsing and text checks.

Why this file exists: the first end-to-end run of the reviewer, plus the code review
that followed it, found four defects in this repo's own change — and three of them
lived in this one module, in `hunk_lines()` and in the per-finding text checks. Both
are pure functions over strings, so they are the cheapest thing in the whole workflow
to test and were the most expensive to get wrong: each defect failed *silently*, either
dropping a valid finding or letting one through a limit the reviewer had been told was
enforced. A green run is not evidence here, because every one of these bugs coexisted
with a green run.

Pure-function tests — no git, no network, no filesystem. Run directly:
    python3 .github/scripts/test_prose_review_post.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prose_review_post import hunk_lines, BARE_REF, SECRET_SHAPES  # noqa: E402

failures = []


def check(name, cond):
    if cond:
        print(f"   ✓ {name}")
    else:
        print(f"   ✗ {name}")
        failures.append(name)


def test_hunk_lines_basic():
    print("\n1. hunk_lines() on ordinary diffs")
    diff = (
        "--- a/f.md\n"
        "+++ b/f.md\n"
        "@@ -1,2 +1,3 @@\n"
        " keep\n"
        "+added\n"
        " tail\n"
    )
    check("context and added lines are commentable", hunk_lines(diff) == {"f.md": {1, 2, 3}})

    removed = "--- a/f.md\n+++ b/f.md\n@@ -1,2 +1,1 @@\n keep\n-gone\n"
    check("removed lines are not commentable", hunk_lines(removed) == {"f.md": {1}})

    single = "--- a/s.md\n+++ b/s.md\n@@ -5 +5 @@\n-old\n+new\n"
    check("hunk header with no new-side count means exactly one line",
          hunk_lines(single) == {"s.md": {5}})


def test_hunk_lines_deleted_file():
    print("\n2. hunk_lines() and `+++ /dev/null`")
    diff = (
        "--- a/gone.md\n"
        "+++ /dev/null\n"
        "@@ -1,2 +0,0 @@\n"
        "-a\n"
        "-b\n"
        "--- a/next.md\n"
        "+++ b/next.md\n"
        "@@ -0,0 +1,2 @@\n"
        "+x\n"
        "+y\n"
    )
    got = hunk_lines(diff)
    check("a deleted file contributes no commentable lines", "gone.md" not in got)
    check("the file after a deletion is still parsed", got == {"next.md": {1, 2}})


def test_hunk_lines_content_resembling_a_header():
    print("\n3. hunk_lines() does not read hunk content as diff syntax")
    # An added line whose own text starts `++ ` renders in the diff as `+++ `. Treating
    # it as a file header re-points every following line at a file that does not exist,
    # so real findings are dropped as "not in this diff" while the run reports success.
    diff = (
        "--- a/real.md\n"
        "+++ b/real.md\n"
        "@@ -1,2 +1,4 @@\n"
        " context\n"
        "+++ b/evil\n"
        "+after\n"
        " tail\n"
    )
    got = hunk_lines(diff)
    check("no phantom file is invented", list(got) == ["real.md"])
    check("every right-hand line stays attributed to the real file",
          got == {"real.md": {1, 2, 3, 4}})

    # Same class, via a hunk header quoted inside content.
    quoted = (
        "--- a/doc.md\n"
        "+++ b/doc.md\n"
        "@@ -1,1 +1,3 @@\n"
        " intro\n"
        "+@@ -99,1 +99,1 @@\n"
        "+still line three\n"
    )
    check("a quoted hunk header does not restart line numbering",
          hunk_lines(quoted) == {"doc.md": {1, 2, 3}})


def test_bare_reference_rule():
    print("\n4. BARE_REF — `issue #N` / `PR #N`, never a bare `#N`")
    check("bare reference is caught", bool(BARE_REF.search("see #182 for context")))
    check("`issue #N` is allowed", not BARE_REF.search("see issue #182"))
    check("`PR #N` is allowed", not BARE_REF.search("see PR #182"))
    check("a URL fragment is not a bare reference",
          not BARE_REF.search("https://example.com/x/#182"))


def test_secret_shapes():
    print("\n5. SECRET_SHAPES — credential-shaped text never becomes a comment")
    check("a GitHub token shape is caught",
          bool(SECRET_SHAPES.search("ghp_" + "A" * 32)))
    check("a fine-grained PAT shape is caught",
          bool(SECRET_SHAPES.search("github_pat_" + "b" * 24)))
    check("an Anthropic key shape is caught",
          bool(SECRET_SHAPES.search("sk-ant-" + "c" * 20)))
    check("ordinary prose is not flagged",
          not SECRET_SHAPES.search("the token is read from the environment"))


def test_quoted_line_counting():
    print("\n6. quoted-line counting covers every quoting form")
    # Mirrors the expression in validate(). Kept here rather than imported because it is
    # an inline sum there; if that changes shape, this test should be updated with it.
    def quoted(text):
        return sum(
            1
            for ln in text.splitlines()
            if ln.startswith(("    ", "\t")) or ln.lstrip().startswith(">")
        )

    check("blockquote lines count", quoted("> a\n> b\n> c") == 3)
    check("four-space indented lines count", quoted("    a\n    b\n    c") == 3)
    check("tab-indented lines count", quoted("\ta\n\tb\n\tc") == 3)
    check("an indented blockquote counts once, not twice", quoted("  > a") == 1)
    check("ordinary prose does not count", quoted("plain\nlines\nhere") == 0)


def main():
    print("Prose-review validator — unit tests")
    test_hunk_lines_basic()
    test_hunk_lines_deleted_file()
    test_hunk_lines_content_resembling_a_header()
    test_bare_reference_rule()
    test_secret_shapes()
    test_quoted_line_counting()

    print()
    if failures:
        print(f"FAILED ({len(failures)}): " + ", ".join(failures))
        return 1
    print("All prose-review validator tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
