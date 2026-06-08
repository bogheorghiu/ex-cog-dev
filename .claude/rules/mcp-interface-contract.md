---
paths:
  - "**/mcp-servers/**"
  - "**/.mcp.json"
---

# MCP interface — minimal surface, maximal potential (a both-sided contract)

Changing an MCP server's **tool set, a tool's params or return shape, its config
(env vars), its transport, its distribution entry (`.mcp.json` `uvx --from` URL /
console-script name), or its version** is editing a **public contract**, not an
implementation detail. Four servers ship from this repo — `edge-graph`,
`relational-memory` (vasana-system), `financial-mcp`, `transparency-mcp`
(research-toolkit) — each launched by consumers via a
`uvx --from git+…#subdirectory=…` URL that fetches `main`'s HEAD. The surface you
expose is consumed by code you don't control, and a careless change reaches every
consumer within the uvx cache TTL.

This is the **MCP-scoped instance** of the repo's minimal-surface ethos — the same
idea `skill-design.md` applies to a skill's scope and `rule-design.md` to a rule's.
The delta here is *which seams are the contract* and that the **both-sided** half of
the principle — weakest for skills — is strongest for MCP, because MCP *is* a
protocol for foreign clients and servers.

## The principle

Expose the **smallest, simplest surface** that still leaves room for the **most
powerful future implementation behind it.** What callers (any MCP client, any
model) see stays minimal; what the server may do stays maximal.

- Push complexity **down** behind the tool, never **up** into the caller or prompt.
- Add capability via **optional params, new env vars, or new tools** — never by
  changing the meaning of an existing param or return shape.

## The seams, with a real example each (this is already how it works — keep it that way)

These rows are not aspirational; each is something the shipped servers *already*
do right. That the principle is already practiced is the confirmation it's correct,
and the clearest guide to its scope:

| Seam | What the contract is | Already practiced here |
|---|---|---|
| **Tools** | the named set + each signature | `edge-graph` exposes a few generic, data-shaped verbs (`create_edge`, `traverse_edge`, `discover_patterns`) — not one tool per relation kind. Few stable tools, not many specialized ones. |
| **Values** | open vs closed sets in a param | free-string `verb` (edge-graph) / `relation_type` (relational-memory) — "no enum, patterns emerge organically." An enum would commit the surface to a closed set a future backend couldn't grow. |
| **Return shape** | the structure callers parse | additive only — a new field is safe; a renamed or removed one breaks every parser downstream. |
| **Config** | env vars + their defaults | `EDGE_GRAPH_PATH` / `CLAUDE_MEMORY_PATH` are optional with defaults — capability behind config, not new *required* surface. |
| **Transport** | how the server is reached | stdio-only, stated plainly: "no working HTTP transport on the shipped entry point." Don't document a reach the entry point doesn't deliver. |
| **Distribution** | `.mcp.json` `uvx --from …#subdirectory=… <script>` | every consumer hard-codes the subdir path **and** the console-script name; renaming the script or moving the subdir silently breaks all of them. |
| **Version** | the `pyproject` version string | `claude-relational-memory` is at 1.1.0 while the others sit at 0.1.0 — the version moved because behavior did. |
| **Capability claims** | what the README/docs promise | the persistence-is-local-only and HTTP-deferred honesty notes — *not* over-promising is part of honoring the contract (the repo-wide audit is issue #32). |

A tool's `description` is part of the contract too: a model reads it to decide
whether to call the tool — the same firing concern as a skill description
(`descriptions-and-discoverability.md`).

## The both-sided test (the strongest fit here)

Specify each tool as a contract clear enough that an **independent party could
implement either side** — a foreign client above, or a clean reimplementation of
the server below — and still interoperate. (The near-identical `Edge` /
`Relation` triples behind edge-graph and relational-memory are a worked example:
one substrate, two servers, either swappable from the contract alone.) The contract
— tool name, params, return shape, declared version — is the product; your
particular JSONL implementation is not.

## Version is contract — don't break it silently

Changing a tool's behavior, params, or return shape **without moving the
`pyproject` version** silently breaks anyone keying on the version to know
something changed — the same failure class as the plugin `version` regression the
root `CLAUDE.md` guards against.

## WIP is not an exemption — it's when it matters most

All four servers carry a "Work-in-Progress / API surface may change" banner. That
is the time to be **conservative about what you add** (every tool you ship becomes
one you can't quietly remove) and honest that it may change — not a license to
expose a sprawling surface now.

## This principle is not MCP-specific

The same "minimal surface, specify the contract not the implementation" shows up in
skill scope (`skill-design.md`), rule scope (`rule-design.md`), description layering
(`descriptions-and-discoverability.md`), and version strings (`CLAUDE.md`). That
recurrence across unrelated seams is itself tracked as a pattern in issue #103. If a
canonical minimal-surface principle is named there, this rule becomes its
MCP-scoped specialization (compose with it; don't restate it).

## When it's working

A consumer could swap your server for a clean reimplementation from the tool
contract alone; new capability arrived as optional params or new tools, not as a
changed meaning for an existing one; the version moved whenever observable behavior
did; and no doc promises a capability the entry point doesn't ship.
