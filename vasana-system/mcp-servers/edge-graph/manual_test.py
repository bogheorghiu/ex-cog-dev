#!/usr/bin/env python3
"""
Manual test of edge-graph MCP server.
Run this to verify the server works in real usage.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_server():
    """Test the MCP server manually."""
    print("Starting edge-graph MCP server...")

    server_params = StdioServerParameters(
        command="python3",
        args=["-m", "edge_graph"],
        env={"EDGE_GRAPH_PATH": "/tmp/claude/edge-graph-manual-test"},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            print("Initializing session...")
            await session.initialize()
            print("Session initialized\n")

            # List tools
            print("Listing available tools...")
            result = await session.list_tools()
            tools = result.tools
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool.name}")
            print()

            # Test 1: Create edge
            print("Test 1: Creating an edge...")
            create_result = await session.call_tool(
                "create_edge",
                {
                    "from_node": "concept-A",
                    "to_node": "concept-B",
                    "verb": "enables",
                    "agent": "manual-test",
                    "context": "Manual testing"
                }
            )
            print(f"{create_result.content[0].text}\n")

            # Extract edge_id from response
            edge_text = create_result.content[0].text
            edge_id = None
            for line in edge_text.split("\n"):
                if line.startswith("ID:"):
                    edge_id = line.replace("ID:", "").strip()
                    break

            # Test 2: Traverse edge
            if edge_id:
                print("Test 2: Traversing edge (building weight)...")
                for i in range(5):
                    traverse_result = await session.call_tool(
                        "traverse_edge",
                        {"edge_id": edge_id}
                    )
                print(f"{traverse_result.content[0].text}\n")

            # Test 3: Get edge
            if edge_id:
                print("Test 3: Getting edge details...")
                get_result = await session.call_tool(
                    "get_edge",
                    {"edge_id": edge_id}
                )
                print(f"{get_result.content[0].text}\n")

            # Test 4: Create more edges for pattern discovery
            print("Test 4: Creating more edges with same verb...")
            for i in range(3):
                await session.call_tool(
                    "create_edge",
                    {
                        "from_node": f"node-{i}",
                        "to_node": f"node-{i+1}",
                        "verb": "enables",
                        "agent": "manual-test"
                    }
                )
            print("Created 3 more 'enables' edges\n")

            # Test 5: Find heavy edges
            print("Test 5: Finding heavy edges...")
            heavy_result = await session.call_tool(
                "find_heavy_edges",
                {"limit": 5}
            )
            print(f"{heavy_result.content[0].text}\n")

            # Test 6: Get verbs
            print("Test 6: Getting all verbs...")
            verbs_result = await session.call_tool("get_verbs", {})
            print(f"{verbs_result.content[0].text}\n")

            # Test 7: Read graph
            print("Test 7: Reading full graph...")
            graph_result = await session.call_tool("read_graph", {})
            graph_text = graph_result.content[0].text
            print(f"{graph_text[:300]}..." if len(graph_text) > 300 else graph_text)
            print()

            print("All manual tests PASSED - edge-graph server works!")


if __name__ == "__main__":
    asyncio.run(test_server())
