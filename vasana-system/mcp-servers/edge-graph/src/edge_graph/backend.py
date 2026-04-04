"""Edge-graph storage backend with traversal weight tracking."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from .models import Edge, EdgeConfig

logger = logging.getLogger(__name__)


class EdgeBackend:
    """
    Edge-defined graph storage with weight tracking.

    Core innovation: Patterns emerge from traversal frequency, not declaration.
    High-weight edges are patterns worth formalizing.
    """

    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            base_path = os.environ.get("EDGE_GRAPH_PATH", "~/.edge-graph")
        self.base_path = Path(base_path).expanduser()
        self._ensure_structure()
        self.config = self._load_config()

    def _ensure_structure(self):
        """Create directory structure if needed."""
        self.base_path.mkdir(parents=True, exist_ok=True)

        config_path = self.base_path / "config.json"
        if not config_path.exists():
            config = EdgeConfig()
            config_path.write_text(config.model_dump_json(indent=2))

    def _load_config(self) -> EdgeConfig:
        """Load configuration."""
        config_path = self.base_path / "config.json"
        if config_path.exists():
            return EdgeConfig(**json.loads(config_path.read_text()))
        return EdgeConfig()

    def _edges_file(self) -> Path:
        """Get the edges storage file."""
        return self.base_path / "edges.jsonl"

    # =========================================================================
    # Core Edge Operations
    # =========================================================================

    def create_edge(
        self,
        from_node: str,
        to_node: str,
        verb: str,
        agent: str,
        confidence: float = 1.0,
        context: str = "",
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Create an edge connecting two nodes.

        The verb is FREE STRING - enables emergent pattern discovery.

        Returns: Edge ID
        """
        if metadata is None:
            metadata = {}
        edge = Edge(
            from_node=from_node,
            to_node=to_node,
            verb=verb,
            agent=agent,
            confidence=confidence,
            context=context,
            metadata=metadata,
        )

        with open(self._edges_file(), "a") as f:
            f.write(edge.to_jsonl() + "\n")

        return edge.id

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by ID."""
        edges_file = self._edges_file()
        if not edges_file.exists():
            return None

        for line in edges_file.read_text().strip().split("\n"):
            if not line:
                continue
            try:
                edge = Edge.from_jsonl(line)
                if edge.id == edge_id:
                    return edge
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"Skipping malformed edge in get_edge: {e}")
                continue
        return None

    def _save_edge(self, edge: Edge):
        """Save an edge back to storage (update in place).

        Uses atomic write (temp file + rename) to prevent partial writes.
        """
        edges_file = self._edges_file()
        if not edges_file.exists():
            return

        lines = edges_file.read_text().strip().split("\n")
        updated_lines = []

        for line in lines:
            if not line:
                continue
            try:
                existing = Edge.from_jsonl(line)
                if existing.id == edge.id:
                    updated_lines.append(edge.to_jsonl())
                else:
                    updated_lines.append(line)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"Skipping malformed edge in _save_edge: {e}")
                updated_lines.append(line)

        # Atomic write: write to temp file, then rename
        content = "\n".join(updated_lines) + "\n" if updated_lines else ""
        temp_file = edges_file.with_suffix(".tmp")
        temp_file.write_text(content)
        temp_file.rename(edges_file)

    # =========================================================================
    # Traversal Tracking (Core Innovation)
    # =========================================================================

    def traverse_edge(self, edge_id: str) -> bool:
        """
        Record a traversal of an edge.

        This is how patterns emerge: edges that get traversed often
        have higher weight and surface in pattern discovery.

        Returns: True if edge found and updated, False otherwise
        """
        edge = self.get_edge(edge_id)
        if edge is None:
            return False

        edge.traversal_count += 1
        edge.last_traversed = datetime.now()
        self._save_edge(edge)
        return True

    def find_heavy_edges(
        self,
        limit: int = 10,
        verb: Optional[str] = None,
        min_weight: float = 0,
    ) -> List[Edge]:
        """
        Find edges with highest traversal weight.

        These are the patterns worth examining - frequently used connections.

        Args:
            limit: Maximum edges to return
            verb: Filter to specific verb type
            min_weight: Minimum traversal count

        Returns: List of Edge objects sorted by weight descending
        """
        edges_file = self._edges_file()
        if not edges_file.exists():
            return []

        edges = []
        for line in edges_file.read_text().strip().split("\n"):
            if not line:
                continue
            try:
                edge = Edge.from_jsonl(line)

                if verb and edge.verb != verb:
                    continue
                if edge.traversal_count < min_weight:
                    continue

                edges.append(edge)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"Skipping malformed edge in find_heavy_edges: {e}")
                continue

        # Sort by weighted score (highest first)
        edges.sort(key=lambda e: e.weighted_score(), reverse=True)
        return edges[:limit]

    # =========================================================================
    # Query Operations
    # =========================================================================

    def find_edges(
        self,
        verb: Optional[str] = None,
        agent: Optional[str] = None,
        from_node: Optional[str] = None,
        to_node: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100,
    ) -> List[dict]:
        """Query edges with flexible filtering."""
        results = []
        edges_file = self._edges_file()

        if not edges_file.exists():
            return []

        for line in edges_file.read_text().strip().split("\n"):
            if not line:
                continue

            try:
                edge = Edge.from_jsonl(line)

                if verb and edge.verb != verb:
                    continue
                if agent and edge.agent != agent:
                    continue
                if from_node and edge.from_node != from_node:
                    continue
                if to_node and edge.to_node != to_node:
                    continue
                if edge.confidence < min_confidence:
                    continue

                results.append(edge.model_dump(mode="json"))

                if len(results) >= limit:
                    break

            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"Skipping malformed edge in find_edges: {e}")
                continue

        return results

    def discover_patterns(
        self,
        min_occurrences: int = 3,
        min_weight: float = 0,
        agent: Optional[str] = None,
    ) -> List[dict]:
        """
        Find recurring verb patterns with weight tracking.

        Enhanced from relational-memory: includes total_weight across all
        edges of each verb type. High-weight patterns are candidates for
        formalization (skills, vasanas, etc).

        Args:
            min_occurrences: Minimum edges with this verb
            min_weight: Minimum total weight across all edges of this verb
            agent: Filter to specific agent

        Returns: List of {verb, count, total_weight, agents, examples, cross_agent}
        """
        edges_file = self._edges_file()

        if not edges_file.exists():
            return []

        verb_data: Dict[str, dict] = {}

        for line in edges_file.read_text().strip().split("\n"):
            if not line:
                continue

            try:
                edge = Edge.from_jsonl(line)

                if agent and edge.agent != agent:
                    continue

                v = edge.verb

                if v not in verb_data:
                    verb_data[v] = {
                        "verb": v,
                        "count": 0,
                        "total_weight": 0,
                        "agents": set(),
                        "examples": [],
                    }

                verb_data[v]["count"] += 1
                verb_data[v]["total_weight"] += edge.traversal_count
                verb_data[v]["agents"].add(edge.agent)

                if len(verb_data[v]["examples"]) < 3:
                    verb_data[v]["examples"].append({
                        "id": edge.id,
                        "from": edge.from_node,
                        "to": edge.to_node,
                        "weight": edge.traversal_count,
                    })

            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"Skipping malformed edge in discover_patterns: {e}")
                continue

        # Filter and format results
        results = []
        for data in verb_data.values():
            if data["count"] >= min_occurrences and data["total_weight"] >= min_weight:
                results.append({
                    "verb": data["verb"],
                    "count": data["count"],
                    "total_weight": data["total_weight"],
                    "agents": list(data["agents"]),
                    "examples": data["examples"],
                    "cross_agent": len(data["agents"]) > 1,
                })

        results.sort(key=lambda x: x["total_weight"], reverse=True)
        return results

    def get_verbs(self) -> List[str]:
        """Get all unique verbs in the graph."""
        edges_file = self._edges_file()

        if not edges_file.exists():
            return []

        verbs = set()
        for line in edges_file.read_text().strip().split("\n"):
            if not line:
                continue
            try:
                edge = Edge.from_jsonl(line)
                verbs.add(edge.verb)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.warning(f"Skipping malformed edge in get_verbs: {e}")
                continue

        return sorted(list(verbs))

    # =========================================================================
    # Node/Entity Queries (for graph traversal)
    # =========================================================================

    def get_node(self, name: str) -> dict:
        """Get all edges involving this node."""
        return {
            "name": name,
            "outgoing": self.find_edges(from_node=name),
            "incoming": self.find_edges(to_node=name),
        }

    def search_nodes(self, query: str) -> dict:
        """Search for nodes matching query."""
        all_edges = self.find_edges(limit=10000)
        query_lower = query.lower()

        matching = [
            e for e in all_edges
            if query_lower in str(e).lower()
        ]

        return {"query": query, "matching_edges": matching}

    def read_graph(self) -> dict:
        """Get all edges in the graph."""
        return {"all_edges": self.find_edges(limit=10000)}
