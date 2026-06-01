# Claude Relational Memory MCP Server

> **Status: Work-in-Progress.** Core memorize/recall functionality and auto-summarization
> work. Some features (pattern discovery) have incomplete implementations. API surface
> may change. Use for experimentation, not production workflows.

> ⚠️ **Local / persistent-disk only.** Memories are stored as JSONL under
> `~/.claude-memory` (or `CLAUDE_MEMORY_PATH`) and **nothing is committed anywhere by
> default**. In an **ephemeral cloud/container session** (e.g. Claude Code on the web) that
> directory is reclaimed at session end, so memories written with `memorize` /
> `add_core_memory` are **silently lost** — they look persisted but won't survive.
> Persistence across sessions is only achieved when the memory directory is on **durable
> local storage**, **committed to a repo**, or **mapped to a durable volume**. The server
> emits a one-time warning when it detects an ephemeral context.

> **Attribution:** Based on the autonomous development system by [@lizTheDeveloper](https://github.com/lizTheDeveloper) at [Multiverse School](https://multiverse.school)

Multi-layered memory system for AI agents working across Claude Code sessions, persistent
on durable local storage (see the local-only note above).

## Features

- 🧠 **5 Memory Layers:** Recent, Current Task, Episodic, Compost, Core Memories
- 🔄 **Auto-Summarization:** Episodic memories compress at 100 entries (fails safe — episodic preserved if summarization fails)
- 🌐 **Cross-Project:** Agents remember experiences from all projects
- 🔑 **No API Keys:** Uses Claude Code agents for LLM operations
- 💾 **Simple Storage:** JSONL files, human-readable, git-friendly
- 🚀 **Standalone:** Works with any Claude Code project via MCP

## Memory Layers

### Recent Memory
Current session context (cleared on session end)

### Current Task
What the agent is actively working on right now

### Episodic Memory
Up to 100 session entries (auto-summarizes when full; compaction failure preserves raw entries)

### Memory Compost
Archive of old/summarized memories

### Core Memories
Permanent principles and project learnings (always loaded)

## Installation

**Option A: uvx (recommended — no install, isolated venv)**

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "relational-memory": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/bogheorghiu/ex-cog-dev#subdirectory=vasana-system/mcp-servers/relational-memory",
        "relational-memory"
      ]
    }
  }
}
```

Requires `uv` installed once per machine (`curl -LsSf https://astral.sh/uv/install.sh | sh` on Linux/macOS, `winget install astral-sh.uv` on Windows). First run is slow (~10–60s while uvx clones and builds the venv); subsequent calls are fast.

**Option B: pip install (local clone)**

```bash
pip install -e .
```

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "relational-memory": {
      "command": "relational-memory"
    }
  }
}
```

## Usage

### Basic Memory Operations

```python
# Store a memory (encode new information)
memorize(
    agent_name="tdd-implementer",
    layer="recent",
    content="Used pytest fixtures for database setup",
    metadata={"task_id": "B2", "rationale": "More maintainable"}
)

# Retrieve memories (recall past information)
memories = recall(
    agent_name="tdd-implementer",
    layers=["recent", "episodic"],
    limit=10
)

# Update current task
update_current_task(
    agent_name="tdd-implementer",
    task="Implement auth endpoints",
    status="in_progress"
)

# Compress episodic memories (manual trigger, auto at 100 entries)
compress(agent_name="tdd-implementer")
```

### From Claude Code Agents

```bash
# Agent automatically loads memory on startup
claude -p "Load my memories and continue working on my current task."
```

The MCP tools are available automatically:
- `memorize` - Store a memory (encode information)
- `recall` - Retrieve memories (search past information)
- `update_current_task` - Update task state
- `get_current_task` - Get current task info
- `add_core_memory` - Add permanent learning
- `get_core_memories` - Read all core memories
- `compress` - Compress episodic memories (auto at 100 entries; preserves raw data on failure)
- `migrate_config` - Opt-in upgrade of config.json to current schema (preserves user-customized values)

### Entity Query Layer (kg-memory compatible)

These tools provide compatibility with Anthropic's kg-memory API pattern:

- `get_entity` - Get all relations for an entity (returns raw data)
- `search_nodes` - Search for entities matching query
- `read_graph` - Get complete relation graph
- `open_nodes` - Batch get multiple entities
- `delete_relations` - Delete relations by criteria

**Note:** These tools return RAW RELATIONS only. Use the `entity-interpreter` agent to derive semantic meaning from the data.

```python
# Example: Get an entity and interpret it
entity = get_entity(name="opus-distillatus")
# Returns raw relations - use entity-interpreter agent for analysis
```

## Transport

stdio only. The installed `relational-memory` console script always runs over stdio for
local Claude Code use; there is no working HTTP/remote transport on the shipped entry point.
(A multi-client HTTP deployment is being developed separately and is intentionally not
documented here until it's wired and tested.)

## Storage Location

All memories stored in: `~/.claude-memory/`, overridable via the `CLAUDE_MEMORY_PATH`
environment variable. Point it at durable storage to persist across ephemeral sessions.

```
~/.claude-memory/
├── agents/
│   ├── tdd-implementer/
│   │   ├── recent.jsonl
│   │   ├── current-task.json
│   │   ├── episodic.jsonl
│   │   └── compost.jsonl
│   └── ...
├── core-memories.md
├── memory-index.json
└── config.json
```

## Configuration

Edit `~/.claude-memory/config.json`:

```json
{
  "memory_limits": {
    "recent_max": 20,
    "episodic_max": 100,
    "auto_summarize_at": 100
  },
  "summarization": {
    "method": "claude_agent",
    "model": "sonnet"
  }
}
```

**Upgrading config:** If you see a startup warning about schema version mismatch,
call the `migrate_config` MCP tool to apply safe defaults (your customizations are preserved).
Only fields still at the old defaults are updated; user-set values are left untouched.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .
```

## License

MIT

## Credits

- Original autonomous development system: [@lizTheDeveloper](https://github.com/lizTheDeveloper) at [Multiverse School](https://multiverse.school)
- Memory system design inspired by Pixar's "Inside Out"
