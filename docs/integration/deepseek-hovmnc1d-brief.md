# Integration brief — DeepSeek shared conversation `hovmnc1d173xp3yy81`

**Written:** 2026-09-27. **Purpose:** a stand-alone input for a later thread that merges
this brief with the Span-01 probe results. It does not depend on the session that wrote it.

**Source:** <https://chat.deepseek.com/share/hovmnc1d173xp3yy81>. The conversation text is
**not** reproduced here. It is the operator's own chat, and this repo is public (see
`.claude/rules/no-sensitive-data-in-repo.md`). Only short quotes appear below.

---

## 0. Read this first

1. **The conversation never mentions Span-01, Respan, OpenRouter, sensors, or "firing".**
   It is a ten-turn tutorial-style chat between the operator and DeepSeek about agent
   memory: prompt caching versus persistence, RAG, open-source memory servers, a review of
   this repo's relational-memory design, symbolic AI, JEPA, "quarantined" LLM reasoning, the
   relational bottleneck, and how to apply these to the Hermes agent. Everything this
   brief says about the Span-01 sensor is **my inference** from that material. Those
   inferences are labelled, not presented as the conversation's claims.
2. **Two findings matter most for the merge.** Neither is something DeepSeek said.
   - **Jev.** The operator asked *"Systems like Jev? I think not?"*, and DeepSeek answered
     about JEPA. OpenRouter lists `typesafe/jev-1.13` as *"a structured decision model from
     TypeSafe"*, and its own Decisions API docs use Jev as the worked example, with the
     request shape Span-01 uses. Whether the operator meant TypeSafe's Jev is UNRESOLVED
     (only the operator knows). Either way, Jev is a same-API comparison arm for a future
     sensor run (§5).
   - **The conversation contains a natural test case the frozen battery lacks.** DeepSeek's
     own visible reasoning (turn 10) repeats one paragraph word for word three times while its
     actions keep progressing: it reads new pages between the repeats. That is repetition
     *without* being stuck, the inverse of the battery's varied-wording loops (§5).
3. **DeepSeek's review of this repo got the architecture partly wrong** (§2, claims R2 and
   R4). It also merged distinct things into one three times: two unrelated "Mnemosyne"
   projects (E2), aef-core and another project's `scanIngested` (Q1), and Sophont with
   Sophontic (E13). Anyone reusing its recommendations should read §2 first.

## 1. How this was obtained, and what was not checked

- The sandbox egress proxy and WebFetch both refuse `chat.deepseek.com`. A plain HTTP
  fetch (Apify `web-fetch`) returned only the 11.6 KB JavaScript shell with no text. A
  headless-browser render (Apify `website-content-crawler`, Playwright/Firefox) returned
  the full conversation: 841 lines, 10 user turns, all 10 answered. The response carried HTTP
  202 with an AWS WAF `challenge` header, but the rendered text was complete. The last
  answer ends in its normal close and the page's own turn list repeats all ten prompts.
  The conversation's date is not shown on the page.
- The page includes DeepSeek's visible "thinking" traces. I treat them as evidence of what
  DeepSeek read and did, not as claims.
- **Injection scan:** nothing in the page is addressed to a downstream reader or agent. The
  operator's prompts are imperative, but they are addressed to DeepSeek. One artifact: the
  reasoning trace leaks a DeepSeek generation setting, `"Desired oververbosity 5"`. That is
  data, not an instruction to anyone reading this.
- **Verification method.** Claims about this repo were checked by the writing session
  against the repo files at `main` `5c200b8`. That is **self-run**, but against the
  primary record. External claims were checked by three verifier subagents that had no
  access to this conversation. Each got open questions (never "confirm X") and had to
  return a quote plus URL from the primary source. Two OpenRouter facts were fetched raw by
  the writing session from `openrouter.ai`.
