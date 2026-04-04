"""Configuration management for substack scraper."""
import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Configuration for substack scraper."""

    substack_url: str
    rate_limit_seconds: float = 2.5
    output_dir: str = "data/articles"
    auth_state_path: str = "auth/browser_state.json"
    progress_file: str = "progress.json"
    max_articles: Optional[int] = None


def load_config(path: str) -> Config:
    """Load configuration from JSON file.

    Args:
        path: Path to JSON config file.

    Returns:
        Config object with values from file, defaults for missing fields.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        json.JSONDecodeError: If config file is invalid JSON.
        KeyError/TypeError: If required field (substack_url) is missing.
    """
    with open(path, "r") as f:
        data = json.load(f)

    # Required field
    substack_url = data["substack_url"]

    return Config(
        substack_url=substack_url,
        rate_limit_seconds=data.get("rate_limit_seconds", 2.5),
        output_dir=data.get("output_dir", "data/articles"),
        auth_state_path=data.get("auth_state_path", "auth/browser_state.json"),
        progress_file=data.get("progress_file", "progress.json"),
        max_articles=data.get("max_articles"),
    )
