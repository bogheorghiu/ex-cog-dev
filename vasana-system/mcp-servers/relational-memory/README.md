# Claude Relational Memory MCP Server

> **Status: Work-in-Progress.** Core memorize/recall functionality works. Some features
> (auto-summarization, pattern discovery) have incomplete implementations. API surface
> may change. Use for experimentation, not production workflows.

> **Attribution:** Based on the autonomous development system by [@lizTheDeveloper](https://github.com/lizTheDeveloper) at [Multiverse School](https://multiverse.school)

Persistent multi-layered memory system for AI agents working across Claude Code sessions.

## Features

- 🧠 **5 Memory Layers:** Recent, Current Task, Episodic, Compost, Core Memories
- 🔄 **Auto-Summarization:** Episodic memories compress at 10 entries
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
Last 10 session summaries (auto-summarizes when full)

### Memory Compost
Archive of old/summarized memories

### Core Memories
Permanent principles and project learnings (always loaded)

## Installation

```bash
# Install the package
pip install -e .

# Configure in Claude Code
# Add to your .mcp.json:
{
  "mcpServers": {
    "relational-memory": {
      "command": "python",
      "args": ["-m", "claude_relational_memory"],
      "type": "stdio"
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

# Compress episodic memories (manual trigger, auto at 10 entries)
compress(agent_name="tdd-implementer")
```

### From Claude Code Agents

```bash
# Agent automatically loads memory on startup
claude --headless << 'EOF'
Load my memories and continue working on my current task.
EOF
```

The MCP tools are available automatically:
- `memorize` - Store a memory (encode information)
- `recall` - Retrieve memories (search past information)
- `update_current_task` - Update task state
- `get_current_task` - Get current task info
- `add_core_memory` - Add permanent learning
- `get_core_memories` - Read all core memories
- `compress` - Compress episodic memories (auto at 10 entries)

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

## Cloud Deployment (Claude AI Web + Claude Code)

Deploy to share memories between Claude AI Web and Claude Code.

> ⚠️ **SECURITY WARNING**: This server has NO built-in authentication.
>
> **For production deployments, you MUST use one of:**
> - Railway private networking (recommended - see below)
> - Cloudflare Access / Zero Trust
> - Reverse proxy with auth (Nginx, Caddy)
> - VPN/private network
>
> **Never expose this server directly to the public internet.**

### Quick Start (Railway with Private Networking)

```bash
# 1. Clone and deploy
git clone https://github.com/YOUR_USERNAME/relational-memory-mcp
cd relational-memory-mcp
railway login
railway init
railway up

# 2. Set environment variables in Railway dashboard:
#    MCP_TRANSPORT=http

# 3. Add persistent volume at /data/claude-memory

# 4. Enable Private Networking in Railway settings
#    This gives you a private URL like: claude-memory.railway.internal
```

### Reverse Proxy Examples

**Nginx with Basic Auth:**
```nginx
location /mcp {
    auth_basic "Memory Server";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:3000;
}
```

**Caddy with API Key:**
```caddyfile
:443 {
    @authorized header X-API-Key your-secret-key
    handle @authorized {
        reverse_proxy localhost:3000
    }
    respond 401
}
```

### Configure Claude Code (Local)

```bash
# With Nginx basic auth:
claude mcp add --transport http relational-memory \
  --header "Authorization: Basic $(echo -n user:pass | base64)" \
  https://your-server.com/mcp

# With Caddy API key:
claude mcp add --transport http relational-memory \
  --header "X-API-Key: your-secret-key" \
  https://your-server.com
```

### Configure Claude AI Web

1. Go to claude.ai → Settings → Integrations
2. Add MCP Server
3. URL: `https://your-server.com` (your reverse proxy URL)
4. Add appropriate auth header for your setup

### Unified Memory

Once both clients point to the same server:
- Memories created in Claude Code → visible in Claude AI Web
- Memories created in Claude AI Web → visible in Claude Code
- Core memories, relations, and entities all shared automatically

### Transport Modes

| Mode | Use Case | Command |
|------|----------|---------|
| `stdio` (default) | Local Claude Code | `python -m claude_memory_mcp` |
| `http` | Cloud/Remote | `MCP_TRANSPORT=http python -m claude_memory_mcp` |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `stdio` | Transport mode: `stdio` or `http` |
| `MCP_HOST` | `0.0.0.0` | HTTP bind address |
| `MCP_PORT` | `3000` | HTTP port (validated, exits on invalid) |
| `CLAUDE_MEMORY_PATH` | `~/.claude-memory` | Storage location |

### Docker

```bash
docker build -t relational-memory-mcp .

# Run behind reverse proxy (recommended)
docker run -p 127.0.0.1:3000:3000 \
  -v /path/to/data:/data/relational-memory \
  relational-memory-mcp

# Note: Bind to 127.0.0.1 only, expose via reverse proxy with auth
```

---

## Storage Location

All memories stored in: `~/.claude-memory/`

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
    "episodic_max": 10,
    "auto_summarize_at": 10
  },
  "summarization": {
    "method": "claude_agent",
    "model": "sonnet"
  }
}
```

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
