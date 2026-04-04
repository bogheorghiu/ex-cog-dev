"""
Edge-Graph MCP Server

Edge-defined graph system where patterns emerge from traversal weight, not node properties.

Core insight: Edges are verbs with weight. Patterns emerge from traversal, not declaration.

Attribution: Evolved from claude-relational-memory by @lizTheDeveloper
"""

__version__ = "0.1.0"

from .models import Edge, EdgeConfig
from .backend import EdgeBackend

__all__ = ["Edge", "EdgeConfig", "EdgeBackend"]
