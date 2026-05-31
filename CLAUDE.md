# CLAUDE.md — ex-cog-dev

Notes for any Claude Code (or human) session working in this repo.

## What's here

Four Claude Code plugins distributed via the `ex-cog-dev` marketplace:

- `vasana-system/` — pattern-recognition skills, plus two MCP servers (`relational-memory`, `edge-graph`)
- `research-toolkit/` — research/analysis skills, plus two MCP servers (`financial-mcp`, `transparency-mcp`)
- `makers-toolkit/` — build-discipline skills (`system-pilot`, `intrinsic-prompt-design`); no MCP servers
- `security-toolkit/` — threat-detection and dangerous-action-blocking hooks; no MCP servers

The four MCP servers are launched by consumers via `uvx --from git+https://github.com/bogheorghiu/ex-cog-dev#subdirectory=<path> <command>` URLs in each plugin's `.mcp.json`. That means every uvx cold-start fetches the latest source from this repo. A bad commit propagates to all consumers within ~24h (uvx cache TTL).

## Release procedure (the `release` branch + smoke test pattern)

The `MCP smoke test` workflow (`.github/workflows/mcp-smoke-test.yml`) runs on every push to `main` and every PR. It builds each of the four MCPs via `uvx --from <local-path>` and feeds them a JSON-RPC `initialize` request — if any server fails to import, build, or respond, the workflow fails.

The intended flow is:

1. **Develop on a feature branch.** Open a PR to `main`. Smoke test runs on the PR.
2. **Merge to `main`.** Smoke test runs again on the merge commit.
3. **Once smoke test passes on `main`,** fast-forward `release` to that commit:
   ```bash
   git fetch origin
   # First time only (creates the branch):
   git push origin origin/main:refs/heads/release
   # Subsequent updates (fast-forward):
   git push origin origin/main:release
   ```
4. **Consumers** pick up the new code on next uvx cache refresh (~24h) or when they run `uvx --refresh`.

> ⚠️ **The plugin `.mcp.json` URLs do not currently include `@release`.** They point at HEAD of `main`, so the `release` branch is a safety net you can opt into later by adding `@release` to each URL (in a follow-up PR). Until then, smoke test still acts as a pre-merge guard, but `release` itself isn't load-bearing.

### To roll back a bad release

```bash
git push --force-with-lease origin <prior-good-sha>:release
```

Then consumers either wait out the uvx cache TTL or run `uvx --refresh`.

## Companion repo

> **Note (2026-05):** This repo is now the source of truth and is pushed to directly. The previous mirroring relationship with `bogheorghiu/Claude-Code-Projects` is no longer active — do **not** mirror changes there unless explicitly asked.

Historically, `bogheorghiu/Claude-Code-Projects` carried a copy of these plugins under `projects/ex-cog-dev/...` and was registered as the `external-cognition-dev` marketplace.
