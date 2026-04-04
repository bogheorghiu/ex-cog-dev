# VOCABULARY EMERGENCE DESIGN - HIGH PRIORITY

> **STATUS: CRITICAL DESIGN DECISION NEEDED**
> This determines whether edge-graph becomes useful or remains write-only.

## Core Philosophy (from user)

```
Never become rigid.
Never say "always use this name" or "always use this method."
Keep it always adaptive and elegant.
No canonical vocabulary, no fixed anything past what already is.
```

## The Pattern: Post-Creation Consolidation

```
1. CREATE edge with spontaneous naming (preserve intuition!)
2. AFTER creation, scan existing relations
3. IF synonymous relations found:
   - Double-check they're REALLY synonymous
   - DECIDE which direction to rename (or neither!)
   - Maybe create NEW term that encompasses both + more
4. Track the consolidation (or not?)
```

## Open Questions

### Q1: Track renames or not?
Option A: Create meta-edge `renamed_to(old_term, new_term)`
Option B: Just rename, history is in git
Option C: Keep both, link with `synonymous_with`

### Q2: What triggers consolidation?
- After every edge creation? (expensive)
- Periodic sweep? (when?)
- On-demand "consolidate now"?
- Threshold-based (when verb count > N)?

### Q3: How to find "synonymous"?
- Exact substring match? (`grounded_in` ≈ `theoretically_grounded_in`)
- Semantic similarity? (needs embeddings)
- Same from_node/to_node patterns?
- Human judgment always?

### Q4: The "NEW encompassing term" pattern
If we find:
- `theoretically_grounded_in`
- `based_on`
- `derives_from`

Do we:
- Pick one as canonical? (NO - violates "never rigid")
- Create new: `foundational_relation` that encompasses all?
- Keep all, link with `is_variant_of`?

### Q5: "Fuzzy node matching" - what does this mean?
NOT: "did you mean X?" at creation time (constraining)
MAYBE: Post-creation merge suggestions?
MAYBE: Query-time expansion ("search for X also matches X_foo, foo_X")
MAYBE: Clustering nodes by edge-pattern similarity?

## Design Principles (emerging)

1. **Creation is free** - never constrain spontaneous naming
2. **Consolidation is reflective** - happens after, with consideration
3. **No canonical forms** - synonyms coexist, linked not replaced
4. **Emergence over enforcement** - patterns surface, aren't mandated
5. **Adaptive vocabulary** - terms can merge, split, evolve
6. **Track lineage optionally** - `evolved_from`, `merged_into` as edges themselves

## Possible Implementation

```python
def post_create_consolidation(new_edge):
    """Run after edge creation, suggest consolidations."""

    # Find similar verbs
    existing_verbs = get_all_verbs()
    similar = find_similar(new_edge.verb, existing_verbs)  # How?

    if similar:
        # Don't auto-rename! Present options:
        suggestions = [
            f"Keep both, link: {new_edge.verb} --variant_of--> {s}"
            f"Rename new to existing: {new_edge.verb} → {s}"
            f"Rename existing to new: {s} → {new_edge.verb}"
            f"Create encompassing term for both"
        ]
        return suggestions  # Human decides

    # Find similar nodes
    # ... similar pattern
```

## Connection to Vasana Consolidation

Vasanas ARE this problem:
- Same behavioral pattern, different names across sessions
- Need to recognize "this vasana is that vasana"
- But also: two vasanas might MERGE into a higher-order pattern
- And: one vasana might SPLIT into more specific variants

The edge-graph vocabulary problem IS the vasana consolidation problem.

## Next Steps

1. [ ] Decide on Q1-Q5 above
2. [ ] Prototype consolidation flow
3. [ ] Test with current 16 edges
4. [ ] Define what "similar" means (Q3)
5. [ ] Build into edge-graph MCP or separate agent?

---

**This file should be reviewed in the session that tackles edge-graph improvements.**
