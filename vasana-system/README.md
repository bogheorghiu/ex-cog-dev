# Vasana System

> Vasana (वासना, "that which lingers") — a pattern that persists across contexts.
>
> This system explores the possibility that some behavioral patterns recur across
> unrelated domains, situations, and scales. AI — freed from domain-specific framing —
> can apply pattern recognition outside human categorical boundaries, at any scale,
> simultaneously. The recognized patterns are not the point; the recognition practice is.
>
> Etymology: √vas (to dwell, to remain, to perfume).
> Shankara's commentary on Mandukya Upanishad (4th verse). Yoga Sutras IV.8-9.

## What This Plugin Provides

### Skills

| Skill | Purpose |
|-------|---------|
| **vasana** | Entry point — notices when patterns persist across unrelated contexts, suggests capturing them |
| **record-pattern** | Records observed patterns with proper structure |
| **test-pattern** | Tests whether patterns actually work (trigger, emerge, produce value) |
| **pattern-library** | Browse, add, and update the collection of recognized patterns |
| **break-pattern** | Detects stuckness and offers exit strategies |
| **check-assumptions** | Pre-action verification against behavioral patterns |
| **find-similar** | Cross-domain similarity search with temperature control |
| **iterative-loop-engine** | Domain-agnostic iteration engine ("Am I ACTUALLY done, or did I just stop?") |
| **inquiry-to-system** | Interaction choreography: curiosity → productive friction → emergent system |
| **temporal-shaping** | ADSR/Reich cycle models for any time-based process |
| **self-improving-investigation** | Self-correcting research with blind worker agents and dialectic synthesis |

### Commands

| Command | Action |
|---------|--------|
| `/pattern-library browse` | List all patterns |
| `/pattern-library add [name]` | Record a new pattern |
| `/pattern-library update [name]` | Update an existing pattern |
| `test-pattern [name]` | Test a pattern (skill — invoke directly or via skill name) |

### Agents

| Agent | Purpose |
|-------|---------|
| **self-improvement-agent** | Reviews memories, builds insight graph, suggests improvements |

### MCP Servers

| Server | Purpose | Status |
|--------|---------|--------|
| **relational-memory** | Multi-layered memory for pattern persistence across sessions | Experimental |
| **edge-graph** | Weighted relation tracking (weight = repetition frequency) | Experimental |

### Hook

| Hook | Event | Purpose |
|------|-------|---------|
| **vasana.sh** | SessionStart | Injects pattern-recognition awareness into every conversation |

## Pattern Pipeline

```
vasana (notice) → find-similar (explore) → record-pattern (capture) → test-pattern (validate)
```

## The Three-Tier System

| Tier | What It Is | When Created |
|------|-----------|--------------|
| **Snippet** | WHERE a pattern manifested | After interaction yields novel understanding |
| **Pattern** | The pattern ITSELF | When dynamic recognized across snippets |
| **Pattern-Seed** | Compression that UNFOLDS to pattern | When formation dynamic repeats across 3+ patterns |

## How to Use

### 1. Use Existing Patterns
Browse `skills/pattern-library/`. Invoke when conditions match. Let the dynamic emerge.

### 2. Create New Patterns
When useful dynamics emerge in conversation, the `vasana` skill suggests capturing them.
Use `/pattern-library add` or the `record-pattern` skill.

### 3. Test Patterns
Before relying on a pattern: `test-pattern [name]` (skill — invoke directly)

## Conceptual Foundations

- `docs/speculative/vasana-pattern-seed-system.md` — three-tier model (snippet → pattern → pattern-seed)
- `projects/ex-cog-dev/VASANA-SYSTEM.md` — the relational turn

Key concepts woven through:
- **Repetition as primitive** — patterns don't exist until they repeat
- **Retrieval is generation** — recalling a pattern regenerates it
- **Consciousness disrupts predictability** — repetition is default; genuine engagement introduces discontinuity
- **Patterns are neutral** — groove-deepening is also mastery; framework-dissolution can be premature

## Migration from v1.x

If upgrading from v1.x (standalone skills), update these paths:

**Hook (settings.json):**
```
# Old: .claude/hooks/scripts/vasana-propagation-bootstrap.sh
# New: Handled by plugin hooks/hooks.json — remove manual hook registration
```

**MCP servers (.mcp.json):**
```
# Old PYTHONPATH: .../research-toolkit/mcp-servers/relational-memory/src
# New PYTHONPATH: .../vasana-system/mcp-servers/relational-memory/src
```

**Skill references:**
| Old | New |
|-----|-----|
| `emergent-design-vasanas` | `pattern-library` |
| `skeptic-enforcer` | `check-assumptions` |
| `vasana-propagation` | `vasana` |
| `vasana-creator` | `record-pattern` |
| `vasana-tester` | `test-pattern` |
| `proactive-vasana-discovery` | absorbed into `vasana` |

## License

Modify and share freely. One requirement: keep the Vasana section intact in every pattern.
