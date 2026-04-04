#!/usr/bin/env python3
"""Ralph-Plus saturation detection for iterative corpus analysis.

Ported from youtube-research skill's self-managing iteration pattern.
Detects when additional parsing passes yield diminishing returns.

Usage:
    from scripts.saturation_detector import SaturationTracker

    tracker = SaturationTracker()
    while True:
        # Do parsing pass
        new_patterns, reinforced = analyze_pass(corpus)

        if not tracker.should_continue(new_patterns, reinforced):
            print(f"Stopping: {tracker.stop_reason}")
            break

        tracker.record_pass(new_patterns, reinforced)
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PassQuality(Enum):
    """Quality assessment for a single parsing pass."""

    HIGH = "HIGH"  # Meaningful new patterns found
    LOW = "LOW"  # Little new information


@dataclass
class PassResult:
    """Result of a single corpus analysis pass."""

    new_patterns: int
    reinforced_patterns: int
    quality: PassQuality
    notes: str = ""


@dataclass
class SaturationTracker:
    """Tracks pattern saturation across iterative parsing passes.

    Ralph-Plus algorithm: Stop when 2+ consecutive LOW passes detected.
    This indicates the corpus has been thoroughly mined for patterns.
    """

    # History of pass results
    history: list[PassResult] = field(default_factory=list)

    # Stop condition: consecutive low-value passes
    consecutive_low_threshold: int = 2

    # Pattern thresholds
    high_pattern_threshold: int = 2  # Patterns needed for HIGH quality

    # State
    stop_reason: str = ""
    is_saturated: bool = False

    def assess_quality(self, new_patterns: int, reinforced_patterns: int) -> PassQuality:
        """Assess quality of a parsing pass.

        Args:
            new_patterns: Count of newly discovered patterns/themes
            reinforced_patterns: Count of previously seen patterns with new evidence

        Returns:
            PassQuality.HIGH if meaningful, PassQuality.LOW if exhausted
        """
        total_value = new_patterns + reinforced_patterns
        return PassQuality.HIGH if total_value >= self.high_pattern_threshold else PassQuality.LOW

    def record_pass(self, new_patterns: int, reinforced_patterns: int, notes: str = "") -> PassResult:
        """Record a completed parsing pass.

        Args:
            new_patterns: Count of newly discovered patterns/themes
            reinforced_patterns: Count of patterns reinforced with new evidence
            notes: Optional notes about this pass

        Returns:
            PassResult for this pass
        """
        quality = self.assess_quality(new_patterns, reinforced_patterns)
        result = PassResult(
            new_patterns=new_patterns,
            reinforced_patterns=reinforced_patterns,
            quality=quality,
            notes=notes,
        )
        self.history.append(result)
        return result

    def should_continue(
        self, preview_new: Optional[int] = None, preview_reinforced: Optional[int] = None
    ) -> bool:
        """Check if iteration should continue.

        Can be called with preview counts before recording, or without
        to check based on current history only.

        Args:
            preview_new: Preview of new patterns (None = no preview, 0 = zero new)
            preview_reinforced: Preview of reinforced patterns (None = no preview)

        Returns:
            True if should continue, False if saturated
        """
        # Build quality history including preview
        qualities = [r.quality for r in self.history]

        # Include preview if both preview args provided (even if both are 0)
        if preview_new is not None and preview_reinforced is not None:
            preview_quality = self.assess_quality(preview_new, preview_reinforced)
            qualities.append(preview_quality)

        # Count consecutive LOW from end
        consecutive_low = 0
        for quality in reversed(qualities):
            if quality == PassQuality.LOW:
                consecutive_low += 1
            else:
                break

        if consecutive_low >= self.consecutive_low_threshold:
            is_preview = preview_new is not None and preview_reinforced is not None
            if not is_preview:
                self.is_saturated = True
                self.stop_reason = f"Data exhausted ({consecutive_low} consecutive low-value passes)"
            return False

        return True

    def get_summary(self) -> dict:
        """Get summary of saturation tracking.

        Returns:
            Dict with pass count, patterns found, saturation status
        """
        total_new = sum(r.new_patterns for r in self.history)
        total_reinforced = sum(r.reinforced_patterns for r in self.history)
        high_passes = sum(1 for r in self.history if r.quality == PassQuality.HIGH)

        return {
            "total_passes": len(self.history),
            "high_value_passes": high_passes,
            "low_value_passes": len(self.history) - high_passes,
            "total_new_patterns": total_new,
            "total_reinforced": total_reinforced,
            "is_saturated": self.is_saturated,
            "stop_reason": self.stop_reason,
        }


def should_continue_simple(pass_history: list[str]) -> tuple[bool, str]:
    """Simple function-based saturation check.

    For lightweight integration without class instantiation.

    Args:
        pass_history: List of "HIGH" or "LOW" strings

    Returns:
        Tuple of (should_continue, reason_if_stopping)
    """
    consecutive_low = 0
    for quality in reversed(pass_history):
        if quality.upper() == "LOW":
            consecutive_low += 1
        else:
            break

    if consecutive_low >= 2:
        return False, "Data exhausted (2+ consecutive low-value passes)"
    return True, ""


def assess_pass_quality_simple(new_patterns: int, reinforced_patterns: int) -> str:
    """Simple quality assessment.

    Args:
        new_patterns: Count of new patterns found
        reinforced_patterns: Count of reinforced patterns

    Returns:
        "HIGH" if >= 2 total patterns, "LOW" otherwise
    """
    return "HIGH" if (new_patterns + reinforced_patterns) >= 2 else "LOW"


if __name__ == "__main__":
    # Demo usage
    print("Ralph-Plus Saturation Detection Demo\n")

    tracker = SaturationTracker()

    # Simulate parsing passes
    test_passes = [
        (5, 2, "First pass - lots of themes"),
        (3, 4, "Second pass - more patterns"),
        (1, 1, "Third pass - slowing down"),
        (0, 1, "Fourth pass - almost done"),
        (0, 0, "Fifth pass - nothing new"),
    ]

    for new, reinforced, notes in test_passes:
        if not tracker.should_continue(new, reinforced):
            print(f"STOPPING before pass: {tracker.stop_reason}")
            break

        result = tracker.record_pass(new, reinforced, notes)
        print(f"Pass {len(tracker.history)}: {result.quality.value} - {notes}")
        print(f"  New: {new}, Reinforced: {reinforced}")

    print("\n--- Summary ---")
    summary = tracker.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
