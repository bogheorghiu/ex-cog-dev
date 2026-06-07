# Substack Scraper

Extract content from a paid Substack subscription for local/personal use.

## Prerequisites

- Python 3.10+
- Active Substack subscription (for paid content access)

## Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### 1. Authenticate (One-time)

Launch a visible browser to log into your Substack:

```bash
python -m scripts.auth_capture https://yoursubstack.substack.com
```

This opens a browser window. Log in manually (handles 2FA, CAPTCHA). After successful login, your session is saved to `auth/browser_state.json`.

### 2. Configure

Copy the example config:

```bash
cp config.example.json config.json
```

Edit `config.json`:

```json
{
  "substack_url": "https://yoursubstack.substack.com",
  "rate_limit_seconds": 2.5,
  "output_dir": "data/articles",
  "auth_state_path": "auth/browser_state.json",
  "progress_file": "progress.json",
  "max_articles": null
}
```

| Field | Description |
|-------|-------------|
| `substack_url` | **Required.** Base URL of the Substack |
| `rate_limit_seconds` | Delay between requests (default: 2.5) |
| `output_dir` | Where to save extracted content |
| `auth_state_path` | Path to saved browser state |
| `progress_file` | Checkpoint file for resuming |
| `max_articles` | Limit extraction (null = all) |

### 3. Run Extraction

```bash
python main.py
```

Or with a custom config:

```bash
python main.py --config /path/to/config.json
```

## Output Structure

```
data/articles/
├── index.json                      # List of all discovered articles
├── all_articles.md                 # Single consolidated markdown (all articles)
├── html/                           # Individual HTML files
│   ├── 2024-01-15-article-slug.html
│   └── 2024-01-16-another-slug.html
└── json/                           # Individual metadata files
    ├── 2024-01-15-article-slug.json
    └── 2024-01-16-another-slug.json
```

### Converting Old Extractions

If you have articles from before Phase 2 (individual `.md` files), convert them:

```bash
python scripts/convert_md_to_single.py data/markdown/ data/all_articles.md
```

### Parsing with AI (Detail Levels 0-10)

Analyze extracted content with configurable detail:

```bash
python scripts/parse_content.py data/articles/ --detail 5 --output data/parsed/
```

| Level | Category | Output |
|-------|----------|--------|
| 0-3 | Quick | Single overview.md with key themes |
| 4-6 | Balanced | overview.md + per-article summaries |
| 7-10 | Comprehensive | Full analysis with themes, connections |

#### Adaptive Detail for Bulk Corpora

For large article collections, detail level is **automatically adjusted** to prevent token waste:

| Corpus Size | Max Level | Mode |
|-------------|-----------|------|
| 100+ articles | 2 | Theme clustering |
| 50-100 articles | 3 | Theme clustering |
| 20-50 articles | 5 | Standard |
| < 20 articles | Requested | Standard |

**Theme Clustering Mode:** For 50+ articles, output shifts from per-article summaries to:
- Theme clusters (5-10 major themes)
- Cross-theme patterns
- Outliers (unique articles)
- Corpus-level insights

Use `--force-level` to override adaptive adjustment:

```bash
python scripts/parse_content.py data/articles/ --detail 7 --force-level
```

## Resuming Interrupted Extraction

If extraction is interrupted, simply re-run `python main.py`. Progress is saved in `progress.json` and already-extracted articles are skipped.

## Development

### Run Tests

```bash
pytest
```

### Project Structure

```
scripts/
├── auth_capture.py         # Interactive authentication
├── config.py               # Configuration management
├── convert_md_to_single.py # Batch convert old .md files to single file
├── discover_articles.py    # Article discovery from archive
├── extract_content.py      # Content extraction and conversion
├── parse_content.py        # AI parsing with detail levels (0-10)
└── utils.py                # Shared utilities
```

## Legal Notes

- **Only for personal use** with your own paid subscription
- Respects rate limiting (2.5s between requests by default)
- Session state (cookies from your manual login) is stored locally with owner-only (0600) permissions in a gitignored dir — treat it as credential-equivalent, don't share it
- No redistribution of extracted content
