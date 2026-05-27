# Integration Status — vasana-system

**As of 2026-05-25.** Plugin is fully active. This note exists to document its overlap with `memory-substrate` and a potential refactor.

## Current runtime role
This plugin is the **actual source** of the `relational-memory` and `edge-graph` MCP servers running in your Claude Code sessions. Both are registered via `.mcp.json`:

```json
{
  "mcpServers": {
    "relational-memory": {
      "command": "uvx",
      "args": ["--from",
        "git+https://github.com/bogheorghiu/ex-cog-dev#subdirectory=vasana-system/mcp-servers/relational-memory",
        "relational-memory"]
    },
    "edge-graph": { ... analogous ... }
  }
}
```

Plus all the vasana-system content proper: `skills/`, `commands/`, `agents/`, `hooks/`.

## Overlap with memory-substrate
The `memory-substrate@external-cognition-dev` plugin (in CCP at `projects/ex-cog-dev/memory-substrate/`) ships a copy of the 5 core source files for `relational-memory` (`backend.py`, `models.py`, `server.py`, `claude_agent.py`, `__init__.py`).

**Note (2026-05-25):** These files are no longer byte-identical. PRs #425 and #429 added significant changes to the vasana-system versions (schema v1.1, per-agent compaction failure flag, atomic config write, `extra="ignore"` on `MemoryConfig`, `--print` CLI fix) that were not ported to memory-substrate. The memory-substrate `claude_agent.py` received the `--print` fix in PR #429 (to prevent the same runtime breakage), but `backend.py` and `models.py` remain at the older schema. Memory-substrate is dormant — vasana-system is the source of truth.

Memory-substrate's framing: "the substrate on which cognitive plugins build." Intent appears to be that vasana-system (and other cognitive plugins) would eventually pull MCP code *from memory-substrate* instead of from the inline GitHub URL above.

That refactor hasn't been done. See `projects/ex-cog-dev/memory-substrate/INTEGRATION-STATUS.md` for the blocker (memory-substrate's pyproject lacks the `[project.scripts]` + `[tool.setuptools.packages.find]` blocks that the hosted version has).

## If you want to do the refactor
Change this plugin's `.mcp.json` to point at memory-substrate's local source. Two paths described in memory-substrate's INTEGRATION-STATUS — both small changes.

## Until then
No action needed on this plugin. It works. Just be aware that touching the relational-memory or edge-graph Python source here is the **source of truth** at runtime — memory-substrate's copies are dormant and behind.
