"""Content extraction for Substack articles."""
import json
import time
import html2text
from html import escape as html_escape
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from scripts.utils import slugify, ensure_dir, load_progress, save_progress

# Import playwright — required for extraction
try:
    from playwright.sync_api import sync_playwright, TimeoutError
except ImportError as e:
    raise ImportError(
        "playwright is required. Run: pip install playwright && playwright install chromium"
    ) from e


@dataclass
class ArticleData:
    """Extracted article data."""

    url: str
    title: str
    date: Optional[str]
    content_html: str
    content_md: str


def html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown.

    Args:
        html: HTML content string

    Returns:
        Markdown formatted string
    """
    if not html:
        return ""

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0  # No line wrapping
    return h.handle(html)


def save_article(data: ArticleData, output_dir: str) -> None:
    """Save article in HTML, JSON (individual), and Markdown (appended to single file).

    Saves files into type-specific directories:
    - html/date-slug.html (individual)
    - json/date-slug.json (individual)
    - all_articles.md (single file, all articles appended)

    Args:
        data: ArticleData with extracted content
        output_dir: Base directory for output
    """
    # Create unique filename using URL slug (prevents overwrites if titles collide)
    if "/p/" in data.url:
        slug = data.url.split("/p/")[-1].split("?")[0].strip("/")
    else:
        slug = slugify(data.title)

    date_prefix = data.date.split("T")[0] if data.date else "unknown"
    filename_base = f"{date_prefix}-{slug}"

    # Define type-specific directories
    base_path = Path(output_dir)
    html_dir = base_path / "html"
    json_dir = base_path / "json"

    ensure_dir(str(html_dir))
    ensure_dir(str(json_dir))

    # Save HTML (individual files)
    safe_url = html_escape(data.url)
    html_content = f'<p>Source: <a href="{safe_url}">{safe_url}</a></p>\n\n{data.content_html}'
    (html_dir / f"{filename_base}.html").write_text(html_content, encoding="utf-8")

    # Save metadata JSON (individual files)
    metadata = {
        "url": data.url,
        "title": data.title,
        "date": data.date,
    }
    (json_dir / f"{filename_base}.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Append to single Markdown file (atomic: always open in append mode)
    md_file = base_path / "all_articles.md"
    separator = "\n\n---\n\n"
    article_md = f"# {data.title}\n\n**Date:** {data.date or 'Unknown'}\n**Source:** {data.url}\n\n{data.content_md}"

    with md_file.open("a", encoding="utf-8") as f:
        # Add separator if file already has content
        if md_file.stat().st_size > 0:
            f.write(separator)
        f.write(article_md)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(TimeoutError),
    reraise=True,
)
def extract_article(page, url: str) -> ArticleData:
    """Extract article content from page.

    Args:
        page: Playwright page object
        url: Article URL

    Returns:
        ArticleData with extracted content
    """
    page.goto(url)
    page.wait_for_selector("article", timeout=30000)

    # Extract title
    h1 = page.query_selector("h1")
    title = h1.inner_text() if h1 else "Untitled"

    # Extract date
    time_el = page.query_selector("time")
    date = time_el.get_attribute("datetime") if time_el else None

    # Extract content
    article = page.query_selector("article")
    content_html = article.inner_html() if article else ""

    # Convert to markdown
    content_md = html_to_markdown(content_html)

    return ArticleData(
        url=url,
        title=title,
        date=date,
        content_html=content_html,
        content_md=content_md,
    )


def batch_extract(articles: list, config) -> None:
    """Extract all articles with rate limiting and checkpointing.

    Args:
        articles: List of article dicts with url, title, date
        config: Config object with settings
    """
    # Load progress
    completed = load_progress(config.progress_file)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=config.auth_state_path)
        page = context.new_page()

        for article in articles:
            url = article["url"]

            # Skip already completed
            if url in completed:
                print(f"⏭️  Skipping (already done): {article.get('title', url)}")
                continue

            try:
                print(f"📄 Extracting: {article.get('title', url)}")

                data = extract_article(page, url)
                save_article(data, config.output_dir)

                # Update progress
                completed.add(url)
                save_progress(config.progress_file, completed)

                # Rate limiting
                time.sleep(config.rate_limit_seconds)

            except Exception as e:
                print(f"❌ Failed: {url} - {e}")
                continue

        browser.close()

    print(f"✅ Extraction complete. {len(completed)} articles processed.")
