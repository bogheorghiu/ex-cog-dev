#!/usr/bin/env python3
"""Parse every plugin agent's YAML frontmatter and fail if any of it is unloadable.

Why this exists, and why parsing rather than reading is the whole point: an agent whose
frontmatter does not parse still *appears* in the harness's agent list, so nothing looks
broken - but every field is gone. Its `tools:` allowlist, its `model:`, its `skills:`
preload and its `description:` (the interface the main loop matches on to delegate at all)
are silently discarded. There is no error a reader would see and no failing test, because
until now nothing in CI parsed these files. Three of the four research-toolkit agents
shipped in exactly that state and it was found only by watching a live spawn come back
without its preloaded skill.

The shape that caused it is worth naming, because it reads as correct:

    description: "What here is NOT actually working?" - Adversarial verification agent...

YAML ends the double-quoted scalar at the closing quote, then meets ` - ...` and reports a
sequence entry where none may appear. Writing the same text as a folded `>-` block scalar
carries the quotes as ordinary characters and parses. This checker is what makes that
distinction visible before a merge instead of after a consumer's agent misbehaves.

Run from the repo root:  python3 .github/scripts/check_agent_frontmatter.py
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by the CI env, not the suite
    sys.exit(
        "FATAL: PyYAML is required.\n"
        "A stdlib approximation would accept some of the very constructs this checker "
        "exists to reject, and a checker that cannot fail is worse than none.\n"
        "Run it as: uv run --no-project --with pyyaml python "
        ".github/scripts/check_agent_frontmatter.py"
    )

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
KEBAB = re.compile(r"\A[a-z0-9]+(-[a-z0-9]+)*\Z")
LIST_FIELDS = ("tools", "skills", "disallowedTools")


def plugin_dirs(root: Path):
    """Derive the plugin set from the tree, so a new plugin is covered without an edit here.

    The manifest sits at <plugin>/.claude-plugin/plugin.json, so the plugin root is two
    levels up from the file, not one.
    """
    return sorted(p.parent.parent for p in root.glob("*/.claude-plugin/plugin.json"))


def check_file(path: Path, repo_root: Path):
    """Return a list of human-readable problems with this agent file (empty == clean)."""
    rel = path.relative_to(repo_root)
    text = path.read_text(encoding="utf-8")

    match = FRONTMATTER.match(text)
    if not match:
        return [f"{rel}: no YAML frontmatter block at the top of the file"]

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        detail = str(exc).splitlines()[0]
        return [
            f"{rel}: frontmatter does not parse as YAML - {detail}\n"
            f"    Every field is silently dropped when this happens. If the description "
            f"mixes quotes with trailing text, rewrite it as a folded block scalar:\n"
            f"        description: >-\n"
            f"          \"Some quoted question?\" - the rest of the sentence..."
        ]

    if not isinstance(data, dict):
        return [f"{rel}: frontmatter parsed as {type(data).__name__}, expected a mapping"]

    problems = []

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        problems.append(f"{rel}: missing or empty required field 'name'")
    else:
        if ":" in name:
            problems.append(
                f"{rel}: name {name!r} contains ':', which is reserved for plugin-scoped "
                f"identifiers - Claude Code refuses to load the file"
            )
        elif not KEBAB.match(name):
            problems.append(f"{rel}: name {name!r} is not kebab-case")
        if name != path.stem:
            problems.append(f"{rel}: name {name!r} does not match filename stem {path.stem!r}")

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        problems.append(
            f"{rel}: missing or empty required field 'description' - this is the interface "
            f"the main loop matches on, so an agent without one is unreachable by delegation"
        )

    for field in LIST_FIELDS:
        if field not in data:
            continue
        value = data[field]
        if isinstance(value, str):
            continue  # the comma-separated string form is documented and valid
        if not isinstance(value, list) or not value:
            problems.append(f"{rel}: '{field}' must be a non-empty list (or a string)")
            continue
        for entry in value:
            if not isinstance(entry, str) or not entry.strip():
                problems.append(f"{rel}: '{field}' contains a non-string or empty entry: {entry!r}")

    return problems


def main(argv):
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()

    agent_files = []
    for plugin in plugin_dirs(repo_root):
        agent_files.extend(sorted((plugin / "agents").glob("*.md")))

    if not agent_files:
        # A silent zero-file pass is the failure mode this whole file guards against.
        print(f"FAIL: found no agent files under {repo_root}/*/agents/ - checker is not looking "
              f"where the agents live")
        return 1

    problems = []
    for path in agent_files:
        found = check_file(path, repo_root)
        problems.extend(found)
        print(f"{'FAIL' if found else '  ok'}  {path.relative_to(repo_root)}")

    if problems:
        print(f"\n{len(problems)} problem(s) across {len(agent_files)} agent file(s):\n")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(f"\nAll {len(agent_files)} agent frontmatter blocks parse and carry their required fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