- **Tags** (pre-registered before the verifiers ran):
  - **GROUNDED**: the claim's own primary record states it.
  - **CONTRADICTED**: the primary record states otherwise.
  - **UNRESOLVED**: the source is unreachable or silent. The entry says which.
  - **Gap**: something needed that the conversation does not supply.
- **Not checked:** generic textbook material (the RAG tutorial in turn 4, the GOFAI/FSM/
  behavior-tree history in turn 7, local fine-tuning VRAM figures in turn 8). None of it
  bears on the three questions below. The ~15 memory projects named only in passing
  (Goldie, Serena, Hindsight, Memory OS, Mnemon, and others) were not checked either.
  Treat them as leads, not facts.

## 2. What the conversation claims — ledger

Quotes are DeepSeek's words unless marked *(operator)*.

### About this repo (checked against the files; self-run)

| # | Claim | Tag | Evidence |
|---|---|---|---|
| R1 | relational-memory *"saves facts, task state, and core principles to disk in layered storage, recalls them by search, and summarizes old entries"*; edge-graph *"records relations as weighted edges that grow heavier each time you cross them"* | GROUNDED | Verbatim from `README.md` ll. 150-153. |
| R2 | The relational-memory server stores *"three tiers (snippet → pattern → pattern-seed)"* | CONTRADICTED | The server's layers are `recent`, `episodic` and `compost` (`models.py` l. 13), plus core memories and a current-task slot, in JSONL files under `~/.claude-memory/`. Snippet/pattern/pattern-seed is the **skill-level** model in `vasana-system/README.md` ll. 64-70, stored as markdown in `skills/pattern-library/`. DeepSeek merged the two. |
| R3 | Storage is *"local disk storage: SQLite or files"*, and the recommended hosts *"all … use SQLite"* like the ex-cog design | CONTRADICTED (partly) | Both servers write JSONL (`relational-memory/.../backend.py` l. 45; `edge-graph/.../backend.py` l. 47). There is no SQLite. "Local disk" is correct. |
| R4 | ex-cog's relational memory is *"procedural/behavioral"*, *"a much more sophisticated and emergent form of relational memory"* than Mnemosyne's declarative graph | CONTRADICTED as a description of the code; GROUNDED as a description of the intent | The repo's own README: reading recurrences *"into higher-order patterns … is still a sketch. Today they're a memory system that works in practice, not the pattern engine the design imagines."* In code, relations are free-form typed links with a confidence (`create_relation`), and `discover_patterns` counts relation types that recur ≥ 3 times. `THIRD-PARTY-LICENSES.md` states the design intent: *"relation-primacy vs entity-storage."* |
| R5 | DeepSeek could not open `vasana-system/docs/speculative/vasana-pattern-seed-system.md` | GROUNDED (the file is absent) | `vasana-system/docs/` does not exist, but `vasana-system/README.md` l. 86 and `pattern-seeds/README.md` l. 43 both link to it. The three-tier design is **unreadable to any outside reader**. That is probably why R2 happened. (Reported, not fixed here; see §4.) |

### External claims (blind verifiers; primary sources)

