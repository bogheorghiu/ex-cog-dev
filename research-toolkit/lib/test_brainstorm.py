#!/usr/bin/env python3
"""Unit tests for brainstorm.py (JSON brainstorm session recorder).

Pure-logic tests — no network. Redirects the module's storage directory to a
temp dir so the real ~/tmp store is never touched. Exits non-zero on failure.
"""

import importlib.util
import shutil
import tempfile
from pathlib import Path

# Load brainstorm.py directly by path (it lives in lib/, not an installed pkg).
_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("brainstorm", _HERE / "brainstorm.py")
brainstorm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(brainstorm)

failures = 0


def check(label, condition):
    global failures
    if condition:
        print(f"   ✓ {label}")
    else:
        failures += 1
        print(f"   ✗ FAILED: {label}")


test_dir = Path(tempfile.mkdtemp(prefix="brainstorm-test-"))
# Redirect all storage to the temp dir for the duration of the test.
brainstorm.BRAINSTORM_DIR = test_dir
print(f"Testing in: {test_dir}")

try:
    # Test 1: a fresh session seeds its own id/created/empty collections.
    print("\n1. Testing BrainstormSession defaults...")
    session = brainstorm.BrainstormSession("memory-redesign")
    check("topic stored", session.topic == "memory-redesign")
    check("session_id auto-generated", isinstance(session.session_id, str) and session.session_id)
    check("agents starts empty", session.agents == [])
    check("messages starts empty", session.messages == [])
    check("created timestamp set", isinstance(session.created, str) and session.created)

    # Test 2: add_message records the author and tracks unique agents.
    print("\n2. Testing add_message()...")
    session.add_message("investigator", "I found a leak.")
    session.add_message("skeptic", "Have you reproduced it?", priority="high")
    session.add_message("investigator", "Yes, twice.")
    check("three messages recorded", len(session.messages) == 3)
    check("agents deduplicated", session.agents == ["investigator", "skeptic"])
    check("message metadata preserved", session.messages[1]["metadata"] == {"priority": "high"})
    # Message.__post_init__ normalizes a missing metadata (None) to an empty dict.
    check("message with no metadata defaults to {}", session.messages[0]["metadata"] == {})

    # Test 3: save() then load() round-trips the session from disk.
    print("\n3. Testing save() / load() round-trip...")
    path = session.save()
    check("save returns an existing path", path.exists())
    reloaded = brainstorm.BrainstormSession.load(path)
    check("reloaded topic matches", reloaded.topic == "memory-redesign")
    check("reloaded message count matches", len(reloaded.messages) == 3)

    # Test 4: get_path() sanitizes path-traversal characters in the topic.
    print("\n4. Testing get_path() sanitization...")
    evil = brainstorm.BrainstormSession("../../etc/passwd")
    safe_path = evil.get_path()
    check("no '..' in generated filename", ".." not in safe_path.name)
    check("no '/' in generated filename", "/" not in safe_path.name)
    check("stays within BRAINSTORM_DIR", safe_path.parent == test_dir)

    # Test 5: find_by_topic / latest locate saved sessions.
    print("\n5. Testing find_by_topic() / latest()...")
    found = brainstorm.BrainstormSession.find_by_topic("memory-redesign")
    check("find_by_topic returns the saved session", len(found) == 1)
    latest = brainstorm.BrainstormSession.latest("memory-redesign")
    check("latest returns a session", latest is not None and latest.topic == "memory-redesign")
    check("latest is None for unknown topic", brainstorm.BrainstormSession.latest("nope") is None)

    # Test 6: as_context() / summary() render without error.
    print("\n6. Testing as_context() / summary()...")
    ctx = session.as_context()
    check("as_context includes a message body", "I found a leak." in ctx)
    check("summary reports the message count", "Messages: 3" in session.summary())

    if failures == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failures} check(s) failed.")
finally:
    shutil.rmtree(test_dir, ignore_errors=True)
    print("✓ Cleanup complete")

raise SystemExit(1 if failures else 0)
