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

No git and no network. Any test that needs the filesystem builds a temporary directory
and removes it again; the rest are pure functions over strings. One of them chmods a file
to 0o000 to make it unreadable, and self-skips where that fails to -- as it does under
root. Run directly:
    python3 .github/scripts/test_prose_review_post.py
"""

import io
import json
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
    screened as scrub_screen,
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

        check("a round with matches still returns 0, so it is archived", rc == 0)
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
        check("an undecodable file with no credential keeps its bytes exactly",
              (work / "blob.bin").read_bytes() == b"\xff\xfe\x00binary")
        check("three files reported as redacted", "scrub: 3 file(s) redacted" in out)
        check("the log names paths and never echoes the match",
              literal not in out and secret not in out)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        prose_review_post.SECRET_LITERALS = ()


def test_scrub_fails_closed_on_unreadable_file():
    print("\n10. scrub() fails rather than skipping a file it could not read")
    # A file the screen could not READ is not a file it has cleared. Skipping past it
    # would leave it in the directory the upload step publishes, which is the
    # bypass-by-crashing the docstring refuses. So the error must escape: the workflow
    # gates the upload on this step succeeding, and a failure there withholds the
    # artifact. Binary content raises UnicodeDecodeError (skipped, covered above), so
    # only a genuine I/O failure reaches this path.
    work = Path(tempfile.mkdtemp(prefix="scrub-oserror-"))
    try:
        (work / "readable.json").write_text("{}", encoding="utf-8")
        unreadable = work / "unreadable.json"
        unreadable.write_text("secret-bearing", encoding="utf-8")
        unreadable.chmod(0o000)

        # Root ignores the mode bits, so the unreadable state cannot be created there.
        # Say so and pass, rather than asserting a setup this user could not build.
        if os.access(unreadable, os.R_OK):
            check("skipped - this user can read a 0o000 file (root?)", True)
            return

        prose_review_post.SECRET_LITERALS = ("secret-bearing",)
        raised = False
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                scrub(work)
        except OSError:
            raised = True
        check("an unreadable file raises instead of being skipped", raised)
    finally:
        try:
            (work / "unreadable.json").chmod(0o600)
        except OSError:
            pass
        shutil.rmtree(work, ignore_errors=True)
        prose_review_post.SECRET_LITERALS = ()


def test_scrub_catches_escaped_and_undecodable_credentials():
    print("\n11. scrub() catches a credential the raw-text screens cannot see")
    # Two bypasses of a screen that only reads a file's bytes as text. Both were found by
    # /code-review on 2026-08-02, and both let a live token reach the public artifact.
    literal = "s3cr3t-literal-value-xyz"
    shaped = "ghp_" + "B" * 30

    work = Path(tempfile.mkdtemp(prefix="scrub-bypass-"))
    try:
        # (a) JSON escapes. Escaped and raw are the SAME VALUE, so the token survives
        # json.loads while matching neither screen as text -- the property this repo
        # already met from the other direction in the ensure_ascii incident.
        escaped = json.dumps({"detail": shaped}).replace("ghp_", "\\u0067\\u0068\\u0070_")
        assert shaped not in escaped, "fixture must not contain the raw token"
        (work / "findings.json").write_text(escaped, encoding="utf-8")

        # (b) One invalid UTF-8 byte makes read_text raise, and an earlier version skipped
        # the file entirely -- publishing it. The literal check works fine on bytes.
        (work / "odd.log").write_bytes(b"\xff prefix " + literal.encode() + b" suffix")

        # (c) The same escape plus ONE syntax error. An earlier fix parsed the JSON and
        # fell through to the raw pass when the parse failed -- so a single stray comma
        # was enough to carry the token through intact, and nothing downstream reads
        # refuted.json to catch it. Collapsing escapes textually has nothing to malform.
        (work / "refuted.json").write_text(escaped[:-1] + ",", encoding="utf-8")

        prose_review_post.SECRET_LITERALS = (literal,)
        buf = io.StringIO()
        with redirect_stdout(buf):
            scrub(work)
        out = buf.getvalue()

        after_json = (work / "findings.json").read_text(encoding="utf-8")
        check("the escaped token no longer decodes to a credential",
              shaped not in json.dumps(json.loads(after_json)))
        check("the escaped file is reported as redacted",
              "findings.json" in out)
        check("a credential in an undecodable file is redacted, not skipped",
              literal.encode() not in (work / "odd.log").read_bytes())
        check("the undecodable file keeps its surrounding bytes",
              (work / "odd.log").read_bytes().startswith(b"\xff prefix "))
        after_broken = (work / "refuted.json").read_text(encoding="utf-8")
        check("a MALFORMED json file does not smuggle the escaped token through",
              shaped not in prose_review_post.ESCAPE_SEQUENCE.sub(
                  prose_review_post._decode_escape, after_broken))
        check("neither log line echoes the credential",
              literal not in out and shaped not in out)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        prose_review_post.SECRET_LITERALS = ()


def test_scrub_fails_closed_on_composed_bypass():
    print("\n12. scrub() fails closed when the two bypasses are composed")
    # One invalid byte routes a file down the bytes branch, where only the LITERAL screen
    # runs -- no escape collapsing, no shape regex. An escaped shaped token therefore
    # passes it untouched. Found by the reviewer as a refuted candidate and confirmed:
    # composing two separately-closed bypasses reopened the screen.
    #
    # There is no safe in-place redaction (offsets in a lenient decode do not map back to
    # the original bytes), so this must fail closed and withhold the artifact.
    shaped = "ghp_" + "D" * 30
    escaped = shaped.replace("ghp_", "\\u0067\\u0068\\u0070_")

    work = Path(tempfile.mkdtemp(prefix="scrub-composed-"))
    try:
        (work / "odd.json").write_bytes(b"\xff " + escaped.encode())
        prose_review_post.SECRET_LITERALS = ()
        message = None
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                scrub(work)
        except RuntimeError as exc:
            message = str(exc)
        check("an undecodable file still carrying a credential refuses to publish",
              message is not None)
        # Asserted on the EXCEPTION, not on stdout. Nothing is printed down this path --
        # the byte pass matched no literal and scrub() raises before its closing tally --
        # so a stdout assertion held for any implementation, including one that echoed the
        # token. The raised message is what a failing step surfaces to the public log, so
        # it is the text that has to be clean.
        check("the refusal names the file", message is not None and "odd.json" in message)
        check("the refusal names no matched text",
              message is not None and shaped not in message and escaped not in message)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        prose_review_post.SECRET_LITERALS = ()


def test_screened_preserves_everything_it_did_not_match():
    print("\n13. screened() redacts the matched span and leaves the rest alone")
    # Matching happens on the escape-collapsed text; redaction has to happen on the
    # ORIGINAL. Returning the collapsed form decoded every unrelated escape as a side
    # effect, and `\\u0022` becoming a bare quote turned a valid JSON archive invalid --
    # the archive this whole branch exists to preserve.
    tok = "ghp_" + "G" * 30
    prose_review_post.SECRET_LITERALS = ()
    try:
        src = '{"a": "he said \\u0022hi\\u0022", "t": "%s"}' % tok
        out = scrub_screen(src)
        check("the credential is gone", tok not in out)
        check("unrelated escapes are NOT decoded", "\\u0022" in out)
        check("the archive still parses as JSON", json.loads(out) is not None)

        esc = '{"t": "\\u0067\\u0068\\u0070_%s"}' % ("G" * 30)
        out2 = scrub_screen(esc)
        check("an escaped credential is still caught", REDACTED in out2)
        check("and its file still parses", json.loads(out2) is not None)

        clean = json.dumps({"note": "ok", "q": 'a "quoted" word'})
        check("a file with nothing to redact is byte-identical",
              scrub_screen(clean) == clean)
    finally:
        prose_review_post.SECRET_LITERALS = ()


def test_comment_path_collapses_escapes_too():
    print("\n14. the PR-comment gate collapses escapes, like the artifact gate")
    # The seventh bypass, and the worst: the escape-collapse fix reached scrub() and the
    # log and stopped there, leaving the two functions that gate a LIVE PUBLIC COMMENT
    # matching raw text. The comment posts in an earlier workflow step than the artifact
    # screen, so nothing could have taken it back.
    import importlib
    fake = "ghp_" + "Z" * 32
    saved = os.environ.get("GH_TOKEN")
    os.environ["GH_TOKEN"] = fake
    try:
        mod = importlib.reload(prose_review_post)
        escaped = "".join(chr(92) + "u%04x" % ord(c) for c in fake)
        finding = {"file": "f.py", "line": 1, "rule": mod.BUG, "severity": "blocking",
                   "summary": "s", "detail": "leaked: " + escaped}
        manifest = {"bindings": {"f.py": [mod.BUG]}, "rules_snapshot": "."}
        accepted, rejected = mod.validate([finding], manifest, {"f.py": {1}})
        check("an escaped credential is rejected, not posted", not accepted and len(rejected) == 1)
        check("and rejected as a LIVE credential, not merely shaped",
              rejected and "live credential" in rejected[0][1])

        buf = io.StringIO()
        with redirect_stdout(buf):
            header = mod.screen_header("leaked: " + escaped)
        check("an escaped credential in the summary falls back to the neutral header",
              header == mod.NEUTRAL_HEADER)

        ordinary = {**finding, "detail": "an ordinary finding about a rule"}
        ok, _ = mod.validate([ordinary], manifest, {"f.py": {1}})
        check("an ordinary finding is unaffected", len(ok) == 1)
    finally:
        if saved is None:
            os.environ.pop("GH_TOKEN", None)
        else:
            os.environ["GH_TOKEN"] = saved
        importlib.reload(prose_review_post)


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
    test_scrub_fails_closed_on_unreadable_file()
    test_scrub_catches_escaped_and_undecodable_credentials()
    test_scrub_fails_closed_on_composed_bypass()
    test_screened_preserves_everything_it_did_not_match()
    test_comment_path_collapses_escapes_too()

    print()
    if failures:
        print(f"FAILED ({len(failures)}): " + ", ".join(failures))
        return 1
    print("All prose-review validator tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
