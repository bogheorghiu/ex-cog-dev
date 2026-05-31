#!/usr/bin/env python3
"""Basic functional test of the edge-graph backend.

Exercises EdgeBackend directly: recording edges, weight accumulation on
repetition, traversal, strongest-edge ranking, and on-disk persistence.
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

    # Test 1: record() creates a new edge with seeded weight/count.
    print("\n1. Testing record() creates an edge...")
    edge = backend.record(source="A", target="B", relation="leads_to")
    check("returns an edge with weight 1.0", edge.weight == 1.0)
    check("observation_count starts at 1", edge.observation_count == 1)
    check("first_seen and last_seen are set", edge.first_seen is not None and edge.last_seen is not None)

    # Test 2: repetition strengthens the same edge (weight = repetition count).
    print("\n2. Testing weight accumulation on repetition...")
    edge = backend.record(source="A", target="B", relation="leads_to")
    check("weight accumulates to 2.0", edge.weight == 2.0)
    check("observation_count increments to 2", edge.observation_count == 2)

    # Test 3: weight_delta is respected.
    print("\n3. Testing custom weight_delta...")
    edge = backend.record(source="A", target="B", relation="leads_to", weight_delta=3.0)
    check("weight reflects the delta (5.0)", edge.weight == 5.0)
    check("observation_count is now 3", edge.observation_count == 3)

    # Test 4: distinct (source, target, relation) tuples are separate edges.
    print("\n4. Testing distinct edges stay separate...")
    backend.record(source="B", target="C", relation="leads_to")
    backend.record(source="A", target="B", relation="contradicts")
    strongest = backend.strongest_edges()
    check("three distinct edges recorded", len(strongest) == 3)
    check("strongest edge is A->B leads_to (weight 5.0)", strongest[0]["weight"] == 5.0)
    check("strongest_edges is sorted descending", strongest[0]["weight"] >= strongest[-1]["weight"])

    # Test 5: traverse() follows edges above min_weight.
    print("\n5. Testing traverse()...")
    reachable = backend.traverse(start="A", min_weight=0.0)
    targets = {r["edge"]["target"] for r in reachable}
    check("traversal from A reaches B", "B" in targets)
    check("traversal from A reaches C (via B)", "C" in targets)
    filtered = backend.traverse(start="A", min_weight=2.0)
    weak_kept = [r for r in filtered if r["edge"]["weight"] < 2.0]
    check("min_weight filters out weak edges", len(weak_kept) == 0)

    # Test 6: persistence — a fresh backend reloads the same edges from disk.
    print("\n6. Testing persistence across instances...")
    reloaded = EdgeBackend(str(test_dir))
    reloaded_strongest = reloaded.strongest_edges()
    check("reloaded backend sees all 3 edges", len(reloaded_strongest) == 3)
    check("reloaded A->B leads_to retains weight 5.0", reloaded_strongest[0]["weight"] == 5.0)

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    shutil.rmtree(test_dir, ignore_errors=True)
    print("✓ Cleanup complete")

raise SystemExit(1 if failures else 0)
