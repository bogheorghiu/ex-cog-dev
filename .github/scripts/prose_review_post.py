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
afterwards. It also means the model has no write channel: the only thing that reaches a
public surface is text this script chose to send.

Links are generated here too, so a malformed permalink is not something the reviewer can
get wrong.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Findings above this are worth a comment; below it they are noise. The reviewer is
# told the same threshold, so this is a backstop against drift, not the primary filter.
MIN_SEVERITY = {"blocking", "should-fix"}

REQUIRED_FIELDS = ("file", "line", "rule", "severity", "summary", "detail")

# The one citation that is not a rule file. A change whose own text contradicts itself —
# a doc stating a default the code sets differently, a comment describing behaviour the
# code does not have — is worth reporting and cites no rule, because it is wrong on its
# own terms rather than against a convention. Without this the protocol would invite such
# findings and the validator would silently drop every one, which is the worst shape a
# disagreement between two components can take.
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
BARE_REF = re.compile(r"(?<!issue )(?<!PR )(?<![\w/])#\d+")

# A finding becomes a public comment, so its text is an output channel. The reviewer has
# no reason to ever quote a credential, and the job environment is readable from inside
# the runner (/proc/self/environ), so anything token-shaped in a finding is either an
# injection succeeding or a mistake. Cheap screen, not a guarantee: it catches known
# prefixes, not an encoded or reworded secret.
SECRET_SHAPES = re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9-]{16,}")


def hunk_lines(diff_text: str) -> dict[str, set[int]]:
    """Map each file in the diff to the new-file line numbers a comment may target.

    Only lines present on the right-hand side of the diff (added or context) can carry
    a review comment; commenting on a line that is not in the diff is rejected by the
    API, so catching it here turns a failed API call into a clear local error.
    """
    commentable: dict[str, set[int]] = {}
    current: str | None = None
    new_line = 0
    for line in diff_text.splitlines():
        header = re.match(r"^\+\+\+ (.*)$", line)
        if header:
            # Any `+++ ` line is a file header, including `+++ /dev/null` for a deleted
            # file. Matching only `+++ b/` would leave `current` pointing at the
            # PREVIOUS file, and the `/dev/null` line — which starts with `+` — would
            # then be counted as an added line of it. That fails open: a finding on a
            # phantom line is accepted here and 422s the entire review at the API.
            target = header.group(1)
            current = target[2:] if target.startswith("b/") else None
            if current is not None:
                commentable.setdefault(current, set())
            continue
        hunk = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if hunk:
            new_line = int(hunk.group(1))
            continue
        if current is None:
            continue
        if line.startswith("+"):
            commentable[current].add(new_line)
            new_line += 1
        elif line.startswith("-"):
            continue
        elif line.startswith(" "):
            commentable[current].add(new_line)
            new_line += 1
    return commentable


def validate(findings: list[dict], manifest: dict, commentable: dict[str, set[int]]):
    """Split findings into (accepted, rejected-with-reason)."""
    accepted, rejected = [], []
    bindings = manifest["bindings"]

    for raw in findings:
        if not isinstance(raw, dict):
            rejected.append(({"raw": repr(raw)[:200]}, "not an object"))
            continue

        missing = [f for f in REQUIRED_FIELDS if not raw.get(f)]
        if missing:
            rejected.append((raw, f"missing required field(s): {', '.join(missing)}"))
            continue

        blob = f"{raw['summary']} {raw['detail']}"
        if SECRET_SHAPES.search(blob):
            # Deliberately does not echo the match.
            rejected.append((raw, "finding text contains something credential-shaped"))
            continue

        text = f"{raw['summary']}\n{raw['detail']}"

        if len(text) > MAX_COMMENT_CHARS:
            rejected.append((raw, f"comment is {len(text)} characters; the limit is {MAX_COMMENT_CHARS}"))
            continue

        quoted = sum(1 for ln in text.splitlines() if ln.lstrip().startswith((">", "    ", "\t")))
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
            if not (REPO_ROOT / ".claude" / "rules" / f"{rule}.md").is_file():
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


def main() -> int:
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    work = Path(os.environ["PROSE_REVIEW_DIR"])

    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    commentable = hunk_lines((work / "diff.patch").read_text(encoding="utf-8"))
    head_sha = manifest["head_sha"]

    findings_file = work / "findings.json"
    if not findings_file.is_file():
        print("::error::reviewer produced no findings.json — treating as a failed run")
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
        print(f"::warning::dropped finding on {finding.get('file', '?')}: {reason}")
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
        # Nothing to say. Posting "0 comments" on every push is pure noise: a required
        # check reads the JOB's conclusion, not a posted review, so the empty post buys
        # nothing. Rejections are already in the log and in rejected.json.
        print(f"nothing to post; {len(rejected)} finding(s) dropped in validation")
        return 0

    header = summary.strip() or "Reviewed against this repository's own conventions."
    body = (
        f"{header}\n\n"
        f"{len(accepted)} comment(s) posted"
        + (f"; {len(rejected)} finding(s) dropped in validation." if rejected else ".")
        + "\n\n<sub>Adapted from Anthropic's `code-review` plugin. Advisory only — "
        "reply or apply the `no-prose-review` label to opt out.</sub>"
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
