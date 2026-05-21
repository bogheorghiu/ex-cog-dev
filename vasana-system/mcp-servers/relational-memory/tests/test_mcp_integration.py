#!/usr/bin/env python3
"""
Integration tests for MCP protocol communication.

Tests the actual MCP server <-> client communication, not just backend functions.
This is TDD - write tests first to define what "decent coffee" looks like!
"""

import pytest
import asyncio
import json
from pathlib import Path
import tempfile
import shutil

# MCP client utilities
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.fixture
async def memory_server(temp_memory_dir):
    """Start MCP server and return client session.

    Manual lifecycle management to avoid pytest async cleanup issues.
    """
    import os

    # Pass environment including temp directory path
    env = os.environ.copy()
    env["CLAUDE_MEMORY_PATH"] = str(temp_memory_dir)

    server_params = StdioServerParameters(
        command="python3",
        args=["-m", "claude_relational_memory"],
        env=env,
    )

    # Manually manage the client/session lifecycle
    client_exit_stack = []

    try:
        # Create client
        client_context = stdio_client(server_params)
        read, write = await client_context.__aenter__()
        client_exit_stack.append(client_context)

        # Create session
        session = ClientSession(read, write)
        await session.__aenter__()
        client_exit_stack.append(session)

        # Initialize
        await session.initialize()

        # Yield for tests
        yield session

    finally:
        # Clean up in reverse order
        for context in reversed(client_exit_stack):
            try:
                await context.__aexit__(None, None, None)
            except Exception:
                pass  # Suppress cleanup errors


