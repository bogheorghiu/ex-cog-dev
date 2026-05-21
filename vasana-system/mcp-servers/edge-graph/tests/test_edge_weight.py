"""TDD tests for edge weight tracking - written FIRST, implementation follows."""

import pytest
import shutil
import uuid
from datetime import datetime, timedelta


@pytest.fixture
def temp_backend_path(tmp_path):
    """Create unique temp directory for each test."""
    test_dir = tmp_path / f"edge-graph-{uuid.uuid4().hex[:8]}"
    test_dir.mkdir(parents=True, exist_ok=True)
    yield str(test_dir)
    # Cleanup after test
    if test_dir.exists():
        shutil.rmtree(test_dir)


class TestEdgeModel:
    """Tests for the Edge model with weight tracking."""

    def test_edge_starts_with_zero_weight(self):
        """New edges have zero traversals."""
        from edge_graph.models import Edge

        edge = Edge(from_node="A", to_node="B", verb="relates_to", agent="test")
        assert edge.traversal_count == 0
        assert edge.last_traversed is None

    def test_edge_has_verb_not_relation_type(self):
        """Edge uses 'verb' terminology, not 'relation_type'."""
        from edge_graph.models import Edge

        edge = Edge(from_node="A", to_node="B", verb="builds_on", agent="test")
        assert edge.verb == "builds_on"
        assert not hasattr(edge, 'relation_type')

    def test_edge_uses_node_not_memory_terminology(self):
        """Edge uses 'from_node/to_node', not 'from_memory/to_memory'."""
        from edge_graph.models import Edge

        edge = Edge(from_node="concept-1", to_node="concept-2", verb="relates_to", agent="test")
        assert edge.from_node == "concept-1"
        assert edge.to_node == "concept-2"
        assert not hasattr(edge, 'from_memory')
        assert not hasattr(edge, 'to_memory')

    def test_weighted_score_basic(self):
        """Edge weight calculation works."""
        from edge_graph.models import Edge

        edge = Edge(
            from_node="A", to_node="B", verb="x", agent="test",
            traversal_count=10, confidence=1.0
        )
        score = edge.weighted_score(days_since=0)
        assert score == 10.0  # 10 * 1.0 * (0.95^0) = 10

    def test_weighted_score_decays_over_time(self):
        """Edges used recently have higher weight than old ones."""
        from edge_graph.models import Edge

        edge = Edge(
            from_node="A", to_node="B", verb="x", agent="test",
            traversal_count=10, confidence=1.0
        )
        recent_weight = edge.weighted_score(days_since=0)
        old_weight = edge.weighted_score(days_since=30)
        assert recent_weight > old_weight

    def test_weighted_score_includes_confidence(self):
        """Confidence affects weight calculation."""
        from edge_graph.models import Edge

        high_conf = Edge(
            from_node="A", to_node="B", verb="x", agent="test",
            traversal_count=10, confidence=1.0
        )
        low_conf = Edge(
            from_node="A", to_node="B", verb="x", agent="test",
            traversal_count=10, confidence=0.5
        )
        assert high_conf.weighted_score() > low_conf.weighted_score()


class TestEdgeBackendTraversal:
    """Tests for backend traversal tracking."""

    def test_traverse_increments_count(self, temp_backend_path):
        """Traversing an edge increments its count."""
        from edge_graph.backend import EdgeBackend

        backend = EdgeBackend(base_path=temp_backend_path)
        edge_id = backend.create_edge("A", "B", "relates_to", "test")

        # Traverse once
        backend.traverse_edge(edge_id)
        edge = backend.get_edge(edge_id)

        assert edge.traversal_count == 1
        assert edge.last_traversed is not None

    def test_multiple_traversals_accumulate(self, temp_backend_path):
        """Multiple traversals accumulate."""
        from edge_graph.backend import EdgeBackend

        backend = EdgeBackend(base_path=temp_backend_path)
        edge_id = backend.create_edge("A", "B", "relates_to", "test")

        for _ in range(5):
            backend.traverse_edge(edge_id)

        edge = backend.get_edge(edge_id)
        assert edge.traversal_count == 5