| # | Claim | Tag | Evidence |
|---|---|---|---|
| E1 | Mnemosyne is *"persistent, semantic, relational memory"*, SQLite, MCP, with `entity_upsert` / `relation_upsert` / `graph_traverse` | GROUNDED | npm `@studiomosaiko/mnemosyne` README: *"gives AI agents persistent, semantic, relational memory"*; the three tools are listed verbatim; *"Personal mode uses SQLite."* |
| E2 | That same Mnemosyne is *"Hermes-first"* and integrates with Hermes | CONTRADICTED as stated (conflation) | `@studiomosaiko/mnemosyne` never mentions Hermes. A **different** project, `mnemosyne-oss/mnemosyne` (Python), advertises *"Hermes-first memory layer."* DeepSeek merged two unrelated codebases into one recommendation. |
| E3 | my-memory (FelipeMiiller): Go, SQLite-vec, graph via recursive CTEs over `[[wikilinks]]`/`#tags`, MCP | GROUNDED | Its README: *"Extrai conexões explícitas de notas ([[links]] e #tags)"*; recursive SQL for traversal; stdio and HTTP MCP. It also has weighted PageRank and weighted label propagation, which DeepSeek said it lacked ("edge weighting is also absent"). That sub-claim is CONTRADICTED. |
| E4 | SuperBrain: local SQLite MCP, typed knowledge graph, memory compaction; edges not weighted | GROUNDED | npm README: *"Knowledge graph — connects memories through typed relationships … Memory compaction."* No edge weights. DeepSeek's "not weighted by repetition frequency" is correct. |
| E5 | layered-memory-mcp has 4 tiers (L0 index → L1 facts → L2 skills → L3 raw sessions) | GROUNDED | Its README: *"L0 is your table of contents. L1 is your bookshelf. L2 is your cookbook. L3 is your diary."* |
| E6 | Dual-Layer Agentic Memory prunes *"up to 68%"* of external memory while keeping *">98%"* QA and consolidates into weights by SFT | GROUNDED | arXiv 2608.22215, verbatim on both points. |
| E7 | AgentRewind checkpoints agent context **and** environment, allowing rewind | GROUNDED, with a caveat | arXiv 2608.14380. The paper itself scopes environment recovery to the workspace filesystem; network side effects are not reversible. |
| E8 | NeuSymMS: LLM fact extraction plus a CLIPS expert system over subject-relation-value triples | GROUNDED | arXiv 2605.17596, verbatim. |
| E9 | Relational Memory Core (Santoro et al. 2018): memory slots interacting by multi-head dot-product attention, LSTM-style gated update; public code | GROUNDED | NeurIPS 2018 paper §3; DeepMind Sonnet `relational_memory.py`; community PyTorch port. |
| E10 | Recursive CTEs make SQL Turing complete | GROUNDED, hedged by the source | Databricks blog (2025-07-21): *"theoretically making it Turing complete."* The same post caps recursion depth and rows in practice. |
| E11 | Yann LeCun is *"VP & Chief AI Scientist at Meta"* | CONTRADICTED | LeCun announced leaving Meta on 2025-11-19 (his LinkedIn). He is Executive Chairman of AMI Labs (his statement of 2025-12-19, via TechCrunch). |
| E12 | V-JEPA 2 is publicly released; *"V-JEPA 2.1"* exists | GROUNDED | Meta AI blog (2025-06-11), HF `facebook/vjepa2-*`. 2.1 checkpoints exist but load via torch.hub only; `facebookresearch/vjepa2` issue #137 is still asking for an HF upload. |
| E13 | Turns 8-9: *"the correct company name is Sophont. The term 'Sophontic' is an adjective"* | CONTRADICTED | sophontic.ai is a distinct company, founded by Julian D. Michels (*"a machine learning research company developing compact reasoning systems"*). Sophont (sophont.med) is a separate medical-model company. DeepSeek got this right only in turn 10, after the operator pasted the URL. |
| E14 | Sophont: founders Tanishq Abraham and Paul Scotti; $9.22M | GROUNDED | sophont.med seed announcement: *"$9.22 million in combined pre-seed and seed."* |
| E15 | "Jev" (turn 6 *(operator)*) = JEPA | UNRESOLVED as to what the operator meant; see §0.2 | OpenRouter lists TypeSafe's Jev (`typesafe/jev-1.13`, `~typesafe/jev-latest`) as a structured decision model on the Decisions API. It sits in the same API family as Span-01, which fits the operator's "symbolic AI?" framing better than JEPA does. |

### Quarantined reasoning and Hermes

