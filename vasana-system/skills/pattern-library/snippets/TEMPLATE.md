# Snippet: [Descriptive Name]

**Date:** YYYY-MM-DD
**Conversation:** [Brief context - what was being discussed]

---

## The Moment of Novelty

What NEW understanding emerged through the interaction?

[Describe what shifted - not just information transferred, but understanding that formed THROUGH the back-and-forth]

---

## How Understanding Emerged

The conversational dynamics that produced the insight:

1. [First move - what was said/asked]
2. [Response - how the other party engaged]
3. [The shift - where understanding transformed]
4. [Arrival - what crystallized]

---

## Vasana Candidate

Does this snippet exhibit a recognizable pattern?

- **Pattern name (if known):** [e.g., "productive-friction", "concrete-to-abstract"]
- **Pattern description (if new):** [How would you describe the dynamic?]
- **Similar snippets:** [Links to other snippets showing same pattern]

---

## Memory Relations

```
# When storing this snippet:
mcp__relational-memory__memorize(
  agent_name="vasana-observer",
  layer="episodic",
  content="[One-sentence summary of the novelty that emerged]",
  metadata={
    "type": "snippet",
    "vasana_candidate": "[pattern-name]",
    "date": "YYYY-MM-DD"
  }
)

# If vasana connection is clear:
mcp__relational-memory__create_relation(
  from_memory="snippet:[this-snippet-id]",
  to_memory="vasana:[vasana-name]",
  relation_type="manifests",
  agent="vasana-observer",
  context="[Why this snippet manifests that vasana]"
)
```

---

## Raw Conversation Extract (Optional)

[If helpful, include the actual exchange that contained the moment]

> Human: ...
> Claude: ...
> Human: ...