@pytest.fixture
def temp_memory_dir():
    """Create temporary memory directory for testing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="mcp-test-"))
    # Override the memory location for tests
    import os
    os.environ["CLAUDE_MEMORY_PATH"] = str(temp_dir)

    yield temp_dir

    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


class TestMCPServerBasics:
    """Test basic MCP server functionality."""

    @pytest.mark.asyncio
    async def test_server_starts(self, memory_server):
        """Test that the MCP server starts and initializes."""
        assert memory_server is not None
        # If we got here, server started successfully!

    @pytest.mark.asyncio
    async def test_list_tools(self, memory_server):
        """Test that server exposes all expected tools."""
        result = await memory_server.list_tools()
        tools = result.tools
        tool_names = [tool.name for tool in tools]

        expected_tools = [
            "memorize",
            "recall",
            "update_current_task",
            "get_current_task",
            "add_core_memory",
            "get_core_memories",
            "compress",
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"

    @pytest.mark.asyncio
    async def test_tool_schemas(self, memory_server):
        """Test that tools have proper input schemas."""
        result = await memory_server.list_tools()
        tools = result.tools

        for tool in tools:
            assert "inputSchema" in tool.model_dump()
            schema = tool.inputSchema

            # Every tool should have a schema with properties
            assert "properties" in schema, f"Tool {tool.name} missing properties"

            # Verify key tools have required fields
            if tool.name == "memorize":
                props = schema["properties"]
                assert "agent_name" in props
                assert "layer" in props
                assert "content" in props

            if tool.name == "recall":
                props = schema["properties"]
                assert "agent_name" in props


class TestMemoryOperations:
    """Test actual memory operations via MCP protocol."""

    @pytest.mark.asyncio
    async def test_memorize_and_recall(self, memory_server):
        """Test storing and retrieving a memory."""
        # Store a memory
        result = await memory_server.call_tool(
            "memorize",
            {
                "agent_name": "test-agent",
                "layer": "recent",
                "content": "Integration test memory entry",
                "metadata": {"test": True},
            },
        )

        assert result is not None
        # Check result contains success message
        assert len(result.content) > 0
        assert "successfully" in result.content[0].text.lower()

        # Retrieve the memory
        recall_result = await memory_server.call_tool(
            "recall",
            {
                "agent_name": "test-agent",
                "layers": ["recent"],
                "limit": 10,
            },
        )

        assert recall_result is not None
        recall_text = recall_result.content[0].text

        # Should contain our memory
        assert "Integration test memory entry" in recall_text

    @pytest.mark.asyncio
    async def test_current_task_workflow(self, memory_server):
        """Test current task update and retrieval."""
        # Update current task
        update_result = await memory_server.call_tool(
            "update_current_task",
            {
                "agent_name": "test-agent",
                "task": "Write integration tests",
                "status": "in_progress",
                "metadata": {"priority": "high"},
            },
        )

        assert update_result is not None
        assert "updated" in update_result.content[0].text.lower()

        # Get current task
        get_result = await memory_server.call_tool(
            "get_current_task",
            {
                "agent_name": "test-agent",
            },
        )

        assert get_result is not None
        task_text = get_result.content[0].text

        assert "Write integration tests" in task_text
        assert "in_progress" in task_text

    @pytest.mark.asyncio
    async def test_core_memories(self, memory_server):
        """Test core memory operations."""
        # Get initial core memories
        initial_result = await memory_server.call_tool("get_core_memories", {})

        assert initial_result is not None
        initial_text = initial_result.content[0].text
        assert "Core Memories" in initial_text

        # Add a core memory
        add_result = await memory_server.call_tool(
            "add_core_memory",
            {
                "category": "learning",
                "content": "Integration tests are essential for decent coffee",
                "justification": "Test-driven development best practice",
            },
        )

        assert add_result is not None
        assert "added" in add_result.content[0].text.lower()

        # Verify it was added
        updated_result = await memory_server.call_tool("get_core_memories", {})
        updated_text = updated_result.content[0].text

        assert "Integration tests are essential" in updated_text


class TestMemoryPersistence:
    """Test that memories persist correctly."""

    @pytest.mark.asyncio
    async def test_memory_persists_across_calls(self, memory_server):
        """Test that stored memories survive multiple calls."""
        agent_name = "persistence-test-agent"

        # Store multiple memories
        for i in range(3):
            await memory_server.call_tool(
                "memorize",
                {
                    "agent_name": agent_name,
                    "layer": "recent",
                    "content": f"Memory entry {i}",
                    "metadata": {"index": i},
                },
            )

        # Recall all
        result = await memory_server.call_tool(
            "recall",
            {
                "agent_name": agent_name,
                "layers": ["recent"],
                "limit": 10,
            },
        )

        result_text = result.content[0].text

        # All three memories should be present
        assert "Memory entry 0" in result_text
        assert "Memory entry 1" in result_text
        assert "Memory entry 2" in result_text


class TestEpisodicCompression:
    """Test episodic memory compression."""

    @pytest.mark.asyncio
    async def test_compress_trigger(self, memory_server):
        """Test manual compression trigger."""
        agent_name = "compress-test-agent"

        # Store some episodic memories
        for i in range(5):
            await memory_server.call_tool(
                "memorize",
                {
                    "agent_name": agent_name,
                    "layer": "episodic",
                    "content": f"Completed task {i}: implemented feature X{i}",
                    "metadata": {"task_id": f"TASK-{i}"},
                },
            )

        # Try to compress (won't work yet, need 10 entries)
        compress_result = await memory_server.call_tool(
            "compress",
            {
                "agent_name": agent_name,
            },
        )

        result_text = compress_result.content[0].text
        # Should say not enough entries
        assert "5 entries" in result_text or "Only 5" in result_text


class TestSemanticSearch:
    """Test semantic search functionality."""

    @pytest.mark.asyncio
    async def test_search_with_query(self, memory_server):
        """Test that query parameter filters results."""
        agent_name = "search-test-agent"

        # Store diverse memories
        memories = [
            "Fixed critical security vulnerability in authentication",
            "Updated documentation for API endpoints",
            "Refactored database connection pooling",
            "Added rate limiting to prevent DDoS attacks",
        ]

        for mem in memories:
            await memory_server.call_tool(
                "memorize",
                {
                    "agent_name": agent_name,
                    "layer": "recent",
                    "content": mem,
                },
            )

        # Search for security-related memories
        result = await memory_server.call_tool(
            "recall",
            {
                "agent_name": agent_name,
                "query": "security vulnerability",
                "layers": ["recent"],
                "limit": 5,
            },
        )

        result_text = result.content[0].text

        # Should prioritize security-related memories
        assert "security" in result_text.lower() or "vulnerability" in result_text.lower()


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_layer(self, memory_server):
        """Test handling of invalid layer name."""
        # Try invalid layer - should either error or handle gracefully
        try:
            result = await memory_server.call_tool(
                "memorize",
                {
                    "agent_name": "test",
                    "layer": "invalid-layer",  # Not a valid layer
                    "content": "test",
                },
            )
            # If it doesn't error, check if it handled gracefully
            assert result is not None
        except Exception as e:
            # Expected - validation should catch this
            assert "invalid" in str(e).lower() or "layer" in str(e).lower()

    @pytest.mark.asyncio
    async def test_missing_required_field(self, memory_server):
        """Test handling of missing required fields."""
        # MCP protocol validation: missing required fields should error
        # Note: MCP might provide default empty values, so we validate both
        # 1. Exception raised (strict validation)
        # 2. Error message in response (graceful validation)

        try:
            result = await memory_server.call_tool(
                "memorize",
                {
                    "agent_name": "test",
                    "layer": "recent",
                    # Missing 'content' field!
                },
            )
            # Check if result contains error message
            result_text = result.content[0].text if result.content else ""
            if "error" in result_text.lower() or "missing" in result_text.lower() or "required" in result_text.lower():
                # Graceful error handling - acceptable
                pass
            else:
                # No error at all - this is the bug we're testing for
                pytest.fail(f"Should have raised error for missing content field. Got: {result_text[:100]}")
        except Exception as e:
            # Expected - strict validation raised exception
            assert "content" in str(e).lower() or "required" in str(e).lower() or "missing" in str(e).lower()

    @pytest.mark.asyncio
    async def test_recall_nonexistent_agent(self, memory_server):
        """Test recalling from non-existent agent."""
        result = await memory_server.call_tool(
            "recall",
            {
                "agent_name": "nonexistent-agent-12345",
                "layers": ["recent"],
            },
        )

        # Should return empty result, not error
        assert result is not None
        result_text = result.content[0].text
        assert "no memories" in result_text.lower() or "0 memories" in result_text.lower()


# Decent Coffee Checklist ☕
"""
What makes this "decent coffee"?

✅ Server starts reliably
✅ All tools are exposed
✅ Tools have proper schemas
✅ Can store memories
✅ Can retrieve memories
✅ Memories persist
✅ Current task tracking works
✅ Core memories work
✅ Search/filtering works
✅ Error handling is graceful

If all these pass → Decent coffee achieved! ☕
"""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
