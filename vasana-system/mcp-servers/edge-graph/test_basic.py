#!/usr/bin/env python3
"""Basic functional test of the edge-graph backend.

Exercises EdgeBackend directly: creating edges, traversal-weight tracking,
heavy-edge ranking, verb pattern discovery, filtered queries, and on-disk
persistence. Weight in this system emerges from traversal frequency, not
from declaration.
"""

from edge_graph.backend import EdgeBackend
from pathlib import Path
import shutil
import tempfile

# Use a temp directory so the test never touches a real ~/.edge-graph store.
test_dir = Path(tempfile.mkdtemp(prefix="edge-graph-test-"))
print(f"Testing in: {test_dir}")

failures = 0


def check(label: str, condition: bool) -> None:
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


try:
    backend = EdgeBackend(str(test_dir))

    # Test 1: create_edge() returns an id and stores a retrievable edge.
    print("\n1. Testing create_edge() / get_edge()...")
    edge_id = backend.create_edge(
        from_node="concept-A", to_node="concept-B", verb="enables", agent="tester"
    )
    check("create_edge returns an edge id", isinstance(edge_id, str) and edge_id.startswith("edge-"))
    edge = backend.get_edge(edge_id)
    check("get_edge round-trips the edge", edge is not None)
    check("from_node/to_node/verb persisted", edge.from_node == "concept-A" and edge.to_node == "concept-B" and edge.verb == "enables")
    check("new edge starts at traversal_count 0", edge.traversal_count == 0)

    # Test 2: traverse_edge() accrues weight (this is the core innovation).
    print("\n2. Testing traverse_edge() weight tracking...")
    for _ in range(4):
        check("traverse_edge returns True for a real edge", backend.traverse_edge(edge_id) is True)
    edge = backend.get_edge(edge_id)
    check("traversal_count accrued to 4", edge.traversal_count == 4)
    check("last_traversed is set after traversal", edge.last_traversed is not None)
    check("traverse_edge returns False for unknown id", backend.traverse_edge("edge-does-not-exist") is False)

    # Test 3: find_heavy_edges() ranks by traversal weight, descending.
    print("\n3. Testing find_heavy_edges()...")
    backend.create_edge(from_node="X", to_node="Y", verb="enables", agent="tester")  # untraversed
    heavy = backend.find_heavy_edges(limit=10)
    check("both edges returned", len(heavy) == 2)
    check("most-traversed edge ranks first", heavy[0].id == edge_id)
    check("ranking is descending by weighted score", heavy[0].weighted_score() >= heavy[1].weighted_score())
    check("min_weight filters out untraversed edges", len(backend.find_heavy_edges(min_weight=1)) == 1)

    # Test 4: discover_patterns() surfaces recurring verbs across agents.
    print("\n4. Testing discover_patterns()...")
    backend.create_edge(from_node="P", to_node="Q", verb="enables", agent="other-agent")
    patterns = backend.discover_patterns(min_occurrences=3)
    enables = next((p for p in patterns if p["verb"] == "enables"), None)
    check("'enables' surfaces as a pattern (>=3 occurrences)", enables is not None)
    check("pattern count reflects all 'enables' edges", enables and enables["count"] == 3)
    check("cross_agent flagged (two distinct agents)", enables and enables["cross_agent"] is True)

    # Test 5: find_edges() filters by node.
    print("\n5. Testing find_edges() filtering...")
    from_a = backend.find_edges(from_node="concept-A")
    check("filter by from_node returns only matching edges", len(from_a) == 1 and from_a[0]["to_node"] == "concept-B")

    # Test 6: get_verbs() returns the unique verb set.
    print("\n6. Testing get_verbs()...")
    verbs = backend.get_verbs()
    check("get_verbs returns the unique verbs", verbs == ["enables"])

    # Test 7: persistence — a fresh backend reloads edges (and their weight).
    print("\n7. Testing persistence across instances...")
    reloaded = EdgeBackend(str(test_dir))
    reloaded_edge = reloaded.get_edge(edge_id)
    check("reloaded backend finds the edge", reloaded_edge is not None)
    check("reloaded edge retains traversal_count 4", reloaded_edge.traversal_count == 4)

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    shutil.rmtree(test_dir, ignore_errors=True)
    print("✓ Cleanup complete")

raise SystemExit(1 if failures else 0)
