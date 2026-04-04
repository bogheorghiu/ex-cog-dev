#!/usr/bin/env python3
"""
Financial Data MCP Server
Clean modular architecture with dynamic tool loading.

Structure:
- tool_definitions.py: Function schemas (like C++ headers)
- implementations/: One file per function (like C++ source files)
- financial_server.py: MCP protocol handler (main entry point)
"""

import asyncio
import importlib
from mcp.server import Server
import mcp.types as types

from tool_definitions import get_tool_definitions


server = Server("financial-data-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    DISCOVERY PHASE: Tell Claude what functions are available.
    Loads tool definitions from separate file.
    """
    return get_tool_definitions()


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    EXECUTION PHASE: Dynamically load and execute the requested tool.
    
    This is the magic of the generic approach:
    - No manual registry needed
    - Adding new tools just requires creating a new file
    - File name must match tool name
    """
    try:
        # Dynamic import: implementations/{tool_name}.py
        module = importlib.import_module(f"implementations.{name}")
        
        # Every implementation file has an 'execute' function
        return await module.execute(arguments)
        
    except ModuleNotFoundError:
        raise ValueError(f"Tool implementation not found: {name}")
    except AttributeError:
        raise ValueError(f"Tool {name} missing execute function")
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Return empty resources list - this server only provides tools."""
    return []


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """Return empty prompts list - this server only provides tools."""
    return []


async def main():
    """Start the MCP server and handle communication with Claude."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main_sync():
    """Sync entry point for pyproject.toml console_scripts.

    Enables installation via:
      pip install ./financial-mcp && financial-mcp
      uvx --from git+https://...#subdirectory=.../financial-mcp financial-mcp
    """
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
