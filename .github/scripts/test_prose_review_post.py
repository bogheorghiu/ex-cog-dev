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

No git and no network. Every test but the last is a pure function over strings; the
artifact scrub necessarily writes files, so it runs against a temporary directory it
creates and removes itself. Run directly:
    python3 .github/scripts/test_prose_review_post.py
"""

import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import prose_review_post  # noqa: E402
from prose_review_post import (  # noqa: E402
    scrub,
    REDACTED,
    hunk_lines,
    quoted_line_count,
    screen_header,
    BARE_REF,
    NEUTRAL_HEADER,
    SECRET_SHAPES,
)

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
    print("\n4. BARE_REF — name the kind, in any of its honest spellings")
    check("bare reference is caught", bool(BARE_REF.search("see #182 for context")))
    check("`issue #N` is allowed", not BARE_REF.search("see issue #182"))
    check("`PR #N` is allowed", not BARE_REF.search("see PR #182"))
    check("a URL fragment is not a bare reference",
          not BARE_REF.search("https://example.com/x/#182"))
    # The check enforces "name the kind", not one spelling of it: the capitalised and
    # spelled-out forms name the kind just as plainly, and the capitalised form appears
    # in the worked example of a rule the reviewer applies to its own writing.
    check("`Issue #N` (capitalised) is allowed", not BARE_REF.search("See Issue #182"))
    check("`pull request #N` (spelled out) is allowed",
          not BARE_REF.search("the pull request #182 adds it"))
    check("`Pr #N` mixed case is allowed", not BARE_REF.search("in Pr #182"))
    check("a bare number after unrelated words is still caught",
          bool(BARE_REF.search("the fix landed in #182")))


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


def test_secret_literals():
    print("\n6. literal credential screen — the actual values this job holds")
    # SECRET_LITERALS is read from the environment at import, so this needs a fresh load
    # of the module with the variables set.
    import importlib

    fake = "s3cret-" + "V" * 24
    saved = {k: os.environ.get(k) for k in ("GH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN")}
    os.environ["GH_TOKEN"] = fake
    os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = "short"  # below the floor, must be ignored
    try:
        import prose_review_post as mod

        mod = importlib.reload(mod)
        check("a live token value is picked up", fake in mod.SECRET_LITERALS)
        check("a value under the 12-char floor is ignored",
              "short" not in mod.SECRET_LITERALS)
        check("a finding quoting the live token would be caught",
              any(s in f"leaked: {fake}" for s in mod.SECRET_LITERALS))
        check("ordinary prose is unaffected",
              not any(s in "a normal finding about a rule" for s in mod.SECRET_LITERALS))
        check("the token does not have to look like a token",
              not mod.SECRET_SHAPES.search(fake))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        importlib.reload(mod)


def test_quoted_line_counting():
    print("\n7. quoted_line_count covers every quoting form, fences included")
    quoted = quoted_line_count

    check("blockquote lines count", quoted("> a\n> b\n> c") == 3)
    check("four-space indented lines count", quoted("    a\n    b\n    c") == 3)
    check("tab-indented lines count", quoted("\ta\n\tb\n\tc") == 3)
    check("an indented blockquote counts once, not twice", quoted("  > a") == 1)
    check("ordinary prose does not count", quoted("plain\nlines\nhere") == 0)
    # The fence form: its content lines carry no per-line marker, so a per-line test
    # counted a 22-line fenced block as zero against a ceiling of six.
    check("fenced block content counts, markers included",
          quoted("```\na\nb\nc\n```") == 5)
    check("a long fenced block is not free",
          quoted("```python\n" + "\n".join("x" for _ in range(22)) + "\n```") == 24)
    check("prose after a closed fence does not count",
          quoted("```\na\n```\nplain prose") == 3)
    check("a language tag on the fence changes nothing",
          quoted("```yaml\nkey: value\n```") == 3)


def test_screen_header():
    print("\n8. screen_header — the summary gets the same screens a finding gets")
    # The summary reaches the public review body without passing through validate(),
    # so it needs its own gate; these mirror the finding-text checks one for one.
    check("an ordinary summary passes through unchanged",
          screen_header("Checked the workflow and both scripts.")
          == "Checked the workflow and both scripts.")
    check("an empty summary falls back to the neutral header",
          screen_header("   ") == NEUTRAL_HEADER)
    check("a credential-shaped summary is replaced",
          screen_header("saw ghp_" + "A" * 32) == NEUTRAL_HEADER)
    check("an over-long summary is replaced",
          screen_header("x" * 5000) == NEUTRAL_HEADER)
    check("a bare issue/PR reference is replaced",
          screen_header("see #182") == NEUTRAL_HEADER)
    check("a proper 'PR #N' reference passes",
          screen_header("see PR #182") == "see PR #182")
    check("a summary over the quoted-line ceiling is replaced",
          screen_header("\n".join("> quoted" for _ in range(7))) == NEUTRAL_HEADER)
    check("a summary within the quoted-line ceiling passes",
          screen_header("intro\n> one quoted line") == "intro\n> one quoted line")


def test_artifact_scrub():
    print("\n9. scrub() over the directory that becomes a public artifact")
    secret = "ghp_" + "A" * 30            # shaped like a token; never a real one
    literal = "s3cr3t-literal-value-xyz"  # stands in for a live env credential

    work = Path(tempfile.mkdtemp(prefix="scrub-test-"))
    try:
        # Written by the validator, never screened before this change.
        (work / "rejected.json").write_text(
            '[{"finding": {"detail": "token is ' + literal + '"}, "reason": "cred"}]',
            encoding="utf-8")
        # Written by the model under an Edit rule, screened by nothing.
        (work / "refuted.json").write_text(
            '[{"refutation": "quotes ' + secret + ' verbatim"}]', encoding="utf-8")
        # Nested, to prove the walk recurses rather than listing one level.
        (work / "rules").mkdir()
        (work / "rules" / "r.md").write_text("leaks " + literal + " too\n", encoding="utf-8")
        clean = "nothing to see here\n"
        (work / "diff.patch").write_text(clean, encoding="utf-8")
        (work / "blob.bin").write_bytes(b"\xff\xfe\x00binary")

        prose_review_post.SECRET_LITERALS = (literal,)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = scrub(work)
        out = buf.getvalue()

        check("returns 0 so a failed round is still archived", rc == 0)
        check("literal credential is gone from rejected.json",
              literal not in (work / "rejected.json").read_text(encoding="utf-8"))
        check("credential-shaped token is gone from refuted.json",
              secret not in (work / "refuted.json").read_text(encoding="utf-8"))
        check("nested files are covered, not just the top level",
              literal not in (work / "rules" / "r.md").read_text(encoding="utf-8"))
        check("a redaction marker is left in place of the match",
              REDACTED in (work / "refuted.json").read_text(encoding="utf-8"))
        check("a clean file is left byte-identical",
              (work / "diff.patch").read_text(encoding="utf-8") == clean)
        check("an undecodable file is skipped rather than crashing",
              (work / "blob.bin").read_bytes() == b"\xff\xfe\x00binary")
        check("three files reported as redacted", "scrub: 3 file(s) redacted" in out)
        check("the log names paths and never echoes the match",
              literal not in out and secret not in out)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        prose_review_post.SECRET_LITERALS = ()


def main():
    print("Prose-review validator — unit tests")
    test_hunk_lines_basic()
    test_hunk_lines_deleted_file()
    test_hunk_lines_content_resembling_a_header()
    test_bare_reference_rule()
    test_secret_shapes()
    test_secret_literals()
    test_quoted_line_counting()
    test_screen_header()
    test_artifact_scrub()

    print()
    if failures:
        print(f"FAILED ({len(failures)}): " + ", ".join(failures))
        return 1
    print("All prose-review validator tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
