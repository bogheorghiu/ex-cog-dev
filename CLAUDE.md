# CLAUDE.md — ex-cog-dev

Notes for any Claude Code (or human) session working in this repo.

## Rule 1 — State the why (the repo's governing rule)

Every decision or instruction — yours or mine — states its rationale. Write
explanation-first: a choice with no "why" is incomplete, because a decision without
its reasoning can't be evaluated, reproduced, or safely revised later. The rationale
is part of the deliverable, not decoration.

This is the **governing** rule the rest of the repo presupposes — the `.claude/rules/`
conventions and the plugins' own command-shaped instructions all assume it. It's also
what keeps "command-shaped" compatible with `intrinsic-prompt-design` (give the model
real reasons, don't just order it more politely): a directive that leads with its why
is a *reasoned* command, not bare obedience. And forcing the justification next to the
claim makes hedge-vs-reasoning and claim-vs-evidence mismatches visible before they
ship — the discipline `.claude/rules/verify-claims.md` builds on.

## What's here

Claude Code plugins distributed via the `ex-cog-dev` marketplace. Each plugin is a top-level directory containing a `.claude-plugin/plugin.json`; `.claude-plugin/marketplace.json` is the manifest of what ships.

**Read those, not a list here.** This file used to carry an inventory of the plugins with their skills and MCP servers, and it drifted — a hand-kept catalog of what exists has no way to notice when the tree moves past it, so it goes stale silently while still reading as authoritative. The directory listing cannot rot this way; it *is* the thing.

Some plugins ship MCP servers, launched by consumers via `uvx --from git+https://github.com/bogheorghiu/ex-cog-dev#subdirectory=<path> <command>` URLs in that plugin's `.mcp.json`. Every uvx cold-start fetches the latest source from this repo, so a bad commit propagates to all consumers within ~24h (uvx cache TTL).

## Version bumping (REQUIRED)

When you change **any** file under **any** plugin directory (a top-level directory with a `.claude-plugin/plugin.json`), you **must** bump that plugin's `.claude-plugin/plugin.json` `version` in the same change, before committing. That version is what `claude plugin update` keys on — a change shipped without a bump is silently skipped by installs (this has regressed before).

- Patch (`x.y.Z+1`) for fixes/docs, minor (`x.Y+1.0`) for new features — your judgment.
- Genuine no-op (e.g. a typo in an unshipped note)? Bypass with `[skip-version-bump]` in the PR title or the `skip-version-bump` label.
- Self-check before pushing — the same guard CI runs on every PR:
  ```bash
  python3 .github/scripts/check_version_bump.py origin/main HEAD
  ```
  Enforced by `.github/workflows/version-bump-guard.yml`; logic + tests in `.github/scripts/`.

## Tracked JSON is ASCII-only (REQUIRED)

Never put a non-ASCII character in a tracked `.json` file — no em-dashes, no curly quotes, no arrows. Use `-` where you'd reach for an em-dash. Typography belongs in READMEs and skills, which are prose; manifests are machine-facing.

The reason is a silent rewrite this repo has already shipped twice. A manifest's `description` is prose, so it attracts typographic characters — and a session bumping a version with `json.load` → edit one field → `json.dump` re-emits **every** non-ASCII character in the file as a `\uXXXX` escape, because Python's `ensure_ascii` defaults to `True`. Lines nobody touched come back rewritten.

Nothing catches it by accident: the tool exits 0, the file still parses, tests still pass, and escaped and raw are the **same JSON value** (jq, Node and Python all agree), so no consumer can tell. Only the bytes differ. Keeping the file ASCII removes the input rather than detecting the output — with nothing non-ASCII present, the rewrite cannot happen.

- Self-check, and the fixer for em-dashes specifically:
  ```bash
  python3 .github/scripts/check_json_ascii.py        # report + fail
  python3 .github/scripts/check_json_ascii.py --fix  # substitute em-dashes only
  ```
- Any **other** non-ASCII character is reported, never auto-replaced — that's a judgment call for the operator.
- Fix by editing the character **in place**. Never "fix" it by piping the file through a JSON formatter: a whole-file rewrite to correct one character is the defect itself.
- Enforced by `.github/workflows/json-ascii-guard.yml`.

This applies to JSON only. Markdown keeps its em-dashes — nothing parses and re-serialises Markdown, so the failure can't occur there.

## Duplicated test utilities are deliberate — but check before you propagate

Some plugins carry their own copy of a structural linter for their skills (`skills/test_skill_structure.py`). The duplication is intentional rather than an oversight: a plugin is installed on its own, and each plugin defines its own skill conventions, so the linter ships inside the plugin it lints.

**Do not assume the copies are interchangeable — read the copy's own docstring first.** Some are true twins, identical apart from the plugin name in a printed banner, and a logic fix belongs in every one of them. At least one is a deliberate fork, calibrated to conventions its own plugin has and the others don't; propagating a change into it blindly would silently delete checks. Each copy's docstring states which it is and why.

CI runs every copy, so the failure cuts both ways: fix one twin and not the other and a gate keeps passing on stale logic in a plugin nobody thought they had touched; overwrite a fork with its "twin" and you drop the checks that fork exists for.

## Release / publish

Every PR to `main`, and every push to `main`, runs the guards in `.github/workflows/`.

**They are not listed here, deliberately.** The directory is the list, and each workflow opens with a header comment saying what it catches and why it exists — so the tree already answers both "which gates run?" and "what is this one for?". A second copy in this file could only drift out of step with it, and did: it claimed "three" while six were running. Where a gate carries a convention you must follow *before* pushing, that convention lives in its own section above, next to the rule it enforces, with the local self-check command.

Green `main` is the pre-publish bar.

**`ex-cog-dev` is the public, canonical marketplace — consumers add and install from it directly.** A merge to `main` *is* the release; there is no second promotion step. (An older split kept a separate public `bogheorghiu/ex-cog` repo, with `ex-cog-dev` as the dev source and a dev→`ex-cog` sync as the release gate — issue #38; that split is retired in favour of this single public repo, and the legacy `ex-cog` repo is being wound down.)

That makes `main` directly load-bearing for everyone: each plugin's `.mcp.json` `uvx --from` URL fetches `ex-cog-dev` HEAD of `main`, so a bad commit reaches every consumer within ~24h (uvx cache TTL) or immediately on `uvx --refresh`. No mirror insulates the public from `main` — green CI is the only gate.

## Development rules (`.claude/rules/`)

Files in `.claude/rules/` are development guidance for working in this repo, loaded by Claude Code itself (a path-scoped rule — one with `paths:` frontmatter — loads its body only when you open a matching file). They are **not** shipped with any plugin: a marketplace plugin carries skills, MCPs, agents, and hooks, never `CLAUDE.md` or rules. So a rule can encode a development convention freely without affecting what consumers install.
