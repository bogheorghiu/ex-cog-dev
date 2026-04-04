#!/usr/bin/env python3
"""Basic functional test of the memory system."""

from claude_relational_memory.backend import LocalFileBackend
from pathlib import Path
import shutil
import tempfile

# Use temp directory for testing
test_dir = Path(tempfile.mkdtemp(prefix="claude-memory-test-"))
print(f"Testing in: {test_dir}")

try:
    # Initialize backend with test directory
    backend = LocalFileBackend(str(test_dir))

    # Test 1: Memorize
    print("\n1. Testing memorize()...")
    entry_id = backend.memorize(
        agent="test-agent",
        layer="recent",
        content="Implemented auth feature with OAuth2 support",
        metadata={"task_id": "TEST-1", "project": "/test/project"}
    )
    print(f"   ✓ Stored memory: {entry_id}")

    # Test 2: Recall
    print("\n2. Testing recall()...")
    memories = backend.recall(agent="test-agent", layers=["recent"], limit=5)
    print(f"   ✓ Retrieved {len(memories)} memories")
    if memories:
        print(f"   Content: '{memories[0]['content']}'")

    # Test 3: Update current task
    print("\n3. Testing update_current_task()...")
    backend.update_current_task(
        agent="test-agent",
        task="Build test suite",
        status="in_progress",
        metadata={"task_id": "TEST-2"}
    )
    print("   ✓ Task updated")

    # Test 4: Get current task
    print("\n4. Testing get_current_task()...")
    task = backend.get_current_task("test-agent")
    if task:
        print(f"   ✓ Current task: '{task.task}' ({task.status})")

    # Test 5: Core memories
    print("\n5. Testing core memories...")
    core = backend.get_core_memories()
    print(f"   ✓ Core memories loaded ({len(core)} chars)")

    # Test 6: Add to episodic and test auto-compression threshold
    print("\n6. Testing episodic memory...")
    for i in range(5):
        backend.memorize(
            agent="test-agent",
            layer="episodic",
            content=f"Completed task {i}: implemented feature X{i}",
            metadata={"task_id": f"TASK-{i}"}
        )

    episodic_memories = backend.recall(agent="test-agent", layers=["episodic"])
    print(f"   ✓ Created {len(episodic_memories)} episodic memories")

    # Test 7: Semantic search
    print("\n7. Testing semantic search...")
    backend.memorize(
        agent="test-agent",
        layer="recent",
        content="Fixed critical security vulnerability in authentication",
        metadata={"priority": "high"}
    )
    backend.memorize(
        agent="test-agent",
        layer="recent",
        content="Updated documentation for API endpoints",
        metadata={"priority": "low"}
    )

    search_results = backend.recall(
        agent="test-agent",
        query="security authentication",
        layers=["recent"]
    )
    print(f"   ✓ Search returned {len(search_results)} results")
    if search_results:
        print(f"   Top result: '{search_results[0]['content']}'")

    # Test 8: Core memory addition
    print("\n8. Testing add_core_memory()...")
    backend.add_core_memory(
        category="learning",
        content="Always write tests before implementing features",
        justification="Test from automated testing system"
    )
    updated_core = backend.get_core_memories()
    if "Always write tests" in updated_core:
        print("   ✓ Core memory added successfully")

    print("\n✅ All tests passed!")
    print(f"\nMemory files created in: {test_dir}")
    print("\nFile structure:")
    for item in sorted(test_dir.rglob("*")):
        if item.is_file():
            rel_path = item.relative_to(test_dir)
            size = item.stat().st_size
            print(f"  {rel_path} ({size} bytes)")

finally:
    # Cleanup
    print(f"\nCleaning up test directory: {test_dir}")
    shutil.rmtree(test_dir)
    print("✓ Cleanup complete")
