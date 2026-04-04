#!/usr/bin/env python3
"""Convert individual markdown files to a single consolidated file.

This script takes a directory of individual .md files (from old extraction format)
and consolidates them into a single all_articles.md file.

Usage:
    python scripts/convert_md_to_single.py [input_dir] [output_file]

    input_dir: Directory containing individual .md files (default: data/markdown/)
    output_file: Output file path (default: data/all_articles.md)

Example:
    python scripts/convert_md_to_single.py data/markdown/ data/all_articles.md
"""
import argparse
import re
import sys
from pathlib import Path


def extract_metadata_from_content(content: str, filename: str) -> dict:
    """Extract title, date, and source URL from markdown content or filename.

    Args:
        content: Markdown file content
        filename: Original filename (e.g., "2024-01-15-article-slug.md")

    Returns:
        Dict with title, date, url keys
    """
    metadata = {"title": None, "date": None, "url": None}

    # Try to extract source URL from content (format: "Source: URL")
    source_match = re.search(r'^Source:\s*(.+)$', content, re.MULTILINE)
    if source_match:
        metadata["url"] = source_match.group(1).strip()

    # Try to extract title (first H1)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1).strip()

    # Extract date from filename (format: YYYY-MM-DD-slug.md)
    date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        metadata["date"] = date_match.group(1)

    # Fallback title from filename if not found in content
    if not metadata["title"]:
        # Remove date prefix and extension, convert dashes to spaces
        title_from_file = re.sub(r'^\d{4}-\d{2}-\d{2}-?', '', filename)
        title_from_file = title_from_file.replace('.md', '').replace('-', ' ').title()
        metadata["title"] = title_from_file or "Untitled"

    return metadata


def format_article_section(content: str, metadata: dict) -> str:
    """Format an article for inclusion in the consolidated file.

    Args:
        content: Original markdown content
        metadata: Extracted metadata dict

    Returns:
        Formatted article section with header
    """
    # Build header
    header_lines = [f"# {metadata['title']}"]

    if metadata["date"]:
        header_lines.append(f"**Date:** {metadata['date']}")

    if metadata["url"]:
        header_lines.append(f"**Source:** {metadata['url']}")

    header = "\n".join(header_lines)

    # Remove existing "Source:" line from content if present (we put it in header)
    content = re.sub(r'^Source:\s*.+\n\n?', '', content, flags=re.MULTILINE)

    # Remove existing H1 if present (we put it in header)
    content = re.sub(r'^#\s+.+\n\n?', '', content, flags=re.MULTILINE)

    return f"{header}\n\n{content.strip()}"


def convert_directory_to_single_file(input_dir: Path, output_file: Path) -> int:
    """Convert all .md files in directory to a single consolidated file.

    Args:
        input_dir: Directory containing individual .md files
        output_file: Output file path

    Returns:
        Number of articles processed
    """
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return 0

    # Find all .md files, sorted by name (which should be date-prefixed)
    md_files = sorted(input_dir.glob("*.md"))

    if not md_files:
        print(f"No .md files found in '{input_dir}'")
        return 0

    print(f"Found {len(md_files)} markdown files to convert")

    # Process each file
    articles = []
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            metadata = extract_metadata_from_content(content, md_file.name)
            formatted = format_article_section(content, metadata)
            articles.append(formatted)
            print(f"  ✓ {md_file.name}: {metadata['title'][:50]}...")
        except Exception as e:
            print(f"  ✗ {md_file.name}: {e}")

    if not articles:
        print("No articles successfully processed.")
        return 0

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write consolidated file
    separator = "\n\n---\n\n"
    consolidated = separator.join(articles)
    output_file.write_text(consolidated, encoding="utf-8")

    print(f"\n✅ Wrote {len(articles)} articles to {output_file}")
    return len(articles)


def main():
    parser = argparse.ArgumentParser(
        description="Convert individual markdown files to a single consolidated file."
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        default="data/markdown",
        help="Directory containing individual .md files (default: data/markdown/)"
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default="data/all_articles.md",
        help="Output file path (default: data/all_articles.md)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files"
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_file = Path(args.output_file)

    if args.dry_run:
        print(f"[DRY RUN] Would convert files from {input_dir} to {output_file}")
        md_files = sorted(input_dir.glob("*.md")) if input_dir.exists() else []
        print(f"Found {len(md_files)} files to process")
        for f in md_files:
            print(f"  - {f.name}")
        return 0

    count = convert_directory_to_single_file(input_dir, output_file)
    return 0 if count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
