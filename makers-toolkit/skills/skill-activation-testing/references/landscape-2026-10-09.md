# Landscape: tools for testing agent skills, surveyed 2026-10-09

This is a decision record: what exists, what this skill does with each tool, and why.
It is dated because this field moves monthly. Re-survey before relying on it after early 2027.

**How each fact was established.** All facts come from primary sources: the repo, its
`LICENSE`, its tags and commit log, and its code or official docs. Each fact is marked with how
far it was checked:

- **[ran]**: this session ran the tool itself.
- **[2 readers]**: two agents read the primary source independently, with no shared notes.
- **[1 reader]**: one agent read the primary source.
- **[snippet]**: only search-result text was reachable.

Nothing beyond `claude plugin eval` was executed. Where a reader inferred behaviour from code
without running it, the entry says so.

## Decisions at a glance

| Tool | What it is | Decision |
|---|---|---|
| `claude plugin eval` | first-party live runner with graders | **Adopt** as the execution engine |
| adewale/skill-eval-harness | multi-harness trigger and outcome harness with the strongest statistics found | **Interoperate**: adopted its sign-flip test; evaluate it as the cross-harness path |
| anthropics/skills `skill-creator` | trigger loop and outcome loop | **Interoperate in concept**; it is not our runner |
| iVamsi/skillcaller | trigger-only gate | **Ignore**; its ideas are already covered |
| microsoft/SkillOpt | optimizes the skill text | **Ignore for now**; it consumes a scorer and is no substitute for one |
| benchflow-ai/skillsbench | outcome benchmark with deterministic verifiers | **Borrow method**, ignore the engine |
| NousResearch/hermes-agent-self-evolution | GEPA-based optimizer | **Ignore** |
| Arcade SkillBench | static rating of skill files | **Ignore** |
| Soarr01/skillbench, aws-samples/sample-agent-skill-eval, jlov7/SkillBench-PD | smaller harnesses | **Ignore** |

## Adopt

