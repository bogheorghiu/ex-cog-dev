# Third-Party Licenses

## ralph-wiggum (Iterative Workflows)

The iterative-investigator agent and iterative-verification skill are conceptually based on the ralph-wiggum methodology. While not a code dependency, this plugin implements the same "iterate until genuinely complete" philosophy for factual accuracy tasks.

**Author:** Daisy Hollman (daisy@anthropic.com)
**Source:** Anthropic claude-code-plugins
**Repository:** https://github.com/anthropics/claude-code-plugins
**License:** MIT (as part of Claude Code ecosystem)

The ralph-wiggum technique was originally described by Geoffrey Huntley (https://ghuntley.com/ralph/) and implemented for Claude Code by Anthropic.

## yfinance (Financial Data)

Used by STONK skill via financial-data-mcp server.

**Source:** https://github.com/ranaroussi/yfinance
**License:** Apache 2.0

```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

## MCP SDK

Used by optional claude-relational-memory server.

**Source:** https://github.com/anthropics/mcp
**License:** MIT

## claude-relational-memory (Included as subcomponent)

Memory system enabling cross-session learning. Used by opus-distillatus agent (now in budget-mastery plugin).

Located in `mcp-servers/relational-memory/`. See `mcp-servers/relational-memory/THIRD-PARTY-LICENSES.md` for full attribution.
