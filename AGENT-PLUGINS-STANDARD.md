# AGENT-PLUGINS-STANDARD.md — the cross-vendor plugin standard, as it bears on this repo

**Created:** 2026-08-31
**Why this file exists:** on August 6, 2026, a vendor-neutral packaging standard
named **Agent Plugins 1.0.0** shipped, backed by Vercel, AWS, Anysphere (Cursor),
GitHub, Microsoft, and OpenAI. It standardizes exactly the two things every plugin
in this marketplace is made of — Agent Skills and MCP server configs — and its
manifest is a file named `plugin.json`, which collides by name with the
`.claude-plugin/plugin.json` this repo's whole release machinery keys on. A repo
that ships Claude Code plugins and maintains a portability doc (PORTABILITY.md)
needs the facts of this standard written down in one place, because they change
what "portable" concretely means and because the naming collision will otherwise
bite the first session that copies a structure from a tutorial without checking
which `plugin.json` the tutorial meant.

This is documentation of an external standard as it bears on this repo — it
proposes no changes and adds no structure (per `no-speculative-structure.md`,
adoption decisions belong to their own issue/PR when and if they happen).
PORTABILITY.md governs the shape of what we ship; this file records the external
target that shape may one day be converted *to*.

## The standard in brief

An Agent Plugin is a directory with a required manifest and optional components
in fixed locations:

```
my-plugin/
├── plugin.json              # required manifest (root level — see collision below)
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md         # Agent Skills spec format
│       ├── scripts/
│       └── references/
├── mcp.json                 # stdio, Streamable HTTP, or legacy HTTP+SSE servers
└── com.example.client/      # reverse-domain namespace for client-specific extras
```

The manifest requires exactly two fields — `$schema` (a constant URL that pins
the spec version: `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`)
and `name` (lowercase, ≤64 chars, no consecutive dots or dashes). `version`,
`description`, `author`, `homepage`, `repository`, `license`, `keywords`, and
`extensions` are optional. The schema sets `additionalProperties: false`, so any
unknown top-level key makes the whole manifest invalid — client-specific manifest
data must go under `extensions` (keyed by reverse-domain namespace) or in a
namespace folder, never at the root. That strictness matters here because this
repo's sessions habitually edit manifests programmatically; against this schema a
single stray copied field is a silent full invalidation, not a warning.

**Deliberately out of scope** — and this is why six competitors could sign it:
distribution and marketplaces, installation and updates, permissions and security
policy, runtimes, and the component types beyond skills and MCP servers
(commands, hooks, sub-agents stay client-defined). The authors call it "a small
interoperability floor for the parts that can be portable." Governance is a
public Technical Steering Committee (Amazon/AWS, Cursor, Microsoft, OpenAI,
Vercel); Anthropic and Google are on neither the launch-client list (ChatGPT,
Codex, Cursor, GitHub Copilot, Kiro, VS Code) nor the committee.

**Claude Code is reachable anyway, via translation, not native parsing.** The
`plugins` CLI (`npx plugins add owner/repo`) auto-detects installed agent tools —
Claude Code among them — and translates the vendor-neutral format into each
client's native plugin system. The precise phrasing matters: "plugins install
into Claude Code via the CLI," not "Claude Code supports Agent Plugins." A
translation layer is a dependency, not a guarantee; native adoption by Anthropic
remains unannounced as of this file's date.

## The `plugin.json` naming collision

Two different files share one filename, and this repo ships one of them:

|                 | Claude Code plugin (this repo)     | Agent Plugin (the standard)      |
| --------------- | ---------------------------------- | -------------------------------- |
| Path            | `.claude-plugin/plugin.json`       | `plugin.json` at the plugin root |
| Schema          | Claude Code's, client-defined      | agent-plugins.org JSON Schema    |
| Required fields | client-defined                     | `$schema` and `name`             |
| Extra fields    | allowed (e.g. our `userConfig`)    | rejected (`additionalProperties: false`) |

Why this is written down rather than left to be noticed: everything in this
repo's release discipline keys on the Claude one — the version-bump guard
resolves "is this file under a plugin?" by finding `.claude-plugin/plugin.json`,
and `claude plugin update` keys on its `version` field. A tutorial, README, or
AI-generated answer that says "add X to your plugin.json" is now ambiguous, and
copying the wrong structure either invalidates a standard manifest (extra fields)
or silently no-ops in Claude Code (root-level file Claude never reads). When you
read "plugin.json" anywhere, resolve which one is meant before copying anything.

