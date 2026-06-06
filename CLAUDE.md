# CLAUDE.md — ex-cog-dev

Notes for any Claude Code (or human) session working in this repo.

## What's here

Four Claude Code plugins distributed via the `ex-cog-dev` marketplace:

- `vasana-system/` — pattern-recognition skills, plus two MCP servers (`relational-memory`, `edge-graph`)
- `research-toolkit/` — research/analysis skills, plus two MCP servers (`financial-mcp`, `transparency-mcp`)
- `makers-toolkit/` — build-discipline skills (`system-pilot`, `intrinsic-prompt-design`); no MCP servers
- `security-toolkit/` — threat-detection and dangerous-action-blocking hooks; no MCP servers

The four MCP servers are launched by consumers via `uvx --from git+https://github.com/bogheorghiu/ex-cog-dev#subdirectory=<path> <command>` URLs in each plugin's `.mcp.json`. That means every uvx cold-start fetches the latest source from this repo. A bad commit propagates to all consumers within ~24h (uvx cache TTL).

## Version bumping (REQUIRED)

When you change **any** file under a plugin directory (`vasana-system/`, `research-toolkit/`, `makers-toolkit/`, `security-toolkit/`), you **must** bump that plugin's `.claude-plugin/plugin.json` `version` in the same change, before committing. That version is what `claude plugin update` keys on — a change shipped without a bump is silently skipped by installs (this has regressed before).

- Patch (`x.y.Z+1`) for fixes/docs, minor (`x.Y+1.0`) for new features — your judgment.
- Genuine no-op (e.g. a typo in an unshipped note)? Bypass with `[skip-version-bump]` in the PR title or the `skip-version-bump` label.
- Self-check before pushing — the same guard CI runs on every PR:
  ```bash
  python3 .github/scripts/check_version_bump.py origin/main HEAD
  ```
  Enforced by `.github/workflows/version-bump-guard.yml`; logic + tests in `.github/scripts/`.

## Release / publish

Every PR to `main` (and every push to `main`) runs three CI gates:

- **MCP smoke test** (`.github/workflows/mcp-smoke-test.yml`) — builds each of the four MCPs via `uvx --from <local-path>` and sends a JSON-RPC `initialize`; fails if any server can't import, build, or respond.
- **Unit tests** (`.github/workflows/unit-tests.yml`) — the per-plugin test suites.
- **Version-bump guard** (`.github/workflows/version-bump-guard.yml`) — see *Version bumping* above.

Green `main` is the pre-publish bar.

**This repo (`ex-cog-dev`) is the development source; the public plugin lives in the separate `bogheorghiu/ex-cog` repo.** Publishing = syncing `ex-cog-dev` → `ex-cog`, and that promotion *is* the release gate. The flow has **no `release`-branch step**: that branch was redundant with the dev/public split and never load-bearing (the `.mcp.json` URLs never pinned `@release`), so it is being retired.

For the dev repo's own `.mcp.json`, the `uvx --from` URLs point at `ex-cog-dev` HEAD of `main`, so a bad commit to `main` here reaches anyone testing against the dev repo within ~24h (uvx cache TTL) or on `uvx --refresh`. The public is insulated from that until the next dev→`ex-cog` sync.

> Reconsidering this? Collapsing the two repos into one — with the public installing directly and a `release` branch + `@release`-pinned URLs as the stability mechanism — is tracked in issue #38. Until that's decided, dev→`ex-cog` is the publish step.

## Development rules (`.claude/rules/`)

Files in `.claude/rules/` are development guidance for working in this repo, loaded by Claude Code itself (a path-scoped rule — one with `paths:` frontmatter — loads its body only when you open a matching file). They are **not** shipped with any plugin: a marketplace plugin carries skills, MCPs, agents, and hooks, never `CLAUDE.md` or rules. So a rule can encode a development convention freely without affecting what consumers install.
