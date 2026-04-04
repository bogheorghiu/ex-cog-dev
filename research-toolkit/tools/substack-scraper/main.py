#!/usr/bin/env python3
"""Substack Scraper - Main entry point.

Orchestrates the full extraction pipeline:
1. Auth (if needed)
2. Article discovery
3. Content extraction
"""
import argparse
import sys
from pathlib import Path

from scripts.config import Config, load_config
from scripts.discover_articles import discover_articles, save_article_index
from scripts.extract_content import batch_extract


def check_auth_state(config: Config) -> bool:
    """Check if authentication state exists."""
    return Path(config.auth_state_path).exists()


def run_discovery(config: Config) -> list:
    """Run article discovery phase."""
    print(f"🔍 Discovering articles from {config.substack_url}...")

    articles = discover_articles(
        config.substack_url,
        config.auth_state_path,
    )

    # Save index
    index_path = Path(config.output_dir) / "index.json"
    save_article_index(articles, str(index_path))

    print(f"📋 Found {len(articles)} articles")
    return articles


def run_extraction(articles: list, config: Config) -> None:
    """Run content extraction phase."""
    if config.max_articles:
        articles = articles[: config.max_articles]
        print(f"📦 Limiting to {config.max_articles} articles")

    print(f"📄 Extracting {len(articles)} articles...")
    batch_extract(articles, config)


def main(config_path: str = "config.json") -> int:
    """Main entry point.

    Args:
        config_path: Path to config JSON file

    Returns:
        Exit code (0 = success, 1 = error)
    """
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        print("Create config.json with at minimum:")
        print('  {"substack_url": "https://example.substack.com"}')
        return 1
    except KeyError as e:
        print(f"❌ Missing required config field: {e}")
        return 1

    # Check auth
    if not check_auth_state(config):
        print(f"❌ Auth state not found: {config.auth_state_path}")
        print("Run auth capture first:")
        print("  python -m scripts.auth_capture <substack_url>")
        return 1

    # Discovery
    articles = run_discovery(config)

    if not articles:
        print("⚠️  No articles found. Check your Substack URL and auth state.")
        return 0

    # Extraction
    run_extraction(articles, config)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Substack content scraper")
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config file (default: config.json)",
    )
    args = parser.parse_args()

    sys.exit(main(args.config))