**`claude plugin eval`** (Claude Code >= 2.1.269; docs: https://code.claude.com/docs/en/plugin-evals)
- **[ran] What it does.** On 2.1.295 it does the following:
  - runs live sessions per case (`runs`, default 3);
  - grades each run with `tool_used`, `regex`, `llm`, `baseline`, `file_exists` or `tool_order`;
  - adds a no-plugin baseline arm under `--ablation with-without`.
- **[ran] Writes** `aggregate-result.json` (schemaVersion 1). Each run's graders carry `passed`.
- **[ran] How firing is detected.** `tool_used` with `tool: Skill` and an `input_match` regex
  detects a named skill firing. `min: 0, max: 0` asserts that it did not fire.
- **[ran] Catalog.** It loads only the plugin(s) under test, so the user's other installed
  plugins never leak in. A case's `plugins:` list can load several plugins when the eval runs
  from their common parent, which gives the competitive condition.
- **[ran] Two rejections.** It refuses grader `weight: 0`, and refuses plugin paths outside the
  directory it runs against.
- **[ran] Model is not recorded.** The results record the model only when `--model` is passed.
- **[1 reader] No statistics.** It has no confidence intervals or significance tests. The
  report gives improved/flat/regressed counts, and an `llm` grader passes on 2 of 3 votes.
- **Why adopt it.** It is first-party, it runs on the deployment harness, its catalog is clean
  by construction, and its output is structured. Before it existed, the repo used a hand-rolled
  `claude -p` loop with a firing hook (issue #72). This replaces that loop for single-turn cases.
- **What it lacks, which is what `scripts/skilltest.py` adds:**
  - cases as a validated design with each case's expected winner named;
  - one design hash binding the run to its pre-registration;
  - per-case intervals, case-level resampling, and paired arm deltas with a p-value;
  - description A/B arms (OLD vs NEW copies) alongside with/without;
  - a ship rule evaluated mechanically, so it cannot be moved after the data.
- **Not covered by plugin eval.** It cannot run multi-turn planted-moment conversations (the
  full-session sim in issue #72). Those stay on the `claude -p --resume` recipe.

## Interoperate

**adewale/skill-eval-harness** (MIT; tag v0.6.0 2026-07-10; last commit 2026-10-09)
- **[2 readers] Trigger detection.** It finds firings by scanning a run's stream-json for a
  `Skill` `tool_use`, falling back to SKILL.md path reads. It has adapters for Claude Code,
  Codex, Pi and Vibe. Gemini is not supported for triggers.
- **[2 readers] Statistics.** It runs a two-sided sign-flip permutation test over per-case
  paired deltas. The test is exact up to 14 non-zero cases and Monte Carlo above that. It
  inverts the test into a 95% interval, and runs a `noise_check` that reports the smallest
  p-value the data could ever produce.
- **[2 readers] Replication.** Runs are repeated per variant.
- **Decision.** We adopted the sign-flip test's logic: `skilltest.sign_flip_p`, the same
  method in our own stdlib code, not a dependency. The reason is that our percentile bootstrap
  is too narrow when there are fewer than about 10 cases per class, and the exact test is
  honest there. For instance, 3 cases floor at p = .25 however large the effect.
- **Why not adopt the whole harness.**
  - Nobody here has run it.
  - It is a large codebase (one file is about 22k lines).
  - Its case format is its own.
- **Where it fits instead.** It is the natural candidate for the "adapter per harness" seam
  that issue #205 asks for: running the same cases on Codex or other agents. That is the next
  thing to evaluate if cross-harness firing becomes a goal.

**anthropics/skills `skill-creator`** (Apache-2.0; skill-creator last changed 2026-03-06)
- **[1 reader] Trigger loop.** It writes the skill into `.claude/commands/`, runs
  `claude -p --output-format stream-json`, and counts a `Skill` or `Read` call naming the
  skill. Defaults are 3 runs per query, a pass at a 0.5 trigger rate, 20 queries, and a 40%
  holdout.
- **[1 reader] Outcome loop.** It runs with-skill vs without-skill subagents and reports mean
  and standard deviation, with no intervals.
- **[1 reader, inference from code] Selection bias.** The best description is chosen by its
  held-out score. That makes the held-out score optimistic, so it is no longer a clean
  held-out estimate.
- **Decision.** It is compatible in concept: should-trigger vs near-miss queries are our
  positives and traps. It is not our runner, for three reasons:
  - it installs into `.claude/commands/` rather than loading the real plugin;
  - its pass bar is 0.5 at 3 runs;
  - it optimizes the description, where this skill measures it.

  Per `.claude/rules/skill-design.md` ("compose, don't fork"), use skill-creator to draft a
  description, then test that description here.

## Ignore, with the reason

- **microsoft/SkillOpt** (MIT; v0.2.0 2026-07-02; last commit 2026-10-06).
  - **[1 reader] What it does.** It optimizes the skill text against outcome scores. The skill
    is injected, so it never measures triggering.
  - **[1 reader] Its gate.** The gate in `gate.py` is a bare `cand_score > current_score`, with
    no margin or repeats. Bootstrap and McNemar statistics exist in an unreleased reporting
    module that does not feed the gate.
  - **Why ignore.** It is a consumer of a scorer, and the scorer is the part we lacked (issue
    #205, step 4). Revisit it only once a functional scorer with a measured noise floor exists.
- **benchflow-ai/skillsbench** (Apache-2.0; v1.1 2026-06-16).
  - **[1 reader] What it does.** It is an outcome-only benchmark with deterministic pytest
    verifiers, run one trial per task per condition in the repo's ablation script.
  - **What we borrow.** Two methods, already recorded in issue #205: the paired with/without
    run, and the oracle "solvability" check. Both are in `protocol.md`.
  - **Why ignore the engine.** It is Docker task packaging built for checkable domain tasks.
    Ours are epistemic skills.
- **NousResearch/hermes-agent-self-evolution** (MIT per pyproject; no LICENSE file; last commit
  2026-06-17).
  - **[1 reader, inference from code against dspy 3.4.0; not run] Phase 1 likely does not run.**
    Its GEPA call passes an argument GEPA does not accept and a 3-argument metric that GEPA's
    signature check rejects, so it falls back to MIPROv2.
  - **[1 reader] Its metric.** It scores by keyword overlap.
  - **Why ignore.** Nothing here to adopt while that holds.
- **Arcade SkillBench** (skillbench.arcade.dev).
  - **[snippet] What it is.** A static 0-100 rating of about 39k skill files, weighted toward
    safety.
  - **Why ignore.** It does not appear to run agents. Its "Discoverability & Activation"
    dimension is a judgment about the text, not a measured rate.
- **iVamsi/skillcaller** (Apache-2.0; v0.1.1 2026-08-27).
  - **[1 reader] What it does.** It is a trigger-only gate: 5 runs, at least 90% triggering,
    at most 5% false triggers, plus collision detection.
  - **Why ignore.** Collision detection is our sibling outcome class. A fixed 90/5 gate at
    n=5 cannot distinguish 90% from 70%: a Wilson interval on 5/5 runs reaches down to 0.57.
- **Soarr01/skillbench, aws-samples/sample-agent-skill-eval, jlov7/SkillBench-PD** [1 reader].
  These are smaller with/without harnesses, a weighted grade, and a progressive-disclosure
  study. Each is subsumed by plugin eval plus `skilltest`.

## What nobody in the field does yet (and so what this skill adds)

None of the tools surveyed does any of the following:

- binds a run to a pre-registered, mechanically-evaluated ship rule;
- scores firing with each case's **expected winner** named, so that a sibling legitimately
  taking a turn is not counted as a miss;
- reports the **power** of a planned run before spending on it.

Two tools come partway on adjacent points:

- adewale/skill-eval-harness comes closest on statistics.
- skill-creator splits held-out data, but uses the split to select.

## Not surveyed (gaps)

- promptfoo, Inspect AI, OpenAI/Vercel skill evals, and agentskills.io tooling were not checked.
- Trigger-eval PRs found in passing were not opened: forjd/better-writing PR #50 and
  open-skill-standard PR #32.
- arXiv, skillsbench.ai and arcade.dev were unreachable from this sandbox. Paper-level figures
  for SkillsBench are therefore unverified, and the published paper versions disagree on task
  and configuration counts.
