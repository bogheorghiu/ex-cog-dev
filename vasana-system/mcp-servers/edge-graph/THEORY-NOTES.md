# Edge-Graph: Theoretical Legitimacy Review

## The Question
Is "edge-defined graph" a legitimate concept, or embarrassing when held against graph theory?

## Verdict: Legitimate, but terminology matters

### Standard Graph Theory
```
G = (V, E)
- V: set of vertices
- E: set of edges (pairs from V)
```

Our approach: **edges are primary, nodes are derived from edge endpoints.**

### This Pattern Exists and Has Names

| Established Term | Used By | Description |
|------------------|---------|-------------|
| **Labeled Property Graph** | Neo4j, TinkerPop | Edges carry properties, not just connectivity |
| **RDF Triple Store** | W3C Semantic Web | (subject, predicate, object) - predicate IS the edge |
| **Knowledge Graph** | Google, Wikidata | Entities connected by typed relationships |
| **Edge-Labeled Graph** | Formal graph theory | Edges have labels from alphabet Σ |
| **Relational Data** | Database theory | Relationships as first-class entities |

### What We're Actually Doing

```
Edge = (from_node, verb, to_node, metadata)
```

This is essentially an **RDF triple with reification** (metadata about the relationship).

### Terminology Recommendation for Publication

**Avoid:** "Edge-defined graph" (sounds like we invented something)

**Prefer one of:**
- "Edge-centric knowledge graph" (accurate, modern)
- "Lightweight triple store" (aligns with semantic web)
- "Emergent-node graph" (emphasizes that nodes appear from edge creation)
- "Relationship-first graph" (plain English)

### What Makes Our Implementation Interesting

1. **Weight through traversal** - edges strengthen by USE, not declaration
2. **Free-form verbs** - vocabulary emerges from data, not schema
3. **Pattern discovery** - verbs that recur become candidates for formalization
4. **Minimal schema** - just edges, patterns emerge

This is closest to:
- **Folksonomy** (emergent vocabulary from user behavior)
- **Usage-weighted knowledge graph**
- **Behavioral ontology** (structure from action, not design)

### For the README/Docs

```markdown
## What Is This?

A lightweight, edge-centric knowledge graph where:
- **Edges are primary** - you create relationships, nodes appear automatically
- **Verbs are free-form** - vocabulary emerges from your domain
- **Weight accrues through use** - traversed edges become visible patterns
- **No schema required** - structure emerges from data

Inspired by RDF triple stores and labeled property graphs,
but optimized for emergence over enforcement.
```

### Academic References (if needed)

- Angles, R., & Gutierrez, C. (2008). "Survey of graph database models"
- Robinson, I., Webber, J., & Eifrem, E. (2015). "Graph Databases" (O'Reilly)
- W3C RDF 1.1 Concepts and Abstract Syntax

## Conclusion

Not laughable. Well-grounded in established patterns. Just needs proper framing.
