# Research Toolkit — MCP server setup

What this plugin contains is readable from the tree itself (`skills/`, `agents/`,
`commands/`, `principles/`, `reference/`, `mcp-servers/`); what it's *for* is in the
plugin's `description`. Neither is repeated here — a hand-kept copy of either only rots.
This file carries the one thing the tree can't express: how to run the two MCP servers
**outside** the plugin.

## You probably don't need this

Installed as a plugin, both servers are already configured: `.mcp.json` registers them
via `uvx` and Claude Code starts them for you. **Nothing below is required.**

The instructions here are only for running a server **standalone** — outside the plugin,
or against a local checkout while developing it.

> Making even that unnecessary — and identical in Claude Code and Cowork — is a tracked
> final action of the current update.

## financial-mcp (standalone)

Stock market data via yfinance. Self-contained — no `PYTHONPATH` setup required, no API key.

**Option A — uvx (no install):** add to your `.mcp.json`, replacing the path with your checkout:

```json
{
  "mcpServers": {
    "financial-mcp": {
      "command": "uvx",
      "args": ["--from", "/path/to/research-toolkit/mcp-servers/financial-mcp", "financial-mcp"]
    }
  }
}
```

**Option B — pip install:**

```bash
cd mcp-servers/financial-mcp
pip install .
financial-mcp
```

**Ticker cache:** `~/.cache/financial-mcp/ticker_cache.db` — override the directory with the
`CACHE_DIR` env var.

## transparency-mcp (standalone)

Free public data from GovTrack, World Bank and ProPublica. **No API keys required.**

**Option A — uvx (no install):**

```json
{
  "mcpServers": {
    "transparency-mcp": {
      "command": "uvx",
      "args": ["--from", "/path/to/research-toolkit/mcp-servers/transparency-mcp", "transparency-mcp"]
    }
  }
}
```

**Option B — pip install:**

```bash
cd mcp-servers/transparency-mcp
pip install .
transparency-mcp
```

Its tools are self-describing over MCP — ask the server rather than trusting a list here.

## License

MIT
