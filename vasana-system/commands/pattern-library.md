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
List all patterns in `skills/pattern-library/vasanas/`.

For each pattern found, show:
```
## [Pattern Name]
**Description:** [From file content]
**Location:** skills/pattern-library/vasanas/[name].md
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

If name provided: Read the pattern at `skills/pattern-library/vasanas/$ARGUMENTS.name.md` and discuss changes.
If no name: List patterns and ask which to update.
