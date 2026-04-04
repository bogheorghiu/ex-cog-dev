#!/usr/bin/env python3
"""AI-powered content parsing with configurable detail levels.

This module provides parsing capabilities for extracted Substack content,
with configurable detail levels (0-10) that control output verbosity.

Detail Levels:
    0-3 (Quick):    Single overview.md with key themes
    4-6 (Balanced): overview.md + per-article summaries
    7-10 (Comprehensive): Full analysis with themes, connections, quotes

Usage:
    from scripts.parse_content import parse_articles, DetailLevel

    # Parse at medium detail
    result = parse_articles(articles_dir, detail_level=5)

    # Parse with custom prompt
    result = parse_articles(articles_dir, detail_level=7, custom_prompt="Focus on AI topics")
"""
import json
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Optional


class DetailLevel(IntEnum):
    """Detail level categories for parsing output."""

    QUICK_MIN = 0
    QUICK_MAX = 3
    BALANCED_MIN = 4
    BALANCED_MAX = 6
    COMPREHENSIVE_MIN = 7
    COMPREHENSIVE_MAX = 10


def get_adaptive_detail_level(article_count: int, requested_level: int) -> tuple[int, bool, str]:
    """Adjust detail level based on corpus size for bulk processing.

    Large corpora (170+ articles) cannot use per-article summaries effectively.
    This function auto-caps detail level and enables clustering mode for bulk.

    Args:
        article_count: Number of articles to process
        requested_level: User's requested detail level (0-10)

    Returns:
        Tuple of (effective_level, use_clustering, reason_message)
        - effective_level: Adjusted detail level
        - use_clustering: Whether to use theme clustering instead of per-article
        - reason_message: Human-readable explanation of adjustment
    """
    if article_count > 100:
        # Bulk corpus: force quick mode + clustering
        # 100+ articles × 500+ words = unusable output at higher levels
        effective = min(requested_level, 2)
        if requested_level > 2:
            reason = f"Bulk corpus ({article_count} articles): auto-reduced to level {effective} with theme clustering"
        else:
            reason = f"Processing {article_count} articles with theme clustering"
        return effective, True, reason

    elif article_count > 50:
        # Large corpus: cap at quick, use clustering
        effective = min(requested_level, 3)
        if requested_level > 3:
            reason = f"Large corpus ({article_count} articles): auto-reduced to level {effective} with theme clustering"
        else:
            reason = f"Processing {article_count} articles with theme clustering"
        return effective, True, reason

    elif article_count > 20:
        # Medium corpus: cap at balanced
        effective = min(requested_level, 5)
        if requested_level > 5:
            reason = f"Medium corpus ({article_count} articles): auto-capped to level {effective}"
        else:
            reason = ""
        return effective, False, reason

    else:
        # Small corpus: use requested level
        return requested_level, False, ""


@dataclass
class ParseConfig:
    """Configuration for parsing operations."""

    detail_level: int = 5
    custom_prompt: Optional[str] = None
    output_dir: Optional[str] = None
    max_articles: Optional[int] = None
    use_clustering: bool = False  # Theme clustering for bulk corpora
    adaptive_reason: str = ""  # Why detail level was adjusted

    def __post_init__(self):
        """Validate detail level is in range."""
        if not 0 <= self.detail_level <= 10:
            raise ValueError(f"Detail level must be 0-10, got {self.detail_level}")

    @property
    def category(self) -> str:
        """Return the category name for this detail level."""
        if self.detail_level <= DetailLevel.QUICK_MAX:
            return "quick"
        elif self.detail_level <= DetailLevel.BALANCED_MAX:
            return "balanced"
        else:
            return "comprehensive"


@dataclass
class ArticleSummary:
    """Summary of a single article."""

    title: str
    date: Optional[str]
    url: str
    summary: str
    key_points: list[str]
    themes: list[str]


@dataclass
class ParseResult:
    """Result of parsing operation."""

    overview: str
    articles: list[ArticleSummary]
    themes: list[str]
    connections: list[str]
    detail_level: int
    use_clustering: bool = False
    adaptive_reason: str = ""


def load_articles_from_dir(articles_dir: Path) -> tuple[list[dict], str]:
    """Load article content and metadata from directory.

    Args:
        articles_dir: Directory containing extracted articles
                     (expects json/ subdir with metadata, parent with all_articles.md)

    Returns:
        Tuple of (list of article metadata dicts, full markdown content string)
    """
    articles = []
    full_content = ""

    # Load from JSON metadata files
    json_dir = articles_dir / "json"
    if json_dir.exists():
        for json_file in sorted(json_dir.glob("*.json")):
            try:
                metadata = json.loads(json_file.read_text(encoding="utf-8"))
                articles.append(metadata)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load {json_file}: {e}")

    # Load actual markdown content from all_articles.md
    md_file = articles_dir / "all_articles.md"
    if md_file.exists():
        try:
            full_content = md_file.read_text(encoding="utf-8")
        except IOError as e:
            print(f"Warning: Could not load {md_file}: {e}")

    return articles, full_content


