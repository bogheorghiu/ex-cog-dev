#!/usr/bin/env python3
"""Structural linter for security-toolkit skills.

TEMPORARY SHAPE - re-architect this rather than growing it. The file is
triplicated across plugins and the copies are kept in step BY HAND, which
nothing enforces. Nothing about packaging justifies that: these linters ARE
delivered with the plugin - everything under a plugin directory reaches the
install cache - but they never RUN for a consumer, so it is execution, not
delivery, that is development-only. They were copied rather than shared, and
hand-sync is the price of that. The right shape is ONE linter parameterised per
plugin - a config naming the skills directory and which conventions apply. Do
not add a fourth copy; replace the mechanism. Tracked in issue #196.

Kept logic-identical to research-toolkit/skills/test_skill_structure.py (the
original; see issue #40/#42) and vasana-system/skills/test_skill_structure.py —
only the plugin name in the docstring and the printed banner differ. If you
change the logic in one copy, change it in all three. Markdown-only skills have
no executable logic to unit-test, but they DO have an interface: the SKILL.md
frontmatter is what the model reads to decide whether to fire, and the house
conventions are easy to break silently. This asserts the invariants that hold
across every security-toolkit skill, so a future skill that breaks one fails
the PR instead of shipping broken:

  - valid YAML frontmatter (the seed-question style invites the footgun below)
  - name == directory, kebab-case, <= 64 chars
  - description present and within Anthropic's 1024-char limit
  - exactly one `## Vasana` section (CLAUDE.md convention), counted outside fences

YAML validity prefers a real parse via PyYAML when importable, and ALWAYS also
runs a stdlib check for the one footgun the house seed-question style invites: a
quoted scalar followed by trailing text (`description: "...?" - ...`), which YAML
reads as a sequence entry and rejects. The stdlib fallback covers only that
shape; the CI step runs this under `uv run --with pyyaml` so the full parser
catches the rest (including the unquoted `key: ... : ...` variant). Exits
non-zero on failure.
"""

import re
import sys
from pathlib import Path

# The status marks below are Unicode; under a non-UTF-8 stdout locale (e.g.
# LC_ALL=C) a bare print would crash with UnicodeEncodeError before any check
# runs. Force UTF-8 where the runtime allows it.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Anthropic's documented frontmatter limits (platform.claude.com Agent Skills).
NAME_MAX = 64
DESC_MAX = 1024
# Soft floor: every shipped description is >= 250 chars; 40 catches an empty or
# stub description without coupling the test to the current house verbosity.
DESC_MIN = 40
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# The canonical `## Vasana` heading, anchored so other `## Vasana …` headings
# (none today, but guarded) don't count.
SELFREP_RE = re.compile(r"^##\s+Vasana\s*$", re.M)
DEPRECATED_SELFREP_RE = re.compile(r"^##\s+Vasana\s+Propagation\s*$", re.M)
# A bare quoted scalar with trailing non-comment text — invalid YAML, and the
# exact shape the seed-question descriptions regressed into.
QUOTED_WITH_TRAILING = re.compile(r'^([A-Za-z_][\w-]*):[ \t]*(["\']).*?\2(.+)$', re.M)

_SKILLS_DIR = Path(__file__).resolve().parent

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


