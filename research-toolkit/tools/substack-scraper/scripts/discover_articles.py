"""Article discovery for Substack archives."""
import json
from pathlib import Path
from typing import Optional

from scripts.utils import ensure_dir

# Import playwright — required for discovery
try:
    from playwright.sync_api import sync_playwright
except ImportError as e:
    raise ImportError(
        "playwright is required. Run: pip install playwright && playwright install chromium"
    ) from e


def extract_article_metadata(element) -> dict:
    """Extract metadata from article link DOM element.

    Args:
        element: Playwright element handle for article link

    Returns:
        Dict with url, title, date (date may be None)
    """
    url = element.get_attribute("href")
    title = element.inner_text()

    # Try to find date in parent container
    date = None
    try:
        parent_handle = element.evaluate_handle("el => el.closest('.post-preview')")
        if parent_handle:
            date_el = parent_handle.query_selector("time")
            if date_el:
                date = date_el.get_attribute("datetime")
            parent_handle.dispose()
    except Exception:
        pass

    return {
        "url": url,
        "title": title,
        "date": date,
    }


def save_article_index(articles: list, output_path: str) -> None:
    """Save article list to JSON file.

    Args:
        articles: List of article metadata dicts
        output_path: Path to save JSON file
    """
    ensure_dir(str(Path(output_path).parent))

    with open(output_path, "w") as f:
        json.dump(articles, f, indent=2)


def discover_articles(
    substack_url: str,
    state_path: str,
    max_scroll_attempts: int = 50,
) -> list:
    """Discover all articles from Substack archive.

    Args:
        substack_url: Base URL of the Substack
        state_path: Path to saved browser state
        max_scroll_attempts: Maximum scroll attempts to load content

    Returns:
        List of article metadata dicts
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=state_path)
        page = context.new_page()

        # Navigate to archive
        archive_url = f"{substack_url.rstrip('/')}/archive"
        page.goto(archive_url)

        # Scroll to load all articles (infinite scroll)
        previous_count = 0
        scroll_attempts = 0

        while scroll_attempts < max_scroll_attempts:
            # Scroll to bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)

            # Count current articles
            # Substack-specific data-testid; update if scraping breaks after DOM changes
            items = page.query_selector_all('a[data-testid="post-preview-title"]')
            current_count = len(items)

            if current_count == previous_count:
                break  # No new articles loaded

            previous_count = current_count
            scroll_attempts += 1

        # Extract metadata from all articles
        articles = []
        elements = page.query_selector_all('a[data-testid="post-preview-title"]')

        for element in elements:
            try:
                metadata = extract_article_metadata(element)
                articles.append(metadata)
            except Exception:
                continue

        browser.close()
        return articles
