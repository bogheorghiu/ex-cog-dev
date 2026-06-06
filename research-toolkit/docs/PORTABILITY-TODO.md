# Portability TODO: Claude Desktop & Non-CC Environments

**Created:** 2026-03-22
**Context:** STONK refactored from monolithic skill into cui-bono (skill) + stonk (agent).
The agent uses `skills:` frontmatter composition which is CC-specific.

> **Status (not yet built):** `cui-bono` ships, but the `stonk` agent was never created —
> no agent file exists. Whether it's needed at all (vs. `cui-bono` + `financial-mcp` invoked
> directly) and its best architecture are being decided in
> [issue #61](https://github.com/bogheorghiu/ex-cog-dev/issues/61) before anything is built.
> The portability notes below are forward-looking until that lands.

---

## The Problem

Claude Desktop (Projects/web) does not support subagents. The `stonk` agent
(which composes `cui-bono` + financial MCP tools) won't work there. Neither will
any other agent in this plugin (adversarial-critic, investigation-orchestrator,
negative-dialectical-spiral, falsifier).

## What Works Everywhere

| Component | Claude Code | Claude Desktop | Other LLMs |
|-----------|-------------|----------------|------------|
| **cui-bono** skill content | Native skill | Project file / system prompt | System prompt |
| **stonk** agent | Native agent + `skills:` | NOT supported | Needs orchestration layer |
| **Financial MCP** | MCP native | MCP supported (Desktop has MCP) | Varies |
| **Methodology files** (lenses, source classifications) | Read by skill | Project files | Context documents |
| **Other agents** (adversarial-critic, etc.) | Native agents | NOT supported | Needs orchestration |

## TODO: Claude Desktop Version

### Option 1: Merged Skill (Recommended for Desktop)

Create `skills/stonk-desktop/SKILL.md` that:
- Inlines the cui-bono methodology (or references it as a companion file)
- Includes financial MCP tool usage instructions directly (Desktop supports MCP)
- Loses agent orchestration but keeps all methodology + data access
- Single file, no subagent dependency

This is essentially the old monolithic STONK skill, but updated with the
cui-bono improvements and postmortem fixes.

### Option 2: Project Knowledge Bundle

For Claude Desktop Projects:
- Upload cui-bono SKILL.md as project knowledge
- Upload methodology files as additional knowledge
- Financial MCP configured in Desktop's MCP settings
- User manually routes between power analysis and financial analysis

### Option 3: System Prompt Adapter

For non-Claude LLMs (GPT, Gemini, local models):
- Generate a single system prompt from cui-bono SKILL.md
- Strip CC-specific references (skills:, agents, MCP)
- Include methodology inline (no file references)
- Financial data via function calling (model-specific)

## Priority

Low — CC is the primary environment. Create Desktop version when:
1. User actively uses Desktop for research
2. Plugin sharing makes portability important
3. Claude Desktop gains subagent support (making this moot)

## Related

- `cui-bono` skill: Pure methodology, already portable as system prompt
- Agent pattern: `skills:` frontmatter is CC-specific composition
- MCP: Cross-platform but configuration differs per environment
