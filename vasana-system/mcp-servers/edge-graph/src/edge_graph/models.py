"""Data models for edge-graph system.

Core insight: Edges are verbs with weight. Patterns emerge from traversal, not declaration.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Edge(BaseModel):
    """
    An edge connecting two nodes with tracked traversal weight.

    The `verb` is intentionally a FREE STRING to enable:
    1. Domain-agnostic usage (memory, mind-maps, vasanas, content navigation)
    2. Emergent pattern naming without code changes
    3. Pattern discovery through traversal frequency

    Weight emerges from use: high-traversal edges are patterns worth formalizing.
    """

    id: str = Field(
        default_factory=lambda: f"edge-{datetime.now().timestamp()}-{uuid.uuid4().hex[:6]}"
    )
    from_node: str  # What the edge connects from
    to_node: str    # What the edge connects to
    verb: str       # The relation type (free-form, emergent)

    # Weight tracking (core innovation)
    traversal_count: int = 0
    last_traversed: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Metadata
    agent: str  # Who created this edge
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    context: str = ""
    metadata: dict = Field(default_factory=dict)

    def weighted_score(self, decay_factor: float = 0.95, days_since: int = 0) -> float:
        """
        Calculate edge weight with optional time decay.

        Formula: traversal_count * confidence * (decay_factor ^ days_since)

        Args:
            decay_factor: How much weight decays per day (0.95 = 5% per day)
            days_since: Days since last traversal (0 = today)

        Returns:
            Weighted score reflecting usage frequency and recency
        """
        base = self.traversal_count * self.confidence
        return base * (decay_factor ** days_since)

    def to_jsonl(self) -> str:
        """Convert to JSONL string."""
        import json
        return json.dumps(self.model_dump(mode="json"))

    @classmethod
    def from_jsonl(cls, line: str) -> "Edge":
        """Parse from JSONL string."""
        import json
        return cls(**json.loads(line))


class EdgeConfig(BaseModel):
    """Configuration for edge-graph system."""

    version: str = "0.1"
    storage: dict = Field(
        default_factory=lambda: {
            "backend": "local",
            "path": "~/.edge-graph",
        }
    )
    weight: dict = Field(
        default_factory=lambda: {
            "decay_factor": 0.95,
            "min_weight_for_pattern": 3,
        }
    )
