"""MCP Server for Claude Memory System."""

import os
from typing import Literal, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import Field

from .backend import LocalFileBackend


# Initialize backend
memory_backend = LocalFileBackend()

# Create MCP server
app = Server("claude-memory")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available memory tools."""
    return [
        Tool(
            name="memorize",
            description=(
                "Store a new memory (encode information). "
                "Use 'recent' for current session context, "
                "'episodic' for session summaries, "
                "'compost' for archived memories."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name/identifier of the agent (e.g., 'tdd-implementer')",
                    },
                    "layer": {
                        "type": "string",
                        "enum": ["recent", "episodic", "compost"],
                        "description": "Which memory layer to store in",
                    },
                    "content": {
                        "type": "string",
                        "description": "Single sentence memory to store",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata (task_id, project, rationale, etc.)",
                        "default": {},
                    },
                },
                "required": ["agent_name", "layer", "content"],
            },
        ),
        Tool(
            name="recall",
            description=(
                "Retrieve memories for an agent. "
                "Can filter by layers, search with query, or filter by project. "
                "Returns most recent memories first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of agent, or null to search all agents",
                    },
                    "layers": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["recent", "episodic", "compost"]},
                        "description": "Which memory layers to search",
                        "default": ["recent", "episodic"],
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional semantic search query",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of memories to return",
                        "default": 10,
                    },
                    "project": {
                        "type": "string",
                        "description": "Optional project path filter",
                    },
                },
                "required": ["agent_name"],
            },
        ),
        Tool(
            name="update_current_task",
            description=(
                "Update the current task state for an agent. "
                "Use this to track what the agent is actively working on."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent",
                    },
                    "task": {
                        "type": "string",
                        "description": "Task description",
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "not_started",
                            "in_progress",
                            "blocked",
                            "completed",
                            "abandoned",
                        ],
                        "description": "Current task status",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata (task_id, branch, roadmap_link, etc.)",
                        "default": {},
                    },
                },
                "required": ["agent_name"],
            },
        ),
        Tool(
            name="get_current_task",
            description="Get the current task for an agent.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent",
                    },
                },
                "required": ["agent_name"],
            },
        ),
        Tool(
            name="add_core_memory",
            description=(
                "Add a permanent core memory (personality principle, learning, or anti-pattern). "
                "Core memories always load with every agent session. "
                "Use sparingly for important patterns observed across 3+ sessions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["personality", "learning", "anti-pattern"],
                        "description": "Type of core memory",
                    },
                    "content": {
                        "type": "string",
                        "description": "The principle/learning/anti-pattern (single sentence or short paragraph)",
                    },
                    "justification": {
                        "type": "string",
                        "description": "Why this should be a core memory (what event/observation led to it)",
                    },
                },
                "required": ["category", "content", "justification"],
            },
        ),
        Tool(
            name="get_core_memories",
            description="Get all core memories (permanent principles and learnings).",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="compress",
            description=(
                "Compress episodic memories into summary. "
                "Condenses 10+ entries into 2-3 key sentences using Claude agent. "
                "Normally happens automatically when episodic layer reaches threshold."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent",
                    },
                },
                "required": ["agent_name"],
            },
        ),
        # =====================================================================
        # Relations Layer - Pattern Discovery Tools
        # =====================================================================
        Tool(
            name="create_relation",
            description=(
                "Create a relation between two memories. The relation_type is a FREE STRING "
                "to enable domain-agnostic usage and emergent pattern discovery. "
                "Examples: 'builds_on', 'contradicts', 'supersedes', 'kept_checking_wrong_layer'. "
                "Relations with recurring types become candidates for vasana (behavioral pattern) documentation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "from_memory": {
                        "type": "string",
                        "description": "Reference to source memory (timestamp ID, content hash, or description)",
                    },
                    "to_memory": {
                        "type": "string",
                        "description": "Reference to target memory",
                    },
                    "relation_type": {
                        "type": "string",
                        "description": "Free-form relation type (e.g., 'builds_on', 'contradicts', 'same_mistake')",
                    },
                    "agent": {
                        "type": "string",
                        "description": "Which agent/context is creating this relation",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "0-1 confidence score (default 1.0)",
                        "default": 1.0,
                    },
                    "context": {
                        "type": "string",
                        "description": "Why this relation was created",
                        "default": "",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional domain-specific data",
                        "default": {},
                    },
                },
                "required": ["from_memory", "to_memory", "relation_type", "agent"],
            },
        ),
        Tool(
            name="find_relations",
            description=(
                "Query relations with flexible filtering. "
                "Can filter by relation_type, agent, source memory, target memory, or confidence."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "relation_type": {
                        "type": "string",
                        "description": "Filter by relation type (exact match)",
                    },
                    "agent": {
                        "type": "string",
                        "description": "Filter by creating agent",
                    },
                    "from_memory": {
                        "type": "string",
                        "description": "Filter by source memory reference",
                    },
                    "to_memory": {
                        "type": "string",
                        "description": "Filter by target memory reference",
                    },
                    "min_confidence": {
                        "type": "number",
                        "description": "Minimum confidence threshold (0-1)",
                        "default": 0.0,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 100,
                    },
                },
            },
        ),
        Tool(
            name="discover_patterns",
            description=(
                "THE VASANA DISCOVERY QUERY. Finds relation_types that appear repeatedly "
                "across contexts - these are behavioral patterns worth examining. "
                "When a relation_type appears 3+ times, it signals a potential vasana. "
                "Returns patterns sorted by occurrence count, with examples and cross-agent indicator."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "min_occurrences": {
                        "type": "integer",
                        "description": "Minimum times a relation_type must appear (default: 3)",
                        "default": 3,
                    },
                    "agent": {
                        "type": "string",
                        "description": "Filter to specific agent (null = all agents)",
                    },
                },
            },
        ),
        Tool(
            name="get_relation_types",
            description=(
                "Get all unique relation types in the system. "
                "Useful for exploring what types have been used and for autocomplete."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # =====================================================================
        # Entity Query Layer - kg-memory compatible raw relation dumps
        # =====================================================================
        Tool(
            name="get_entity",
            description=(
                "Get all relations involving an entity name. Returns RAW RELATIONS only - "
                "no semantic interpretation. Use entity-interpreter agent to derive "
                "types, properties, and relationships from the raw data."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Entity name to query",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="search_nodes",
            description=(
                "Search for entities/nodes matching a query. Returns RAW RELATIONS only. "
                "Matches query against any field in relations. "
                "Use entity-interpreter agent for semantic interpretation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term to match against relation fields",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="read_graph",
            description=(
                "Get ALL relations in the system. Returns RAW RELATIONS only. "
                "Use entity-interpreter agent to derive graph structure."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="open_nodes",
            description=(
                "Get all relations for multiple entity names (batch get_entity). "
                "Returns RAW RELATIONS only. More efficient than calling get_entity repeatedly."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of entity names to query",
                    },
                },
                "required": ["names"],
            },
        ),
        Tool(
            name="delete_relations",
            description=(
                "Delete relations matching the provided criteria. "
                "Each criteria dict can specify from_memory, to_memory, and/or relation_type. "
                "All specified fields must match for a relation to be deleted."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from_memory": {"type": "string"},
                                "to_memory": {"type": "string"},
                                "relation_type": {"type": "string"},
                            },
                        },
                        "description": "List of relation criteria to delete",
                    },
                },
                "required": ["relations"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "memorize":
        # Validate required fields
        required_fields = ["agent_name", "layer", "content"]
        missing = [f for f in required_fields if f not in arguments or not arguments.get(f)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        entry_id = memory_backend.memorize(
            agent=arguments["agent_name"],
            layer=arguments["layer"],
            content=arguments["content"],
            metadata=arguments.get("metadata", {}),
        )
        return [
            TextContent(
                type="text",
                text=f"Memory stored successfully.\nEntry ID: {entry_id}\nAgent: {arguments['agent_name']}\nLayer: {arguments['layer']}",
            )
        ]

    elif name == "recall":
        memories = memory_backend.recall(
            agent=arguments.get("agent_name"),
            layers=arguments.get("layers", ["recent", "episodic"]),
            query=arguments.get("query"),
            limit=arguments.get("limit", 10),
            project=arguments.get("project"),
        )

        if not memories:
            return [TextContent(type="text", text="No memories found.")]

        # Format memories for display
        formatted = []
        for mem in memories:
            formatted.append(
                f"[{mem['timestamp']}] {mem['agent']} ({mem['layer']}): {mem['content']}"
            )
            if mem.get("metadata"):
                formatted.append(f"  Metadata: {mem['metadata']}")

        return [
            TextContent(
                type="text", text=f"Found {len(memories)} memories:\n\n" + "\n\n".join(formatted)
            )
        ]

    elif name == "update_current_task":
        memory_backend.update_current_task(
            agent=arguments["agent_name"],
            task=arguments.get("task"),
            status=arguments.get("status"),
            metadata=arguments.get("metadata", {}),
        )
        return [
            TextContent(
                type="text",
                text=f"Current task updated for {arguments['agent_name']}",
            )
        ]

    elif name == "get_current_task":
        task = memory_backend.get_current_task(arguments["agent_name"])
        if task:
            return [
                TextContent(
                    type="text",
                    text=f"Current task for {arguments['agent_name']}:\n"
                    f"Task: {task.task}\n"
                    f"Status: {task.status}\n"
                    f"Started: {task.started}\n"
                    f"Updated: {task.updated}\n"
                    f"Metadata: {task.metadata}",
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"No current task for {arguments['agent_name']}",
                )
            ]

    elif name == "add_core_memory":
        result = memory_backend.add_core_memory(
            category=arguments["category"],
            content=arguments["content"],
            justification=arguments["justification"],
        )
        return [TextContent(type="text", text=result)]

    elif name == "get_core_memories":
        core_memories = memory_backend.get_core_memories()
        return [TextContent(type="text", text=core_memories)]

    elif name == "compress":
        result = memory_backend.compress(arguments["agent_name"])
        return [TextContent(type="text", text=result)]

    # =========================================================================
    # Relations Layer Tools
    # =========================================================================
    elif name == "create_relation":
        # Validate required fields
        required_fields = ["from_memory", "to_memory", "relation_type", "agent"]
        missing = [f for f in required_fields if f not in arguments or not arguments.get(f)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        relation_id = memory_backend.create_relation(
            from_memory=arguments["from_memory"],
            to_memory=arguments["to_memory"],
            relation_type=arguments["relation_type"],
            agent=arguments["agent"],
            confidence=arguments.get("confidence", 1.0),
            context=arguments.get("context", ""),
            metadata=arguments.get("metadata", {}),
        )
        return [
            TextContent(
                type="text",
                text=f"Relation created successfully.\n"
                f"ID: {relation_id}\n"
                f"Type: {arguments['relation_type']}\n"
                f"From: {arguments['from_memory']}\n"
                f"To: {arguments['to_memory']}",
            )
        ]

    elif name == "find_relations":
        relations = memory_backend.find_relations(
            relation_type=arguments.get("relation_type"),
            agent=arguments.get("agent"),
            from_memory=arguments.get("from_memory"),
            to_memory=arguments.get("to_memory"),
            min_confidence=arguments.get("min_confidence", 0.0),
            limit=arguments.get("limit", 100),
        )

        if not relations:
            return [TextContent(type="text", text="No relations found.")]

        # Format relations for display
        formatted = []
        for rel in relations:
            formatted.append(
                f"[{rel['relation_type']}] {rel['from_memory']} → {rel['to_memory']}\n"
                f"  Agent: {rel['agent']}, Confidence: {rel['confidence']}\n"
                f"  Context: {rel.get('context', 'N/A')}"
            )

        return [
            TextContent(
                type="text",
                text=f"Found {len(relations)} relations:\n\n" + "\n\n".join(formatted),
            )
        ]

    elif name == "discover_patterns":
        patterns = memory_backend.discover_patterns(
            min_occurrences=arguments.get("min_occurrences", 3),
            agent=arguments.get("agent"),
        )

        if not patterns:
            return [
                TextContent(
                    type="text",
                    text="No recurring patterns found. Patterns appear when relation_types repeat 3+ times.",
                )
            ]

        # Format patterns for display
        formatted = []
        for pattern in patterns:
            cross_agent_marker = " 🔄" if pattern["cross_agent"] else ""
            formatted.append(
                f"**{pattern['relation_type']}** ({pattern['count']} occurrences){cross_agent_marker}\n"
                f"  Agents: {', '.join(pattern['agents'])}\n"
                f"  Examples:\n" +
                "\n".join(f"    - {ex['from']} → {ex['to']}" for ex in pattern["examples"])
            )

        return [
            TextContent(
                type="text",
                text=f"🔍 DISCOVERED PATTERNS (potential vasanas):\n\n" + "\n\n".join(formatted) +
                "\n\n---\nPatterns marked with 🔄 appear across multiple agents (stronger signal).",
            )
        ]

    elif name == "get_relation_types":
        types = memory_backend.get_relation_types()

        if not types:
            return [TextContent(type="text", text="No relation types found yet.")]

        return [
            TextContent(
                type="text",
                text=f"Existing relation types ({len(types)}):\n" + "\n".join(f"  - {t}" for t in types),
            )
        ]

    # =========================================================================
    # Entity Query Layer Tools - Raw relation dumps (kg-memory compatible)
    # =========================================================================
    elif name == "get_entity":
        result = memory_backend.get_entity(arguments["name"])

        outgoing_count = len(result["outgoing_relations"])
        incoming_count = len(result["incoming_relations"])

        if outgoing_count == 0 and incoming_count == 0:
            return [
                TextContent(
                    type="text",
                    text=f"No relations found for entity '{arguments['name']}'.",
                )
            ]

        import json
        return [
            TextContent(
                type="text",
                text=f"Entity: {result['name']}\n"
                f"Outgoing relations: {outgoing_count}\n"
                f"Incoming relations: {incoming_count}\n\n"
                f"Raw data (for entity-interpreter agent):\n"
                f"{json.dumps(result, indent=2, default=str)}",
            )
        ]

    elif name == "search_nodes":
        result = memory_backend.search_nodes(arguments["query"])

        match_count = len(result["matching_relations"])

        if match_count == 0:
            return [
                TextContent(
                    type="text",
                    text=f"No relations found matching query '{arguments['query']}'.",
                )
            ]

        import json
        return [
            TextContent(
                type="text",
                text=f"Search results for: {result['query']}\n"
                f"Matching relations: {match_count}\n\n"
                f"Raw data (for entity-interpreter agent):\n"
                f"{json.dumps(result, indent=2, default=str)}",
            )
        ]

    elif name == "read_graph":
        result = memory_backend.read_graph()

        relation_count = len(result["all_relations"])

        if relation_count == 0:
            return [
                TextContent(
                    type="text",
                    text="No relations in the graph yet.",
                )
            ]

        import json
        return [
            TextContent(
                type="text",
                text=f"Complete graph: {relation_count} relations\n\n"
                f"Raw data (for entity-interpreter agent):\n"
                f"{json.dumps(result, indent=2, default=str)}",
            )
        ]

    elif name == "open_nodes":
        result = memory_backend.open_nodes(arguments["names"])

        # Count total relations across all nodes
        total_outgoing = sum(len(v["outgoing_relations"]) for v in result.values())
        total_incoming = sum(len(v["incoming_relations"]) for v in result.values())

        import json
        return [
            TextContent(
                type="text",
                text=f"Opened {len(result)} nodes\n"
                f"Total outgoing relations: {total_outgoing}\n"
                f"Total incoming relations: {total_incoming}\n\n"
                f"Raw data (for entity-interpreter agent):\n"
                f"{json.dumps(result, indent=2, default=str)}",
            )
        ]

    elif name == "delete_relations":
        deleted_count = memory_backend.delete_relations(arguments["relations"])

        return [
            TextContent(
                type="text",
                text=f"Deleted {deleted_count} relation(s).",
            )
        ]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def serve_stdio():
    """Run the MCP server with stdio transport (default, for local use)."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


