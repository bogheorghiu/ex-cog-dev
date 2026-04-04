#!/usr/bin/env python3
"""Migrate existing articles to new folder structure."""
import shutil
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.config import load_config
from scripts.utils import ensure_dir


def migrate():
    try:
        config = load_config("config.json")
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    base_dir = Path(config.output_dir)
    if not base_dir.exists():
        print(f"Output directory {base_dir} does not exist.")
        return

    print(f"Migrating files in {base_dir}...")

    # Create new directories
    html_dir = base_dir / "html"
    md_dir = base_dir / "markdown"
    json_dir = base_dir / "json"

    ensure_dir(str(html_dir))
    ensure_dir(str(md_dir))
    ensure_dir(str(json_dir))

    # Track stats
    moved_count = 0

    # Iterate over items in base directory
    for item in base_dir.iterdir():
        # Skip the new target directories and non-directories
        if not item.is_dir() or item.name in ["html", "markdown", "json"]:
            continue

        # Assume directory name is the slug/base name
        base_name = item.name

        # Define source files
        src_html = item / "content.html"
        src_md = item / "content.md"
        src_json = item / "metadata.json"

        # Move files if they exist
        has_moved = False

        if src_html.exists():
            shutil.move(str(src_html), str(html_dir / f"{base_name}.html"))
            has_moved = True

        if src_md.exists():
            shutil.move(str(src_md), str(md_dir / f"{base_name}.md"))
            has_moved = True

        if src_json.exists():
            shutil.move(str(src_json), str(json_dir / f"{base_name}.json"))
            has_moved = True

        if has_moved:
            moved_count += 1
            print(f"Moved: {base_name}")

            # Clean up old directory
            shutil.rmtree(str(item))

    print(f"✅ Migration complete. Processed {moved_count} articles.")


if __name__ == "__main__":
    migrate()