Note also the MCP config filename is off by a dot: this repo's plugins declare
servers in `.mcp.json` (Claude Code's convention, hidden file); the standard uses
`mcp.json` (visible, plugin root). Same content class — ours are stdio servers
launched via `uvx`, and stdio is one of the standard's three supported
transports — different path.

## What this means for this repo (and what it does not)

**The portability bet PORTABILITY.md made is the one the market standardized
on.** The standard's portable core is Agent Skills in spec format under
`skills/` as whole trees (SKILL.md + `scripts/` + `references/`) plus
declarative MCP configs — which is PORTABILITY.md R1 (frontmatter within the
Agent Skills spec surface) and R2 (whole-tree skills) almost verbatim. The
translation tooling that reaches Claude Code today works *because* content
shaped this way converts mechanically; R1/R2 compliance is what makes this
repo's skills reachable by that tooling in the other direction too. No new rule
is needed for this — the existing ones already point at the standard's core.

**The parts of this repo the standard does not carry** are exactly its declared
out-of-scope list: hooks, commands, agents, and `userConfig`. These plugins use
all four heavily (research-toolkit's firing filter is a hook with a userConfig
master switch; every toolkit ships commands and agents). Under the standard those
would live in a reverse-domain namespace folder or the `extensions` object as
Claude-specific extras — valid everywhere, understood only by Claude. That is
not a defect to fix; it is the standard telling us which fraction of each plugin
is the portable core (skills + MCP) and which is Claude-native, and it matches
the boundary PORTABILITY.md already draws ("the idioms stay, in designated
places").

**Distribution stays ours either way.** The standard deliberately defines no
marketplace; in its ecosystem, "the repo URL is the install address" and GitHub
supplies identity and versioning. That is structurally the same position this
repo already occupies — `ex-cog-dev` on `main` is the canonical source, uvx
fetches HEAD, green CI is the only gate — so adopting or ignoring the standard
changes nothing about our release path.

**The security context cuts in our favor and is worth stating.** The aggregator
that indexes this ecosystem (agenticskills.io) audited 199 catalog MCP servers on
2026-08-07: 43% publish no auditable source at all, and 0 of 33 auditable repos
publish an SBOM. This repo's MCP servers are source-distributed by construction —
the `uvx --from git+...` URLs in each `.mcp.json` mean every consumer fetches the
exact public source this repo carries, auditable to the commit. The flip side is
already in CLAUDE.md: that same mechanism gives a bad commit on `main` a ~24h
blast radius to all consumers. One-command portable installs make the "what is
actually inside this bundle" question more pressing across the ecosystem, not
less; a marketplace whose contents are auditable by construction should keep them
that way.

## The aggregator's "Workflows" layer — the gap the spec left open, being filled

The standard's authors refused to define discovery, and the aggregator layer
filled the gap immediately. agenticskills.io (indexing 181+ skills, 200+ MCP
servers, 18+ platforms as of v1.3.0) publishes a **Workflows** directory:
curated bundles of skills + MCP servers assembled around a task rather than a
vendor — e.g. "The SEO Content Sprint" (5 skills, 4 MCPs: audit → outline →
draft → schema → publish → verify indexing), "Debug Production Issues" (1 skill,
2 MCPs: pull the error from Sentry, root-cause it, PR the fix), "Disciplined
Development" (7 skills: plan before coding, TDD, systematic debugging). Each
bundle is tagged by category (Content & Marketing, Development, DevOps &
Security) and difficulty, and sized in skills + MCP counts.

Why this matters to a marketplace maintainer here, beyond news value:

- **The unit of adoption is converging on the task-shaped bundle, not the
  individual skill.** A "workflow" in their vocabulary is what a plugin already
  is in ours: this repo's toolkits are exactly bundle-shaped (research-toolkit
  is "an investigation stack": N skills + 2 MCPs; security-toolkit is "a repo
  hygiene stack"). The composition this repo does at plugin granularity is the
  thing the discovery layer is learning to present and rank.
- **Discovery and trust are the declared open problems.** The aggregator's own
  closing analysis of the standard names them: given a need, which repo do you
  install, and is it safe? Directories answer with curation plus published
  per-server security scorecards. For this repo that means the legibility
  surfaces — each plugin's manifest `description`, README, and auditable-source
  property — are what a directory indexes and ranks; they are consumer-facing
  metadata, not internal decoration.

## Sources and verification status

Per `verify-claims.md`, claims are tiered by what was actually checked, and the
check date matters — the standard was weeks old when this was written.

**Verified against primary sources (fetched 2026-08-31):**

- agent-plugins.org (the spec site): the standard's purpose and scope
  ("small interoperability floor"), the directory layout, the three MCP
  transports, reverse-domain extension namespaces, open licensing, and TSC
  membership (Amazon, Cursor, Microsoft, OpenAI, Vercel).
- `agent-plugins.org/schemas/1.0.0/plugin.schema.json` (the published JSON
  Schema): `"required": ["$schema", "name"]`, `additionalProperties: false`,
  the `name` pattern (lowercase, ≤64 chars, no `--`/`..`), the full optional
  field list, and `extensions` as namespaced client data.

**From the aggregator (agenticskills.io, published 2026-08-07), not
independently re-verified:** the launch date and launch-client list, Vercel as
proposer, the `plugins` CLI behavior (`npx plugins add`, auto-detection,
translation into Claude Code, `~/.cache/plugins/` shallow clones), the MCP audit
figures, and the Workflows directory contents. The aggregator documents its own
per-claim verification against the Vercel announcement and spec site, and its
one flagged discrepancy (early coverage crediting "Google"; Google appears in no
primary source) checks out against the primary TSC list above — but its claims
remain one hand-off away from primary here.

**What would change this file:** native Agent Plugins support in Claude Code
(collapses the translation-layer caveat and would make an adoption decision
live), a spec revision that pulls hooks/commands/agents into scope (would move
most of each plugin into the portable core), or the naming collision being
resolved upstream. It is a snapshot of a days-old standard, dated so a future
reader can weigh its staleness — the same reasoning as PORTABILITY.md carrying
its own enforcement status.
