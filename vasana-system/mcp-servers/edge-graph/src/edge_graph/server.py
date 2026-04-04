"""MCP Server for Edge-Graph System.

Edge-defined graph where patterns emerge from traversal weight, not node properties.
Self-contained - no dependencies on other monorepo code.
"""

import json
import os
from typing import List
from mcp.server import Server
from mcp.types import Tool, TextContent

from .backend import EdgeBackend


# Initialize backend
edge_backend = EdgeBackend()

# Create MCP server
app = Server("edge-graph")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available edge-graph tools."""
    return [
        # =====================================================================
        # Core Edge Operations
        # =====================================================================
        Tool(
            name="create_edge",
            description=(
                "Create an edge connecting two nodes. The verb is a FREE STRING "
                "enabling emergent pattern discovery. Weight starts at 0 and grows "
                "through traverse_edge calls."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "from_node": {
                        "type": "string",
                        "description": "Source node (concept, entity, idea)",
                    },
                    "to_node": {
                        "type": "string",
                        "description": "Target node",
                    },
                    "verb": {
                        "type": "string",
                        "description": "Relation type (free-form: 'relates_to', 'blocks', 'enables', etc.)",
                    },
                    "agent": {
                        "type": "string",
                        "description": "Who/what created this edge",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "0-1 confidence score (default 1.0)",
                        "default": 1.0,
                    },
                    "context": {
                        "type": "string",
                        "description": "Why this edge was created",
                        "default": "",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional data",
                        "default": {},
                    },
                },
                "required": ["from_node", "to_node", "verb", "agent"],
            },
        ),
        Tool(
            name="traverse_edge",
            description=(
                "Record a traversal of an edge. This is how patterns emerge: "
                "edges that get traversed often have higher weight and surface "
                "in pattern discovery. Call this every time an edge is 'used'."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "edge_id": {
                        "type": "string",
                        "description": "ID of the edge to traverse",
                    },
                },
                "required": ["edge_id"],
            },
        ),
        Tool(
            name="get_edge",
            description="Get an edge by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "edge_id": {
                        "type": "string",
                        "description": "ID of the edge",
                    },
                },
                "required": ["edge_id"],
            },
        ),
        # =====================================================================
        # Weight-Based Discovery (Core Innovation)
        # =====================================================================
        Tool(
            name="find_heavy_edges",
            description=(
                "Find edges with highest traversal weight. These are the patterns "
                "worth examining - frequently used connections that may deserve "
                "formalization (skills, abstractions, etc)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum edges to return",
                        "default": 10,
                    },
                    "verb": {
                        "type": "string",
                        "description": "Filter to specific verb type",
                    },
                    "min_weight": {
                        "type": "number",
                        "description": "Minimum traversal count",
                        "default": 0,
                    },
                },
            },
        ),
        Tool(
            name="discover_patterns",
            description=(
                "Find recurring verb patterns with weight tracking. "
                "Returns verbs sorted by total_weight across all edges. "
                "High-weight patterns are candidates for formalization."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "min_occurrences": {
                        "type": "integer",
                        "description": "Minimum edges with this verb (default: 3)",
                        "default": 3,
                    },
                    "min_weight": {
                        "type": "number",
                        "description": "Minimum total weight across all edges of this verb",
                        "default": 0,
                    },
                    "agent": {
                        "type": "string",
                        "description": "Filter to specific agent",
                    },
                },
            },
        ),
        # =====================================================================
        # Query Operations
        # =====================================================================
        Tool(
            name="find_edges",
            description="Query edges with flexible filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "verb": {
                        "type": "string",
                        "description": "Filter by verb type",
                    },
                    "agent": {
                        "type": "string",
                        "description": "Filter by creating agent",
                    },
                    "from_node": {
                        "type": "string",
                        "description": "Filter by source node",
                    },
                    "to_node": {
                        "type": "string",
                        "description": "Filter by target node",
                    },
                    "min_confidence": {
                        "type": "number",
                        "description": "Minimum confidence threshold",
                        "default": 0.0,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results",
                        "default": 100,
                    },
                },
            },
        ),
        Tool(
            name="get_verbs",
            description="Get all unique verbs in the graph. Useful for exploring vocabulary.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        # =====================================================================
        # Node/Entity Queries
        # =====================================================================
        Tool(
            name="get_node",
            description="Get all edges involving a node (both outgoing and incoming).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Node name to query",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="search_nodes",
            description="Search for nodes/edges matching a query string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="read_graph",
            description="Get all edges in the graph.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""

    # =========================================================================
    # Core Edge Operations
    # =========================================================================
    if name == "create_edge":
        required = ["from_node", "to_node", "verb", "agent"]
        missing = [f for f in required if f not in arguments or not arguments.get(f)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        # Validate non-empty strings for required fields
        empty = [f for f in required if not str(arguments.get(f, "")).strip()]
        if empty:
            raise ValueError(f"Required fields cannot be empty: {', '.join(empty)}")

        edge_id = edge_backend.create_edge(
            from_node=arguments["from_node"],
            to_node=arguments["to_node"],
            verb=arguments["verb"],
            agent=arguments["agent"],
            confidence=arguments.get("confidence", 1.0),
            context=arguments.get("context", ""),
            metadata=arguments.get("metadata", {}),
        )
        return [
            TextContent(
                type="text",
                text=f"Edge created.\nID: {edge_id}\n"
                f"[{arguments['from_node']}] --{arguments['verb']}--> [{arguments['to_node']}]",
            )
        ]

    elif name == "traverse_edge":
        if "edge_id" not in arguments:
            raise ValueError("Missing required field: edge_id")
        if not str(arguments.get("edge_id", "")).strip():
            raise ValueError("edge_id cannot be empty")

        success = edge_backend.traverse_edge(arguments["edge_id"])
        if success:
            edge = edge_backend.get_edge(arguments["edge_id"])
            return [
                TextContent(
                    type="text",
                    text=f"Edge traversed.\nID: {arguments['edge_id']}\n"
                    f"New weight: {edge.traversal_count}",
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Edge not found: {arguments['edge_id']}",
                )
            ]

    elif name == "get_edge":
        if "edge_id" not in arguments:
            raise ValueError("Missing required field: edge_id")
        if not str(arguments.get("edge_id", "")).strip():
            raise ValueError("edge_id cannot be empty")

        edge = edge_backend.get_edge(arguments["edge_id"])
        if edge:
            return [
                TextContent(
                    type="text",
                    text=f"Edge: {edge.id}\n"
                    f"[{edge.from_node}] --{edge.verb}--> [{edge.to_node}]\n"
                    f"Weight: {edge.traversal_count} traversals\n"
                    f"Confidence: {edge.confidence}\n"
                    f"Agent: {edge.agent}\n"
                    f"Created: {edge.created_at}\n"
                    f"Last traversed: {edge.last_traversed or 'never'}",
                )
            ]
        else:
            return [TextContent(type="text", text=f"Edge not found: {arguments['edge_id']}")]

    # =========================================================================
    # Weight-Based Discovery
    # =========================================================================
    elif name == "find_heavy_edges":
        edges = edge_backend.find_heavy_edges(
            limit=arguments.get("limit", 10),
            verb=arguments.get("verb"),
            min_weight=arguments.get("min_weight", 0),
        )

        if not edges:
            return [TextContent(type="text", text="No heavy edges found.")]

        formatted = []
        for e in edges:
            formatted.append(
                f"w:{e.traversal_count} | [{e.from_node}] --{e.verb}--> [{e.to_node}]"
            )

        return [
            TextContent(
                type="text",
                text=f"Heavy edges (by traversal weight):\n\n" + "\n".join(formatted),
            )
        ]

    elif name == "discover_patterns":
        patterns = edge_backend.discover_patterns(
            min_occurrences=arguments.get("min_occurrences", 3),
            min_weight=arguments.get("min_weight", 0),
            agent=arguments.get("agent"),
        )

        if not patterns:
            return [
                TextContent(
                    type="text",
                    text="No patterns found. Patterns emerge when verbs repeat across edges.",
                )
            ]

        formatted = []
        for p in patterns:
            cross = " (cross-agent)" if p["cross_agent"] else ""
            formatted.append(
                f"**{p['verb']}** (count: {p['count']}, weight: {p['total_weight']}){cross}\n"
                f"  Agents: {', '.join(p['agents'])}\n"
                f"  Examples:\n"
                + "\n".join(f"    [{ex['from']}] -> [{ex['to']}] (w:{ex['weight']})" for ex in p["examples"])
            )

        return [
            TextContent(
                type="text",
                text=f"PATTERNS (by total weight):\n\n" + "\n\n".join(formatted),
            )
        ]

    # =========================================================================
    # Query Operations
    # =========================================================================
    elif name == "find_edges":
        edges = edge_backend.find_edges(
            verb=arguments.get("verb"),
            agent=arguments.get("agent"),
            from_node=arguments.get("from_node"),
            to_node=arguments.get("to_node"),
            min_confidence=arguments.get("min_confidence", 0.0),
            limit=arguments.get("limit", 100),
        )

        if not edges:
            return [TextContent(type="text", text="No edges found.")]

        return [
            TextContent(
                type="text",
                text=f"Found {len(edges)} edges:\n\n{json.dumps(edges, indent=2, default=str)}",
            )
        ]

    elif name == "get_verbs":
        verbs = edge_backend.get_verbs()

        if not verbs:
            return [TextContent(type="text", text="No verbs found yet.")]

        return [
            TextContent(
                type="text",
                text=f"Verbs in graph ({len(verbs)}):\n" + "\n".join(f"  - {v}" for v in verbs),
            )
        ]

    # =========================================================================
    # Node/Entity Queries
    # =========================================================================
    elif name == "get_node":
        if "name" not in arguments:
            raise ValueError("Missing required field: name")
        if not str(arguments.get("name", "")).strip():
            raise ValueError("name cannot be empty")

        result = edge_backend.get_node(arguments["name"])

        out_count = len(result["outgoing"])
        in_count = len(result["incoming"])

        if out_count == 0 and in_count == 0:
            return [TextContent(type="text", text=f"No edges for node '{arguments['name']}'.")]

        return [
            TextContent(
                type="text",
                text=f"Node: {result['name']}\n"
                f"Outgoing: {out_count} edges\n"
                f"Incoming: {in_count} edges\n\n"
                f"{json.dumps(result, indent=2, default=str)}",
            )
        ]

    elif name == "search_nodes":
        if "query" not in arguments:
            raise ValueError("Missing required field: query")
        if not str(arguments.get("query", "")).strip():
            raise ValueError("query cannot be empty")

        result = edge_backend.search_nodes(arguments["query"])
        count = len(result["matching_edges"])

        if count == 0:
            return [TextContent(type="text", text=f"No matches for '{arguments['query']}'.")]

        return [
            TextContent(
                type="text",
                text=f"Search: {result['query']}\n"
                f"Matches: {count}\n\n"
                f"{json.dumps(result, indent=2, default=str)}",
            )
        ]

    elif name == "read_graph":
        result = edge_backend.read_graph()
        count = len(result["all_edges"])

        if count == 0:
            return [TextContent(type="text", text="Graph is empty.")]

        return [
            TextContent(
                type="text",
                text=f"Complete graph: {count} edges\n\n"
                f"{json.dumps(result, indent=2, default=str)}",
            )
        ]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# =============================================================================
# Server Entry Points
# =============================================================================

async def serve_stdio():
    """Run with stdio transport (default, for local use)."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


async def serve_http():
    """Run with HTTP transport (for remote deployment).

    SECURITY: No built-in auth. Deploy behind reverse proxy with auth.
    """
    import mcp.server.streamable_http as streamable_http

    host = os.getenv("MCP_HOST", "0.0.0.0")
    port_str = os.getenv("MCP_PORT", "3000")

    try:
        port = int(port_str)
        if not (1 <= port <= 65535):
            raise ValueError(f"Port {port} out of range")
    except ValueError as e:
        print(f"Invalid MCP_PORT '{port_str}': {e}")
        raise SystemExit(1)

    print(f"Edge-Graph MCP starting on {host}:{port}")
    print("")
    print("⚠️  SECURITY WARNING ⚠️")
    print("No authentication is implemented.")
    print("DO NOT expose to internet without a reverse proxy with auth.")
    print("See README.md for deployment guidance.")
    print("")

    await streamable_http.run(app, host=host, port=port)


async def main():
    """Main entry point - selects transport based on MCP_TRANSPORT env var."""
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "http":
        await serve_http()
    else:
        await serve_stdio()


# Backwards compatibility
serve = serve_stdio


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
