#!/usr/bin/env python3
"""
JSON Brainstorming Infrastructure for Agent-to-Agent Communication

Minimal framework for multi-agent brainstorming sessions.
Design goal: As few rigid structures as possible - agents can extend on the fly.

Note: Claude Code users should prefer Teams (TeamCreate + SendMessage) for real-time
agent coordination. Teams provide native messaging, mid-task redirection, and shared
task lists. This module remains useful for non-Claude-Code environments or when
JSON-based session recording is needed for offline review.

Usage:
    from brainstorm import BrainstormSession

    session = BrainstormSession("memory-system-redesign")
    session.add_message("investigator", "I found...")
    session.add_message("skeptic-enforcer", "But have you considered...")
    session.save()

Directory: /tmp/claude/brainstorm/
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

BRAINSTORM_DIR = Path("/tmp/claude/brainstorm")


@dataclass
class Message:
    """A single message in the brainstorm."""
    agent: str
    content: str
    timestamp: str
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BrainstormSession:
    """
    A brainstorming session between agents.

    Minimal schema - extend via metadata as needed.
    """
    topic: str
    session_id: str = None
    agents: list = None
    messages: list = None
    created: str = None
    metadata: dict = None

    def __post_init__(self):
        if self.session_id is None:
            self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        if self.agents is None:
            self.agents = []
        if self.messages is None:
            self.messages = []
        if self.created is None:
            self.created = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def add_message(self, agent: str, content: str, **metadata) -> None:
        """Add a message from an agent."""
        if agent not in self.agents:
            self.agents.append(agent)

        msg = Message(
            agent=agent,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata if metadata else None
        )
        self.messages.append(asdict(msg))

    def get_path(self) -> Path:
        """Get the file path for this session."""
        # Sanitize topic to prevent path traversal attacks
        safe_topic = self.topic.replace('/', '_').replace('..', '').replace('\\', '_')
        return BRAINSTORM_DIR / f"{safe_topic}-{self.session_id}.json"

    def save(self) -> Path:
        """Save session to JSON file."""
        BRAINSTORM_DIR.mkdir(parents=True, exist_ok=True)
        path = self.get_path()
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
        return path

    @classmethod
    def load(cls, path: Path) -> 'BrainstormSession':
        """Load session from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def find_by_topic(cls, topic: str) -> list['BrainstormSession']:
        """Find all sessions for a topic."""
        BRAINSTORM_DIR.mkdir(parents=True, exist_ok=True)
        sessions = []
        for path in BRAINSTORM_DIR.glob(f"{topic}-*.json"):
            sessions.append(cls.load(path))
        return sorted(sessions, key=lambda s: s.created, reverse=True)

    @classmethod
    def latest(cls, topic: str) -> Optional['BrainstormSession']:
        """Get the most recent session for a topic."""
        sessions = cls.find_by_topic(topic)
        return sessions[0] if sessions else None

    def summary(self) -> str:
        """Get a brief summary of the session."""
        return (
            f"Topic: {self.topic}\n"
            f"Agents: {', '.join(self.agents)}\n"
            f"Messages: {len(self.messages)}\n"
            f"Created: {self.created}"
        )

    def as_context(self) -> str:
        """Format session as context for an agent prompt."""
        lines = [f"# Brainstorm: {self.topic}", ""]
        for msg in self.messages:
            lines.append(f"**{msg['agent']}:** {msg['content']}")
            lines.append("")
        return "\n".join(lines)


def list_sessions() -> list[dict]:
    """List all brainstorm sessions."""
    BRAINSTORM_DIR.mkdir(parents=True, exist_ok=True)
    sessions = []
    for path in BRAINSTORM_DIR.glob("*.json"):
        try:
            session = BrainstormSession.load(path)
            sessions.append({
                "topic": session.topic,
                "session_id": session.session_id,
                "agents": session.agents,
                "message_count": len(session.messages),
                "created": session.created
            })
        except (json.JSONDecodeError, OSError, KeyError) as e:
            # Skip corrupted/unreadable session files
            print(f"Warning: Could not load {path.name}: {e}", file=sys.stderr)
    return sorted(sessions, key=lambda s: s["created"], reverse=True)


def cleanup_old_sessions(days: int = 7) -> int:
    """Remove sessions older than N days."""
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=days)
    removed = 0
    for path in BRAINSTORM_DIR.glob("*.json"):
        try:
            session = BrainstormSession.load(path)
            created = datetime.fromisoformat(session.created)
            if created < cutoff:
                path.unlink()
                removed += 1
        except (json.JSONDecodeError, OSError, ValueError, KeyError) as e:
            # Skip files that can't be processed, but log for debugging
            print(f"Warning: Could not process {path.name} for cleanup: {e}", file=sys.stderr)
    return removed


# CLI interface
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Brainstorm session manager')
    parser.add_argument('--list', action='store_true', help='List all sessions')
    parser.add_argument('--topic', type=str, help='Show sessions for topic')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Remove sessions older than N days')

    args = parser.parse_args()

    if args.cleanup:
        removed = cleanup_old_sessions(args.cleanup)
        print(f"Removed {removed} old sessions")
    elif args.topic:
        sessions = BrainstormSession.find_by_topic(args.topic)
        for s in sessions:
            print(s.summary())
            print("---")
    elif args.list:
        for s in list_sessions():
            print(f"{s['topic']} ({s['session_id']}): {s['message_count']} messages by {', '.join(s['agents'])}")
    else:
        parser.print_help()