def frontmatter_block(text):
    """Return the YAML frontmatter between the opening and closing `---`, else None."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else None


def strip_fenced_code(text):
    """Return `text` with fenced code blocks (``` or ~~~) removed.

    Counted line-by-line, toggling on lines whose first non-space content opens a
    fence — so a skill that *shows* the section inside a ```markdown``` template
    can't trip a false 'duplicate ## Vasana'. Inline backticks (never line-start)
    are ignored, and it stays well-defined under an unbalanced fence count.
    """
    out, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _unquote(value):
    """Strip a single matched pair of surrounding quotes (only when both ends match).

    `.strip("\"'")` would chop a leading quote off `"seed?" - trailing` and leave
    the inner quote dangling, mis-measuring the value; this only unwraps a true
    `"..."` / '...' scalar.
    """
    v = value.strip()
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        return v[1:-1]
    return v


def parse_frontmatter(fm):
    """Extract (name, description) from a frontmatter block.

    Hand-rolled because the stdlib fallback path has no YAML parser. Handles
    plain, quoted, and folded/literal block scalars (>- , > , | , |-) — the forms
    the house skills actually use.
    """
    nm = re.search(r"^name:[ \t]*(.+?)[ \t]*$", fm, re.M)
    name = _unquote(nm.group(1)) if nm else None

    # Capture from `description:` to the next top-level key (e.g. changelog:) or
    # end of block. Indented block-scalar lines start with whitespace, so they
    # never match the `\n<key>:` boundary.
    dm = re.search(r"^description:[ \t]*(.*?)(?:\n[A-Za-z_][\w-]*:|\Z)", fm, re.S | re.M)
    desc = None
    if dm:
        raw = dm.group(1).strip()
        raw = re.sub(r"^[>|][+-]?[ \t]*\n?", "", raw)  # drop block-scalar indicator
        desc = _unquote(re.sub(r"\s+", " ", raw).strip())

    return name, desc


def frontmatter_keys(fm):
    """Return the set of top-level keys in a frontmatter block.

    Lines starting with whitespace are block-scalar continuations and never
    count; only `key:` at column 0 does. Used by the PORTABILITY.md R1 check:
    skill frontmatter carries name + description only, so CC-only composition
    keys (`skills:`, `tools:`, `model:`) can never hide in a SKILL.md.
    """
    keys = set()
    for line in fm.splitlines():
        if line[:1] in (" ", "\t"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):", line)
        if m:
            keys.add(m.group(1))
    return keys


def yaml_validity_error(fm):
    """Return an error string if the frontmatter isn't valid YAML, else None.

    Prefers a real parse via PyYAML; always also runs the stdlib footgun check so
    a dependency-free run still catches the `key: "..." - trailing` shape. The
    fallback covers only that pattern, not every YAML error — PyYAML covers the
    rest where it is installed (the CI step ensures it is).
    """
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    if yaml is not None:
        try:
            data = yaml.safe_load(fm)
        except Exception as e:  # report any parse failure
            return f"YAML parse error: {str(e).splitlines()[0]}"
        if not isinstance(data, dict):
            return "frontmatter is not a YAML mapping"
        return None
    for m in QUOTED_WITH_TRAILING.finditer(fm):
        trailing = m.group(3).strip()
        if trailing and not trailing.startswith("#"):
            return f"key '{m.group(1)}': quoted value followed by trailing text"
    return None


skill_files = sorted(_SKILLS_DIR.glob("*/SKILL.md"))

print(f"\nLinting {len(skill_files)} security-toolkit skills under {_SKILLS_DIR.name}/ ...")
check("glob found skills to lint", len(skill_files) > 0)

for path in skill_files:
    slug = path.parent.name
    print(f"\n{slug}")
    text = path.read_text(encoding="utf-8")

    fm = frontmatter_block(text)
    check("has a frontmatter block", fm is not None)
    if fm is None:
        continue

    yaml_err = yaml_validity_error(fm)
    check(f"frontmatter is valid YAML{'' if not yaml_err else f' — {yaml_err}'}", yaml_err is None)
    if yaml_err:
        # Downstream checks read the frontmatter as structured data; on malformed
        # YAML their results are meaningless noise. Report and move on.
        continue

    name, desc = parse_frontmatter(fm)
    check("name + description both present", bool(name) and bool(desc))
    if not name or not desc:
        continue

    # PORTABILITY.md R1: skill frontmatter carries name + description only.
    # CC-only composition keys (skills:, tools:, model:) belong in agent
    # files, never SKILL.md — a converter must be able to render frontmatter
    # mechanically, and anything else is a harness assumption in the one
    # place the model reads every turn.
    extra_keys = frontmatter_keys(fm) - {"name", "description"}
    check(
        f"frontmatter keys within {{name, description}}{'' if not extra_keys else f' — extra: {sorted(extra_keys)}'}",
        not extra_keys,
    )

    check(f"name matches directory ('{name}' == '{slug}')", name == slug)
    check(f"name is kebab-case and <= {NAME_MAX} chars", bool(NAME_RE.match(name)) and len(name) <= NAME_MAX)
    check(f"description length {len(desc)} within [{DESC_MIN}, {DESC_MAX}]", DESC_MIN <= len(desc) <= DESC_MAX)
    # CLAUDE.md convention: exactly one `## Vasana` section, counted outside fenced
    # code so a template example doesn't inflate it.
    body = strip_fenced_code(text)
    check("exactly one '## Vasana' section", len(SELFREP_RE.findall(body)) == 1)
    check("no deprecated '## Vasana Propagation' heading", len(DEPRECATED_SELFREP_RE.findall(body)) == 0)


if failures == 0:
    print("\n✅ All skill-structure checks passed!")
else:
    print(f"\n❌ {failures} check(s) failed.")

raise SystemExit(1 if failures else 0)
