# PORTABILITY.md — converting these plugins to other harnesses

**Status: PROPOSAL — conventions for review, not yet enforced in CI.**

**Created:** 2026-08-07
**Why this file exists:** the plugins in this marketplace are Claude Code
plugins, but the skills and logic inside them are portable to other agent
harnesses (Hermes, Codex, etc.). The conversion is cheap when the portable
parts are shaped portably; it is expensive when Claude-specific constructs
leak into places the model reads every turn. These conventions keep Claude
features fully usable — nothing here forbids a Claude idiom — while making
conversion mechanical instead of hand-ported.

The test that any convention must pass: **a converter should be able to
render this plugin for another harness with deterministic rules, not per-file
human judgment.** Each rule below exists because a specific conversion cost
was measured or anticipated.

## R1 — Skill frontmatter stays harness-agnostic: name + description only

- CC-only frontmatter keys (`skills:`, `tools:`, `model:`, `allowed-tools:`)
  never appear in `SKILL.md` frontmatter. They belong in agent files, where
  CC composition lives.
- Description: trigger self-contained in the first ~57 characters (both
  harnesses truncate the skill index there) and ≤1024 characters (Hermes
  hard cap; the existing linter already enforces Anthropic's 1024).

Why: frontmatter is what the model reads every turn. It is the part that
must stay portable. The repo's 22 research-toolkit skills already comply
(verified 2026-08-07); this rule keeps it true. Enforced by the R1 key check
in each plugin's `test_skill_structure.py`.

## R2 — Skill content is whole-tree (SKILL.md + references/ + scripts/)

- No `.skill` zips, no flat single-file skills with everything inline.
- Both harnesses support the whole-tree shape natively; the converter copies
  the tree and rewrites references.

## R3 — Hook logic lives in a pure engine; the wrapper is the only CC seam

- The hook's decision logic is a standalone program (e.g. Python) that reads
  environment variables and writes structured output — it never touches
  Claude APIs, never assumes a Claude-specific payload beyond stdin/env.
- The hook script registered in `hooks.json` is a thin shim translating the
  Claude hook invocation into the engine's args.

Why: this is the single highest-leverage convention. A pure engine ports by
renaming events and env vars; an engine that embeds Claude assumptions must
be rewritten. The research-toolkit firing filter already follows this shape;
keep it.

## R4 — Paths resolve through one documented root var

- Every path in scripts and skills resolves through `${CLAUDE_PLUGIN_ROOT}`
  (or an equivalent documented root var), never a hardcoded relative
  assumption.
- Why: path rewriting is the most common silent breakage in ports. One root
  var = one rewrite rule.

## R5 — userConfig options reach code as documented env vars

- `plugin.json` userConfig options are read by hooks/scripts via
  `CLAUDE_PLUGIN_OPTION_*` env vars (already true for the firing-filter
  master switch). Keep option names stable and documented in the plugin
  README, since both harnesses export them as env.
- Why: stable option names = one config mapping in the port, forever.

## R6 — Agents declare composition twice: frontmatter (CC) + body (portable)

- Keep `skills:` in agent frontmatter — Claude composes from it.
- ALSO list the same skills as a plain ordered list in the agent body (e.g.
  a `## Composition` section), so another harness can generate an equivalent
  delegation wrapper from the body alone.

Why: `skills:` frontmatter is the ONE construct in this repo with no direct
analog in other harnesses. A body-side declaration makes agent conversion
mechanical instead of hand-written, and keeps the body authoritative for
humans reading the agent.

## R7 — Version the plugin; ports pin to it

- Keep the existing per-plugin version bump discipline (`plugin.json`
  version). A port pins `pin_plugin_version`, so "update from source" keys
  on a semantic version, not a raw SHA.

## R8 — Keep dev scaffolding out of the shipped surface

- `CLAUDE.md`, `.claude/rules/`, workflows, githooks, CI = repo governance,
  NOT plugin content. Never referenced from a shipped skill/hook/command.
- Why: the converter must have a clean "ship boundary" to scan. The renderer
  knows the six shipped part types (skills, MCP, hooks, commands, agents,
  userConfig) and stops if it sees anything else; scaffolding inside the
  shipped surface breaks that scan.

## What these rules do NOT do

- They do not restrict agents, hooks, commands, or any Claude feature.
- They do not ask for dual-maintained versions of anything in another format.
- They do not make the repo "harness-agnostic" by dropping CC idioms — the
  idioms stay, in designated places.

## Enforcement (proposed)

Extend each plugin's `test_skill_structure.py` (they are deliberate twins —
keep logic identical, only the plugin name differs) with:

- **R1 key check:** frontmatter keys ⊆ {name, description} for every
  SKILL.md. Catches CC-only keys and stray keys at PR time.
- **R4 path check:** no hardcoded absolute paths in skill bodies/scripts
  (scan for `C:\`, `/home/`, `/Users/`).
- **R6 composition check:** every `agents/*.md` with a `skills:` frontmatter
  list also has a `## Composition` body section naming the same skills.

Per the existing convention (issue #196), do NOT add a fourth linter copy —
extend the three twins, and if this grows, replace the mechanism with one
parameterized linter.

## Related

- `.claude/rules/skill-design.md`, `shipped-skill-config.md` — the repo's
  existing skill conventions (this file complements, does not replace them)
- `docs/PORTABILITY-TODO.md` (research-toolkit) — earlier portability notes