async def serve_http():
    """Run the MCP server with HTTP transport (for remote/cloud deployment).

    SECURITY: This server has NO built-in authentication.
    For production, deploy behind a reverse proxy with auth:
    - Railway private networking
    - Cloudflare Access / Zero Trust
    - Nginx/Caddy with auth middleware
    """
    import mcp.server.streamable_http as streamable_http

    host = os.getenv("MCP_HOST", "0.0.0.0")

    # Validate port - fail fast on invalid config
    port_str = os.getenv("MCP_PORT", "3000")
    try:
        port = int(port_str)
        if not (1 <= port <= 65535):
            raise ValueError(f"Port {port} out of valid range (1-65535)")
    except ValueError as e:
        print(f"❌ FATAL: Invalid MCP_PORT '{port_str}': {e}")
        print("   Set a valid port number (1-65535) or remove MCP_PORT to use default 3000")
        raise SystemExit(1)

    # Security warning - this server does NOT implement auth
    print(f"🚀 Starting HTTP server on {host}:{port}")
    print("")
    print("⚠️  SECURITY: This server has NO built-in authentication.")
    print("   For production, deploy behind a reverse proxy with auth:")
    print("   - Railway private networking")
    print("   - Cloudflare Access / Zero Trust")
    print("   - Nginx/Caddy with auth middleware")
    print("")

    await streamable_http.run(app, host=host, port=port)


async def main():
    """Main entry point - selects transport based on environment."""
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "http":
        await serve_http()
    else:
        await serve_stdio()


# Backwards compatibility alias
serve = serve_stdio


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
