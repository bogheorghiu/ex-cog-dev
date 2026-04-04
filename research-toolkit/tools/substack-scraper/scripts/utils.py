"""Utility functions for substack scraper."""
import json
import os
import re
import unicodedata
from pathlib import Path


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug.

    - Lowercase
    - Replace spaces with dashes
    - Remove special characters
    - Handle unicode
    - Collapse multiple dashes
    - Strip leading/trailing dashes
    """
    if not text:
        return ""

    # Normalize unicode (é -> e)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Lowercase
    text = text.lower()

    # Remove apostrophes (what's -> whats)
    text = text.replace("'", "")

    # Replace non-alphanumeric with dashes
    text = re.sub(r"[^a-z0-9]+", "-", text)

    # Collapse multiple dashes
    text = re.sub(r"-+", "-", text)

    # Strip leading/trailing dashes
    text = text.strip("-")

    return text


def load_progress(path: str) -> set:
    """Load completed URLs from checkpoint file.

    Returns empty set if file doesn't exist or is invalid.
    """
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return set(data)
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_progress(path: str, completed: set) -> None:
    """Save completed URLs to checkpoint file."""
    with open(path, "w") as f:
        json.dump(list(completed), f, indent=2)


def ensure_dir(path: str) -> str:
    """Create directory if it doesn't exist. Returns path."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path
