#!/usr/bin/env python3
"""Keep tracked JSON files pure ASCII, with no \\uXXXX escape sequences.

Why this gate exists
--------------------
A JSON manifest here is machine-facing, but its `description` field is *prose* -
a sentence shown to a human browsing the marketplace. Prose attracts typographic
characters (em-dashes especially), and a non-ASCII character in a JSON file is
the input a whole class of silent rewrites needs:

  json.load(f) -> change one field -> json.dump(f)

Python's `json.dump` defaults to `ensure_ascii=True`, so that round trip re-emits
*every* non-ASCII character in the file as a `\\uXXXX` escape - including
characters on lines nobody was editing. It happened twice in this repo (June
2026, two plugin manifests); one instance shipped and sat on main unnoticed for
over a month. The tool exits 0, the file still parses, the tests still pass, and
the change is semantically null: escaped and raw are the *same* JSON value, so
no consumer can tell. Only the bytes differ - which means only a diff, a grep, or
a byte check can see it.

Detecting that after the fact was the original plan. Removing the input is
better: with no non-ASCII character in the file, there is nothing to re-encode,
and the failure mode cannot occur at all. Hence "ASCII-only" rather than "no
escape sequences" - it is the blunter rule, and the one that cannot be argued
with.

Why it does NOT reformat
------------------------
The fixer replaces the offending *bytes* and nothing else. It never parses and
re-serialises the file, because that is the original defect wearing a fix's
clothes: rewriting a whole file to correct one line is exactly what produced the
damage this guard exists to prevent.

CI runs this WITHOUT --fix, so the job reports and fails but never modifies a
file. Rewriting files from CI would put an unreviewed whole-file write on the
publish path.

Scope: tracked `*.json` only. Markdown is deliberately untouched - the repo's
prose carries ~1700 em-dashes as house style, nothing parses and re-serialises
Markdown, and this failure has never occurred there.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# The one character we substitute automatically. It is punctuation with an exact,
# meaning-preserving ASCII stand-in, and it is the character that caused every
# recorded instance. Anything else is a judgement call the operator makes.
EM_DASH = "—".encode()
EM_DASH_REPLACEMENT = b"-"

# An escaped non-ASCII character is pure ASCII on disk, so the non-ASCII scan below
# cannot see it - but it is precisely what the bad round trip *produces*, so it is
# caught separately. Matching is deliberately narrow: a backslash-u followed by four
# hex digits. \\uXXXX inside a JSON string is the escape; a doubled backslash is not.
ESCAPE_RE = re.compile(rb"(?<!\\)\\u[0-9a-fA-F]{4}")


def tracked_json_files(repo_root: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "*.json"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    ).stdout
    return [repo_root / p.decode() for p in out.split(b"\0") if p]


def line_of(data: bytes, index: int) -> int:
    return data.count(b"\n", 0, index) + 1


def scan(data: bytes) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """Return (non_ascii, escapes) as lists of (line_number, detail)."""
    non_ascii: list[tuple[int, str]] = []
    for match in re.finditer(rb"[^\x00-\x7F]+", data):
        text = match.group().decode("utf-8", errors="replace")
        for ch in dict.fromkeys(text):  # unique, order-preserving
            non_ascii.append((line_of(data, match.start()), f"U+{ord(ch):04X} {ch!r}"))

    escapes = [
        (line_of(data, m.start()), m.group().decode("ascii"))
        for m in ESCAPE_RE.finditer(data)
    ]
    return non_ascii, escapes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Replace em-dashes with '-' in place (byte substitution, no reformatting). "
        "Any other non-ASCII character is reported and left alone - it needs a human "
        "decision, not a default.",
    )
    args = parser.parse_args()

    repo_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
    )

    files = tracked_json_files(repo_root)

    # Fail loudly on an empty file set rather than reporting success over nothing.
    # A guard that inspects zero files prints the same "all clear" as one that
    # inspected everything and found nothing - so a broken invocation (wrong cwd,
    # a glob that stops matching, a checkout that did not happen) would read as a
    # green tick forever. This repo always tracks JSON manifests; zero means the
    # scan is broken, not that the tree is clean.
    if not files:
        print(
            "No tracked JSON files found - refusing to report success.\n"
            "This guard is meaningless over an empty set; check the working "
            "directory and that the repository is checked out.",
            file=sys.stderr,
        )
        return 1

    failures = 0
    fixed_files = 0

    for path in files:
        data = path.read_bytes()

        if args.fix and EM_DASH in data:
            path.write_bytes(data.replace(EM_DASH, EM_DASH_REPLACEMENT))
            data = path.read_bytes()
            fixed_files += 1
            print(f"fixed (em-dash -> '-'): {path.relative_to(repo_root)}")

        non_ascii, escapes = scan(data)
        rel = path.relative_to(repo_root)

        for line, detail in non_ascii:
            failures += 1
            print(f"{rel}:{line}: non-ASCII character {detail}", file=sys.stderr)
        for line, detail in escapes:
            failures += 1
            print(f"{rel}:{line}: escape sequence {detail}", file=sys.stderr)

    if failures:
        print(
            f"\n{failures} problem(s) found in tracked JSON.\n"
            "  Em-dashes:  python3 .github/scripts/check_json_ascii.py --fix\n"
            "  Anything else: decide deliberately, then edit the character in place.\n"
            "    Do NOT reformat the file or pipe it through a JSON dumper - a whole-file\n"
            "    rewrite to fix one character is the defect this guard exists to prevent.",
            file=sys.stderr,
        )
        return 1

    if fixed_files:
        print(f"\n{fixed_files} file(s) fixed; tracked JSON is now ASCII-only.")
    else:
        print("Tracked JSON is ASCII-only, with no escape sequences.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
