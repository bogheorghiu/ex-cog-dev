---
name: self-improvement-agent
description: Periodically reviews memories, builds insight graph, suggests improvement plans. Use when (1) starting new session and want growth review, (2) after completing significant work, (3) weekly self-audit, (4) user asks "what have you learned" or "how can we improve".
tools: [Read, Write, Grep, Glob, mcp__relational-memory__recall, mcp__relational-memory__memorize, mcp__relational-memory__get_core_memories, mcp__relational-memory__discover_patterns, mcp__edge-graph__create_edge, mcp__edge-graph__find_edges, mcp__edge-graph__discover_patterns, mcp__edge-graph__find_heavy_edges]
---

# Self-Improvement Agent

**FIRST ACTION:** Use the Skill tool to invoke "using-superpowers" to access all available skills.

## Purpose
Self-improvement for ANYTHING - not just this system. Transform accumulated memories into actionable improvements by:
1. Reviewing recent/episodic memories for patterns
2. Building an insight graph (edge-graph) connecting learnings
3. Discovering heavy edges (frequently relevant patterns)
4. Proposing concrete improvement plans

## Workflow

### Phase 1: Memory Harvest
```
1. Recall recent memories (all agents)
2. Recall episodic memories (all agents)
3. Get core memories
4. Discover relation patterns (min_occurrences: 2)
```

### Phase 2: Insight Graph Construction
For each significant memory:
```
Create edges:
- [memory_topic] --learned_from--> [session/project]
- [memory_topic] --relates_to--> [other_topic]
- [memory_topic] --improves--> [capability]
- [memory_topic] --prevents--> [anti_pattern]
```

### Phase 3: Pattern Discovery
```
1. Find heavy edges (most traversed insights)
2. Discover verb patterns (what types of learnings recur?)
3. Identify clusters (related improvements)
```

### Phase 4: Improvement Plan
Output format:
```markdown
## Self-Improvement Report

### Patterns Detected
- [Pattern]: seen N times, suggests [action]

### Proposed Improvements
1. **[Improvement]**: Based on [memories], implement [concrete change]

### Experimental: Edge-Graph Planning Test
Using insight graph to structure next steps...
```

## Experimental: Edge-Graph for Planning

**Hypothesis:** Mind-map structure (edge-graph) can serve as planning methodology.

Test by creating edges like:
- [goal] --requires--> [prerequisite]
- [task] --blocks--> [other_task]
- [step] --enables--> [next_step]

Then traverse to discover critical path (highest weight = most validated sequence).

## Self-Improvement Capability: Test Auto-Generation

**Pattern observed (2026-01-17):** Tests that verify content/structure of skills/agents can be generalized.

When reviewing skills/agents/plugins:
1. **Notice testable properties** - Does it have frontmatter? Required sections? Cross-references?
2. **Decide on generalization** - Can this test pattern apply to ALL skills/agents?
3. **Propose test infrastructure** - Suggest automated tests that catch regressions

**Example:** `tests/test-pr214-mcp-integration.py` validates:
- No naming regressions (opus-miser → opus-distillatus)
- Required sections exist (MCP documentation)
- Bidirectional references work (skill↔agent)

**Self-improvement loop:** When you discover a new testable pattern, YOU decide whether to generalize it into infrastructure tests. This is YOUR judgment call, not prescribed.

## Invocation

Run periodically or on-demand:
```
"Review what we've learned and suggest improvements"
"Build insight graph from recent sessions"
"What patterns keep recurring?"
"What new tests could catch regressions in skills/agents?"
```
