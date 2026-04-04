"""Integration with Claude Code agents for LLM operations."""

import subprocess
import tempfile
import json
from pathlib import Path
from typing import Optional


class ClaudeAgent:
    """Spawns Claude Code agents for LLM operations (summarization, semantic search)."""

    def __init__(self, model: str = "sonnet", headless: bool = True):
        self.model = model
        self.headless = headless

    def summarize_memories(self, memories: list[dict], agent_name: str) -> str:
        """
        Use Claude Code agent to summarize a list of memories.

        Args:
            memories: List of memory entries to summarize
            agent_name: Name of the agent (for context)

        Returns:
            Summarized text (2-3 sentences)
        """
        # Create temp file with memories
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(memories, f, indent=2, default=str)
            temp_path = f.name

        try:
            # Create prompt for summarization
            prompt = f"""Summarize these {len(memories)} memory entries for agent '{agent_name}' into 2-3 key sentences.

Focus on:
1. Main tasks completed
2. Key decisions made
3. Important learnings or patterns

Memory entries:
{Path(temp_path).read_text()}

Provide only the summary, no preamble. Make it concise and actionable."""

            # Run Claude Code agent
            result = subprocess.run(
                [
                    "claude",
                    "--model",
                    self.model,
                    "--headless" if self.headless else "--no-headless",
                ],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,  # 1 minute timeout
            )

            if result.returncode != 0:
                return f"Error summarizing memories: {result.stderr}"

            # Extract summary from output
            summary = result.stdout.strip()

            # Remove any markdown formatting if present
            if summary.startswith("```") and summary.endswith("```"):
                lines = summary.split("\n")
                summary = "\n".join(lines[1:-1])

            return summary

        finally:
            # Cleanup temp file
            Path(temp_path).unlink(missing_ok=True)

    def semantic_search(
        self, memories: list[dict], query: str, limit: int = 10
    ) -> list[dict]:
        """
        Use Claude Code agent to perform semantic search on memories.

        Args:
            memories: List of memory entries to search
            query: Search query
            limit: Maximum results to return

        Returns:
            Filtered and ranked list of memories
        """
        # Create temp file with memories
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(memories, f, indent=2, default=str)
            temp_path = f.name

        try:
            prompt = f"""You are helping search through agent memories.

Query: "{query}"

From these memories, select the top {limit} most relevant ones and return them as a JSON array of indices (0-based).

Memories:
{Path(temp_path).read_text()}

Return ONLY a JSON array of indices, like: [3, 7, 1, 12, 5]"""

            result = subprocess.run(
                [
                    "claude",
                    "--model",
                    self.model,
                    "--headless" if self.headless else "--no-headless",
                ],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                # Fallback to simple text matching
                return self._simple_text_search(memories, query, limit)

            # Parse indices from output
            output = result.stdout.strip()

            # Extract JSON array from output
            try:
                # Try to find JSON array in output
                start = output.find("[")
                end = output.rfind("]") + 1
                if start != -1 and end > start:
                    indices = json.loads(output[start:end])
                    return [memories[i] for i in indices if 0 <= i < len(memories)][:limit]
            except Exception:
                pass

            # Fallback to simple search
            return self._simple_text_search(memories, query, limit)

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def _simple_text_search(
        self, memories: list[dict], query: str, limit: int
    ) -> list[dict]:
        """Fallback: simple text matching."""
        query_lower = query.lower()
        scored = []

        for memory in memories:
            content_lower = memory["content"].lower()
            score = sum(word in content_lower for word in query_lower.split())
            if score > 0:
                scored.append((score, memory))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scored[:limit]]