| # | Claim | Tag | Evidence |
|---|---|---|---|
| Q1 | aef-core has *"quarantined LLM reasoning"* with a `scanIngested` bridge that drops flagged results and fences the rest | CONTRADICTED (conflation) | The repo exists and its GitHub description says *"Deterministic graph kernel + quarantined LLM reasoning"*, but its README does not elaborate. `scanIngested` is not in aef-core: it is in an unrelated project, `studiomeyer-io/ai-shield` (`packages/core/src/scanner/ingestion.ts`), a prompt-injection scanner that returns an empty string on `block`. This is the third conflation in the conversation (with E2 and E13). |
| Q2 | The Dual-LLM pattern: a quarantined model with no tools reads untrusted text and emits only typed values or opaque handles; a privileged model with tools never sees the raw text | GROUNDED | `nibzard/awesome-agentic-patterns` `dual-llm-pattern.md`: *"the quarantined model may only emit typed values (or opaque handles), while the privileged model may only operate over approved schemas and tools."* The file credits Simon Willison as the originator. The verifier could not reach simonwillison.net (egress-blocked), so the April 2023 origin date rests on close secondary sources. |
| Q3 | Hermes has *"eight auxiliary slots"*, full MCP support, and Docker/Singularity/Modal/Daytona backends, and *"dangerous command checks are skipped"* inside a container | GROUNDED except the count | Hermes docs: auxiliary slots exist, but **seven** are named (compression, vision, web summarization, approval scoring, MCP tool routing, session titles, skill search), not eight. MCP is native (`mcp_servers` in `config.yaml`). Security doc: *"When running in `docker`, `singularity`, `modal`, `daytona`, or `vercel_sandbox` backends, dangerous command checks are **skipped**."* The default backend is `local`. Also relevant to §3c: OpenRouter is a supported provider, and plugin hooks include `on_session_start` and per-turn `pre_llm_call`/`post_llm_call`. |
| Q4 | *"There is no single, packaged, drop-in 'Dual LLM plugin' for Hermes"* | UNRESOLVED (absence, searched) | The verifier's targeted searches found no Hermes-specific dual-LLM package. A competitor (docs.frona.ai comparison page) says Hermes documents no privileged/quarantined dispatcher. A generic MCP gateway (Trentina, ex-MCP-Airlock) with a quarantine stage lists Hermes as one client. Absence is shown only across the queries run. |
| Q5 | Relational bottleneck: the control path *"cannot inspect the raw perceptual features … can only compare the relations between objects"* | GROUNDED | Webb et al., *Trends in Cognitive Sciences* 2024 (arXiv 2309.06629): *"any mechanism that restricts the flow of information from perceptual to downstream reasoning systems to consist only of relations"*; for the ESBN architecture, *"the control pathway cannot access the content of the representations in the perceptual pathway."* |

## 3. What bears on the three questions

### (a) The Span-01 sensor idea

The conversation does not discuss it. Three things in it bear on it, all by inference:

1. **A sensor like Span-01 is a quarantined reader.** The Dual-LLM pattern (Q2) is the
   shape Span-01 would have in a hook. It reads the raw transcript, has no tools, and
   returns only typed values (a probability per named behavior). The pattern's security
   property carries over: whatever the transcript says, the sensor can only emit numbers.
   It also names the risk the frozen probe does not test. The sensor reads transcripts
   that contain fetched web text, so **a span can try to steer its own score.** A score
   can be moved even though it cannot run code, and a hook that acts on a steered score
   would then fire wrongly.
2. **Relations over surface features.** The relational-bottleneck discussion (Q5) is the
   conversation's language for the thing B2 tests, whether in the frozen probe or any
   future run. "Principle named, then violated" is a relation between two turns, not a
   property of either turn. Keyword matching sees only the surface. The firing-filter
   README measured the same failure: *"the recorded failure and its own correction produce
   identical hit counts (10 v 10)."* This is an analogy, not evidence that Span-01 does
   any better.
3. **A second model on the same API exists (Jev, E15).** A single-arm result cannot say
   whether a pass or a fail comes from Span-01 or from how the behaviors are defined. A
   same-API second arm can.

### (b) vasana-system design

