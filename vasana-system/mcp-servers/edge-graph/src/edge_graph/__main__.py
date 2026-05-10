"""Entry point for the MCP server."""

import asyncio
from .server import serve


def main() -> None:
    asyncio.run(serve())


if __name__ == "__main__":
    main()
