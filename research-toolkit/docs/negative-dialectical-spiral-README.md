# Negative Dialectical Spiral: Portability Guide

## What This Agent Does

The Negative Dialectical Spiral generates increasingly fine-grained data about
where concepts fail against particulars. It refuses synthesis — holding
contradictions open rather than resolving them.

The core architecture requires **three context-isolated roles** running in
parallel, then sequencing their outputs through iterative cycles.

---

## Component Portability Map

| Component | CC-Specific? | Portable? | Adaptation Notes |
|-----------|-------------|-----------|-----------------|
| **Methodology** (Adorno + vasana framework) | No | Fully portable | Pure content — works as system prompt anywhere |
| **Role definitions** (S, N, A) | No | Fully portable | Natural language role descriptions |
| **Context isolation** (team agents) | **YES** | Needs adaptation | See "Achieving Context Isolation" below |
| **File-based handoff** (`/tmp/claude/nds/`) | **YES** | Needs adaptation | Any shared filesystem or message passing works |
| **Orchestrator loop** | Partially | Mostly portable | Loop logic is universal; agent spawning is platform-specific |
| **Data compounding** | No | Fully portable | Post-processing step, any LLM can do this |
| **Output format** (markdown) | No | Fully portable | Standard markdown |
| **Stopping conditions** | No | Fully portable | Semantic novelty assessment is model-agnostic |

---

## CC-Specific Components

### 1. Team Agent Spawning

```
TeamCreate(team_name="nds-spiral")
Agent(team_name="nds-spiral", name="synthesizer", ...)
```

This is Claude Code's native team mechanism. It provides:
- True context isolation (separate context windows per agent)
- Message-based coordination (SendMessage between agents)
- Shared task visibility
- Background execution with notification on completion

### 2. File-Based Handoff

Agents write to `/tmp/claude/nds/cycle-N/` and read each other's outputs.
This is a filesystem convention, not a CC feature — but the paths assume
CC's sandbox and ephemeral `/tmp/claude/` directory.

### 3. Model Selection

`model: opus` in frontmatter. CC-specific model routing.

---

## Achieving Context Isolation in Other Environments

The critical requirement is that **Role S (Synthesizer) and Role N (Negative
Dialectician) cannot see each other's output during the same cycle.** This is
not a nice-to-have — it's the core architectural constraint. If S sees N's
tension map, S pre-accommodates, destroying measurement independence.

### OpenAI Assistants API / GPT

**Approach:** Create separate Assistant instances per role.

```python
# Pseudocode
synthesizer = client.beta.assistants.create(
    name="NDS-Synthesizer",
    instructions=ROLE_S_PROMPT,
    model="gpt-4o"  # or latest
)
dialectician = client.beta.assistants.create(
    name="NDS-Dialectician",
    instructions=ROLE_N_PROMPT,
    model="gpt-4o"
)
# Each gets its own Thread (= context isolation)
s_thread = client.beta.threads.create()
n_thread = client.beta.threads.create()
```

Context isolation is achieved via separate Threads. Orchestrator logic
runs in application code (Python/JS), not in an LLM.

### Google Gemini

**Approach:** Separate chat sessions per role.

```python
s_chat = model.start_chat(history=[])
n_chat = model.start_chat(history=[])
# Each chat = separate context
```

### AutoGen / CrewAI / LangGraph

**Approach:** These frameworks natively support multi-agent with separate contexts.

- **AutoGen:** `ConversableAgent` per role, with `GroupChat` for orchestration.
  Set `allow_repeat_speaker=False` and route messages explicitly.
- **CrewAI:** `Agent` per role with separate `Task` assignments.
  Use `Process.sequential` for orchestrator control.
- **LangGraph:** Define S, N, A as separate nodes with explicit edges.
  State is passed via the graph, not shared context.

### Claude Desktop (Projects)

**Limitation:** No subagent support as of March 2026.

**Workaround:** Use the single-agent fallback (role simulation within one
context). Quality is lower due to inevitable context leakage between roles,
but the methodology still produces value.

**Alternative:** If Claude Desktop gains MCP tool support for spawning
processes, an MCP server could orchestrate the three roles as separate
API calls.

### A2A Protocol (Emerging Standard)

The Agent2Agent (A2A) protocol (Google → Linux Foundation, v0.3, 150+ adopters)
is the emerging universal standard for agent interoperability. It complements
MCP (which handles tools/resources) by handling agent-to-agent communication.

**Why it matters for NDS:** A2A could replace platform-specific adaptations
with a single transport layer. The file-based handoff pattern maps naturally
to A2A task artifacts.

**Mapping NDS to A2A concepts:**

| NDS Concept | A2A Equivalent |
|-------------|---------------|
| Role S, N, A definitions | **Agent Cards** — capability/skill declarations per agent |
| File-based handoff (`/tmp/claude/nds/cycle-N/`) | **Task artifacts** — structured output attached to tasks |
| Orchestrator loop | **Task lifecycle** — pending → working → completed, with streaming |
| Cycle outputs | **Task history** — messages exchanged during task execution |
| Stopping conditions | **Task completion** — agent signals done via task state |

**When to use A2A for NDS:**
- When building NDS as a service (e.g., a research API endpoint)
- When NDS agents need to interoperate with agents from other frameworks
- When you want NDS discoverable by other agent systems (Agent Cards)

**When NOT to use A2A:**
- Local single-environment execution (file handoff is simpler)
- CC team agents (native messaging is more integrated)
- Single-agent fallback (no agent communication needed)

**Current status (March 2026):** A2A is adopted by 150+ organizations but no
LLM coding environment (CC, Cursor, Windsurf) natively supports it yet. Design
NDS handoffs to be A2A-compatible (structured artifacts, clear task boundaries)
so migration is smooth when native support arrives.

---

### Single-Agent Fallback (Any Environment)

When multi-agent isn't available:

1. Write Role S output. **Mentally close that context.**
2. Return to original input (NOT your synthesis). Write Role N.
3. Read ONLY Role S output. Write Role A.

This is the weakest isolation but still useful. The agent document
includes this as a built-in fallback.

---

## Adaptation Checklist

When porting to a new environment:

- [ ] Can the environment run 2+ LLM calls in parallel with separate contexts?
  - Yes → Use true multi-agent (best quality)
  - No → Use single-agent fallback (acceptable quality)
- [ ] Can agents write/read shared files or pass messages?
  - Yes → Use file handoff pattern (adapt paths)
  - No → Use return values from API calls
- [ ] Does the environment support iterative loops?
  - Yes → Implement the full cycle logic
  - No → Run a fixed number of cycles (3 minimum)
- [ ] Can the orchestrator track stopping conditions?
  - Yes → Implement semantic novelty tracking
  - No → Use fixed cycle count (3-7)

---

## Quality Comparison

| Mechanism | Context Isolation | Quality | Speed |
|-----------|------------------|---------|-------|
| CC team agents | True (separate context windows) | Highest | Slowest (parallel API calls) |
| Multi-agent frameworks (AutoGen, CrewAI) | True (separate instances) | Highest | Moderate |
| OpenAI Assistants (separate threads) | True (separate threads) | High | Moderate |
| Single-agent simulation | Simulated (discipline-based) | Moderate | Fastest |
| Claude Desktop (no subagents) | Simulated | Moderate | Fast |

---

## What's NOT Portable

The **team messaging pattern** (SendMessage, inbox polling, Cowork bridge)
is CC-specific infrastructure. The NDS doesn't heavily use it — agents
communicate via files, not messages. But if you wanted live crosstalk
between S and N (which you shouldn't for this agent — isolation is the point),
you'd need environment-specific message passing.