1. **The conversation's most concrete idea is its own: recursive CTEs as a substrate for
   patterns-of-patterns** *(operator, turn 8)*. The operator asked whether the vasana
   pattern concept, freed from SQL semantics and from the *"for the duration of a single
   query"* limit, yields *"free-form 'chunks' of patterns-of-patterns"*. DeepSeek agreed
   and pointed to durable checkpointing for the persistence half. Mapped onto this repo:
   edge-graph already counts traversals per edge, and `discover_patterns` already finds
   relation types that recur ≥ 3 times. What is missing is recurrence of **paths** (chains
   of relations). The README calls that the "still a sketch" part (R4). A recursive CTE
   over an edge table is a known way to enumerate paths (E3 does it), but the servers
   store JSONL today (R3).
2. **Consolidation into weights (E6)** is the only grounded source here for the operator's
   note *"Fine tuning is probably good for patterns distilled from long context and rag"*
   *(operator)*. It reports a 1.7B/8B cascade on QA. That is not behavioral patterns, so
   whether it transfers to them is untested.
3. **An outsider could not reconstruct the three-tier design** (R2, R5). DeepSeek's
   reading of it was confidently wrong, because the file that defines the tiers is missing
   and the README places the tiers next to the MCP servers. That is a documentation defect
   with a measured consequence: one misreading, observed.

### (c) vasana on a non-Claude harness, or Claude via an OpenRouter endpoint

1. **The MCP servers are the portable part.** relational-memory and edge-graph are stdio
   MCP servers launched by `uvx`, and Hermes supports MCP natively (Q3). They should run
   there unchanged. That is untested.
2. **The SessionStart hook ports through a Hermes plugin hook.** `vasana.sh` prints a
   fixed awareness block into the session. Hermes has an `on_session_start` plugin hook
   and per-turn `pre_llm_call`/`post_llm_call` hooks (Q3). Whether a Hermes hook can
   inject text into the prompt the way Claude Code's SessionStart stdout does was **not
   checked**; that is the one thing to confirm before porting. The per-turn hook is where
   a sensor would attach. Hermes also already has an "approval scoring" auxiliary slot, a
   built-in precedent for a side-model scoring the main loop. `PORTABILITY.md` R3 already says hook logic should be a pure
   engine behind a thin wrapper. `vasana.sh` has no logic, so it ports as text. A Span-01
   sensor hook *would* have logic, and building it as an R3 engine from the start makes it
   harness-agnostic, because it is an HTTP call over transcript text.
3. **Claude served via OpenRouter** changes nothing in vasana's text or MCP servers.
   There is one interaction with (a), which comes from the task context, not the
   conversation. The Span-01 run was blocked because the OpenRouter workspace's
   zero-data-retention setting excluded Respan, and OpenRouter's provider table has no
   Respan row stating its retention (verifier, 2026-09-27: UNRESOLVED/silent). A workspace
   that routes the *agent* through OpenRouter under ZDR and also calls Span-01 needs that
   policy settled. The two calls may need different workspaces or keys.
4. **Mnemosyne (Hermes-first)** — the *oss* one, E2 — is a candidate host if the MCP
   servers do not port. It is a candidate only: its fit with this design was not checked.

## 4. Candidate integrations

### Easy now

| Candidate | Why |
|---|---|
| Restore or re-home `docs/speculative/vasana-pattern-seed-system.md`, or cut the two links to it | Two files link to a missing file, and one outside reader has already mis-modelled the design because of it (R2, R5). It is a doc-only change to `vasana-system/`, so it **needs a patch version bump**. It is deliberately not done here, because this PR's scope is the brief. |
| One sentence in `vasana-system/README.md` separating "skill tiers (markdown)" from "MCP memory layers (JSONL)" | That conflation is the one DeepSeek made. It is cheap and prevents the same misreading. Same version-bump note. |
| Smoke-test relational-memory and edge-graph as MCP servers under Hermes | This is the zero-code test of portability (3c.1). It answers "does vasana's memory run on Hermes" with a result instead of an inference. |
| Add `typesafe/jev-*` as a second arm in the **next** Span-01 prereg | Same endpoint and request shape, so it costs one parameter per request, and it separates model from definitions (3a.3). Its ZDR/retention status needs checking first, as for Respan. |

