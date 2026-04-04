# Claude Relational Memory - Usage Guide

> **Attribution:** Based on the autonomous development system by [@lizTheDeveloper](https://github.com/lizTheDeveloper) at [Multiverse School](https://multiverse.school)

## Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd claude-relational-memory

# Install in editable mode
pip3 install -e .
```

### 2. Configure for Claude Code

Add to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "claude-memory": {
      "command": "python3",
      "args": ["-m", "claude_relational_memory"],
      "type": "stdio"
    }
  }
}
```

### 3. Start Using Memory!

The MCP tools are now available in Claude Code:

```bash
claude --headless << 'EOF'
# The memory tools are available!
# memorize(), recall(), compress(), etc.
EOF
```

## Memory Tools Reference

### `memorize(agent_name, layer, content, metadata={})`

**Store a new memory** (encode information).

**Parameters:**
- `agent_name` (required): Your agent's identifier (e.g., "tdd-implementer", "code-reviewer")
- `layer` (required): Which memory layer - `"recent"`, `"episodic"`, or `"compost"`
- `content` (required): Single sentence describing what happened
- `metadata` (optional): Additional context (task_id, project, rationale, etc.)

**Layers:**
- **`recent`**: Current session context (cleared when you finish your task)
- **`episodic`**: Session summaries (auto-compresses at 10 entries)
- **`compost`**: Archived old memories (long-term storage)

**Example:**

```python
memorize(
    agent_name="tdd-implementer",
    layer="recent",
    content="Refactored authentication to use OAuth2 instead of custom tokens",
    metadata={
        "task_id": "AUTH-123",
        "project": "/Users/me/my-app",
        "rationale": "Industry standard, better security",
        "files_changed": ["src/auth/oauth.py", "tests/test_auth.py"]
    }
)
```

---

### `recall(agent_name, layers=["recent", "episodic"], query=None, limit=10, project=None)`

**Retrieve memories** (search past information).

**Parameters:**
- `agent_name` (required): Agent to recall memories for (or `None` for all agents)
- `layers` (optional): Which layers to search (default: `["recent", "episodic"]`)
- `query` (optional): Semantic search query (uses Claude agent for smart search)
- `limit` (optional): Max memories to return (default: 10)
- `project` (optional): Filter to specific project path

**Returns:** List of memory objects, newest first.

**Examples:**

```python
# Get recent memories for this agent
memories = recall(agent_name="tdd-implementer")

# Search all agents for auth-related work
auth_memories = recall(
    agent_name=None,  # All agents
    query="authentication security fixes",
    layers=["recent", "episodic", "compost"]
)

# Get episodic memories for specific project
project_history = recall(
    agent_name="tdd-implementer",
    project="/Users/me/my-app",
    layers=["episodic"]
)
```

---

### `update_current_task(agent_name, task=None, status=None, metadata={})`

**Update what you're currently working on.**

**Parameters:**
- `agent_name` (required): Your agent identifier
- `task` (optional): Task description
- `status` (optional): `"not_started"`, `"in_progress"`, `"blocked"`, `"completed"`, `"abandoned"`
- `metadata` (optional): task_id, branch, roadmap_link, tests_passing, blockers, etc.

**Example:**

```python
# Claim a task
update_current_task(
    agent_name="tdd-implementer",
    task="Implement user registration endpoint",
    status="in_progress",
    metadata={
        "task_id": "USER-45",
        "branch": "feature/user-registration",
        "roadmap_link": "plans/roadmap.md#user-45",
        "tests_passing": 0,
        "tests_failing": 0
    }
)

# Update progress
update_current_task(
    agent_name="tdd-implementer",
    status="in_progress",
    metadata={
        "tests_passing": 5,
        "tests_failing": 2
    }
)

# Mark complete
update_current_task(
    agent_name="tdd-implementer",
    status="completed",
    metadata={
        "tests_passing": 7,
        "tests_failing": 0,
        "committed": True
    }
)
```

---

### `get_current_task(agent_name)`

**Get the current task state.**

**Returns:** Current task object or `None`.

**Example:**

```python
task = get_current_task("tdd-implementer")
if task:
    print(f"Working on: {task.task} ({task.status})")
    print(f"Started: {task.started}")
```

---

### `compress(agent_name)`

**Compress episodic memories into summary.**

Condenses 10+ episodic entries into 2-3 key sentences using a Claude agent, then moves originals to compost (archive).

**Normally happens automatically** when episodic layer reaches 10 entries. Use this to manually trigger.

**Example:**

```python
# Manual compression
compress("tdd-implementer")
```

**Output:**
```
"Week focused on authentication: implemented OAuth2, added comprehensive tests, deployed to staging"
```

---

### `add_core_memory(category, content, justification)`

**Add a permanent core memory.**

Core memories ALWAYS load with every agent session. Use sparingly for important patterns observed across 3+ sessions.

**Parameters:**
- `category`: `"personality"`, `"learning"`, or `"anti-pattern"`
- `content`: The principle/learning (1-2 sentences)
- `justification`: Why this should be permanent

**Example:**

```python
add_core_memory(
    category="anti-pattern",
    content="Never work directly on main branch. Always create feature branch to avoid conflicts.",
    justification="Observed 3 times: agents working simultaneously caused merge conflicts"
)
```

---

### `get_core_memories()`

**Get all core memories.**

Returns the full core-memories.md content (personality principles, learnings, anti-patterns).

**Example:**

```python
core = get_core_memories()
print(core)  # Full markdown document
```

---

## Common Workflows

### Workflow 1: Agent Session Startup

```python
# Load your memories
memories = recall(agent_name="tdd-implementer", layers=["recent", "episodic"])

# Check what you were working on
task = get_current_task("tdd-implementer")

# Read core principles
core = get_core_memories()

# Now you have full context to continue work!
```

### Workflow 2: During Development

```python
# Claim a task
update_current_task(
    agent_name="tdd-implementer",
    task="Add user authentication",
    status="in_progress",
    metadata={"task_id": "AUTH-1", "branch": "feature/auth"}
)

# Make progress, store key decisions
memorize(
    agent_name="tdd-implementer",
    layer="recent",
    content="Chose bcrypt for password hashing over argon2 for compatibility",
    metadata={"task_id": "AUTH-1", "rationale": "Better library support"}
)

memorize(
    agent_name="tdd-implementer",
    layer="recent",
    content="Added rate limiting to login endpoint to prevent brute force",
    metadata={"task_id": "AUTH-1", "security": True}
)

# Complete task
update_current_task(
    agent_name="tdd-implementer",
    status="completed",
    metadata={"tests_passing": 12}
)
```

### Workflow 3: Session End Summary

```python
# Promote important recent memories to episodic
important_decisions = recall(
    agent_name="tdd-implementer",
    layers=["recent"],
    query="important decision rationale"
)

for decision in important_decisions:
    memorize(
        agent_name="tdd-implementer",
        layer="episodic",
        content=decision["content"],
        metadata=decision["metadata"]
    )

# System will auto-compress when you hit 10 episodic entries
```

### Workflow 4: Learning from Past Sessions

```python
# Search for how you solved similar problems before
past_solutions = recall(
    agent_name="tdd-implementer",
    query="authentication security best practices",
    layers=["episodic", "compost"],
    limit=5
)

for solution in past_solutions:
    print(f"[{solution['timestamp']}] {solution['content']}")
```

### Workflow 5: Cross-Agent Learning

```python
# See what other agents have learned
all_auth_work = recall(
    agent_name=None,  # All agents!
    query="authentication implementation",
    layers=["episodic"]
)

# Learn from another agent's experience
reviewer_insights = recall(
    agent_name="code-reviewer",
    query="security vulnerabilities found"
)
```

---

## Memory Best Practices

### 1. Keep Content Concise

✅ **Good:**
```python
memorize(
    content="Switched from REST to GraphQL for user API",
    metadata={"rationale": "Reduced over-fetching, better mobile performance"}
)
```

❌ **Bad:**
```python
memorize(
    content="We had a long discussion about APIs and decided that maybe GraphQL would be better than REST because it has some advantages like reducing over-fetching and the mobile team said it would be better for them..."
)
```

### 2. Use Metadata for Context

Metadata doesn't bloat the memory content but provides rich context for filtering:

```python
memorize(
    content="Fixed XSS vulnerability in search input",
    metadata={
        "security": True,
        "severity": "high",
        "cve": "CVE-2025-XXXX",
        "task_id": "SEC-789",
        "files": ["src/search.py"]
    }
)
```

### 3. Recent → Episodic → Compost Flow

**Recent:** Detailed notes during work
```python
memorize(layer="recent", content="Tried approach A, failed due to X")
memorize(layer="recent", content="Switched to approach B, works better")
memorize(layer="recent", content="Added tests for edge cases Y and Z")
```

**Episodic:** Session summary (promote at end)
```python
memorize(
    layer="episodic",
    content="Implemented feature X using approach B with comprehensive tests"
)
```

**Compost:** Auto-generated from 10 episodic entries
```
"Month focused on core features: auth, payments, notifications—all deployed with 95% test coverage"
```

### 4. Core Memories = 3+ Observations

Only promote to core memories when you've seen a pattern **at least 3 times**:

```python
# After 3rd occurrence of same issue
add_core_memory(
    category="anti-pattern",
    content="Database migrations must be backward compatible for zero-downtime deploys",
    justification="Breaking migration caused production outage 3 times (DEPLOY-12, DEPLOY-34, DEPLOY-56)"
)
```

---

## Storage & Configuration

### Storage Location

All memories stored in: `~/.claude-memory/`

```
~/.claude-memory/
├── agents/
│   ├── tdd-implementer/
│   │   ├── recent.jsonl              # Current session
│   │   ├── current-task.json         # Active task
│   │   ├── episodic.jsonl            # Last 10 session summaries
│   │   └── compost.jsonl             # Archived memories
│   └── code-reviewer/
│       └── ...
├── core-memories.md                   # Permanent principles
├── memory-index.json                  # Fast lookup index
└── config.json                        # Configuration
```

### Configuration

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

**Options:**
- `recent_max`: Max recent memories before warning (default: 20)
- `episodic_max`: Max episodic memories before auto-compression (default: 10)
- `auto_summarize_at`: Trigger compression at N entries (default: 10)
- `model`: Which Claude model for summarization - `"sonnet"` (balanced) or `"haiku"` (faster/cheaper)

---

## Troubleshooting

### Memory not persisting?

Check the storage location exists:
```bash
ls -la ~/.claude-memory/
```

### Compression not working?

Compression requires Claude Code to be installed and in PATH:
```bash
which claude
# Should output: /path/to/claude
```

### MCP server not starting?

Check server logs:
```bash
python3 -m claude_memory_mcp 2>&1 | tee mcp-server.log
```

### Want to reset all memories?

```bash
# Backup first!
mv ~/.claude-memory ~/.claude-memory-backup

# Fresh start
# (will auto-create on next use)
```

---

## Advanced: Agent Coordination Example

```python
# Agent 1: Claim task
update_current_task(
    agent_name="worker-1",
    task="Implement payment processing",
    status="in_progress",
    metadata={"task_id": "PAY-100", "branch": "feature/payments"}
)

# Agent 2: Check what's in progress (avoid conflicts)
all_tasks = recall(agent_name=None, query="current task in_progress")

# Agent 2: Pick different task
update_current_task(
    agent_name="worker-2",
    task="Write documentation",
    status="in_progress",
    metadata={"task_id": "DOCS-50"}
)

# Both agents store their progress
memorize(agent_name="worker-1", layer="recent", content="Integrated Stripe API")
memorize(agent_name="worker-2", layer="recent", content="Documented payment API endpoints")

# Later: Review agent learns from both
payment_work = recall(
    agent_name=None,
    query="payment processing Stripe",
    layers=["recent", "episodic"]
)
```

---

## Next Steps

- See `test_basic.py` for functional examples
- Read `docs/operational/memory/memory-storage-schema.md` for technical details
- Read `docs/operational/memory/autonomous-development-system.md` for full autonomous agent setup
- Join discussion: https://github.com/lizTheDeveloper (original author)
