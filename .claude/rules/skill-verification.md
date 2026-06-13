---
paths:
  - "**/skills/**"
  - "**/.claude-plugin/plugin.json"
---

# Verifying a skill or prompt change

You're changing a skill — its description, body, references — or another prompt
artifact. **"Tested" is not "CI is green."** The `unit-tests` / `smoke-test` jobs
exercise *code* (MCP servers, hooks, scripts); they say nothing about prose.
Verify by the tier that fits the change, and **state what the tier you ran
cannot see.**

## The tiers (cheapest first)

1. **Structural** — deterministic. Frontmatter parses as YAML, `name == dir`,
   description ≤ 1024 chars, house conventions (e.g. a single `## Vasana` in
   plugins that use it). A linter does this; where one isn't wired for the
   plugin yet, run the checks by hand and say so.
2. **Triggering — Tier-1 proxy** — cheap, runs anywhere. Blind LLM "router"
   judges pick which skill they'd auto-invoke, **OLD vs NEW description, one
   variable**, identical catalog + turns. Measures routing recall/precision. It
   **cannot** measure attention-capture — an explicit router reads every
   description by construction. This is the `skill-activation-testing` skill's
   method; run it for any description change and record the result *with its
   limit*.
3. **Triggering — Tier-2 live** — the real "fires under load" claim. Run a
   session with the plugin installed so its skills **and** the
   `count-skill-firings.sh` hook are active; issue many realistic, busy turns;
   count firings from `~/.claude/logs/skill-firings.log`. Numerator = the log;
   denominator = your should-have-fired turns (which lives in your run design,
   nowhere else).

## Settled facts — don't re-derive or doubt these

- **The firing hook exists and ships *with* the plugin.** It's declared in
  `vasana-system/hooks/hooks.json` (`PreToolUse`, matcher `Skill`,
  `${CLAUDE_PLUGIN_ROOT}/hooks/count-skill-firings.sh`). It activates **when the
  plugin is installed/enabled — never by hand-editing `settings.json`.** A
  dev-source session (like this repo) hasn't "installed" the plugin, so the hook
  is dark there; load it for a test with `claude --plugin-dir ./<plugin>` at
  session launch.
- **The harness *does* emit `PreToolUse` for the `Skill` tool — confirmed live.**
  A nested `claude --plugin-dir` run logged real firings (the Claude Code hooks +
  tools reference documents it too). So Tier-2's numerator is real — it just
  needs a live session to count, not a new mechanism. A worked live run (rates +
  the proxy-vs-live gap) is recorded in issue #53 (kept there rather than shipped
  — the specific run results are dev-facing).
- **The Tier-2 instrument matches Anthropic's own practice.** The Claude Code
  team logs skill usage through `PreToolUse` hooks to find skills "undertriggering
  compared to our expectations" — the same mechanism as `count-skill-firings.sh`.
  Source, worth a full read for description/trigger-keyword practice too:
  <https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills>
  (the item-by-item integration map for this repo is issue #134).

## Mistakes this protocol exists to prevent

- Reporting **"CI green" as if the changed prose were tested.** Name the tier you
  actually ran.
- Conflating **"haven't run Tier-2" with "can't be tested."** Only Tier-1's
  attention-blindness is *by construction*; Tier-2 is merely *undone* until a
  live session runs it.
- Assuming the **firing hook is absent.** It isn't — it's in the plugin.
- Calling a wording change **"better" at n=0.** It's a claim until a tier
  measures it.
- Trusting the Tier-1 proxy as a **quantitative** predictor. It's a sound
  *directional* screen, but it over-predicts live firing on borderline turns
  (measured: a boundary turn was ~2/3 on the proxy, ~1/5 live).

## This is the seed of the publish-readiness standard

This is the **interim** verification protocol. The publish-readiness bar (#53)
will formalize it into per-artifact criteria + automation, and the
testing-taxonomy (#52) refines the tiers. Written to be **extended, not
rewritten,** when those land.

**Before designing a new Tier-2 run, read issue #72's procedure harvest.** The
campaign-level procedure as actually executed (two-batch ceiling-gate structure,
pre-registered decision rules, the exact dev recipe, the proxy-blind
lexical-anchor regression class) lives in issue #72's comments pending
formalization into the `skill-activation-testing` skill — valuable now, not yet
in any shipped artifact, and this pointer is what keeps it findable until it is.
