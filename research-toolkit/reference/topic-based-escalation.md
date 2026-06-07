# Topic-Based Escalation Reference

> **Not a skill** — a reference file that skills READ. Defines routing logic in one place.
> Referenced by: `/research` hub, `youtube-research`, `substack-research`, and any future research skill.

> **Note on financial/investment routing:** power-structure methodology lives in the
> **cui-bono** skill; market data comes from the **financial-mcp** tools. A dedicated
> **stonk** agent to orchestrate the two automatically is in design — see
> [issue #61](https://github.com/bogheorghiu/ex-cog-dev/issues/61). Until it ships, route
> investment questions to **cui-bono + financial-mcp** directly.

## Escalation Table

| Topic Domain | Primary Skill | Depth | Why |
|-------------|--------------|-------|-----|
| Geopolitical/military | DIP (full) + cui-bono lenses | 4+ rounds | Source omission, multi-polar analysis critical |
| Financial/investment | cui-bono + financial-mcp | 4+ rounds | Power structure, ethical framework, financial data |
| Power structure / "who benefits" | cui-bono | 4+ rounds | Core cui-bono territory |
| Safety/health/trust | DIP (full) | 4+ rounds | Marketing-vs-reality gap detection |
| Corporate trustworthiness | DIP | 3-4 rounds | Surface > flow tracing > verification |
| Product comparison | dialectic-spiral (light) | 2 rounds | Sufficient for hardware/tool choices |
| Tutorial/how-to/practitioner | None | 0 | Practitioner knowledge, verify by doing |
| Contrarian single-source claim | dialectic-spiral (full) + iterative-verification | 4+ rounds | High risk of manufactured dissent |
| Multi-domain (trust + investment) | DIP first > cui-bono + financial-mcp | 4+ rounds each | Establish reliability, then ethical positioning |
| Job / studio defense-screening | dev-job-defense-ties (runs cui-bono first) | 1-2 passes | Buyer-chain to end user + operator red-line classification |

## Rules

1. Escalation is SUGGESTED, not forced. Always state the recommendation and reason.
2. In budget mode: cap dialectic at 2 rounds, note limitation in output.
3. When a research skill (youtube/substack) encounters a topic in this table, it should mention the escalation option to the user.
4. The `/research` hub applies this table automatically on first routing.
5. Individual skills reference this table for mid-research escalation (e.g., youtube-research discovers geopolitical content mid-extraction).

## When to Use DIP vs cui-bono

| Question | Use | Why |
|----------|-----|-----|
| "Is X trustworthy/safe?" | DIP | Surface > systemic gap detection |
| "Should I invest in / support X?" | cui-bono + financial-mcp | Power structure + ethical framework + market data |
| "Who benefits from X?" | cui-bono | Multi-polar power structure mapping |
| "Compare X vs Y vs Z" (with ethics) | cui-bono | Multi-entity + ethical dimensions + lenses |
| "What's really happening with X?" | DIP | General investigation, source sweep |
| Trust AND investment/power | DIP first > cui-bono | Establish reliability, then positioning |
| Geopolitical/military analysis | DIP + cui-bono lenses | DIP for methodology, cui-bono's lenses for domain depth |

DIP = broader methodology, any domain with information asymmetry.
cui-bono = specialized instantiation for power + money + ethics + multi-polar analysis.
Both use dialectic-spiral. Both use evidence tiers. That overlap is intentional.

## What Each Uniquely Adds

| DIP Unique | cui-bono Unique |
|-----------|-------------|
| 5-stage progression (surface > flows > verification > risk > calibration) | Mandatory framework clarification FIRST |
| Risk Assessment stage (investigation reliability self-check) | 6 specialized lenses (weapons, labor, environmental, governance, supply chain, geopolitical) |
| Technical Expert Sourcing (Postol Pattern) | Symmetric multi-polar analysis (same standards for all power poles) |
| Social media integration as deliberate source | Framework-conditional output ("If priority A, then X; if B, then Y") |
| Trust/Quality Decision Framework | Financial MCP integration (structured market data) |
| Source omission as mandatory investigation step | Multi-tradition named techniques (ACH, Bulletproofing, ARIJ) |

## Examples of Escalation in Practice

For worked examples demonstrating DIP + cui-bono + dialectic-spiral on geopolitical, tech/trade, and corporate topics, see investigation files under `docs/research/`.
