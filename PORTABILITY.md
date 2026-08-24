# PORTABILITY.md — converting these plugins to other harnesses

**Status: R1 is enforced in CI (see Enforcement); R2–R8 are proposed for review.**

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

## R1 — Skill frontmatter stays within the portable surface

- Skill frontmatter uses the Agent Skills spec's six fields — `name`,
  `description`, `license`, `compatibility`, `metadata`, `allowed-tools` —
  plus documented per-harness keys that only that harness reads at root level
  (Claude Code's extension set; tracked in issue #234).
- It never carries agent-definition composition keys; those belong in agent
  files, and the linter rejects them at PR time.
- Description: trigger self-contained in the first sentence (Hermes truncates
  its skill index at ~57 characters) and ≤1024 characters (the spec limit,
  already enforced by the linter).

Why: frontmatter is what every harness reads every turn, so it is the one
surface that must stay portable. The six spec fields are the shared baseline.
Harness-specific keys stay at root level where their harness reads them —
moving a root-level key under `metadata` hides it from the harness that needs
it, so `metadata` is not a place to relocate Claude's keys; it is only a home
for keys a harness genuinely reads from there (e.g. Hermes' `metadata.hermes.*`).

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

## R6 — Agent composition declared in the body (portable), not only frontmatter

No agent in this repo currently uses `skills:` frontmatter; if one ever does
(Claude composes from it), also list the same skills as a plain ordered list in
the agent body, so another harness can generate an equivalent delegation
wrapper from the body alone.

Why: agent composition has no shared format across harnesses (the mapping is
tracked in issue #233); a body-side list keeps agent conversion mechanical even when
the frontmatter form is harness-specific.

## R7 — Version the plugin; ports pin to it

- Keep the existing per-plugin version bump discipline (`plugin.json`
  version). A port pins `pin_plugin_version`, so "update from source" keys
  on a semantic version, not a raw SHA.

## R8 — Shipped content never references dev scaffolding

- `CLAUDE.md`, `.claude/rules/`, workflows, githooks, CI = repo governance,
  not plugin content; a shipped skill/hook/command never reads or imports them.
- Co-located dev files (e.g. the `test_skill_structure.py` linters under
  `skills/`) may ship inert — they never run for a consumer — and that is
  tolerated; the rule is about *referencing*, not *presence*.
- Why: the converter needs a deterministic "ship boundary" to scan, and a
  shipped artifact that reads governance files breaks that boundary.

## What these rules do NOT do

- They do not restrict agents, hooks, commands, or any Claude feature.
- They do not ask for dual-maintained versions of anything in another format.
- They do not make the repo "harness-agnostic" by dropping CC idioms — the
  idioms stay, in designated places.

## Enforcement

- **R1 key check (implemented):** every `SKILL.md` frontmatter in
  research-toolkit, security-toolkit and vasana-system is checked for
  agent-definition composition keys, which are rejected at PR time.
  makers-toolkit ships skills but carries no linter twin (issue #196 caps the
  copies at three), so its skills are not behind this gate today. The
  portable baseline (the spec's six fields) is documented above, not enumerated
  in code — see issue #234 for the full surface discussion.
- **R4 / R6 (proposed, not implemented):** path and composition checks are
  listed for future work; neither is enforced today.

Per the existing convention (issue #196), do NOT add a fourth linter copy —
extend the three twins, and if this grows, replace the mechanism with one
parameterized linter.

## Related

- `.claude/rules/skill-design.md`, `shipped-skill-config.md` — the repo's
  existing skill conventions (this file complements, does not replace them)
- `docs/PORTABILITY-TODO.md` (research-toolkit) — earlier portability notes
