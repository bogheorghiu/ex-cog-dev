# Edge-Graph MCP

> **Status: Work-in-Progress.** Core edge creation and traversal work. Pattern discovery
> and vocabulary emergence features have incomplete implementations. API surface may change.
> Use for experimentation, not production workflows.

Edge-defined graph system where patterns emerge from traversal weight, not node properties.

## Core Concept

**Edges are verbs with weight.** Patterns emerge from traversal frequency, not declaration.

- Create edges connecting nodes with free-form verbs
- Call `traverse_edge` every time an edge is "used"
- High-weight edges surface as patterns worth formalizing

## Installation

**Option A: uvx (recommended — no install, isolated venv)**

Add to `.mcp.json`:

```json
"edge-graph": {
    "command": "uvx",
    "args": [
        "--from",
        "git+https://github.com/bogheorghiu/ex-cog-dev#subdirectory=vasana-system/mcp-servers/edge-graph",
        "edge-graph"
    ]
}
```

Requires `uv` installed once per machine (`curl -LsSf https://astral.sh/uv/install.sh | sh` on Linux/macOS, `winget install astral-sh.uv` on Windows). First run is slow (~10–60s while uvx clones and builds the venv); subsequent calls are fast.

**Option B: pip install (local clone)**

```bash
cd edge-graph-mcp
pip install -e .
```

Add to `.mcp.json`:

```json
"edge-graph": {
    "command": "edge-graph"
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EDGE_GRAPH_PATH` | `~/.edge-graph` | Storage directory |

## MCP Tools

### Core Operations

| Tool | Description |
|------|-------------|
| `create_edge` | Create edge between nodes with free-form verb |
| `traverse_edge` | Increment edge weight (call on every "use") |
| `get_edge` | Get edge by ID |

### Weight-Based Discovery

| Tool | Description |
|------|-------------|
| `find_heavy_edges` | Find highest-weight edges |
| `discover_patterns` | Find recurring verbs with total weight |

### Queries

| Tool | Description |
|------|-------------|
| `find_edges` | Query edges with filtering |
| `get_verbs` | List all unique verbs |
| `get_node` | Get all edges for a node |
| `search_nodes` | Search edges by query |
| `read_graph` | Get complete graph |

## Example Usage

```python
# Create edges
create_edge(from_node="concept-A", to_node="concept-B", verb="enables", agent="claude")
create_edge(from_node="concept-B", to_node="concept-C", verb="blocks", agent="claude")

# Record traversals (weight grows with use)
traverse_edge(edge_id="edge-...")
traverse_edge(edge_id="edge-...")

# Discover patterns
find_heavy_edges(limit=5)  # Most-used edges
discover_patterns()         # Recurring verbs by total weight
```

## Design Principles

1. **Verbs are free strings** - No enum, patterns emerge organically
2. **Weight from use** - Traversal count determines importance
3. **Self-contained** - No dependencies on external systems
4. **Application-agnostic** - Works for mind-maps, memory, content navigation

## Time Decay (Optional)

The `Edge.weighted_score()` method supports optional time decay:

```python
# Default: no decay (days_since=0)
edge.weighted_score()  # traversal_count * confidence

# With decay: weight diminishes over time
edge.weighted_score(decay_factor=0.95, days_since=7)  # 5% per day decay
```

**Currently:** Time decay is available but not actively applied. `find_heavy_edges` uses `weighted_score()` without decay by default, prioritizing total traversal count.

**Future:** Applications can implement their own decay strategies by calculating `days_since` from `edge.last_traversed`.

## Limitations

**Status: Experimental**

This is a simple JSONL-based implementation optimized for clarity over performance.

### Performance Characteristics

| Operation | Complexity | Notes |
|-----------|------------|-------|
| `create_edge` | O(1) | Append to file |
| `traverse_edge` | O(n) | **Full file rewrite** |
| `get_edge` | O(n) | Scans entire file |
| `find_edges` | O(n) | Scans entire file |

**Why O(n)?** Every edge update reads the entire JSONL file, updates one edge, and rewrites the entire file. This is intentional for simplicity but limits scalability.

### Recommended Scale

- **<100 edges**: Fast, responsive
- **100-500 edges**: Noticeable but acceptable latency
- **500-1000 edges**: Slower, consider SQLite migration
- **>1000 edges**: Not recommended

### Other Limitations

- **Concurrency**: Single-process only. Not safe for concurrent writes.
- **No indexing**: All queries scan the full dataset.
- **Corruption handling**: Malformed edges are logged and skipped (data may be incomplete).

For production use with larger graphs, consider migrating to SQLite backend.

## Transport

stdio only. The installed `edge-graph` console script always runs over stdio for local
Claude Code use; there is no working HTTP/remote transport on the shipped entry point. (HTTP
serving scaffolding exists in the source but is not reachable via the console script, and is
intentionally undocumented as a deployment option until it's wired and tested.)

## License

MIT
