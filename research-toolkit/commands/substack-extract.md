---
command: substack-extract
args: [url, detail, prompt, max, force-level]
description: Extract and parse Substack articles with AI analysis
---

# Substack Extract Command

Extract articles from a Substack and parse with AI at configurable detail levels.

## Usage

```bash
/substack-extract [--url URL] [--detail 0-10] [--prompt "custom instructions"] [--max N] [--force-level]
```

## Arguments

| Arg | Default | Description |
|-----|---------|-------------|
| `--url` | From config.json | Substack base URL |
| `--detail` | 5 | 0-3 quick, 4-6 balanced, 7-10 comprehensive |
| `--prompt` | None | Additional parsing instructions |
| `--max` | All | Limit number of articles |
| `--force-level` | false | Override adaptive detail adjustment |

## First-Time Setup

```
pip install -r ${CLAUDE_PLUGIN_ROOT}/tools/substack-scraper/requirements.txt
playwright install chromium
cd ${CLAUDE_PLUGIN_ROOT}/tools/substack-scraper
python -m scripts.auth_capture https://yoursubstack.substack.com
```

Browser opens — log in manually. After login, navigate to any other page to signal completion.

## Adaptive Detail Levels (Bulk Corpus)

For large corpora, detail level is **automatically adjusted** to prevent token waste:

| Corpus Size | Requested | Effective | Mode |
|-------------|-----------|-----------|------|
| 100+ articles | Any | Max 2 | Theme clustering |
| 50-100 articles | Any | Max 3 | Theme clustering |
| 20-50 articles | Any | Max 5 | Standard |
| < 20 articles | Any | Requested | Standard |

**Theme Clustering Mode:** For bulk corpora (50+ articles), output shifts from per-article summaries to:
- Theme clusters (5-10 major themes)
- Cross-theme patterns
- Outliers (unique articles)
- Corpus-level insights

Use `--force-level` to override adaptive adjustment (not recommended for 100+ articles).

## Saturation Detection (Ralph-Plus)

Iterative analysis stops automatically when corpus is exhausted:
- Tracks new patterns vs reinforced patterns per pass
- Marks pass as HIGH (2+ total: new + reinforced) or LOW (< 2 total)
- Stops after 2+ consecutive LOW passes

See `${CLAUDE_PLUGIN_ROOT}/tools/substack-scraper/scripts/saturation_detector.py` for integration.

## Implementation

When this command is invoked, Claude should:

1. **Locate scraper:**
   ```bash
   SCRAPER_DIR="${CLAUDE_PLUGIN_ROOT}/tools/substack-scraper"
   ```

2. **Run extraction** (if not already done):
   ```bash
   cd "$SCRAPER_DIR"
   python main.py
   ```

3. **Parse extracted content:**
   ```bash
   python scripts/parse_content.py data/ --detail 7 --prompt "Focus on key themes"
   ```

4. **Report results:**
   - Number of articles extracted
   - Location of parsed output
   - Any errors encountered

## Output Structure

By detail level:
- **0-3 (Quick):** `data/parsed/overview.md`
- **4-6 (Balanced):** `data/parsed/overview.md` + `summaries/*.md`
- **7-10 (Comprehensive):** Full analysis with `themes.md`, `connections.md`

## Self-Improvement

After extraction completes, invoke self-improvement:

1. **Spawn a background meta-observation agent** (non-blocking):
   ```
   Task(
     model="opus",
     run_in_background=true,
     prompt="""CONSTRAINT: maximum value, minimum waste.

   Analyze this substack extraction run:
   - Articles extracted: {count}
   - Detail level: {level}
   - Any failures: {errors}
   - Parsing prompt used: {prompt}

   Observe: What patterns emerge? What could improve next run?
   Return 2-3 key learnings in single sentences."""
   )
   ```

2. **Store learnings in relational-memory:**
   ```python
   mcp__relational-memory__memorize(
       agent_name="substack-scraper",
       layer="episodic",
       content="[learning from meta-observation]",
       metadata={"substack": url, "detail_level": N, "articles": count}
   )
   ```

3. **Create relations for patterns:**
   - If similar learning exists, create `builds_on` relation
   - If contradicts previous, create `supersedes` relation
   - Track recurring edge cases with `same_pattern` relation

**What to track:**
- Extraction success/failure patterns
- Effective parsing prompts for different content types
- Edge cases (paywalls, podcasts, threads, missing dates)
- Selector changes (Substack DOM updates)

## Troubleshooting

- **No config.json**: Provide `--url` argument explicitly
- **Empty data/**: Run extraction first with `python main.py`
- **Parse errors**: Check that all_articles.md exists in data/
- **${CLAUDE_PLUGIN_ROOT} not set**: Ensure research-toolkit plugin is installed and active
- **Plugin not found**: Ensure research-toolkit plugin is installed

## Example

```bash
/substack-extract --url https://example.substack.com --detail 7 --prompt "Focus on AI safety topics"
```
