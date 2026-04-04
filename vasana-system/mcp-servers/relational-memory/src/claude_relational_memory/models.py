"""Data models for memory system."""

import uuid
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    """A single memory entry in JSONL format."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    layer: Literal["recent", "episodic", "compost"]
    agent: str
    content: str  # Single sentence memory
    metadata: dict = Field(default_factory=dict)

    def to_jsonl(self) -> str:
        """Convert to JSONL string."""
        import json

        data = self.model_dump(mode="json")
        data["timestamp"] = data["timestamp"]  # ISO format from Pydantic
        return json.dumps(data)

    @classmethod
    def from_jsonl(cls, line: str) -> "MemoryEntry":
        """Parse from JSONL string."""
        import json

        data = json.loads(line)
        return cls(**data)


class CurrentTask(BaseModel):
    """Current task state for an agent."""

    task: str
    task_id: Optional[str] = None
    status: Literal["not_started", "in_progress", "blocked", "completed", "abandoned"] = (
        "not_started"
    )
    project: Optional[str] = None
    branch: Optional[str] = None
    started: Optional[datetime] = None
    updated: datetime = Field(default_factory=lambda: datetime.now())
    metadata: dict = Field(default_factory=dict)


class CoreMemoryCategory(str):
    """Categories for core memories."""

    PERSONALITY = "personality"
    LEARNING = "learning"
    ANTI_PATTERN = "anti-pattern"


class Relation(BaseModel):
    """
    A relation between two memories - the substrate for pattern discovery.

    The `relation_type` is intentionally a FREE STRING (not an enum) to enable:
    1. Domain-agnostic usage across different memory systems
    2. Emergent pattern naming without code changes
    3. Vasana (behavioral pattern) self-discovery through repetition

    When the same relation_type appears across multiple contexts/sessions,
    it signals a behavioral pattern worth examining.

    Example relation_types by domain:
    - Agent Memory: "task_id", "project", "builds_on", "supersedes"
    - Learning Memory: "prerequisites", "builds_on", "contradicts"
    - Conversation Memory: "follows_up", "contradicts", "elaborates"
    - Project Memory: "affects", "depends_on", "conflicts_with"
    """

    id: str = Field(default_factory=lambda: f"rel-{datetime.now().timestamp()}-{uuid.uuid4().hex[:6]}")
    from_memory: str  # Memory content hash, timestamp ID, or reference
    to_memory: str    # Memory content hash, timestamp ID, or reference
    relation_type: str  # FREE STRING - domain-specific, emergent patterns
    agent: str  # Which agent/context created this relation
    discovered_at: datetime = Field(default_factory=lambda: datetime.now())
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)  # 0-1, how certain is this relation?
    context: str = ""  # Why was this relation created?
    metadata: dict = Field(default_factory=dict)

    def to_jsonl(self) -> str:
        """Convert to JSONL string."""
        import json
        return json.dumps(self.model_dump(mode="json"))

    @classmethod
    def from_jsonl(cls, line: str) -> "Relation":
        """Parse from JSONL string."""
        import json
        return cls(**json.loads(line))


class MemoryConfig(BaseModel):
    """Configuration for memory system."""

    version: str = "1.0"
    storage: dict = Field(
        default_factory=lambda: {
            "backend": "local",
            "path": "~/.claude-memory",
            "auto_backup": True,
            "backup_path": "~/.claude-memory-backups",
        }
    )
    memory_limits: dict = Field(
        default_factory=lambda: {
            "recent_max": 20,
            "episodic_max": 10,
            "auto_summarize_at": 10,
        }
    )
    summarization: dict = Field(
        default_factory=lambda: {
            "method": "claude_agent",
            "model": "sonnet",
            "compression_ratio": 0.3,
        }
    )
    agents: dict = Field(
        default_factory=lambda: {
            "default_model": "sonnet",
            "headless_mode": True,
            "skip_permissions": True,
        }
    )