class TestHeavyEdgeDiscovery:
    """Tests for finding heavily-used edges."""

    def test_find_heavy_edges_returns_most_traversed(self, temp_backend_path):
        """find_heavy_edges returns edges sorted by weight."""
        from edge_graph.backend import EdgeBackend

        backend = EdgeBackend(base_path=temp_backend_path)

        # Create edges with varying traversal counts
        id1 = backend.create_edge("A", "B", "link", "test")
        id2 = backend.create_edge("C", "D", "link", "test")
        id3 = backend.create_edge("E", "F", "link", "test")

        # Traverse different amounts
        for _ in range(2):
            backend.traverse_edge(id1)
        for _ in range(10):
            backend.traverse_edge(id2)
        for _ in range(50):
            backend.traverse_edge(id3)

        heavy = backend.find_heavy_edges(limit=2)

        assert len(heavy) == 2
        assert heavy[0].from_node == "E"  # Most traversed (50)
        assert heavy[1].from_node == "C"  # Second most (10)

    def test_find_heavy_edges_filters_by_verb(self, temp_backend_path):
        """Can filter heavy edges by verb type."""
        from edge_graph.backend import EdgeBackend

        backend = EdgeBackend(base_path=temp_backend_path)

        id1 = backend.create_edge("A", "B", "blocks", "test")
        id2 = backend.create_edge("C", "D", "helps", "test")

        for _ in range(10):
            backend.traverse_edge(id1)
        for _ in range(20):
            backend.traverse_edge(id2)

        # Filter to only "blocks" verbs
        heavy = backend.find_heavy_edges(verb="blocks")

        assert len(heavy) == 1
        assert heavy[0].verb == "blocks"


class TestPatternDiscoveryWithWeight:
    """Tests for pattern discovery enhanced with weight."""

    def test_discover_patterns_includes_total_weight(self, temp_backend_path):
        """discover_patterns reports total traversal weight per verb."""
        from edge_graph.backend import EdgeBackend

        backend = EdgeBackend(base_path=temp_backend_path)

        # Create multiple edges with same verb
        id1 = backend.create_edge("A", "B", "blocks", "agent1")
        id2 = backend.create_edge("C", "D", "blocks", "agent2")

        for _ in range(5):
            backend.traverse_edge(id1)
        for _ in range(10):
            backend.traverse_edge(id2)

        patterns = backend.discover_patterns(min_occurrences=1)

        blocks_pattern = next(p for p in patterns if p["verb"] == "blocks")
        assert blocks_pattern["total_weight"] == 15
        assert blocks_pattern["count"] == 2

    def test_discover_patterns_min_weight_filters(self, temp_backend_path):
        """min_weight threshold filters out low-weight patterns."""
        from edge_graph.backend import EdgeBackend

        backend = EdgeBackend(base_path=temp_backend_path)

        # Light pattern: 3 edges with low traversals (total weight = 3)
        for i in range(3):
            edge_id = backend.create_edge(f"L{i}", f"L{i+1}", "maybe_relates", "test")
            backend.traverse_edge(edge_id)  # 1 traversal each

        # Heavy pattern: 3 edges with high traversals (total weight = 150)
        for i in range(3):
            edge_id = backend.create_edge(f"H{i}", f"H{i+1}", "definitely_relates", "test")
            for _ in range(50):
                backend.traverse_edge(edge_id)  # 50 traversals each

        # With high min_weight, only heavy pattern survives
        # Both patterns have 3 edges (meet default min_occurrences=3)
        heavy_patterns = backend.discover_patterns(min_weight=30)

        assert len(heavy_patterns) == 1
        assert heavy_patterns[0]["verb"] == "definitely_relates"
        assert heavy_patterns[0]["total_weight"] == 150
