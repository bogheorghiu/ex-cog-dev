"""
Claude Memory MCP Server

Persistent multi-layered memory system for AI agents.

Attribution: Based on autonomous development system by @lizTheDeveloper
"""

__version__ = "0.1.0"

from .server import serve
from .backend import LocalFileBackend

__all__ = ["serve", "LocalFileBackend"]
