#!/usr/bin/env python3
"""Helper script to add source URLs to existing HTML and Markdown files.

This script iterates through the local JSON metadata files to find the URL,
then prepends it to the corresponding HTML and Markdown files if missing.
This avoids re-scraping the content from the web while ensuring all files
have the source link.
"""
import json
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.config import load_config


def update_files():
    try:
        config = load_config("config.json")
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    base_dir = Path(config.output_dir)
    json_dir = base_dir / "json"
    html_dir = base_dir / "html"
    md_dir = base_dir / "markdown"

    if not json_dir.exists():
        print(f"No JSON directory found at {json_dir}")
        return

    print(f"Updating files in {base_dir}...")

    updated_count = 0
    processed_count = 0

    # Iterate through all metadata files
    for json_file in json_dir.glob("*.json"):
        try:
            processed_count += 1

            # 1. Get URL from metadata
            try:
                data = json.loads(json_file.read_text())
                url = data.get("url")
            except Exception:
                print(f"⚠️  Could not read metadata: {json_file.name}")
                continue

            if not url:
                continue

            # Get the base filename (e.g., "2023-01-01-my-post")
            base_name = json_file.stem
            updated_this_article = False

            # 2. Update HTML file
            html_file = html_dir / f"{base_name}.html"
            if html_file.exists():
                content = html_file.read_text()

                # Check if header already exists (avoid duplication)
                if "Source: <a href=" not in content[:300]:
                    header = f'<p>Source: <a href="{url}">{url}</a></p>\n\n'
                    html_file.write_text(header + content)
                    updated_this_article = True

            # 3. Update Markdown file
            md_file = md_dir / f"{base_name}.md"
            if md_file.exists():
                content = md_file.read_text()

                # Check if header already exists
                if not content.startswith("Source: "):
                    header = f"Source: {url}\n\n"
                    md_file.write_text(header + content)
                    updated_this_article = True

            if updated_this_article:
                updated_count += 1
                print(f"Updated: {base_name}")

        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")

    print(f"\n✅ Update complete.")
    print(f"   Processed: {processed_count}")
    print(f"   Updated:   {updated_count}")


if __name__ == "__main__":
    update_files()