def generate_parsing_prompt(config: ParseConfig, articles: list[dict], content: str = "") -> str:
    """Generate the parsing prompt based on detail level and config.

    Args:
        config: Parsing configuration
        articles: List of article metadata
        content: Full markdown content from all_articles.md

    Returns:
        Prompt string for AI parsing
    """
    base_prompt = f"""Analyze the following {len(articles)} Substack articles.

Detail Level: {config.detail_level}/10 ({config.category})
"""

    # Add adaptive reasoning if detail was auto-adjusted
    if config.adaptive_reason:
        base_prompt += f"\n⚠️ {config.adaptive_reason}\n"

    # Clustering mode for bulk corpora - theme-first, not per-article
    if config.use_clustering:
        base_prompt += """
MODE: THEME CLUSTERING (bulk corpus optimization)

Output structure (optimized for large corpus):
1. **Theme Clusters** (primary output):
   - Identify 5-10 major themes across all articles
   - For each theme: 2-3 sentence summary with representative article references
   - Group articles by primary theme (list titles only)

2. **Cross-Theme Patterns**:
   - Connections between theme clusters
   - Contradictions or debates within the corpus
   - Evolution of ideas (if dates span time)

3. **Outliers** (articles that don't fit major themes):
   - List with 1-line description of why unique

4. **Corpus-Level Insights**:
   - What does this author/publication focus on?
   - Key recurring concepts, frameworks, or mental models
   - Actionable takeaways (bullet points)

DO NOT write per-article summaries. Focus on patterns, not individual articles.
Target length: 800-1200 words.
"""
    elif config.category == "quick":
        base_prompt += """
Output a concise overview covering:
- Main themes across all articles (2-3 sentences each)
- Key takeaways (bullet points)
- Notable quotes (if any stand out)

Keep response under 500 words.
"""
    elif config.category == "balanced":
        base_prompt += """
Output:
1. Executive overview (1 paragraph)
2. For each article: 1-2 sentence summary
3. Recurring themes with examples
4. Cross-article connections

Target length: 1000-1500 words.
"""
    else:  # comprehensive
        base_prompt += """
Output comprehensive analysis:
1. Executive summary
2. Detailed per-article analysis:
   - Core argument/thesis
   - Key points with quotes
   - Unique insights
3. Theme deep-dives with cross-references
4. Pattern analysis across the corpus
5. Connections and contradictions between articles

Be thorough. Include specific quotes where relevant.
"""

    if config.custom_prompt:
        base_prompt += f"\n\nAdditional Instructions:\n{config.custom_prompt}"

    # Add article metadata index
    base_prompt += "\n\n---\n\nArticles to analyze:\n"
    for i, article in enumerate(articles, 1):
        base_prompt += f"\n{i}. {article.get('title', 'Untitled')}"
        if article.get('date'):
            base_prompt += f" ({article['date']})"
        if article.get('url'):
            base_prompt += f"\n   URL: {article['url']}"

    # Add actual article content if available
    if content:
        base_prompt += "\n\n---\n\n## Full Article Content\n\n"
        base_prompt += content

    return base_prompt


