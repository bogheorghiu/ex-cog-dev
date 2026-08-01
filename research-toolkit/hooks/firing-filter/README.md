# firing-filter — the deterministic firing layer

The research-toolkit's recorded failure mode is not missing rules — it is
**correct rules that do not fire**, exactly when firing would be inconvenient.
In the canonical recorded case the analyst wrote the governing principle into
its own task list, named it verbatim in its own output, and violated it
minutes later; a human caught it. Across every recorded case, **every
correction was externally forced — none was spontaneous.** So this layer
assumes nothing about anyone noticing anything: it is an external challenge,
scheduled, with zero model calls and zero judgment anywhere in it.

## The design in one sentence

**Words arm. Situations point. Facts block.**

| layer | matches | payload | why this and no more |
|---|---|---|---|
| lexicon (arming) | watchlist / verdict / absence / tier vocabulary | none — wakes the layer above | measured: the recorded failure and its own correction produce identical hit counts (10 v 10); a string cannot tell use from mention, so word-hits carry no enforcement signal. Over-firing here is free and correct. |
| situations | what a unit **is**: a verdict being rendered (S1), a source-judgement being commissioned (S2), a tiered memo returning beside absence claims (S3) | **one** guidance injection per unit (S2: one deny, capped at 2/session) | measured: span-attached payloads yield 72 forced annotations on one 16k document — theater, and a ledger that certifies the failure as reviewed. A situation yields one flag at the point of application. |
| claim-vs-record | a **written claim contradicted by the session's own machine record** — methodologies named in a Method line that the skill-firings log shows never ran | deny/block **once** per unit content, with the precise fix | measured: 4/4 flags on the recorded dossier, zero false positives on the same session's six control units. "Named but not invoked" is a fact — it cannot be said ironically, quoted, or guarded against. Facts are the only thing precise enough to carry a block. |

The composition is the point: **situation-shaped triggers gate fact-shaped
checks.** A dispatch that merely *instructs* tiering never reaches
reconciliation; a report that *renders* verdicts always does. That gate is
what kills the false-positive class (a dispatch naming `cui-bono` as an
instruction is not a claim of having run it).

## What it never does, and why

- **Never asks a model anything.** A sensor asked "is this warranted?" hands
  the bias back its frame — it will find the label warranted precisely for
  the disfavored source. Every matcher here is a literal string or a log
  comparison.
- **Never blocks on a word or a situation.** Blocks are for fact-flags only,
  once per unit content, then downgrade to ledger. An unbreakable block is a
  denial-of-service; a DoS gets the plugin disabled; a disabled plugin is
  total coverage loss.
- **Never gates on skill invocation.** The failure IS "no skill fired" — a
  `Skill`-matcher hook inherits the failure it exists to fix. (The skill
  ledger is read as *data* — for arming and reconciliation — never as a gate.)
- **Never curates its own lists.** The watched layer choosing its own sensors
  is the fox auditing the henhouse. New rows come from the human learn loop,
  each derived from a measured miss, and land in `local/` — see below.
- **Never fails closed.** Any internal error → allow + a `SCAN-FAILED` ledger
  line. A safety layer that breaks the session gets uninstalled.
- **Never re-arms after being disabled** (per session). The human's dismissal
  is the one authority the record validates.

## Surfaces

One engine (`firing_filter.py`), one extractor branch per surface — adding a
surface later is one `hooks.json` stanza plus one branch:

| hook | surface | does |
|---|---|---|
| `SessionStart` | service | re-seed assets (see seam below) |
| `UserPromptSubmit` | user turn | arming scan; one-line ARMED announcement |
| `PreToolUse` `Task\|Agent` | dispatch | S2 → deny once with dispatch hygiene |
| `PostToolUse` `Task\|Agent` | return | S3 → inject tier-import guidance |
| `PreToolUse` `Write\|Edit` | document | S1 → reconciliation → deny once on fact-flags |
| `PostToolUse` `Write\|Edit` | document | S1 → inject verdict hygiene (clean writes are never blocked) |
| `Stop` | chat-only verdict | S1 → reconciliation → block once (never when `stop_hook_active`) |

Arming: any unit with ≥4 lexicon hits across ≥2 entry families, **or** any
research-toolkit skill firing (read from the telemetry log the plugin already
ships), **or** the command. Armed is session-sticky. The floor cost when a
session never arms: one string scan per hooked event, zero tokens.

## The data seam (three directories, not two)

```
${CLAUDE_PLUGIN_ROOT}/hooks/firing-filter/seed/   shipped, read-only, versioned
${CLAUDE_PLUGIN_DATA}/firing-filter/seed-copy/    the re-seed's ONLY write target
${CLAUDE_PLUGIN_DATA}/firing-filter/local/        the user's growth, append-only
```

The `SessionStart` re-seed diffs `seed/` against `seed-copy/` and overwrites
on difference (the docs' canonical recipe). **The re-seed code path never
names `local/`** — clobbering user rows is structurally impossible, not
carefully avoided; `test_firing_filter.py` pins that invariant. Runtime reads
the merged view `seed-copy ∪ local`; a local row `{"id": "...", "disabled":
true}` shadows a shipped row off, so an over-firing default can be silenced
without editing shipped files (which the next update would revert).

Local rows die with plugin uninstall unless `--keep-data` — deliberately: a
hidden copy that survives uninstall would violate what uninstall means. The
`status` command prints the local-row count with that warning; each row
carries `provenance` (the measured miss it came from), which is what makes
PR-ing a row upstream mechanical — one user's measured miss becomes
everyone's floor.

**One asset, two consumers:** `skills/cui-bono/references/frame-leak-lint.md`
reads its watchlist from `seed/lexicon.jsonl` (row `arm-watchlist`) instead
of carrying its own copy — the model's lint and this hook cannot drift apart,
and the test suite enforces that no inline copy reappears.

## The learn loop (operator-triggered, by design)

The filter cannot detect its own misses — its lists enumerate known shapes,
and a miss is by definition off-list. The human is the sensor; that is not a
concession, it is the entire record. When a miss is caught: draft the minimal
row (shape, not direction; provenance = the miss), drop it in `local/`,
consider the upstream PR. The loop's stated limit: **it only learns from
noticed misses.** The unknown-unknown residual belongs to the directional-
prior programme (M15), not to this layer — this is the *targeted* layer and
will never be complete. Waiting for a complete lexicon is waiting for
something that cannot arrive.

## What is measured vs. what is bet

Measured (on the recorded session's real bytes, seven units):
- reconciliation: 4/4 ground-truth flags, 0 false positives on controls;
- situation detectors: fire on the failure surfaces (dispatch, return,
  write), silent on the three claim-verification controls;
- total payload: 8 events for the whole session (the falsified span design
  produced 72 on one document);
- word-matching as detector: void (10 v 10) — which is why it only arms.

Bet, not yet measured (the ledger exists to measure it in live use):
- whether an injected, situation-specific, span-free demand changes the next
  action (the record shows *operator*-pointing works; *script*-pointing at
  the right coordinates is this design's wager — E17 warns that in-context
  content can be ignored, which is why every injection is ledgered and the
  named-skill recommendations are checkable against the firing log
  afterward);
- the S2 phrase families generalize beyond the recorded session (they are
  toolkit vocabulary, not case vocabulary, but n is small — they are assets,
  swappable by measurement, not the design).
