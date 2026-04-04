# INTEGRATION BACKLOG — Research Toolkit

> **DO NOT SKIP THIS FILE.** It tracks unintegrated material from the CT session
> handoff (March 2026) and subsequent refactoring work.
>
> **Source:** `docs/handoffs/research-toolkit-update/` (tarballs + session maps)

---

## Status Key

| Symbol | Meaning |
|--------|---------|
| **DONE** | Integrated, committed |
| **READY** | Material exists, needs integration |
| **NEEDS RESEARCH** | Requires investigation before integration |
| **DEFERRED** | Intentionally postponed (with reason) |

---

## 1. False Consciousness as Behavioral Vasana — DONE

**Integrated:** `vasana-system/skills/pattern-library/vasanas/false-consciousness-as-behavior.md`

**Source:** `Pattern-Seed__False_Consciousness_as_Behavioral_Vasana.md` (in ct-session tar)

**What it is:** False consciousness operates as performed behavior, not held belief. Correction requires consistent memetically successful action at the edge of acceptable change, not preaching.

---

## 2. STONK Postmortem Fixes — DONE

**Integrated into:** `cui-bono/SKILL.md` sections 2a, 2b, 3, 3a, 3b

Five fixes from the proof-of-life postmortem (March 2026):
1. Symmetric beneficiary mapping (section 2a)
2. Unexamined dichotomy investigation (section 2b)
3. Evidence-structure tiering (section 3)
4. Source topology mapping (section 3a)
5. Expert stakeholder mapping (section 3b)

---

## 3. Negative Dialectical Spiral Team Architecture — DONE

**Integrated:** `agents/negative-dialectical-spiral.md` (upgraded to CC team agents)

**Portability guide:** `docs/negative-dialectical-spiral-README.md`

**Source:** `Negative_Dialectical_Spiral_Architecture.md` (in ct-session tar)

---

## 4. Research Toolkit Motto as Operational Directive — DONE

**Integrated:** Added `> *Relentless self-reflexive dialectical thinking...*` to 6 core methodology skills (dialectic-spiral, text-deconstruction, iterative-verification, manufactured-consensus-detection, source-omission-analysis, frame-rotation). Already in cui-bono and DIP.

---

## 5. Investigation Methodology Ecosystem Map (45KB) — LEAD (triaged, not implemented)

**Source:** `cc-investigation-ecosystem-handoff.tar.gz` in handoff dir

**What it is:** Comprehensive mapping of the entire investigation methodology ecosystem — how all skills, agents, and MCPs relate. 45KB master document.

**Triaged to:** `reference/ecosystem-positioning.md` — framework comparison, novelty analysis, gap tracking. Full source preserved in tarball.

**What's been extracted (reference only, not implemented):**
- Framework comparison table: DISARM, Bellingcat, Oxford, Chomsky vs our toolkit
- 4 genuinely novel capabilities identified (unexamined dichotomy detection, recursive self-observation, source topology as evidence evaluation, cross-layer integration)
- Integration architecture layer model (orchestration → classification → verification → computation → taxonomy)
- Gap analysis: DISARM TTP skill, Sherloq MCP, WorldView MCP, SunCalc — all future build items

**What still needs doing (deferred until after plugin refactor):**
- DISARM TTP taxonomy integration (skill or cui-bono extension)
- Verification procedures skill (multi-tradition: Bellingcat + Al Jazeera + Russian OSINT)
- Sherloq image forensics MCP (wrap Popescu-Farid algorithms)
- WorldView data fusion MCP (OpenSky + ADS-B Exchange + CelesTrak)
- Source topology graph tool (citation chain + amplification mapping)

