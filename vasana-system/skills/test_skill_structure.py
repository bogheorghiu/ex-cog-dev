#!/usr/bin/env python3
"""Structural linter for vasana-system skills.

Lifted from research-toolkit/skills/test_skill_structure.py (issue #40) and
calibrated to vasana-system's conventions (issue #41). Markdown-only skills have
no executable logic to unit-test, but they DO have an interface: the SKILL.md
frontmatter is what the model reads to decide whether to fire, and the house
conventions are easy to break silently. This asserts the invariants that hold
across every vasana-system skill, so a future skill that breaks one fails the PR
instead of shipping broken:

  - valid YAML frontmatter (the seed-question style invites the footgun below)
  - name == directory, kebab-case, <= 64 chars
  - description present and within Anthropic's 1024-char limit
  - a self-replication section, per CLAUDE.md's Self-Replication Principle

Two deltas from the research-toolkit original, because vasana-system's skills
genuinely differ (verified against the shipped tree, not assumed):

  - Self-replication heading: research-toolkit uses exactly one `## Vasana`.
    vasana-system ships the same section under two heading variants — `## Vasana`
    and `## Vasana Propagation` — and the teaching skill `record-pattern` legibly
    repeats it. So the invariant here is "at least one" of either variant.
  - `pattern-library` ships a 1127-char description (> 1024). That's a real
    latent bug, but a different one from #41's invalid-YAML scope, and trimming
    it changes what the model reads to fire that skill — an editorial call, not a
    mechanical reformat. It is quarantined as a known exception (warned, not
    failed) so the bound stays hard for every other and future skill, pending a
    separate owner decision.

YAML validity prefers a real parse via PyYAML when importable, and ALWAYS also
runs a stdlib check for the one footgun the house seed-question style invites: a
quoted scalar followed by trailing text (`description: "...?" - ...`), which YAML
reads as a sequence entry and rejects. The stdlib fallback covers only that
shape; the CI step runs this under `uv run --with pyyaml`, so the full parser
catches the rest (including the unquoted `key: ... : ...` variant). Exits
non-zero on failure.
"""

import re
from pathlib import Path

# Anthropic's documented frontmatter limits (platform.claude.com Agent Skills).
NAME_MAX = 64
DESC_MAX = 1024
# Soft floor: every shipped description is >= 250 chars; 40 catches an empty or
# stub description without coupling the test to the current house verbosity.
DESC_MIN = 40
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# A self-replication heading: `## Vasana` or `## Vasana Propagation` (CLAUDE.md
# Self-Replication Principle). Anchored so `## Testing This Vasana`,
# `## Behavioral Patterns (Vasanas)`, etc. do not count.
SELFREP_RE = re.compile(r"^##\s+Vasana(?:\s+Propagation)?\s*$", re.M)
# A bare quoted scalar with trailing non-comment text — invalid YAML, and one of
# the shapes the seed-question descriptions regressed into.
QUOTED_WITH_TRAILING = re.compile(r'^([A-Za-z_][\w-]*):[ \t]*(["\']).*?\2(.+)$', re.M)
# Pre-existing description overflow (> DESC_MAX), out of #41's invalid-YAML scope.
# Quarantined so the upper bound stays hard for every other/future skill.
KNOWN_OVERLONG = {"pattern-library"}

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

print(f"\nLinting {len(skill_files)} vasana-system skills under {_SKILLS_DIR.name}/ ...")
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

    name, desc = parse_frontmatter(fm)
    check("name + description both present", bool(name) and bool(desc))
    if not name or not desc:
        continue

    check(f"name matches directory ('{name}' == '{slug}')", name == slug)
    check(f"name is kebab-case and <= {NAME_MAX} chars", bool(NAME_RE.match(name)) and len(name) <= NAME_MAX)
    check(f"description length {len(desc)} >= {DESC_MIN}", len(desc) >= DESC_MIN)
    if slug in KNOWN_OVERLONG and len(desc) > DESC_MAX:
        print(f"   ⚠ KNOWN: description length {len(desc)} > {DESC_MAX} — pre-existing "
              f"pattern-library overflow, out of #41 scope; bound stays hard elsewhere.")
    else:
        check(f"description length {len(desc)} <= {DESC_MAX}", len(desc) <= DESC_MAX)
    # CLAUDE.md Self-Replication Principle: every skill carries the self-replication
    # section (shipped as `## Vasana` or `## Vasana Propagation`).
    selfrep = len(SELFREP_RE.findall(text))
    check("has a self-replication section ('## Vasana' / '## Vasana Propagation')", selfrep >= 1)


if failures == 0:
    print("\n✅ All skill-structure checks passed!")
else:
    print(f"\n❌ {failures} check(s) failed.")

raise SystemExit(1 if failures else 0)
