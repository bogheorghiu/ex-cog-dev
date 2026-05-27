"""Storage backend implementations for memory system."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
from .models import MemoryEntry, CurrentTask, MemoryConfig, Relation
from .claude_agent import ClaudeAgent


# Schema version expected by this code. _load_config warns (but does NOT
# mutate) when the on-disk config has an older version. See migrate_config
# for the opt-in upgrade path.
CURRENT_CONFIG_SCHEMA = "1.1"


def _version_tuple(v: str) -> tuple[int, ...]:
    """Parse a dotted version string into a tuple of ints for comparison.

    Avoids the string-ordering trap where "1.9" > "1.10" alphabetically.
    Returns (0,) for unparseable strings — older-than-anything fallback.
    """
    try:
        return tuple(int(p) for p in v.split("."))
    except (ValueError, AttributeError):
        return (0,)


class LocalFileBackend:
    """Stores memories in local JSONL files at ~/.claude-memory/"""

    def __init__(self, base_path: str | None = None):
        # Respect CLAUDE_MEMORY_PATH environment variable for testing
        if base_path is None:
            base_path = os.environ.get("CLAUDE_MEMORY_PATH", "~/.claude-memory")
        self.base_path = Path(base_path).expanduser()
        self._ensure_structure()
        self.config = self._load_config()

        # Per-agent compaction failure flag. When True, auto-compaction
        # is skipped for that agent (still allowed via manual compress()).
        # Set by compress() on summarization failure; cleared on success.
        # In-memory only — resets on server restart, providing a natural
        # retry cadence per session without spamming on every write.
        self._compaction_failed: dict[str, bool] = {}

        # Stale-schema warning surfacing. PR #426 prints a warning to
        # stderr when config schema is older than CURRENT_CONFIG_SCHEMA,
        # but stderr from MCP subprocesses doesn't reach the Claude Code
        # UI — it's captured to daemon logs the user never sees. This
        # flag + consume_stale_warning() below makes the warning part of
        # the first MCP tool response of the session, so the agent
        # actually surfaces it. Cleared on success or after first emit.
        self._stale_warning_pending: bool = (
            _version_tuple(self.config.version)
            < _version_tuple(CURRENT_CONFIG_SCHEMA)
        )

    def consume_stale_warning(self) -> str:
        """Return the stale-schema warning ONCE per Backend instance.

        Subsequent calls return ''. Cleared on successful migrate_config
        too so a fresh post-migration session never warns. Called by the
        server's call_tool wrapper to inject the warning into the first
        tool response of the session.
        """
        if not self._stale_warning_pending:
            return ""
        self._stale_warning_pending = False
        return (
            f"\n\n⚠️  rel-mem: your config schema is v{self.config.version} "
            f"(current v{CURRENT_CONFIG_SCHEMA}). Call the `migrate_config` "
            f"MCP tool to apply new defaults — user-customized values are "
            f"preserved.\n\n"
        )

    def _ensure_structure(self):
        """Create directory structure if it doesn't exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "agents").mkdir(exist_ok=True)

        # Create default config if missing
        config_path = self.base_path / "config.json"
        if not config_path.exists():
            config = MemoryConfig()
            config_path.write_text(config.model_dump_json(indent=2))

        # Create default core memories if missing
        core_path = self.base_path / "core-memories.md"
        if not core_path.exists():
            core_path.write_text(self._default_core_memories())

        # Create memory index if missing
        index_path = self.base_path / "memory-index.json"
        if not index_path.exists():
            index_path.write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "last_updated": datetime.now().isoformat(),
                        "agents": {},
                        "statistics": {
                            "total_memories": 0,
                            "total_agents": 0,
                            "total_projects": 0,
                        },
                    },
                    indent=2,
                )
            )

    def _load_config(self) -> MemoryConfig:
        """Load configuration from config.json.

        Passive migration policy: if the on-disk config's schema version
        is older than CURRENT_CONFIG_SCHEMA, print a one-line warning to
        stderr suggesting the migrate_config MCP tool. Never mutates user
        config without explicit user action (call to migrate_config).
        Respects users who set their own thresholds intentionally.
        """
        config_path = self.base_path / "config.json"
        if not config_path.exists():
            # Fresh install — defaults from MemoryConfig() (current schema).
            return MemoryConfig()

        try:
            raw = json.loads(config_path.read_text())
        except json.JSONDecodeError as e:
            # Don't crash MCP startup on a malformed config; fall back to
            # defaults and warn loudly. User can fix the file and restart.
            print(
                f"rel-mem: {config_path} is malformed ({e}). "
                f"Using package defaults for this session — fix the file and restart.",
                file=sys.stderr,
            )
            return MemoryConfig()

        on_disk_version = raw.get("version", "1.0")
        # Warn only on UPGRADE (disk older than code). On downgrade — e.g.,
        # someone rolls back to a previous package — the warning body would
        # describe pre-fix defaults that no longer apply. Skip silently.
        if _version_tuple(on_disk_version) < _version_tuple(CURRENT_CONFIG_SCHEMA):
            print(
                f"rel-mem: config schema is v{on_disk_version} "
                f"(current is v{CURRENT_CONFIG_SCHEMA}). "
                f"Pre-fix defaults (auto_summarize_at=10, episodic_max=10) "
                f"trigger compaction every 10 entries — now fail-safe thanks "
                f"to PR #425, but wastes a subprocess spawn per failure. To "
                f"opt in to new defaults call the `migrate_config` MCP tool, "
                f"or edit {config_path} directly. Continuing with your current "
                f"values.",
                file=sys.stderr,
            )
        return MemoryConfig(**raw)

    def migrate_config(self) -> str:
        """Opt-in migration of on-disk config to the current schema.

        Idempotent. Only updates fields whose values are at the known-bad
        pre-fix defaults (e.g., `auto_summarize_at == 10`). User-customized
        values (anything other than 10) are preserved untouched. Always
        bumps the schema version to CURRENT_CONFIG_SCHEMA after running.

        Returns a human-readable summary of what changed (or didn't).
        """
        config_path = self.base_path / "config.json"
        if not config_path.exists():
            return "No config file on disk — nothing to migrate. Defaults are current."

        try:
            raw = json.loads(config_path.read_text())
        except json.JSONDecodeError as e:
            return f"Error: {config_path} is malformed and cannot be migrated: {e}"
        on_disk_version = raw.get("version", "1.0")
        changes: list[str] = []

        # READ-only probe; do NOT mutate raw unless a migration actually
        # applies. Earlier version used setdefault here, which created an
        # empty `memory_limits: {}` in raw even when nothing was being
        # migrated — Pydantic's default_factory doesn't fire on explicit
        # empty dicts, so the resulting MemoryConfig had no thresholds and
        # the next access KeyError'd.
        limits_view = raw.get("memory_limits", {})
        # Both `auto_summarize_at` and `episodic_max` had pre-fix default 10
        # (see git history for models.py prior to PR #425) and were raised
        # together to 100. Migrating both keeps them in sync.
        auto_at_stale = limits_view.get("auto_summarize_at") == 10
        epi_max_stale = limits_view.get("episodic_max") == 10

        if auto_at_stale or epi_max_stale:
            limits = raw.setdefault("memory_limits", {})
            if auto_at_stale:
                limits["auto_summarize_at"] = 100
                changes.append("memory_limits.auto_summarize_at: 10 -> 100")
            if epi_max_stale:
                limits["episodic_max"] = 100
                changes.append("memory_limits.episodic_max: 10 -> 100")

        # Always bump schema version on a migration call, even if no values
        # changed (suppresses the load-time warning on the next start).
        # Tuple comparison handles future "1.10" > "1.9" correctly.
        if _version_tuple(on_disk_version) < _version_tuple(CURRENT_CONFIG_SCHEMA):
            raw["version"] = CURRENT_CONFIG_SCHEMA
            changes.append(f"version: {on_disk_version} -> {CURRENT_CONFIG_SCHEMA}")

        if not changes:
            return f"Config already at schema v{CURRENT_CONFIG_SCHEMA} with current defaults. Nothing to do."

        # Atomic write via tmp+rename: an interrupt mid-write leaves the
        # original config intact rather than truncated. Same disk so the
        # rename is atomic.
        tmp_path = config_path.with_suffix(config_path.suffix + ".tmp")
        try:
            tmp_path.write_text(json.dumps(raw, indent=2) + "\n")
            os.replace(tmp_path, config_path)
        except OSError as e:
            # Disk full, permissions, locked file — surface a friendly
            # error rather than letting an opaque exception escape to the
            # MCP layer. Caller (server tool dispatch) returns the string
            # to the agent.
            tmp_path.unlink(missing_ok=True)
            return f"Error writing config: {e}. No changes saved."

        # Update this Backend instance directly from the already-validated
        # raw dict. Avoids a redundant file read + version-check that would
        # only have re-validated what we just wrote.
        self.config = MemoryConfig(**raw)
        # Schema is now current; suppress the pending stale warning so
        # the first post-migration tool call doesn't still surface it.
        self._stale_warning_pending = False
        return "Config migrated:\n  - " + "\n  - ".join(changes)

    def _default_core_memories(self) -> str:
        """Default core memories template."""
        return """# Core Memories

> Permanent principles and learnings that shape all agent behavior.
> These memories ALWAYS load with every agent session.

Last updated: {date}

## Personality Principles

### Action Over Documentation
Never just describe what should be done—do it. Code first, document after.

**Origin:** Best practice for autonomous agents.

### Test-First Discipline
Write tests before implementation code, even when it feels unnecessary.

**Origin:** Software engineering best practices.

### Autonomous Coordination
Use roadmap for work claiming, communicate via established channels.

**Origin:** Multi-agent coordination pattern.

## Project Learnings

(Add learnings as they emerge)

## Anti-Patterns Discovered

(Add anti-patterns as they are discovered)

---

## Adding New Core Memories

Core memories should only be added when:
1. A pattern is observed across **3+ sessions**
2. A critical failure teaches an important lesson
3. A principle significantly improves agent performance

Use the MCP tool `add_core_memory(category, content, justification)` to propose additions.
""".format(
            date=datetime.now().strftime("%Y-%m-%d")
        )

    def _agent_dir(self, agent: str) -> Path:
        """Get agent's memory directory, creating if needed."""
        agent_dir = self.base_path / "agents" / agent
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir

    def _update_index(self, agent: str, layer: str):
        """Update memory index after writing."""
        index_path = self.base_path / "memory-index.json"
        index = json.loads(index_path.read_text())

        if agent not in index["agents"]:
            index["agents"][agent] = {
                "recent_count": 0,
                "episodic_count": 0,
                "compost_count": 0,
                "last_active": datetime.now().isoformat(),
                "current_task": None,
                "projects": [],
            }

        # Count entries in file
        agent_dir = self._agent_dir(agent)
        layer_file = agent_dir / f"{layer}.jsonl"
        if layer_file.exists():
            count = sum(1 for _ in layer_file.read_text().strip().split("\n") if _)
            index["agents"][agent][f"{layer}_count"] = count

        index["agents"][agent]["last_active"] = datetime.now().isoformat()
        index["last_updated"] = datetime.now().isoformat()

        # Update statistics
        index["statistics"]["total_agents"] = len(index["agents"])
        index["statistics"]["total_memories"] = sum(
            agent_data["recent_count"]
            + agent_data["episodic_count"]
            + agent_data["compost_count"]
            for agent_data in index["agents"].values()
        )

        index_path.write_text(json.dumps(index, indent=2))

    def memorize(
        self,
        agent: str,
        layer: Literal["recent", "episodic", "compost"],
        content: str,
        metadata: dict = {},
    ) -> str:
        """
        Store a memory entry (encode new information).

        Returns: entry_id (timestamp-based for reference)
        """
        entry = MemoryEntry(layer=layer, agent=agent, content=content, metadata=metadata)

        # Append to JSONL
        agent_dir = self._agent_dir(agent)
        layer_file = agent_dir / f"{layer}.jsonl"

        with open(layer_file, "a") as f:
            f.write(entry.to_jsonl() + "\n")

        # Update index
        self._update_index(agent, layer)

        # Check if compression needed. Uses `>=` for liveness (recover natural
        # cadence as soon as count reaches threshold), gated by a per-agent
        # failure flag set by `compress()` so we don't subprocess-spawn-storm
        # while compaction is broken. The flag clears on successful
        # compaction OR on server restart (in-memory only); manual
        # `compress(agent)` always retries regardless of the flag.
        if layer == "episodic":
            episodic_file = agent_dir / "episodic.jsonl"
            if episodic_file.exists():
                count = sum(1 for _ in episodic_file.read_text().strip().split("\n") if _)
                if count >= self.config.memory_limits["auto_summarize_at"]:
                    if not self._compaction_failed.get(agent, False):
                        self.compress(agent)

        return entry.timestamp.isoformat()

    def recall(
        self,
        agent: str | None = None,
        layers: list[str] = ["recent", "episodic"],
        query: str | None = None,
        limit: int = 10,
        project: str | None = None,
    ) -> list[dict]:
        """
        Retrieve memories.

        If agent is None, searches all agents.
        If query is provided, performs semantic search using Claude agent.
        If project is provided, filters to that project.
        """
        results = []

        # Determine which agents to search
        agents_to_search = []
        if agent:
            agents_to_search = [agent]
        else:
            # Search all agents
            agents_dir = self.base_path / "agents"
            if agents_dir.exists():
                agents_to_search = [d.name for d in agents_dir.iterdir() if d.is_dir()]

        # Collect memories from all specified layers
        for agent_name in agents_to_search:
            agent_dir = self._agent_dir(agent_name)

            for layer in layers:
                layer_file = agent_dir / f"{layer}.jsonl"
                if not layer_file.exists():
                    continue

                for line in layer_file.read_text().strip().split("\n"):
                    if not line:
                        continue

                    try:
                        entry = MemoryEntry.from_jsonl(line)

                        # Filter by project if specified
                        if project and entry.metadata.get("project") != project:
                            continue

                        results.append(entry.model_dump(mode="json"))
                    except Exception as e:
                        # Skip malformed entries
                        print(f"Warning: Skipping malformed entry: {e}")
                        continue

        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x["timestamp"], reverse=True)

        # If query provided, use semantic search
        if query:
            results = self._semantic_search(results, query, limit)
        else:
            results = results[:limit]

        return results

    def _semantic_search(self, memories: list[dict], query: str, limit: int) -> list[dict]:
        """
        Perform semantic search using Claude Code agent.
        Falls back to simple text matching if agent fails.
        """
        # Try Claude agent semantic search
        claude = ClaudeAgent(model=self.config.summarization["model"])

        try:
            return claude.semantic_search(memories, query, limit)
        except Exception as e:
            print(f"Warning: Claude agent search failed, using text matching: {e}")
            # Fallback to simple text matching
            query_lower = query.lower()
            scored = []

            for memory in memories:
                content_lower = memory["content"].lower()
                # Simple relevance score based on keyword overlap
                score = sum(word in content_lower for word in query_lower.split())
                if score > 0:
                    scored.append((score, memory))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [mem for _, mem in scored[:limit]]

    def update_current_task(
        self,
        agent: str,
        task: str | None = None,
        status: str | None = None,
        metadata: dict = {},
    ):
        """Update the current task state."""
        agent_dir = self._agent_dir(agent)
        task_file = agent_dir / "current-task.json"

        # Load existing or create new
        if task_file.exists():
            current = CurrentTask(**json.loads(task_file.read_text()))
        else:
            current = CurrentTask(task=task or "")

        # Update fields
        if task is not None:
            current.task = task
            if current.started is None:
                current.started = datetime.now()

        if status is not None:
            current.status = status  # type: ignore

        if metadata:
            current.metadata.update(metadata)

        current.updated = datetime.now()

        # Save
        task_file.write_text(current.model_dump_json(indent=2))

        # Update index
        index_path = self.base_path / "memory-index.json"
        index = json.loads(index_path.read_text())
        if agent in index["agents"]:
            index["agents"][agent]["current_task"] = current.task_id
        index_path.write_text(json.dumps(index, indent=2))

    def get_current_task(self, agent: str) -> Optional[CurrentTask]:
        """Get the current task for an agent."""
        agent_dir = self._agent_dir(agent)
        task_file = agent_dir / "current-task.json"

        if task_file.exists():
            return CurrentTask(**json.loads(task_file.read_text()))
        return None

    def add_core_memory(
        self,
        category: Literal["personality", "learning", "anti-pattern"],
        content: str,
        justification: str,
    ) -> str:
        """
        Add to core-memories.md.

        This is a write to the markdown file. In a production system,
        this should include human-in-the-loop approval.
        """
        core_path = self.base_path / "core-memories.md"
        core_content = core_path.read_text()

        # Find the appropriate section
        category_headers = {
            "personality": "## Personality Principles",
            "learning": "## Project Learnings",
            "anti-pattern": "## Anti-Patterns Discovered",
        }

        header = category_headers[category]

        # Format the new entry
        today = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"""
### {content.split('.')[0]}
{content}

**Origin:** {justification}
**Added:** {today}
"""

        # Insert after the header
        if header in core_content:
            parts = core_content.split(header)
            # Find next ## to insert before it
            after_header = parts[1]
            next_section_idx = after_header.find("\n##")

            if next_section_idx != -1:
                core_content = (
                    parts[0]
                    + header
                    + after_header[:next_section_idx]
                    + new_entry
                    + after_header[next_section_idx:]
                )
            else:
                core_content = parts[0] + header + after_header + new_entry
        else:
            # Append new section
            core_content += f"\n{header}\n{new_entry}"

        # Update last updated date
        core_content = core_content.replace(
            f"Last updated: {core_content.split('Last updated: ')[1].split()[0]}",
            f"Last updated: {today}",
        )

        core_path.write_text(core_content)
        return f"Added to core memories: {category}"

    def get_core_memories(self) -> str:
        """Get all core memories."""
        core_path = self.base_path / "core-memories.md"
        return core_path.read_text()

    def compress(self, agent: str) -> str:
        """
        Compress episodic memories into summary using Claude Code agent.

        Condenses 10+ episodic entries into 2-3 key sentences,
        then moves originals to compost (archive).
        """
        agent_dir = self._agent_dir(agent)
        episodic_file = agent_dir / "episodic.jsonl"

        if not episodic_file.exists():
            return "No episodic memories to summarize"

        entries = [
            MemoryEntry.from_jsonl(line)
            for line in episodic_file.read_text().strip().split("\n")
            if line
        ]

        if len(entries) < self.config.memory_limits["auto_summarize_at"]:
            return f"Only {len(entries)} entries, need {self.config.memory_limits['auto_summarize_at']} to compress"

        # Use Claude Code agent to intelligently summarize
        claude = ClaudeAgent(model=self.config.summarization["model"])

        # Convert entries to dicts for agent
        entries_data = [entry.model_dump(mode="json") for entry in entries]

        # Hoisted above try/except: both branches write to compost.
        compost_file = agent_dir / "compost.jsonl"
        date_range = f"{entries[0].timestamp.isoformat()} to {entries[-1].timestamp.isoformat()}"

        try:
            summary = claude.summarize_memories(entries_data, agent)
        except Exception as e:
            # CRITICAL: Do not wipe episodic on summarization failure.
            #
            # Previous behavior wrote a degenerate "Week of work: N tasks
            # completed..." fallback summary AND cleared episodic. Combined
            # with the broken `claude --headless` invocation in claude_agent,
            # every threshold-triggered compaction silently destroyed N raw
            # entries — months of memory loss across all agents before the
            # 2026-05-25 incident. The fallback summary contained no content,
            # only a count, so the raw data was unrecoverable.
            #
            # Preserve raw entries on failure. Log a marker to compost so the
            # failure is auditable. Episodic may briefly exceed
            # auto_summarize_at; next successful compaction will reduce it.
            print(
                f"Warning: rel-mem summarization failed for agent {agent!r}, "
                f"episodic preserved ({len(entries)} entries): {e}"
            )
            failure_marker = MemoryEntry(
                layer="compost",
                agent=agent,
                content=f"Compaction failed, raw entries preserved in episodic: {e}",
                metadata={
                    "original_entry_count": len(entries),
                    "date_range": date_range,
                    "summarized_by": "compaction_failure_marker",
                    "destructive": False,
                },
            )
            with open(compost_file, "a") as f:
                f.write(failure_marker.to_jsonl() + "\n")
            self._update_index(agent, "compost")
            # Set the per-agent flag so memorize() doesn't retry every write.
            # Manual compress() always retries (it bypasses memorize()'s gate).
            self._compaction_failed[agent] = True
            return f"Compaction failed; {len(entries)} episodic entries preserved. Reason: {e}"

        # Successful summarization — move entries to compost and clear episodic
        compost_entry = MemoryEntry(
            layer="compost",
            agent=agent,
            content=summary,
            metadata={
                "original_entry_count": len(entries),
                "date_range": date_range,
                "summarized_by": "claude_agent",
            },
        )

        with open(compost_file, "a") as f:
            f.write(compost_entry.to_jsonl() + "\n")

        # Clear episodic file (only on confirmed successful summarization)
        episodic_file.write_text("")

        # Clear the per-agent failure flag — natural cadence resumes.
        self._compaction_failed.pop(agent, None)

        self._update_index(agent, "episodic")
        self._update_index(agent, "compost")

        return f"Summarized and composted {len(entries)} memories"

    # =========================================================================
    # Relations Layer - The substrate for pattern discovery
    # =========================================================================

    def _relations_file(self) -> Path:
        """Get the global relations file path."""
        return self.base_path / "relations.jsonl"

    def create_relation(
        self,
        from_memory: str,
        to_memory: str,
        relation_type: str,
        agent: str,
        confidence: float = 1.0,
        context: str = "",
        metadata: dict = {},
    ) -> str:
        """
        Create a relation between two memories.

        The relation_type is a FREE STRING - this is intentional to enable:
        1. Domain-agnostic usage (agent memory, learning memory, project memory)
        2. Emergent pattern naming without code changes
        3. Vasana discovery through repetition analysis

        Args:
            from_memory: Reference to source memory (timestamp, hash, or ID)
            to_memory: Reference to target memory
            relation_type: Free-form relation type (e.g., "builds_on", "contradicts")
            agent: Which agent/context created this relation
            confidence: 0-1 confidence score (default 1.0)
            context: Why this relation was created
            metadata: Additional domain-specific data

        Returns: Relation ID
        """
        relation = Relation(
            from_memory=from_memory,
            to_memory=to_memory,
            relation_type=relation_type,
            agent=agent,
            confidence=confidence,
            context=context,
            metadata=metadata,
        )

        # Append to JSONL
        with open(self._relations_file(), "a") as f:
            f.write(relation.to_jsonl() + "\n")

        return relation.id

    def find_relations(
        self,
        relation_type: str | None = None,
        agent: str | None = None,
        from_memory: str | None = None,
        to_memory: str | None = None,
        min_confidence: float = 0.0,
        limit: int = 100,
    ) -> list[dict]:
        """
        Query relations with flexible filtering.

        Args:
            relation_type: Filter by relation type (exact match)
            agent: Filter by creating agent
            from_memory: Filter by source memory reference
            to_memory: Filter by target memory reference
            min_confidence: Minimum confidence threshold
            limit: Maximum results to return

        Returns: List of relation dicts matching criteria

        Note: Currently scans full file. Consider adding indexing for >10k relations.
        """
        results = []
        relations_file = self._relations_file()

        if not relations_file.exists():
            return []

        for line in relations_file.read_text().strip().split("\n"):
            if not line:
                continue

            try:
                relation = Relation.from_jsonl(line)

                # Apply filters
                if relation_type and relation.relation_type != relation_type:
                    continue
                if agent and relation.agent != agent:
                    continue
                if from_memory and relation.from_memory != from_memory:
                    continue
                if to_memory and relation.to_memory != to_memory:
                    continue
                if relation.confidence < min_confidence:
                    continue

                results.append(relation.model_dump(mode="json"))

                if len(results) >= limit:
                    break

            except Exception as e:
                print(f"Warning: Skipping malformed relation: {e}")
                continue

        return results

    def discover_patterns(
        self,
        min_occurrences: int = 3,
        agent: str | None = None,
    ) -> list[dict]:
        """
        THE VASANA DISCOVERY QUERY.

        Finds relation_types that appear repeatedly - these are behavioral patterns
        worth examining. When a relation_type appears across multiple contexts,
        it signals a potential vasana (habitual behavioral pattern).

        Args:
            min_occurrences: Minimum times a relation_type must appear (default: 3)
            agent: Filter to specific agent (None = all agents)

        Returns: List of {relation_type, count, agents, examples} sorted by count desc

        Example usage:
            patterns = discover_patterns(min_occurrences=3)
            # Returns: [
            #   {"relation_type": "kept_checking_wrong_layer", "count": 7, ...},
            #   {"relation_type": "premature_optimization", "count": 5, ...},
            # ]

        These recurring patterns are candidates for vasana documentation.
        """
        relations_file = self._relations_file()

        if not relations_file.exists():
            return []

        # Count occurrences by relation_type
        type_data: dict[str, dict] = {}

        for line in relations_file.read_text().strip().split("\n"):
            if not line:
                continue

            try:
                relation = Relation.from_jsonl(line)

                # Filter by agent if specified
                if agent and relation.agent != agent:
                    continue

                rt = relation.relation_type

                if rt not in type_data:
                    type_data[rt] = {
                        "relation_type": rt,
                        "count": 0,
                        "agents": set(),
                        "examples": [],
                    }

                type_data[rt]["count"] += 1
                type_data[rt]["agents"].add(relation.agent)

                # Keep up to 3 examples
                if len(type_data[rt]["examples"]) < 3:
                    type_data[rt]["examples"].append({
                        "id": relation.id,
                        "from": relation.from_memory,
                        "to": relation.to_memory,
                        "context": relation.context,
                    })

            except Exception as e:
                print(f"Warning: Skipping malformed relation in discover_patterns: {e}")
                continue

        # Filter by min_occurrences and format results
        results = []
        for data in type_data.values():
            if data["count"] >= min_occurrences:
                results.append({
                    "relation_type": data["relation_type"],
                    "count": data["count"],
                    "agents": list(data["agents"]),  # Convert set to list
                    "examples": data["examples"],
                    "cross_agent": len(data["agents"]) > 1,  # Pattern appears across agents
                })

        # Sort by count descending
        results.sort(key=lambda x: x["count"], reverse=True)

        return results

    def get_relation_types(self) -> list[str]:
        """
        Get all unique relation types in the system.

        Useful for exploring what relation types have been used,
        and for building UI/autocomplete for relation creation.
        """
        relations_file = self._relations_file()

        if not relations_file.exists():
            return []

        types = set()
        for line in relations_file.read_text().strip().split("\n"):
            if not line:
                continue
            try:
                relation = Relation.from_jsonl(line)
                types.add(relation.relation_type)
            except Exception:
                continue

        return sorted(list(types))

    # =========================================================================
    # Entity Query Layer - Raw relation dumps for kg-memory compatibility
    # =========================================================================
    #
    # These functions return RAW RELATIONS only - zero semantic interpretation.
    # Interpretation is delegated to the entity-interpreter agent which has
    # its own memory and learns relation patterns over time.

    def get_entity(self, name: str) -> dict:
        """
        Get all relations involving this name. NO semantic interpretation.

        Returns raw outgoing and incoming relations for the entity-interpreter
        agent to analyze using its learned patterns.

        Args:
            name: The entity name to query

        Returns:
            {
                "name": name,
                "outgoing_relations": [...],  # Relations where name is "from"
                "incoming_relations": [...],  # Relations where name is "to"
            }
        """
        return {
            "name": name,
            "outgoing_relations": self.find_relations(from_memory=name),
            "incoming_relations": self.find_relations(to_memory=name),
        }

    def search_nodes(self, query: str) -> dict:
        """
        Search for nodes matching query in relations. NO semantic interpretation.

        Returns all relations where the query appears in any field.
        Interpretation delegated to entity-interpreter agent.

        Args:
            query: Search term to match against relation fields

        Returns:
            {
                "query": query,
                "matching_relations": [...]
            }
        """
        all_rels = self.find_relations(limit=10000)
        query_lower = query.lower()

        matching = [
            r for r in all_rels
            if query_lower in str(r).lower()
        ]

        return {"query": query, "matching_relations": matching}

    def read_graph(self) -> dict:
        """
        Get ALL relations in the system. NO semantic interpretation.

        Returns the complete graph for the entity-interpreter agent
        to analyze and structure as needed.

        Returns:
            {"all_relations": [...]}
        """
        return {"all_relations": self.find_relations(limit=10000)}

    def open_nodes(self, names: list[str]) -> dict:
        """
        Get all relations for multiple entity names. NO semantic interpretation.

        Batch version of get_entity for efficiency.

        Args:
            names: List of entity names to query

        Returns:
            {name: get_entity(name) result for each name}
        """
        return {name: self.get_entity(name) for name in names}

    def delete_relations(self, relations: list[dict]) -> int:
        """
        Delete relations matching the provided criteria.

        Each dict in relations should specify matching criteria:
        - from_memory: Match source
        - to_memory: Match target
        - relation_type: Match type

        All specified fields must match for a relation to be deleted.

        Args:
            relations: List of relation criteria to delete

        Returns:
            Count of deleted relations
        """
        relations_file = self._relations_file()

        if not relations_file.exists():
            return 0

        # Read all relations
        lines = relations_file.read_text().strip().split("\n")
        kept = []
        deleted_count = 0

        for line in lines:
            if not line:
                continue

            try:
                relation = Relation.from_jsonl(line)
                should_delete = False

                # Check each deletion criteria
                for criteria in relations:
                    matches = True
                    if "from_memory" in criteria and relation.from_memory != criteria["from_memory"]:
                        matches = False
                    if "to_memory" in criteria and relation.to_memory != criteria["to_memory"]:
                        matches = False
                    if "relation_type" in criteria and relation.relation_type != criteria["relation_type"]:
                        matches = False

                    if matches:
                        should_delete = True
                        break

                if should_delete:
                    deleted_count += 1
                else:
                    kept.append(line)

            except Exception:
                # Keep malformed entries
                kept.append(line)

        # Write back kept relations
        relations_file.write_text("\n".join(kept) + "\n" if kept else "")

        return deleted_count