**Reference docs (don't lose these):**
- `projects/ex-cog-dev/research-toolkit/reference/ecosystem-positioning.md` — framework comparison table, novelty analysis, gap tracking, integration architecture
- Full 619-line source: `docs/handoffs/research-toolkit-update/cc-investigation-ecosystem-handoff.tar.gz` → `investigation-methodology-ecosystem-map.md`

**Why deferred:** The plugin refactor (items #11, plugin-refactoring-backlog.md) must land first. Building new skills into a plugin that's about to split creates migration work. Visualize the refactor → decide the split → build new items into the right plugin.

---

## 6. Non-Western OSINT Methodology — LEAD (researched, not implemented)

**Sources:** `non-western-osint-deep-dive-directive-1.md` in handoff dir + ecosystem map section 12

**What it is:** Extending investigation capability to non-English-language source ecosystems. This is the toolkit's biggest structural blind spot — cui-bono principle 4 demands symmetric multi-polar analysis but source acquisition is English-weighted.

### Concrete Leads Found

**Chinese 舆情分析 (Public Opinion Analysis):**
- StoneDT/思通舆情 — fully open-source monitoring system (`javabloger/yuqing` on GitHub/Gitee). Docker-deployable. Monitors WeChat, Weibo, Douyin, Kuaishou, Zhihu + international platforms.
- Lambda architecture (Kafka + RabbitMQ + Elasticsearch) — more technically sophisticated than most Western OSINT tooling
- 传播分析 (propagation analysis) algorithms — trace how info spreads through Chinese platform topology
- Key insight: **managerial framing** ("what's happening?") vs Western **military framing** ("who's attacking?"). Fundamentally different starting point than DISARM.
- Search for additional tools IN CHINESE on CSDN, Zhihu, Gitee — StoneDT is one system, competitors exist

**Russian OSINT:**
- Five-stage methodology: Search → Selection → Collection → Analysis → Dissemination
- Explicitly includes leaked databases as OSINT source (Western frameworks formally exclude this — different epistemic boundary)
- Z-военкоры (Z-war correspondents): Rybar, WarGonzo — conflict-zone-stress-tested verification
- OSINT-бджоли (Ukrainian OSINT Bees) — openly describe methods as hybrid warfare tools
- Key insight: **More honest about OSINT as weapon** than Western discourse. No pretense of neutral truth-finding.
- Academic work: Belarusian Ministry of Internal Affairs academy paper on OSINT methodology

**Arabic OSINT:**
- Al Jazeera E-Learning: full OSINT investigations course (Sarah Krita)
- Al Jazeera Media Institute critical analysis: "The Citizen Journalist and the Open Source Intelligence Trap" — citizen OSINT feeds intelligence agencies' data pipeline. **This IS our "OSINT feeds agencies" principle 6.**
- Al-Zubaidi book (ISBN 9786140135345): "How Strategic Research Centers Deal with Open Source Intelligence" — methodology from OUTSIDE Western OSINT ecosystem. Available from Arab Scientific Publishers.
- Key insight: Arabic discourse is more situated within intelligence/counter-terrorism frame, but Al Jazeera's media institute shows critical awareness of OSINT→power pipeline

### What to Build (after plugin refactor)

| Item | Approach | Plugin Home |
|------|----------|-------------|
| Chinese propagation analysis skill | Extract StoneDT algorithms, build lighter version | cui-bono or research-acquisition |
| Multi-language search skill | Extend principle 5 ("search in languages of traditions") with concrete search patterns | cui-bono |
| Russian OSINT epistemic boundaries | Document leaked-database boundary, conflict-zone verification | reference doc |
| Arabic OSINT-feeds-agencies integration | Already in DIP principle 6; deepen with Al Jazeera methodology | cui-bono/DIP |
| Chinese 舆情分析 MCP | Real-time monitoring, sentiment + propagation + early warning | stonk or research-acquisition |

### Physical Acquisition

- Al-Zubaidi book — order from Dubai Library Distributors, Itihad Bookshop (Lebanon), or Snoonu (Qatar)

**Why deferred:** Same as #5 — plugin refactor must land first. Also genuinely needs research time (assessing which non-English sources are accessible via web search vs requiring specialized tools/APIs).

---

## 7. CT Philosophical Grounding — LEAD (reference doc created, not operationalized)

**Source:** `CT-Session-Map-March-2026.md` in handoff dir

**What it is:** Detailed mappings between:
- Frankfurt School (Horkheimer, Adorno, Marcuse) → vasana framework
- Foucault (power-as-productive, discourse analysis) → vasana-core
- Derrida (deconstruction, supplement, différance) → text-deconstruction skill
- Blake/Romanticism → build-first, imagination as counter-instrument

**Triaged to:** `docs/reference/ct-philosophical-grounding.md` — curated reference doc with thinker→toolkit mapping, 5 operational insights, proximity map, anti-patterns. Raw session map preserved in handoff dir.

**What still needs doing (deferred):**
- Vasana-core mappings: Foucault's power-as-productive could enrich vasana-system's VASANA-SYSTEM.md (when vasana rename happens, item #10)
- DIP self-catch pattern: Claude repeated "CT crystallized in academia" without applying DIP methodology — this self-catching capability could be operationalized as a check-assumptions extension
- Supplement logic as investigation principle: "protective mechanism requires the institution it protects against" could become a named technique in cui-bono (alongside ACH)
- Deleuze's affirmative reasoning connection to existing affirmative-reasoning language framework (frame-rotation)

**Reference docs (don't lose these):**
- `docs/reference/ct-philosophical-grounding.md` — curated thinker→toolkit mapping, operational insights, proximity map, anti-patterns
- Raw session map: `docs/handoffs/research-toolkit-update/CT-Session-Map-March-2026.md`

**Why deferred:** These are enrichments, not structural changes. Do them AFTER the plugin refactor lands — the philosophical grounding informs WHERE skills live (e.g., frame-rotation may move to vasana-system per refactoring backlog), so implementing now risks putting work in the wrong plugin.

---

## 8. Recursive Debiasing at Every Layer — DONE

**Integrated:** `cui-bono/SKILL.md` section 4a — "Recursive Debiasing Check"

Operationalized as a structured check within cui-bono's symmetric multi-polar analysis (section 4):
- Quantitative asymmetry test (evidence count, source diversity, tier distribution per pole)
- Explicit search remediation when asymmetry detected
- Meta-check: "Did my debiasing itself introduce a new bias?"
- Recursive exit criterion (no new asymmetry concerns, or explicitly noted genuine asymmetry)

Chose in-skill operationalization over separate agent/loop because the debiasing check needs access to the analysis context (evidence counts, source lists) — isolating it loses the data it needs to compare.

**Future enhancement (backlog):** The in-skill check catches bias within a single analysis context. For investigations with multiple passes (ralph loop), a stronger pattern would be multi-agent debiasing with clean context per iteration: a separate assessor agent reads the analysis output without the original context's priming, checking for asymmetric scrutiny from a fresh standpoint. This is the same pattern as the NDS architecture and the iterative-loop-engine upgrade (backlog #13). When #13 lands, recursive debiasing becomes a natural application — the assessor's criteria include "check evidence distribution across poles." Not implementing now because #13 must land first.

---

## 9. Claude Desktop Portability — DEFERRED

**Tracked in:** `docs/PORTABILITY-TODO.md`

**Reason:** CC is primary environment. Desktop lacks subagent support. Create Desktop versions when:
- User actively uses Desktop for research
- Plugin sharing makes portability important
- Desktop gains subagent support (making this moot)

---

## 10. Vasana System Plugin Rename — READY

**Rename:** `vasana-system` → `vasana`

**Scope:**
- Plugin directory: `projects/ex-cog-dev/vasana-system/` → `projects/ex-cog-dev/vasana/`
- `plugin.json` name field
- All cross-references in CLAUDE.md, rules files, plugin registry table
- Installed copies in `.claude/skills/`, `.claude/agents/`

**Effort:** Medium — mechanical rename + cross-reference sweep.

**Priority:** Low. Cosmetic. Do when convenient, not blocking anything.

**Note:** NOT version 3.0. Edge-graph + sqlite memory rewrite must land first for a major version bump.

---

## 11. Research Toolkit v3.0 Naming — NEEDS DECISION

**Problem:** "research-toolkit" is generic. User suggested "cui-bono" but it doesn't cover all contents.

**Plugin contains three distinct clusters:**

| Cluster | Skills/Agents | "cui-bono" fits? |
|---------|--------------|-----------------|
| **Critical investigation** | cui-bono, DIP, manufactured-consensus, source-omission, frame-rotation | Yes — this IS cui-bono |
| **Epistemic tools** | dialectic-spiral, text-deconstruction, iterative-verification, NDS, falsifier, adversarial-critic | Partially — these serve investigation but are general-purpose |
| **Research acquisition + financial** | substack/youtube/video extraction, portfolio-reader, macro-monitor, financial MCPs, stonk | No — these are data acquisition, not power analysis |

**Options:**

**A. Split into two plugins:**
- `cui-bono` — clusters 1 + 2 (investigation + epistemic tools)
- `research-acquisition` (or `source-pipeline`) — cluster 3 (extraction, portfolio, financial MCPs)
- Pro: each plugin has coherent identity. Con: stonk agent bridges both (uses cui-bono + financial MCPs)

**B. Split into three plugins:**
- `cui-bono` — cluster 1 only
- `epistemic-toolkit` (or `dialectic-tools`) — cluster 2
- `research-acquisition` — cluster 3
- Pro: maximum cohesion. Con: over-fragmentation, more plugin overhead

**C. Keep one plugin, different name:**
- `ex-cog` (externalized cognition) — the umbrella concept
- `critical-research` — covers investigation + epistemic + research
- `epistemic-investigation` — covers the methodology, not the acquisition
- Pro: single plugin simplicity. Con: name still won't perfectly fit everything

**D. Keep "cui-bono" as the plugin name, accept imperfect fit:**
- The motto "who benefits?" applies even to data acquisition (why are we reading THIS source?)
- Pro: memorable, distinctive. Con: portfolio-reader is a stretch

**Recommendation:** Option A (split into two). The stonk agent bridge is solvable — it can reference skills from cui-bono plugin while living in the financial/acquisition plugin, or vice versa.

**Deferred until:** User decides on split vs. rename approach.

---

## 12. A2A Protocol as Handoff Transport — READY

**What it is:** The Agent2Agent (A2A) protocol (Google → Linux Foundation, v0.3, 150+ adopters) is the emerging standard for agent interoperability. Uses HTTP/JSON-RPC/SSE, supports async long-running tasks, capability discovery via Agent Cards.

**Relevance to this plugin:**
- NDS portability guide (`docs/negative-dialectical-spiral-README.md`) maps file-based handoff to various platforms. A2A could be a universal transport layer replacing platform-specific adaptations.
- The file-based handoff pattern (agents write to `/tmp/claude/nds/cycle-N/`) maps cleanly to A2A task artifacts.
- A2A "Agent Cards" could describe S, N, A roles — making NDS discoverable by other agent systems.

**Integration approach:**
- Add A2A section to NDS portability README (done this session)
- Track A2A adoption for future: when CC supports A2A natively, file-based handoff becomes A2A task exchange
- Consider A2A for cross-plugin agent communication (stonk agent ↔ cui-bono skills across plugin boundary)

**Effort:** Low for documentation, Medium-High for actual A2A implementation.

**Priority:** Low for implementation (standard is young, CC doesn't support it yet). High for awareness (design decisions should be A2A-compatible where possible).

**Reference:** A2A spec at Linux Foundation; complementary to MCP (MCP = tools, A2A = agents).

---

## 13. iterative-loop-engine Upgrade to Multi-Agent Ralph Pattern — READY

**Current state:** iterative-loop-engine is a single-agent loop (one context, self-assessing completion). Lives in vasana-system plugin.

**Target state:** Upgrade to the documented multi-agent ralph pattern — separate executor and assessor agents with isolated contexts. The assessor evaluates the executor's output without sharing the executor's confirmation bias.

**References:**
- Current skill: `vasana-system/skills/iterative-loop-engine/`
- Ralph loop documentation: `.claude/rules/iterative-default.md`, `.claude/rules/verification-essence.md`
- PR code quality loop (working example of multi-agent iteration): `.claude/rules/pr-code-quality.md`
- NDS architecture (context isolation pattern): `research-toolkit/agents/negative-dialectical-spiral.md`

**Key design decisions:**
- Executor runs a pass → writes output to file
- Assessor (separate context) reads output + completion criteria → pass/fail
- Orchestrator manages the loop, tracks iteration count, enforces max iterations
- Team agents preferred over background agents (controllable, messageable)

**Future home:** ex-cog-tools (used by investigation, research, vasana — shared infrastructure)

**Effort:** Medium-high — architecture change, not just a tweak.

**Priority:** High. The single-agent self-assessment pattern has a known weakness: the same context that produced the work evaluates it. This is exactly the comprehension debt problem.

---

## 14. Local Docs Clone Refresh Rule — READY

**What it is:** `docs/reference/anthropic/anthropic-docs-clone/` contains local copies of Claude Code official documentation. These are referenced instead of external URLs (which rot). But the clones themselves go stale — Claude Code ships updates frequently, and our local copies were last refreshed at various dates (some Dec 2025, some Mar 2026).

**Proposed rule:** Add to `.claude/rules/documentation.md` or create `.claude/rules/docs-refresh.md`:
- Periodic refresh of `docs/reference/anthropic/anthropic-docs-clone/` (monthly or when a feature is referenced that seems wrong)
- Check `README.md` in that dir for last-cloned dates
- When refreshing: compare old vs new, note discrepancies in `README-DISCREPANCIES.md`
- Could be automated via a SessionStart hook or a scheduled skill

**Effort:** Low for the rule, Medium for automation.

**Priority:** Medium. The PR review caught us citing an external URL because the local clone existed but we didn't trust it was current. A refresh cadence prevents this.

---

## Session Notes

**Created:** 2026-03-22 during STONK → cui-bono + stonk agent refactor

**How to use this file:**
1. New session picks up work → check this file first
2. Complete an item → mark DONE with integration location
3. Discover new material → add with appropriate status
4. Item becomes irrelevant → mark DEFERRED with reason

**Don't let this file become stale.** If you're working in research-toolkit, check this file.
