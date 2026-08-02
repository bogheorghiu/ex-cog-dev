#!/usr/bin/env python3
"""Gather every input the prose reviewer needs, deterministically, before it runs.

Why this exists: the reviewer is given no shell and no network. It reads files and writes
files, and does nothing else. Everything it needs to see -- the diff, which files changed,
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

import hashlib
import json
import os
import re
import shutil
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


def paths_globs(value: object) -> list[str]:
    """Normalise a frontmatter `paths:` value to a list of glob strings.

    The parser returns a list for the block-sequence form, but the scalar form
    (`paths: "**/skills/**"`) and the bracketed inline form (`paths: [a, b]`) are
    equally valid YAML and arrive as a plain string. Iterating that string directly
    treats every CHARACTER as a glob — and a lone `*` matches any top-level path —
    so the rule would silently bind every changed root file and none of its intended
    targets. Silently is the operative defect: nothing warned, and this module's own
    comments call a rule that quietly stops being enforced the worse outcome.
    """
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("[") and text.endswith("]"):
            return [p.strip().strip("\"'") for p in text[1:-1].split(",") if p.strip()]
        return [text] if text else []
    if isinstance(value, list):
        return [g for g in value if isinstance(g, str)]
    return []


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
        globs = paths_globs(meta.get("paths", []))
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

    # --- The rules as THIS pull request defines them --------------------------------
    # This script runs on the PR head, but the review action then restores `.claude/`
    # from the base branch before the reviewer starts, because a PR head is untrusted
    # and `.claude/` can carry executable config -- hooks, MCP servers, agents.
    #
    # Rule *text* is not executable, so reverting it buys no safety while costing
    # correctness twice over: the reviewer would read the superseded version of every
    # rule the PR edits, and find no file at all for a rule it adds -- which the
    # validator downstream then reads as "cites a rule that does not exist" and drops,
    # losing a valid finding for a reason that is not the reviewer's fault. Rule edits
    # are a large share of this repo's pull requests, so that is precisely where the
    # reviewer would otherwise be least reliable.
    #
    # So the rules are copied out here, while the PR's version is still on disk, and
    # both the reviewer and the validator resolve rules from this snapshot instead of
    # from the reverted checkout. `bindings` above was already derived from the same
    # pre-revert tree, so this also stops the two from disagreeing.
    rules_snapshot = out_dir / "rules"
    rules_snapshot.mkdir(parents=True, exist_ok=True)
    for rule in artifact_rules + conversation_rules:
        shutil.copyfile(REPO_ROOT / rule["path"], rules_snapshot / f"{rule['name']}.md")

    # --- Both files the reviewer is required to produce -------------------------------
    # Seeded here, rather than left for the reviewer to create, so a reader can tell "the
    # reviewer wrote nothing" apart from "the reviewer found nothing" -- which a missing
    # file cannot express, since both arrive as an absence. Each seed's digest goes in the
    # manifest, so an untouched file is recognisable as untouched rather than reported as
    # a vanished one.
    #
    # refuted.json is seeded for a WEAKER reason, stated exactly because the strong one
    # does not hold. Its seed is `[]`, and the protocol tells the reviewer to write `[]`
    # when it refuted nothing -- the same two bytes -- so no digest can separate "skipped
    # stage 3" from "refuted nothing". findings.json's seed discriminates only because it
    # carries an empty `summary` that any real result must overwrite.
    #
    # What seeding refuted.json does buy is the weaker distinction: present-and-empty is
    # at least distinguishable from ABSENT, so a round that never reached stage 3 at all
    # no longer looks like a round that got there and found nothing to argue down. That
    # matters because this pull request exists so a PERSON can tell a well-calibrated
    # filter from a harsh one, and nothing downstream branches on the file.
    findings_seed = json.dumps({"summary": "", "findings": []}, indent=2)
    (out_dir / "findings.json").write_text(findings_seed, encoding="utf-8")
    refuted_seed = json.dumps([], indent=2)
    (out_dir / "refuted.json").write_text(refuted_seed, encoding="utf-8")

    manifest = {
        "pr": int(pr_number),
        "head_sha": pr.get("headRefOid"),
        "findings_seed_sha256": hashlib.sha256(findings_seed.encode("utf-8")).hexdigest(),
        "refuted_seed_sha256": hashlib.sha256(refuted_seed.encode("utf-8")).hexdigest(),
        "changed_files": changed,
        "bindings": bindings,
        "artifact_rules": [r["name"] for r in artifact_rules],
        "conversation_rules": [r["name"] for r in conversation_rules],
        # Where the validator resolves rule names. Carried in the manifest rather than
        # hardcoded in both scripts, so the two cannot drift to different directories.
        "rules_snapshot": str(rules_snapshot),
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
        "Read a rule's text from the path given below, NOT from `.claude/rules/` in the",
        "checkout. The checkout's copy was restored from the base branch before you",
        "started, so for any rule this pull request adds or edits it is the wrong text —",
        "or missing entirely. The paths below are a snapshot of the rules as this pull",
        "request defines them.",
        "",
        "## Per changed file",
        "",
    ]
    for file_path in changed:
        bound = bindings[file_path]
        lines.append(f"### `{file_path}`")
        if bound:
            for name in bound:
                lines.append(f"- `{name}` — `{rules_snapshot}/{name}.md`")
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
        lines.append(f"- `{rule['name']}` — `{rules_snapshot}/{rule['name']}.md`")
    if not conversation_rules:
        lines.append("- (none)")
    lines.append("")

    (out_dir / "rule-bindings.md").write_text("\n".join(lines), encoding="utf-8")

    # The reviewer must know the limits it will be held to BEFORE it writes, otherwise
    # every run wastes a repair round rediscovering them. Values come from the workflow
    # env, so changing a limit is a one-line workflow edit and the model, the validator
    # and this file cannot drift apart.
    limits = {
        "max_comment_chars": int(os.environ.get("PROSE_REVIEW_MAX_COMMENT_CHARS", "1200")),
        "max_quoted_lines": int(os.environ.get("PROSE_REVIEW_MAX_QUOTED_LINES", "6")),
        "repair": os.environ.get("PROSE_REVIEW_REPAIR_ENABLED", "true") == "true",
    }
    (out_dir / "constraints.md").write_text(
        "# Constraints your findings are held to\n\n"
        "These are enforced by a script after you write. A finding that breaks one is not\n"
        "posted, so it costs you the finding rather than merely earning a warning.\n\n"
        f"- **Comment length**: at most **{limits['max_comment_chars']} characters** for\n"
        f"  `summary` and `detail` combined.\n"
        f"- **Quoting**: at most **{limits['max_quoted_lines']} lines** of quoted source per\n"
        f"  finding. This job's logs and comments are publicly readable; quote the minimum\n"
        f"  that makes the point.\n"
        f"- **Issue and PR references**: write `issue #N` or `PR #N`, never a bare `#N`.\n"
        f"  GitHub renders a hovercard for a bare number on the web, but review comments\n"
        f"  also arrive as plain-text email, where there is no icon and no preview.\n"
        + (
            "- **Repair**: if findings are rejected you get **one** pass to fix and\n"
            "  resubmit them, with the exact reason for each; whatever still fails after\n"
            "  that is dropped. Spend it on findings that were genuinely misfiled, not on\n"
            "  arguing a rejection.\n"
            if limits["repair"] else
            "- **Repair**: none. A rejected finding is dropped immediately, so get it\n"
            "  right the first time.\n"
        ),
        encoding="utf-8")

    print(f"prepared {len(changed)} changed files, "
          f"{len(artifact_rules)} artifact rules, "
          f"{len(conversation_rules)} conversation rules, "
          f"{len(slim)} prior comments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