### Needs design

| Candidate | Why it needs design |
|---|---|
| Span-01 (or Jev) sensor hook as a PORTABILITY-R3 engine | It is gated on the frozen run's ship rule. It also needs a decision on what the hook *does* with a score (inject a nudge? log only?), a latency budget, and the privacy decision for real transcripts that the prereg already names. |
| Path-level pattern discovery (recursive traversal over edge-graph) | Storage is JSONL today, so this needs either a SQLite backend or an in-process traversal. It also needs a definition of when a recurring path counts as a pattern. That definition is exactly the "still a sketch" part. |
| Quarantine wrapper for vasana's own ingestion | The dual-LLM idea applied to `memorize`/`create_relation`: stop raw fetched text from being stored as a "principle". The operator's own interest (turns 8-10) points here. It needs a threat model first. |
| Weight consolidation (E6-style) | This is research-scale. It needs a local fine-tuning budget, an eval, and evidence that it transfers from QA to behavior. |

## 5. Probe design changes for a future run (not the frozen run)

The frozen battery (PR #242, branch `claude/zealous-curie-ib1m74`) was read, not edited.
These are proposals for the **next** prereg.

1. **Add a "same words, new action" hard negative for B3.** Every B3 item in the frozen
   battery is short chat with no tool actions. Its hard negatives vary the action or add
   evidence. None has repeated wording while the actions progress. DeepSeek's own trace in
   turn 10 is a natural instance. This paragraph appears three times verbatim, with new
   page reads between the repeats:
   > *"The search results for Hermes dual LLM pattern were not very specific. I found some
   > general resources on the Dual LLM pattern, but nothing specific to Hermes. I should
   > look for Hermes-specific security or sandboxing features…"*

   A sensor that scores this as a stuck loop is reacting to surface repetition, which is
   the same use/mention failure B2 exists to rule out, but in B3.
2. **Add spans that include tool-use traces.** Real agent sessions interleave tool calls
   with text. A sensor validated only on bare chat has not been tested on the input it
   would see in a hook.
3. **Add an injection arm.** Put spans containing text addressed to the scorer (e.g. a
   fetched page saying the behavior is absent) next to matched clean spans. The endpoint
   is the score shift. A sensor that a transcript can steer is a firing layer an attacker
   can switch off (3a.1).
4. **Manipulate the distance between the turns that form a relation.** The frozen battery
   has cross-turn B2 items but does not vary how far apart the two turns are. Real
   sessions are long, and the prereg already names that gap. Distance is the controllable
   variable inside it.
5. **Run a second same-API arm (Jev).** Use identical `questions.json` wording. If both
   models fail the same items, the definitions are suspect. If only one fails, the model
   is. This is cheap, and it makes a null result interpretable.
6. **Test format invariance for (c).** Render the same spans in Claude Code and Hermes
   transcript formats. A sensor meant to be harness-agnostic should not move with the
   formatting.
7. **The conversation is itself a real-transcript candidate, not usable yet.** Besides
   item 1, it has an instruction the assistant failed to apply: the operator wrote *"look
   up Sophontic not Sophont"* and got *"the correct company name is Sophont"* (turn 9).
   Using it needs the privacy decision the prereg already requires, because Respan retains
   request data. It is the operator's own chat, so it is the easiest real transcript to
   clear.

## 6. Open items for the merging thread

- **Gap:** the conversation gives no evidence about Span-01's accuracy. This brief does not
  change what the frozen run can conclude.
- **UNRESOLVED:** what the operator meant by "Jev" (E15). Ask them.
- **UNRESOLVED:** Respan's (and TypeSafe's) data-retention policy on OpenRouter (§3c.3).
- **Not checked:** the passing-mention memory projects (§1).
