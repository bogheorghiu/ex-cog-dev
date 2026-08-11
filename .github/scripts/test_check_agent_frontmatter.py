#!/usr/bin/env python3
"""Suite for check_agent_frontmatter.py.

Its first duty is to show the checker FAILS on the real defect, not merely that it passes
on the current tree. The `quoted_then_trailing` fixture is a verbatim reduction of the
description line that shipped in three research-toolkit agents; a checker that accepts it
would restore the exact silence this guard was written to end.

Run from the repo root:
    uv run --no-project --with pyyaml python .github/scripts/test_check_agent_frontmatter.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_agent_frontmatter as guard  # noqa: E402

FAILURES = []


def check(label, condition):
    print(f"{'  ok' if condition else 'FAIL'}  {label}")
    if not condition:
        FAILURES.append(label)


def build_repo(root: Path, agents: dict):
    """Write a throwaway one-plugin repo whose agents/ holds `agents` (name -> file text)."""
    plugin = root / "demo-plugin"
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".claude-plugin" / "plugin.json").write_text(
        '{"name": "demo-plugin", "version": "0.0.1"}', encoding="utf-8"
    )
    (plugin / "agents").mkdir()
    for filename, body in agents.items():
        (plugin / "agents" / filename).write_text(body, encoding="utf-8")
    return root


GOOD = """---
name: good-agent
description: >-
  "Is this actually working?" - a well-formed agent whose description mixes a quoted
  question with trailing prose, written as a folded scalar so it parses.
tools: [Read, Grep]
skills: [some-skill]
---

Body.
"""

# The defect this guard exists for, reduced from research-toolkit/agents/falsifier.md.
QUOTED_THEN_TRAILING = """---
name: bad-agent
description: "What here is NOT actually working?" - Adversarial verification agent.
tools: [Read, Grep]
---

Body.
"""

NO_FRONTMATTER = "# Just a heading\n\nBody with no frontmatter at all.\n"

MISSING_DESCRIPTION = """---
name: bare-agent
tools: [Read]
---

Body.
"""

NAME_MISMATCH = """---
name: not-the-filename
description: A description long enough to be meaningful for the checker.
---

Body.
"""

COLON_IN_NAME = """---
name: plugin:scoped-agent
description: A description long enough to be meaningful for the checker.
---

Body.
"""

BAD_TOOLS = """---
name: bad-tools-agent
description: A description long enough to be meaningful for the checker.
tools: []
---

Body.
"""


def run(agents: dict):
    with tempfile.TemporaryDirectory() as tmp:
        root = build_repo(Path(tmp), agents)
        return guard.main(["check_agent_frontmatter.py", str(root)])


print("== the checker must REJECT each of these ==")
check("quoted-scalar-then-trailing-text is rejected (the shipped defect)",
      run({"bad-agent.md": QUOTED_THEN_TRAILING}) != 0)
check("a file with no frontmatter is rejected",
      run({"no-frontmatter.md": NO_FRONTMATTER}) != 0)
check("a missing description is rejected",
      run({"bare-agent.md": MISSING_DESCRIPTION}) != 0)
check("a name that disagrees with the filename is rejected",
      run({"name-mismatch.md": NAME_MISMATCH}) != 0)
check("a ':' in the name is rejected",
      run({"colon-in-name.md": COLON_IN_NAME}) != 0)
check("an empty tools list is rejected",
      run({"bad-tools-agent.md": BAD_TOOLS}) != 0)
check("one bad agent fails the run even when a good one sits beside it",
      run({"good-agent.md": GOOD, "bad-agent.md": QUOTED_THEN_TRAILING}) != 0)

print("\n== the checker must ACCEPT this ==")
check("a well-formed agent passes", run({"good-agent.md": GOOD}) == 0)

print("\n== the checker must not pass vacuously ==")
with tempfile.TemporaryDirectory() as tmp:
    empty = Path(tmp)
    check("a tree with no agents at all fails rather than reporting success",
          guard.main(["check_agent_frontmatter.py", str(empty)]) != 0)

print("\n== the live repo must be clean ==")
repo_root = Path(__file__).resolve().parents[2]
check("every agent in this repo parses and carries its required fields",
      guard.main(["check_agent_frontmatter.py", str(repo_root)]) == 0)

if FAILURES:
    print(f"\n{len(FAILURES)} check(s) failed:")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)

print("\nAll agent-frontmatter guard checks passed.")