def parse_articles(
    articles_dir: str,
    detail_level: int = 5,
    custom_prompt: Optional[str] = None,
    output_dir: Optional[str] = None,
    max_articles: Optional[int] = None,
    force_level: bool = False,
) -> ParseResult:
    """Generate analysis prompts for articles at specified detail level.

    Returns a ParseResult where `overview` contains a structured prompt
    for Claude to analyze, and each article summary is initially
    "[Pending AI analysis]". Actual AI analysis is performed by the
    /substack-extract command invoker (Claude Code reads the prompt and
    does the analysis work).

    For bulk corpora (50+ articles), detail level is auto-adjusted and
    theme clustering is enabled. Use force_level=True to override.

    Args:
        articles_dir: Directory containing extracted articles
        detail_level: 0-10, controls output verbosity
        custom_prompt: Additional parsing instructions
        output_dir: Where to write parsed output
        max_articles: Limit number of articles to parse
        force_level: If True, use exact detail_level without adaptation

    Returns:
        ParseResult with overview prompt, pending summaries, and themes
    """
    articles_path = Path(articles_dir)
    articles, full_content = load_articles_from_dir(articles_path)

    if max_articles:
        articles = articles[:max_articles]

    # Apply adaptive detail level for bulk corpora
    if force_level:
        effective_level = detail_level
        use_clustering = False
        adaptive_reason = ""
    else:
        effective_level, use_clustering, adaptive_reason = get_adaptive_detail_level(
            len(articles), detail_level
        )

    config = ParseConfig(
        detail_level=effective_level,
        custom_prompt=custom_prompt,
        output_dir=output_dir,
        max_articles=max_articles,
        use_clustering=use_clustering,
        adaptive_reason=adaptive_reason,
    )

    if not articles and not full_content:
        return ParseResult(
            overview="No articles found to parse.",
            articles=[],
            themes=[],
            connections=[],
            detail_level=effective_level,
            use_clustering=use_clustering,
            adaptive_reason=adaptive_reason,
        )

    # Generate the prompt with actual content (AI call happens via Claude Code)
    prompt = generate_parsing_prompt(config, articles, full_content)

    # For now, return structure with the prompt as overview
    # Actual AI parsing will be done when /substack-extract command invokes this
    mode_indicator = " CLUSTERING" if use_clustering else ""
    return ParseResult(
        overview=f"[PARSING PROMPT - {len(articles)} articles at detail {effective_level}{mode_indicator}]\n\n{prompt}",
        articles=[
            ArticleSummary(
                title=a.get("title", "Untitled"),
                date=a.get("date"),
                url=a.get("url", ""),
                summary="[Pending AI analysis]",
                key_points=[],
                themes=[],
            )
            for a in articles
        ],
        themes=["[Pending AI analysis]"],
        connections=["[Pending AI analysis]"],
        detail_level=effective_level,
        use_clustering=use_clustering,
        adaptive_reason=adaptive_reason,
    )


def write_parsed_output(result: ParseResult, output_dir: str) -> None:
    """Write parsing results to output directory.

    Args:
        result: ParseResult from parse_articles
        output_dir: Directory to write output files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Always write overview
    (output_path / "overview.md").write_text(result.overview, encoding="utf-8")

    # For balanced+ detail, write per-article summaries
    if result.detail_level >= DetailLevel.BALANCED_MIN and result.articles:
        summaries_dir = output_path / "summaries"
        summaries_dir.mkdir(exist_ok=True)

        for i, article in enumerate(result.articles, 1):
            summary_content = f"""# {article.title}

**Date:** {article.date or 'Unknown'}
**Source:** {article.url}

## Summary
{article.summary}

## Key Points
{chr(10).join(f'- {point}' for point in article.key_points) or '- [Pending analysis]'}

## Themes
{', '.join(article.themes) or '[Pending analysis]'}
"""
            filename = f"{i:02d}-{article.title[:50].replace(' ', '-').lower()}.md"
            (summaries_dir / filename).write_text(summary_content, encoding="utf-8")

    # For comprehensive detail, write additional analysis files
    if result.detail_level >= DetailLevel.COMPREHENSIVE_MIN:
        # Themes file
        themes_content = "# Themes Across Articles\n\n"
        for theme in result.themes:
            themes_content += f"## {theme}\n\n[Detailed analysis pending]\n\n"
        (output_path / "themes.md").write_text(themes_content, encoding="utf-8")

        # Connections file
        connections_content = "# Cross-Article Connections\n\n"
        for conn in result.connections:
            connections_content += f"- {conn}\n"
        (output_path / "connections.md").write_text(connections_content, encoding="utf-8")

    print(f"✅ Wrote parsed output to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse extracted Substack articles with AI"
    )
    parser.add_argument(
        "articles_dir",
        help="Directory containing extracted articles"
    )
    parser.add_argument(
        "-d", "--detail",
        type=int,
        default=5,
        help="Detail level 0-10 (default: 5)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: articles_dir/parsed/)"
    )
    parser.add_argument(
        "-p", "--prompt",
        help="Custom parsing instructions"
    )
    parser.add_argument(
        "-n", "--max",
        type=int,
        help="Maximum number of articles to parse"
    )
    parser.add_argument(
        "--force-level",
        action="store_true",
        help="Force exact detail level without adaptive adjustment"
    )

    args = parser.parse_args()

    output_dir = args.output or str(Path(args.articles_dir) / "parsed")

    result = parse_articles(
        articles_dir=args.articles_dir,
        detail_level=args.detail,
        custom_prompt=args.prompt,
        output_dir=output_dir,
        max_articles=args.max,
        force_level=args.force_level,
    )

    write_parsed_output(result, output_dir)
    config = ParseConfig(detail_level=result.detail_level)
    print(f"\nDetail level: {result.detail_level}/10 ({config.category})")
    print(f"Articles: {len(result.articles)}")
    if result.adaptive_reason:
        print(f"⚠️ {result.adaptive_reason}")
