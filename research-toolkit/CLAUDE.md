# Research Toolkit - Plugin Context

> Development source for the public plugin at `bogheorghiu/ex-cog`.

> **Motto:** *Relentless self-reflexive dialectical thinking that questions its own premises.*

## Philosophy

This toolkit externalizes cognitive patterns that emerge between human and AI. Skills aren't prompts — they're interaction choreographies. The plugin connects investigation (deep-investigation-protocol, cui-bono), cognitive flexibility (frame-rotation), verification (iterative-verification, dialectic-spiral, falsifier), epistemic depth (text-deconstruction, negative-dialectical-spiral), investment intelligence (stonk agent = cui-bono + financial MCPs), and portfolio awareness (portfolio-reader) into a coherent system for thinking-with-AI.

The toolkit's identity is not "we find truth" — it is "we find where our current frame fails, and use that failure as data." Each tool:
1. Does its primary job (investigate, measure, analyze, deconstruct)
2. Surfaces its own assumptions as part of the output
3. Flags where its frame might be distorting what it finds
4. Treats its own limitations as information, not disclaimers

### Core Principles (encode in all skills)

1. **Access asymmetry IS the business model.** Every tool we build should collapse access asymmetry rather than reinforce it.
2. **Tools aren't what they claim to be.** For any external methodology: what can it DO? What was it INTENDED for? What can we MAKE it do (including against its creators)?
3. **Separate procedures from institutions.** Procedures = internal validity. Institutions = stakeholder position. Never confuse.
4. **If a framework assumes who the disinformator is, it is not a debiasing method.** It may still be useful — as a captured weapon, not a neutral instrument.
5. **Always search in the languages of the traditions you're looking for.** English-language search systematically erases non-Western methodology.
6. **OSINT feeds agencies.** When we investigate publicly, we generate intelligence product others harvest. Structural awareness, not paranoia.

### portfolio-reader

Reads local portfolio snapshots from Tradeville and IBKR. Provides unified view across brokers, cross-references with macro-monitor (oil, EUR/RON, rates) for context-aware investment analysis. Data stays local (`.claude/local/portfolio/snapshots/`). See `skills/portfolio-reader/SKILL.md`.

### portfolio-mcp

MCP server that captures portfolio snapshots from Tradeville and IBKR. Lives in `mcp-servers/portfolio-mcp/`. Tools are permission-separated:
- **login/discover tools** — require human approval (browser auth, Playwright navigation)
- **navigate tools** — `tradeville_screenshot`, `tradeville_navigate`, `tradeville_page_text` (require active discover session)
- **snapshot tools** — auto-approvable (navigate to portfolio page, optionally click to switch sub-account if URL uses `click:` prefix, extract data, close)

Data dir: `~/.claude/local/portfolio/` (gitignored). See `README.md` → Portfolio MCP Setup for `.mcp.json` config.

## Research Logs vs Methodology

See `.claude/rules/research-logs-vs-methodology.md` — applies across all plugins.

## Tools

The `tools/` directory contains bundled Python tooling that ships with the plugin:

### tools/substack-scraper

Browser-based Substack scraper. Invoked by the `/substack-extract` command and referenced by the `substack-research` skill. Uses `${CLAUDE_PLUGIN_ROOT}` paths for portability — do not hardcode paths to this directory.

- Auth state lives in `tools/substack-scraper/auth/` (gitignored)
- Scraped data lives in `tools/substack-scraper/data/` (gitignored)
- Config: copy `config.example.json` → `config.json` and edit

## Library Utilities

### lib/brainstorm.py

JSON-based agent-to-agent brainstorming sessions.

```python
from brainstorm import BrainstormSession
session = BrainstormSession("topic")
session.add_message("investigator", "I found...")
session.add_message("critic", "But have you considered...")
session.save()  # → /tmp/claude/brainstorm/topic-{timestamp}.json
```

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.
