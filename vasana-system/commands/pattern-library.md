---
name: pattern-library
description: Browse, add, or update patterns in the library
arguments:
  - name: action
    required: false
    description: "Action: browse (default), add, or update"
  - name: name
    required: false
    description: Pattern name (for add/update)
---

# Pattern Library Command

Manage the pattern library — browse existing patterns, add new ones, or update existing.

## Actions

### browse (default)
List all patterns in the canonical pattern-library `patterns/` directory (default: `ClaudeShared/pattern-library/patterns/`). The bundled `skills/pattern-library/patterns/` is seed data — falls back to it only if no canonical location is configured.

For each pattern found, show:
```
## [Pattern Name]
**Description:** [From file content]
**Location:** ~/ClaudeShared/pattern-library/patterns/[name].md
  (or configured canonical location — see plugin CLAUDE.md; falls back to bundled `skills/pattern-library/patterns/[name].md` if no canonical location is set)
---
```

After listing, suggest:
- `/pattern-library add [name]` to record a new pattern
- `/test-pattern [name]` to test one
- Read any pattern file to see full description

### add
Record a new pattern. Uses the `record-pattern` skill.

If name provided: Create a pattern named `$ARGUMENTS.name` based on current conversation or described interaction.
If no name: Ask the user to describe the interaction pattern, then suggest a name.

### update
Update an existing pattern.

If name provided: Read the pattern at `~/ClaudeShared/pattern-library/patterns/$ARGUMENTS.name.md` (the canonical library; falls back to bundled `skills/pattern-library/patterns/$ARGUMENTS.name.md` if no canonical location is set) and discuss changes.
If no name: List patterns and ask which to update.
