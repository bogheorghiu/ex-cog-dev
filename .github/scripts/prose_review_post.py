#!/usr/bin/env python3
"""Validate the reviewer's findings, then post only the ones that hold up.

Why the reviewer does not post its own comments: a protocol line saying "verify your
citation before posting" is a request, and nothing notices when it is skipped. Moving
the pen here turns three requirements into machine checks that a finding cannot route
around —

  1. the rule it cites exists;
  2. that rule actually binds the file it is commenting on (per the same derived
     bindings the reviewer was given, so it cannot invent a scope);
  3. the line it targets is really in this diff.

A finding failing any of these is never posted at all, rather than posted and audited
afterwards. So the only thing reaching the PULL REQUEST is text this script chose to
send. That is narrower than "the only thing reaching a public surface": the workflow
also publishes the work directory as a build artifact and prints the reviewer's closing
text to a world-readable log, both carrying model-written bytes that these checks never
see. Both get the credential screen and nothing more, and it is the SAME screen: the
artifact through `scrub()` below, the log through `screened()` imported into the step
that prints it. Issue #197 carries whether those channels should exist at all.

Links are generated here too, so a malformed permalink is not something the reviewer can
get wrong.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Findings above this are worth a comment; below it they are noise. The reviewer is
# told the same threshold, so this is a backstop against drift, not the primary filter.
MIN_SEVERITY = {"blocking", "should-fix"}

REQUIRED_FIELDS = ("file", "line", "rule", "severity", "summary", "detail")

# One of the two citations that are not rule files (`BUG` below is the other). A change
# whose own text contradicts itself — a doc stating a default the code sets differently,
# a comment describing behaviour the code does not have — is worth reporting and cites
# no rule, because it is wrong on its own terms rather than against a convention.
# Without this the protocol would invite such findings and the validator would silently
# drop every one, which is the worst shape a disagreement between two components can
# take.
SELF_CONTRADICTION = "self-contradiction"

# A change that is simply wrong, citing no convention. Kept as its own category rather
# than folded into self-contradiction because the two route differently in triage: a
# self-contradiction is a documentation defect, a bug is a code defect.
BUG = "bug"

RESERVED_CITATIONS = {SELF_CONTRADICTION, BUG}

# Limits come from the environment, and the same values are published to the reviewer in
# constraints.md before it writes. Hardcoding them in two places is how the model's idea
# of the rules and the enforcement of them drift apart.
MAX_COMMENT_CHARS = int(os.environ.get("PROSE_REVIEW_MAX_COMMENT_CHARS", "1200"))
MAX_QUOTED_LINES = int(os.environ.get("PROSE_REVIEW_MAX_QUOTED_LINES", "6"))

# `issue #N` / `PR #N`, never a bare `#N`. GitHub renders a hovercard for the bare form
# on the web, which is why the repo's rule permits it in issue bodies -- but review
# comments also arrive as plain-text email, where no icon or preview exists, so the
# strict form is what actually serves the reader here.
#
# IGNORECASE and the `request ` lookbehind, because the check enforces "name the kind",
# not one exact spelling of it: without them `See Issue #182` and `pull request #182`
# were rejected even though both name the kind -- and the capitalised form is the one
# `explain-changes`, which the reviewer is told to apply to its own writing, uses in
# its own worked example.
BARE_REF = re.compile(r"(?<!issue )(?<!request )(?<!PR )(?<![\w/])#\d+", re.IGNORECASE)

# A finding becomes a public comment, so its text is the one output channel out of this
# job that these checks control — the artifact and the run log are the other two, and both
# get only `screened()` below (see the header). The job holds two
# live tokens on all three. The reviewer is given `Read` without a path
# scope (it has to be able to read the repo it reviews), which means /proc/self/environ
# is reachable to it, so this is a real channel and not a theoretical one. The reviewer
# has no legitimate reason to ever quote a credential, so anything matching here is
# either an injection succeeding or a mistake, and both should stop at the same gate.
#
# Shape matching alone is a weak screen: it knows today's prefixes and nothing else.
SECRET_SHAPES = re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9-]{16,}")

# So the primary check is the literal one: the actual secret values this job was handed,
# matched exactly. That does not care what a token looks like, whether the provider
# changes its prefix, or whether the reviewer paraphrased around the shape -- it only
# cares whether the bytes are the ones we hold. It cannot catch an *encoded* secret, so
# the shape screen above stays as the second layer rather than being replaced.
#
# The 12-character floor keeps a short or empty variable from matching most findings and
# rejecting the entire review. Values are read once, at import, and never logged.
SECRET_ENV_VARS = ("GH_TOKEN", "GITHUB_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY")
SECRET_LITERALS = tuple(
    value
    for value in (os.environ.get(name, "").strip() for name in SECRET_ENV_VARS)
    if len(value) >= 12
)


def quoted_line_count(text: str) -> int:
    """Count the lines of quoted source in model-written text.

    Three quoting forms count: blockquotes, indented code blocks, and fenced code
    blocks. The fence form needs a toggle because its content lines carry no marker of
    their own — testing lines one at a time missed every line between the backticks,
    which let a 22-line fenced block through a six-line ceiling. Fence markers count
    too: they are part of the quoted block, and counting them keeps the ceiling from
    reading an empty fence as free.

    An indent is tested on the raw line and a blockquote marker on the stripped one;
    testing both on `lstrip()` output once made the indent arms unreachable, since a
    stripped line never begins with whitespace.

    One function, used by the finding check and the summary check both, so the two
    ceilings cannot drift apart the way duplicated inline sums already did once.
    """
    count = 0
    in_fence = False
    for ln in text.splitlines():
        stripped = ln.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            count += 1
        elif in_fence or ln.startswith(("    ", "\t")) or stripped.startswith(">"):
            count += 1
    return count


def hunk_lines(diff_text: str) -> dict[str, set[int]]:
    """Map each file in the diff to the new-file line numbers a comment may target.

    Only lines present on the right-hand side of the diff (added or context) can carry
    a review comment; commenting on a line that is not in the diff is rejected by the
    API, so catching it here turns a failed API call into a clear local error.
    """
    commentable: dict[str, set[int]] = {}
    current: str | None = None
    new_line = 0
    # Right-hand-side lines still owed by the current hunk header. While this is above
    # zero every line is hunk CONTENT and is never re-read as diff syntax. Without the
    # budget, an added line whose own text begins `++ ` renders in the diff as `+++ `
    # and parses as a file header — silently re-pointing everything after it at a file
    # that does not exist. This repo is mostly prose, much of it about diffs and
    # patches, so that content is not hypothetical. It fails closed on real findings:
    # they are dropped as "not in this diff" while the review reports success.
    new_remaining = 0
    for line in diff_text.splitlines():
        if new_remaining <= 0:
            # Between hunks: the only lines that carry meaning are the file header and
            # the next hunk header. Everything else here (`diff --git`, `index`,
            # `--- a/…`, trailing removals of a spent hunk) contributes no commentable
            # line, so it is skipped rather than counted.
            header = re.match(r"^\+\+\+ (.*)$", line)
            if header:
                # Any `+++ ` line is a file header, including `+++ /dev/null` for a
                # deleted file. Matching only `+++ b/` would leave `current` pointing at
                # the PREVIOUS file, and the `/dev/null` line — which starts with `+` —
                # would then be counted as an added line of it. That fails open: a
                # finding on a phantom line is accepted and 422s the entire review.
                target = header.group(1)
                current = target[2:] if target.startswith("b/") else None
                if current is not None:
                    commentable.setdefault(current, set())
                continue
            # The new-side count is optional in unified diff; absent means exactly one.
            hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
            if hunk:
                new_line = int(hunk.group(1))
                new_remaining = 1 if hunk.group(2) is None else int(hunk.group(2))
            continue
        if line.startswith("-"):
            continue  # left side only; owes nothing to the new-side budget
        if line.startswith("\\"):
            continue  # `\ No newline at end of file` annotates, it is not a line
        # Added or context. Counted even when `current` is None (a deleted file), so the
        # budget still drains and the next file header is not swallowed.
        if current is not None:
            commentable[current].add(new_line)
        new_line += 1
        new_remaining -= 1
    return commentable


def validate(findings: list[dict], manifest: dict, commentable: dict[str, set[int]]):
    """Split findings into (accepted, rejected-with-reason)."""
    accepted, rejected = [], []
    bindings = manifest["bindings"]
    # Rules are resolved from the snapshot the prepare step took on the PR head, not from
    # `.claude/rules/` in the checkout: by the time this runs the review action has
    # restored `.claude/` from the base branch, so a rule this PR adds would look
    # nonexistent here and every finding citing it would be dropped as uncitable.
    rules_dir = Path(manifest["rules_snapshot"])

    for raw in findings:
        if not isinstance(raw, dict):
            rejected.append(({"raw": repr(raw)[:200]}, "not an object"))
            continue

        missing = [f for f in REQUIRED_FIELDS if not raw.get(f)]
        if missing:
            rejected.append((raw, f"missing required field(s): {', '.join(missing)}"))
            continue

        # Matched on the escape-COLLAPSED text, for the same reason the artifact screen
        # is: an escaped token matches neither check as raw text and decodes to a live one
        # for anything that reads it. That fix reached `scrub()` and the log and stopped
        # here, which left the STRONGEST channel the weakest -- a review comment is public
        # the moment it posts, and `scrub()` runs in a later workflow step, so nothing can
        # take it back. Collapse only for the decision; the finding is rejected whole, so
        # no collapsed text is ever published.
        blob = _collapse_with_map(f"{raw['summary']} {raw['detail']}")[0]
        # Neither branch echoes what it matched, and the literal check is deliberately
        # first: it is the one that is certain rather than heuristic.
        if any(secret in blob for secret in SECRET_LITERALS):
            rejected.append((raw, "finding text contains a live credential from this job"))
            continue
        if SECRET_SHAPES.search(blob):
            rejected.append((raw, "finding text contains something credential-shaped"))
            continue

        text = f"{raw['summary']}\n{raw['detail']}"

        if len(text) > MAX_COMMENT_CHARS:
            rejected.append((raw, f"comment is {len(text)} characters; the limit is {MAX_COMMENT_CHARS}"))
            continue

        quoted = quoted_line_count(text)
        if quoted > MAX_QUOTED_LINES:
            rejected.append((raw, f"quotes {quoted} lines; the limit is {MAX_QUOTED_LINES}"))
            continue

        bare = BARE_REF.search(text)
        if bare:
            rejected.append((raw, f"writes a bare '{bare.group(0)}'; use 'issue {bare.group(0)}' or 'PR {bare.group(0)}'"))
            continue

        severity = str(raw["severity"]).lower()
        if severity not in MIN_SEVERITY:
            rejected.append((raw, f"severity '{severity}' below the reporting threshold"))
            continue

        file_path, rule = str(raw["file"]), str(raw["rule"])

        if file_path not in bindings:
            rejected.append((raw, f"'{file_path}' is not a file changed by this PR"))
            continue

        # The reserved citation cites no rule, so the two rule checks do not apply to it.
        # Every other check still does -- it must target a real changed file at a real
        # line in the diff.
        if rule not in RESERVED_CITATIONS:
            if not (rules_dir / f"{rule}.md").is_file():
                rejected.append((raw, f"cites rule '{rule}', which does not exist"))
                continue

            if rule not in bindings[file_path]:
                bound = ", ".join(bindings[file_path]) or "none"
                rejected.append(
                    (raw, f"rule '{rule}' does not bind '{file_path}' (bound rules: {bound})")
                )
                continue

        try:
            line_no = int(raw["line"])
        except (TypeError, ValueError):
            rejected.append((raw, f"line '{raw['line']}' is not a number"))
            continue

        if line_no not in commentable.get(file_path, set()):
            rejected.append((raw, f"line {line_no} of '{file_path}' is not in this diff"))
            continue

        accepted.append({**raw, "line": line_no, "rule": rule, "file": file_path})

    return accepted, rejected


# What the review body opens with when the model-written summary cannot be used.
NEUTRAL_HEADER = "Reviewed against this repository's own conventions."


def screen_header(summary: str) -> str:
    """Hold the top-level summary to the same screens every finding's text gets.

    The summary is model-written and lands verbatim in the posted review body — the
    same public surface as a finding, reached without passing through validate(). A
    summary that trips a screen is replaced with the neutral header rather than
    repaired: unlike a finding there is no repair round for it, and the failure is
    logged, so nothing is silently rewritten.
    """
    # Collapsed before matching, same reason as validate(): this text becomes the review
    # body, which is public on post.
    text = _collapse_with_map(summary.strip())[0]
    if not text:
        return NEUTRAL_HEADER
    quoted = quoted_line_count(text)
    reason = None
    if any(secret in text for secret in SECRET_LITERALS):
        reason = "contains a live credential from this job"
    elif SECRET_SHAPES.search(text):
        reason = "contains something credential-shaped"
    elif len(text) > MAX_COMMENT_CHARS:
        reason = f"is {len(text)} characters; the limit is {MAX_COMMENT_CHARS}"
    elif quoted > MAX_QUOTED_LINES:
        reason = f"quotes {quoted} lines; the limit is {MAX_QUOTED_LINES}"
    elif BARE_REF.search(text):
        reason = "writes a bare '#N' reference"
    if reason:
        print(f"::warning::review summary dropped — it {reason}; using the neutral header")
        return NEUTRAL_HEADER
    return text


def comment_body(finding: dict, repo: str, head_sha: str) -> str:
    rule = finding["rule"]
    if rule == SELF_CONTRADICTION:
        cite = "_The change contradicts itself; no rule is cited._"
    elif rule == BUG:
        cite = "_Reported as a defect in the change itself; no rule is cited._"
    else:
        link = f"https://github.com/{repo}/blob/{head_sha}/.claude/rules/{rule}.md"
        cite = f"Rule: [`{rule}`]({link})"
    return (
        f"**{finding['summary']}**\n\n"
        f"{finding['detail']}\n\n"
        f"{cite}\n"
        f"<!-- prose-review:{rule} -->"
    )


REDACTED = "[REDACTED-CREDENTIAL]"


def _collapse_with_map(value: str) -> tuple[str, list[tuple[int, int]]]:
    r"""Collapse escapes, and record which span of the ORIGINAL each collapsed char came from.

    The map is what lets a redaction touch only the matched span. Rewriting the whole
    string as its collapsed form would decode every unrelated escape too -- and `\u0022`
    decoding to a bare `"` turns a valid JSON file into an invalid one, which is the
    archive this branch exists to preserve.
    """
    out: list[str] = []
    origin: list[tuple[int, int]] = []
    pos = 0
    for match in ESCAPE_SEQUENCE.finditer(value):
        literal = value[pos:match.start()]
        out.append(literal)
        origin.extend((pos + i, pos + i + 1) for i in range(len(literal)))
        decoded = _decode_escape(match)
        out.append(decoded)
        origin.extend((match.start(), match.end()) for _ in decoded)
        pos = match.end()
    tail = value[pos:]
    out.append(tail)
    origin.extend((pos + i, pos + i + 1) for i in range(len(tail)))
    return "".join(out), origin


def _secret_spans(text: str) -> list[tuple[int, int]]:
    """Every span of `text` holding a live credential or something shaped like one."""
    spans = [(m.start(), m.end()) for m in SECRET_SHAPES.finditer(text)]
    for secret in SECRET_LITERALS:
        at = text.find(secret)
        while at != -1:
            spans.append((at, at + len(secret)))
            at = text.find(secret, at + 1)
    return sorted(spans)


def screened(value: str) -> str:
    r"""Redact credential material from a string about to reach a public surface.

    Used by every path that prints or publishes model-written bytes -- the artifact
    screen, the dropped-finding warnings, and the workflow's diagnostic step -- so all
    three apply exactly the same rules. A second copy would drift from the first, which is
    the defect this branch spent a dozen rounds on.

    Matching happens on the escape-COLLAPSED text and redaction happens on the ORIGINAL,
    through a position map. Both halves are load-bearing. Matching raw would miss an
    escaped token, which matches neither the literal nor the shape as text -- the bypass
    already closed once for the artifact and once for the log. Returning the collapsed
    text would decode every unrelated escape as a side effect, and a `\u0022` becoming a
    bare quote makes a JSON archive unparseable.

    A string with nothing to redact comes back unchanged, byte for byte.
    """
    collapsed, origin = _collapse_with_map(value)
    spans = _secret_spans(collapsed)
    if not spans:
        return value

    # Merge overlaps, then splice from the end so earlier offsets stay valid.
    merged: list[tuple[int, int]] = []
    for lo, hi in spans:
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))

    out = value
    for lo, hi in reversed(merged):
        out = out[: origin[lo][0]] + REDACTED + out[origin[hi - 1][1] :]
    return out


def _string_carries_secret(value: str) -> bool:
    """True if this string holds a live credential or something shaped like one."""
    return any(s in value for s in SECRET_LITERALS) or bool(SECRET_SHAPES.search(value))


# A surrogate PAIR is matched as one unit, before the single-escape alternative, so that a
# non-BMP character decodes to the one character it encodes rather than two halves of it.
# json.dumps writes every emoji this way under its default ensure_ascii, and a collapsed
# view that mangles them is a view the screens read wrongly.
ESCAPE_SEQUENCE = re.compile(
    r"\\u([dD][89abAB][0-9a-fA-F]{2})\\u([dD][c-fC-F][0-9a-fA-F]{2})"
    r"|\\u([0-9a-fA-F]{4})"
)


def _decode_escape(match: re.Match) -> str:
    """Turn one escape -- or one surrogate pair -- back into the character it encodes.

    An UNPAIRED surrogate is left as the literal escape text it already was, because a
    lone surrogate is not a character any consumer of this view can handle -- and nothing
    is lost, since it cannot be part of a credential either. Historical note, because the
    shape of this function looks over-careful without it: an earlier design wrote the
    collapsed text back to disk, and lone surrogates made that write raise. The write is
    gone; correct matching is what the care is for now.
    """
    high, low, single = match.groups()
    if single is None:
        return chr(0x10000 + (int(high, 16) - 0xD800) * 0x400 + (int(low, 16) - 0xDC00))
    code = int(single, 16)
    if 0xD800 <= code <= 0xDFFF:
        return match.group(0)
    return chr(code)


def scrub(work: Path) -> int:
    """Redact credential material from every file that is about to be published.

    The findings screen guards the review comment. That is one of THREE public surfaces
    this job now has -- the header above lists them -- and this function covers exactly
    one more: the work directory uploaded as an artifact. The third, the reviewer's
    closing text printed to a world-readable log, cannot be reached from here at all --
    those bytes are emitted before this runs -- so the diagnostic step imports `screened()`
    and applies it there. Counting the
    artifact as "the second channel" and stopping there is how an audit of what must be
    covered misses the one that gets no cover at all.

    ALL THREE model-written files in the artifact reach it unscreened. The findings screen
    decides which entries become a comment; it never rewrites a file, so `findings.json`
    is uploaded exactly as the model left it -- including any entry the screen refused.
    `rejected.json` records each rejected finding IN FULL, one of them rejected precisely
    for containing a live credential. `refuted.json` is written under an Edit rule and read
    by nothing. Counting two here rather than three would be the same under-count the
    paragraph above warns about, one file down instead of one channel.

    Screening those three by name would be the wrong shape. This branch's own history is a
    claim about which files exist going stale as files were added, so the guard is a choke
    point over the directory instead: every file that will be uploaded, whatever wrote it
    and whenever it appeared. A new output is covered on the day it is invented rather
    than on the day someone remembers to add it here.

    A match is REDACTED, not fatal, wherever redacting is possible -- which is every
    decodable file. Redacting is the only thing that changes what gets published, and a
    match is the screen working rather than an error, so it is loud (an error annotation
    naming the file) and the round is still archived with the credential removed.

    TWO cases are deliberately fatal, and both for the same reason -- the file cannot be
    cleared, not that a match occurred. A file that is not valid UTF-8 and still carries
    credential material after the byte pass: positions in a lenient decode do not map back
    to the original bytes, so there is nothing safe to write. And a file that cannot be
    READ at all: an OSError is caught nowhere here, because skipping past an unread file
    would leave it in the directory the next step publishes.

    An unexpected crash lands the same way for a third reason: a screen that can be
    bypassed by crashing is not a screen. In all three, the upload -- gated on this step
    succeeding -- withholds the round, and losing one round's archive is the cheaper of
    the two ways to be wrong.
    """
    redacted_files = 0
    for path in sorted(p for p in work.rglob("*") if p.is_file()):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Two passes here, and they end differently. LITERAL values are redacted in
            # the raw bytes, which needs no decoding and so is exact. Everything the
            # literal pass cannot reach -- a shaped token, an escaped one -- is only
            # DETECTABLE, on a lenient decode whose offsets do not map back to the
            # original bytes, so there is nothing safe to write and that path ends fatal.
            #
            # An earlier version skipped the file outright, reasoning that "neither screen
            # applies to what it cannot decode". That was false for the literal half, and
            # it left one invalid byte enough to smuggle a credential past a screen that
            # then published it.
            #
            # An OSError is still caught nowhere here on purpose: a file the screen could
            # not READ is not a file it has cleared, and skipping past it would leave it in
            # the directory the next step publishes -- the bypass-by-crashing the paragraph
            # above refuses. Letting it escape fails the step, and the upload is gated on
            # this step succeeding.
            data = path.read_bytes()
            scrubbed = data
            for secret in SECRET_LITERALS:
                scrubbed = scrubbed.replace(secret.encode("utf-8"), REDACTED.encode("utf-8"))
            if scrubbed != data:
                path.write_bytes(scrubbed)
                redacted_files += 1
                print(f"::error::redacted credential bytes from "
                      f"{path.relative_to(work)} (undecodable file) before upload")

            # The byte pass catches a LITERAL and nothing else -- it cannot collapse an
            # escape and cannot run the shape regex. So the two bypasses this screen has
            # already closed COMPOSE: one invalid byte routes a file down this branch, and
            # an escaped shaped token then passes it untouched. Verified.
            #
            # There is no safe in-place redaction here, because the offsets in a lenient
            # decode do not map back to the original bytes. So this fails closed, which is
            # the posture the docstring already sets: an undecodable file is not something
            # this pipeline produces, and one that also carries a credential is deliberate.
            # The message names the file and never what matched.
            # BOTH decodings, because each hides what the other reveals. With
            # errors="replace" every bad byte becomes U+FFFD, which is in none of the
            # shape pattern's character classes -- so one `\xff` dropped into the middle
            # of a token splits it into two runs and neither matches. With
            # errors="ignore" the bad byte vanishes and the token reads whole again.
            # Checking only the first was the gap; checking only the second would lose a
            # token whose bytes really are separated by content.
            views = [
                scrubbed.decode("utf-8", errors="replace"),
                scrubbed.decode("utf-8", errors="ignore"),
            ]
            if any(_string_carries_secret(ESCAPE_SEQUENCE.sub(_decode_escape, v))
                   for v in views):
                raise RuntimeError(
                    f"{path.relative_to(work)} is not valid UTF-8 and still carries "
                    f"credential material after the byte pass; refusing to publish"
                )
            continue

        # An escaped credential hides from both screens without hiding from a reader:
        # written as `\uXXXX` sequences a token matches neither the literal nor the shape
        # as raw text, and anything that decodes the file gets a live one back. Escaped and
        # raw are the SAME VALUE -- the property this repo already met from the other
        # direction in the ensure_ascii incident -- so a screen reading only bytes is
        # strictly weaker than the one guarding the comment path, which decodes first.
        #
        # Done by collapsing the escapes rather than by parsing JSON, deliberately. An
        # earlier version parsed, and fell through to the raw pass when the parse failed --
        # which left a model-written file needing only ONE syntax error to carry an escaped
        # credential past the screen intact. Nothing downstream would have caught it:
        # `refuted.json` is read by nothing. Collapsing is also not JSON-specific and
        # cannot be defeated by malformed input, because there is nothing to malform.
        #
        # Only rewritten when a credential is actually there, so an ordinary file keeps its
        # bytes exactly.
        redacted = screened(text)
        if redacted != text:
            path.write_text(redacted, encoding="utf-8")
            redacted_files += 1
            # The path, never the match: echoing what matched would republish the secret
            # in the run log, the same mistake one channel further along.
            print(f"::error::redacted credential material from "
                  f"{path.relative_to(work)} before upload")
    print(f"scrub: {redacted_files} file(s) redacted")
    return 0


def main() -> int:
    work = Path(os.environ["PROSE_REVIEW_DIR"])
    if os.environ.get("PROSE_REVIEW_SCRUB") == "1":
        # Returns before anything below reads the PR because the scrub needs none of it --
        # not because those files might be missing. This path is entered only from the
        # screening step, which is gated on `prepare` succeeding, and that gate is the
        # whole guarantee. Coupling a redaction pass to files it never opens would be one
        # more way to break it.
        return scrub(work)

    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]

    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    commentable = hunk_lines((work / "diff.patch").read_text(encoding="utf-8"))
    head_sha = manifest["head_sha"]

    findings_file = work / "findings.json"
    if not findings_file.is_file():
        # The prepare step seeds this file, so its absence means something deleted it
        # rather than that the reviewer declined to write -- a different fault, said
        # differently, because the two want different investigations.
        print("::error::findings.json is missing entirely; it is seeded before the "
              "reviewer runs, so something removed it")
        return 1

    raw_text = findings_file.read_text(encoding="utf-8")
    seed_digest = manifest.get("findings_seed_sha256")
    if seed_digest and hashlib.sha256(raw_text.encode("utf-8")).hexdigest() == seed_digest:
        # Distinguished from "found nothing", which is a legitimate empty result the
        # reviewer states deliberately. An untouched seed means the reviewer ran and never
        # wrote the one output this script validates, so there is no review to validate and
        # nothing to learn from validating it. Named precisely so the run's log says
        # which of the two happened.
        print("::error::the reviewer did not write findings.json — the file is still "
              "byte-identical to the seed. The Review step's own result is the place "
              "to look: it reports success even when the model produced no output.")
        return 1

    try:
        payload = json.loads(findings_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"::error::findings.json is not valid JSON: {exc}")
        return 1

    findings = payload.get("findings", []) if isinstance(payload, dict) else payload
    summary = payload.get("summary", "") if isinstance(payload, dict) else ""

    accepted, rejected = validate(findings, manifest, commentable)

    # Rejections are surfaced, never swallowed: a reviewer that keeps citing rules that
    # do not bind the file it is looking at is itself the finding.
    for finding, reason in rejected:
        # Screened because validate()'s own checks do not cover these fields: they run
        # over `summary` and `detail`, while this line interpolates `file` and the reason
        # strings interpolate `rule`, `line` and `severity`. scrub() cannot reach it
        # either -- it rewrites files on disk and this is already printed by then, the
        # same reason the closing text needed the screen imported into the step that
        # prints it.
        print(screened(f"::warning::dropped finding on "
                       f"{finding.get('file', '?')}: {reason}"))
    (work / "rejected.json").write_text(
        json.dumps([{"finding": f, "reason": r} for f, r in rejected], indent=2),
        encoding="utf-8",
    )

    if os.environ.get("PROSE_REVIEW_VALIDATE_ONLY") == "1":
        # First pass of the repair loop: report what failed and stop, so the reviewer
        # gets one chance to fix its own findings rather than losing them silently.
        print(f"validate-only: {len(accepted)} would post, {len(rejected)} rejected")
        gh_out = os.environ.get("GITHUB_OUTPUT")
        if gh_out:
            with open(gh_out, "a", encoding="utf-8") as fh:
                fh.write(f"rejected={len(rejected)}\n")
        return 0

    if not accepted:
        # Nothing to say, and the job stays green. Two outcomes are being kept apart
        # here, because conflating them is what made four broken rounds look fine:
        # "the reviewer never wrote its file" is a FAULT and fails above, on the seed
        # digest; "the reviewer ran and found nothing" is a RESULT and passes here.
        # Seeding findings.json exists to make that distinction machine-checkable
        # rather than inferred, so it would be self-defeating to fail on both.
        # No "found nothing" comment either: posting "0 comments" on every clean push
        # is pure noise, a required check reads the JOB's conclusion rather than a
        # posted review, and rejections are already in the log and in rejected.json.
        print(f"nothing to post; {len(rejected)} finding(s) dropped in validation")
        return 0

    header = screen_header(summary)
    body = (
        f"{header}\n\n"
        f"{len(accepted)} comment(s) posted"
        + (f"; {len(rejected)} finding(s) dropped in validation." if rejected else ".")
        + "\n\n<sub>Adapted from Anthropic's `code-review` plugin. These comments are "
        "advisory: none of them blocks a merge. A red check on this job never means a "
        "finding is blocking -- it means the job itself failed, either producing no "
        "review at all or withholding this run's archive from publication, which is a "
        "different thing and worth looking at. Reply, or apply the `no-prose-review` "
        "label to opt out.</sub>"
    )

    review = {
        "commit_id": head_sha,
        "body": body,
        "event": "COMMENT",
        "comments": [
            {
                "path": f["file"],
                "line": f["line"],
                "side": "RIGHT",
                "body": comment_body(f, repo, head_sha),
            }
            for f in accepted
        ],
    }

    request = work / "review-request.json"
    request.write_text(json.dumps(review, indent=2), encoding="utf-8")

    if os.environ.get("PROSE_REVIEW_DRY_RUN") == "1":
        print(f"dry run: would post {len(accepted)} comment(s); request at {request}")
        return 0

    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/pulls/{pr_number}/reviews",
         "--method", "POST", "--input", str(request)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(f"::error::failed to post review\n{proc.stderr}\n")
        return 1

    print(f"posted {len(accepted)} comment(s), dropped {len(rejected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
