#!/usr/bin/env python3
"""Tests for the ephemeral-storage persistence warning (handoff Task 4).

Covers the local/persistent-disk-only declaration that warns an agent, before
it trusts the store, that memories won't survive an ephemeral session:
  - _storage_is_ephemeral() detection (env + container marker, injected)
  - consume_persistence_warning() one-shot semantics + content
  - the call_tool wrapper prepending the warning to the first tool response

Needs mcp/pydantic, so it runs via uvx in CI:
    uvx --from <server> python test_persistence_warning.py
"""

import asyncio
import tempfile

from claude_relational_memory.backend import LocalFileBackend, EPHEMERAL_ENV_MARKERS

failures = []


def check(name, cond):
    if cond:
        print(f"   ✓ {name}")
    else:
        print(f"   ✗ {name}")
        failures.append(name)


def test_detector():
    print("\n1. _storage_is_ephemeral() detection (injected env/container)")
    b = LocalFileBackend(base_path=tempfile.mkdtemp())

    # An explicit CLAUDE_MEMORY_PATH is checked first and short-circuits to
    # False, even when ephemeral markers and the container marker are present.
    check(
        "explicit CLAUDE_MEMORY_PATH suppresses (even with CI + container)",
        b._storage_is_ephemeral(
            env={"CLAUDE_MEMORY_PATH": "/durable", "CI": "1"}, container_present=True
        )
        is False,
    )

    # Default path + any single ephemeral marker -> ephemeral.
    for m in EPHEMERAL_ENV_MARKERS:
        check(
            f"marker {m} -> ephemeral",
            b._storage_is_ephemeral(env={m: "1"}, container_present=False) is True,
        )

    # Default path, no markers, no container -> NOT ephemeral (no false alarm).
    check(
        "clean env + no container -> not ephemeral",
        b._storage_is_ephemeral(env={}, container_present=False) is False,
    )

    # Default path + container marker alone -> ephemeral.
    check(
        "container marker alone -> ephemeral",
        b._storage_is_ephemeral(env={}, container_present=True) is True,
    )

    # Empty-string env values are falsy and must not trip the detector.
    check(
        "empty-string marker value is falsy",
        b._storage_is_ephemeral(env={"CI": ""}, container_present=False) is False,
    )


def test_consume_warning():
    print("\n2. consume_persistence_warning() one-shot semantics + content")
    tmp = tempfile.mkdtemp()
    b = LocalFileBackend(base_path=tmp)

    # Force the pending state directly; detection itself is covered above.
    b._persistence_warning_pending = True
    w = b.consume_persistence_warning()
    check("first call returns a warning", bool(w))
    check("warning names the actual storage path", tmp in w)
    for needle in ("ephemeral", "local/persistent-disk", "CLAUDE_MEMORY_PATH"):
        check(f"warning mentions '{needle}'", needle in w)
    check("second call returns '' (fires once)", b.consume_persistence_warning() == "")

    # A non-pending backend never warns.
    b2 = LocalFileBackend(base_path=tempfile.mkdtemp())
    b2._persistence_warning_pending = False
    check("non-ephemeral backend never warns", b2.consume_persistence_warning() == "")


def test_call_tool_injection():
    print("\n3. call_tool wrapper prepends the warning to the first response only")
    from claude_relational_memory import server
    from mcp.types import TextContent

    backend = LocalFileBackend(base_path=tempfile.mkdtemp())
    backend._persistence_warning_pending = True
    backend._stale_warning_pending = False  # isolate: only the persistence warning
    server.memory_backend = backend

    # get_core_memories is a benign read that returns a TextContent list.
    first = asyncio.run(server.call_tool("get_core_memories", {}))
    check("first response is TextContent", bool(first) and isinstance(first[0], TextContent))
    check("first response carries the warning", "ephemeral" in first[0].text)

    second = asyncio.run(server.call_tool("get_core_memories", {}))
    check("second response has no warning", "ephemeral" not in second[0].text)


def test_warning_ordering():
    print("\n4. when both warnings pend, persistence is surfaced before stale")
    from claude_relational_memory import server
    from mcp.types import TextContent

    backend = LocalFileBackend(base_path=tempfile.mkdtemp())
    backend._persistence_warning_pending = True
    backend._stale_warning_pending = True
    server.memory_backend = backend

    resp = asyncio.run(server.call_tool("get_core_memories", {}))
    text = resp[0].text if resp and isinstance(resp[0], TextContent) else ""
    has_both = "ephemeral" in text and "config schema" in text
    check("both warnings present on first response", has_both)
    if has_both:
        check(
            "persistence (ephemeral) appears before stale-schema",
            text.index("ephemeral") < text.index("config schema"),
        )


if __name__ == "__main__":
    print("Testing persistence warning (handoff Task 4)...")
    test_detector()
    test_consume_warning()
    test_call_tool_injection()
    test_warning_ordering()
    if failures:
        print(f"\n❌ {len(failures)} check(s) failed: {failures}")
        raise SystemExit(1)
    print("\n✅ All persistence-warning tests passed!")
