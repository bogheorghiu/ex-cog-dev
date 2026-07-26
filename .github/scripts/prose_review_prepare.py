#!/usr/bin/env python3
"""Gather every input the prose reviewer needs, deterministically, before it runs.

Why this exists: the reviewer is given no shell and no network. It reads files and
writes one findings file. Everything it needs to see -- the diff, which files changed,
the PR's own text, what previous rounds already said, and which of this repo's rules
bind which file -- is assembled here, by code, and handed over as plain files.

That split is the whole security posture: an instruction hidden inside a PR diff cannot
make the reviewer fetch something, run something, or reach anything it was not handed.

Rule binding is derived from each rule's own `paths:` frontmatter rather than from a
hand-kept mapping, because a hand-kept list goes stale silently as rules are added --
which has already happened in this repo (see .claude/rules/, which grew by three
always-on rules between two branches).

No third-party imports on purpose: this runs on a bare runner before anything is
installed, and a dependency here would be one more thing that can break or be swapped.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# A rule carrying this scope governs prose written TO the operator (chat, status
# updates), not artifacts in a diff. Checking a changed file against it produces
# nonsense, so it never enters a file's binding set -- but it does constrain how the
# reviewer writes its own comments, so it is handed over separately.
CONVERSATION_SCOPE = "conversation"

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = REPO_ROOT / ".claude" / "rules"


def run(*args: str) -> str:
    """Run a command and return stdout, failing loudly rather than silently empty."""
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(f"::error::command failed: {' '.join(args)}\n{proc.stderr}\n")
        raise SystemExit(1)
    return proc.stdout


def parse_frontmatter(text: str) -> dict[str, object]:
    """Read the two frontmatter keys we care about: `scope` (scalar) and `paths` (list).

    Deliberately hand-rolled rather than PyYAML: the surface is two keys, the runner
    has no guaranteed YAML module, and a full parser would accept far more than this
    format should. Unrecognised keys are ignored; unrecognised *scope values* are
    reported by the caller rather than silently swallowed.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]

    data: dict[str, object] = {}
    current_list_key: str | None = None
    for raw in block.splitlines():
        line = raw.split("#", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        item = re.match(r"^\s*-\s*(.+?)\s*$", line)
        if item and current_list_key:
            data.setdefault(current_list_key, [])
            value = item.group(1).strip().strip("\"'")
            data[current_list_key].append(value)  # type: ignore[union-attr]
            continue
        kv = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", line)
        if kv:
            key, value = kv.group(1), kv.group(2).strip()
            if value:
                data[key] = value.strip("\"'")
                current_list_key = None
            else:
                current_list_key = key
                data.setdefault(key, [])
    return data


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a gitignore-style glob to a regex.

    `fnmatch` is not usable here: it treats `*` as matching across `/`, so
    `**/skills/**` and `*.py` would both match far more than intended. The three
    cases that matter are handled explicitly.
    """
    out = ["^"]
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if pattern.startswith("**/", i):
            out.append(r"(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(r".*")
            i += 2
        elif char == "*":
            out.append(r"[^/]*")
            i += 1
        elif char == "?":
            out.append(r"[^/]")
            i += 1
        else:
            out.append(re.escape(char))
            i += 1
    out.append("$")
    return re.compile("".join(out))


def load_rules() -> tuple[list[dict], list[dict], list[str]]:
    """Return (artifact_rules, conversation_rules, warnings).

    A rule with no `paths:` is always-on -- it binds every changed file. A rule with
    `paths:` binds only matching files. A rule scoped to conversation binds no file.
    An unrecognised scope is treated as artifact-scoped (the safe default: a rule that
    quietly stops being enforced is worse than one that produces a reviewable finding)
    and is reported, so nothing about the bucketing is silent.
    """
    artifact, conversation, warnings = [], [], []
    for path in sorted(RULES_DIR.glob("*.md")):
        meta = parse_frontmatter(path.read_text(encoding="utf-8"))
        scope = meta.get("scope")
        globs = [g for g in meta.get("paths", []) if isinstance(g, str)]
        entry = {
            "name": path.stem,
            "path": str(path.relative_to(REPO_ROOT)),
            "paths": globs,
            "always_on": not globs,
        }
        if scope == CONVERSATION_SCOPE:
            conversation.append(entry)
        else:
            if scope is not None:
                warnings.append(
                    f"rule '{path.stem}' declares unrecognised scope '{scope}' -- "
                    f"treating it as artifact-scoped; add handling or fix the value"
                )
            artifact.append(entry)
    return artifact, conversation, warnings


def bind_rules(changed: list[str], artifact_rules: list[dict]) -> dict[str, list[str]]:
    """Map each changed file to the rules that bind it."""
    compiled = {
        rule["name"]: [glob_to_regex(g) for g in rule["paths"]] for rule in artifact_rules
    }
    bindings: dict[str, list[str]] = {}
    for file_path in changed:
        bound = []
        for rule in artifact_rules:
            if rule["always_on"] or any(rx.match(file_path) for rx in compiled[rule["name"]]):
                bound.append(rule["name"])
        bindings[file_path] = bound
    return bindings


def main() -> int:
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    out_dir = Path(os.environ["PROSE_REVIEW_DIR"])
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- PR metadata, diff, changed files -----------------------------------------
    pr = json.loads(
        run("gh", "pr", "view", pr_number, "--repo", repo,
            "--json", "title,body,author,baseRefName,headRefOid,files")
    )
    (out_dir / "pr.json").write_text(json.dumps(pr, indent=2), encoding="utf-8")

    diff = run("gh", "pr", "diff", pr_number, "--repo", repo)
    (out_dir / "diff.patch").write_text(diff, encoding="utf-8")

    # `gh pr view --json files` caps at 100 files. The largest PR in this repo's history
    # is well under that, so this is a note rather than a fix -- but a >100-file PR would
    # be under-reviewed silently, so say so in the log rather than let it pass unseen.
    changed = [f["path"] for f in pr.get("files", [])]
    if len(changed) >= 100:
        print("::warning::100-file cap reached; some changed files were not reviewed")
    (out_dir / "changed-files.txt").write_text("\n".join(changed) + "\n", encoding="utf-8")

    # --- What previous rounds already said ----------------------------------------
    # Handed over so a finding can only be re-raised when something changed. Fetched
    # here rather than by the reviewer so it can be withheld until after its own blind
    # pass -- reading them first primes it toward re-finding what it found last time.
    prior = json.loads(
        run("gh", "api", f"repos/{repo}/pulls/{pr_number}/comments", "--paginate")
    )
    slim = [
        {
            "path": c.get("path"),
            "line": c.get("line") or c.get("original_line"),
            "body": c.get("body"),
            "created_at": c.get("created_at"),
            "author": (c.get("user") or {}).get("login"),
        }
        for c in prior
    ]
    (out_dir / "prior-comments.json").write_text(json.dumps(slim, indent=2), encoding="utf-8")

    # --- Which rules bind which file ----------------------------------------------
    artifact_rules, conversation_rules, warnings = load_rules()
    bindings = bind_rules(changed, artifact_rules)

    for warning in warnings:
        print(f"::warning::{warning}")

    manifest = {
        "pr": int(pr_number),
        "head_sha": pr.get("headRefOid"),
        "changed_files": changed,
        "bindings": bindings,
        "artifact_rules": [r["name"] for r in artifact_rules],
        "conversation_rules": [r["name"] for r in conversation_rules],
        "warnings": warnings,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # A readable rendering of the same data, because the reviewer reads prose better
    # than it reads JSON and this is the file it consults most.
    lines = [
        "# Rule bindings for this pull request",
        "",
        "Derived from each rule's own `paths:` frontmatter at run time. This is the",
        "complete and only set of rules you may cite against a changed file.",
        "",
        "## Per changed file",
        "",
    ]
    for file_path in changed:
        bound = bindings[file_path]
        lines.append(f"### `{file_path}`")
        if bound:
            for name in bound:
                lines.append(f"- `{name}` — `.claude/rules/{name}.md`")
        else:
            lines.append("- (no rules bind this file — do not cite any rule against it)")
        lines.append("")

    lines += [
        "## Rules that bind YOUR writing, not the diff",
        "",
        "These govern prose written to the operator. Never cite them against a changed",
        "file. Do apply them to the comments you write: name things in plain language",
        "rather than by bare handle, and never state a finding with more confidence than",
        "your evidence supports.",
        "",
    ]
    for rule in conversation_rules:
        lines.append(f"- `{rule['name']}` — `{rule['path']}`")
    if not conversation_rules:
        lines.append("- (none)")
    lines.append("")

    (out_dir / "rule-bindings.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"prepared {len(changed)} changed files, "
          f"{len(artifact_rules)} artifact rules, "
          f"{len(conversation_rules)} conversation rules, "
          f"{len(slim)} prior comments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
