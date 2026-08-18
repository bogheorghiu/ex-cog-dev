# Brief: intrinsic-prompt-design review pass

**Branch-scoped working file. Delete before merge.** This is process, not repo
content.

## What this branch is for

`makers-toolkit/skills/intrinsic-prompt-design` received an external critique in
August 2026 — three models from three different vendors, none of them the model
that wrote the skill, each given the full skill text and a neutral brief with no
knowledge of each other's findings. Roughly 145 numbered findings.

This branch is where those findings get turned into drafted edits. Drafts, not
proposals: write the change into the files.

The critique itself is held privately and is not in this repo — it carries
material that should not ship in a public repository. It **is** available to read
locally, outside this repository; your session brief points you at it, and it
opens with its own index and reading map.

Everything strictly needed to act is restated below in this repo's own terms, so
this brief stands alone if you cannot reach the source. What the source adds is
the full argument behind each finding, and the record of which ones were already
argued down. Read it before drafting anything in section A.

**Do not copy the source material into this repo**, in files or in commit
messages. If you want to cite a finding, restate it.

## Verified before you start

All five skill files are byte-for-byte identical to the text the critics read
(`SKILL.md` 14,660B; `agent-prompts-starter.md` 5,529B; `firing-experiment.md`
7,504B; `trigger-rewrite-experiment.md` 6,054B; `worked-example-system-pilot.md`
9,287B). Every finding is live against current `main`. If you edit before
drafting, re-check.

## Two scope decisions — already made by the operator

**1. This is a posture skill, not a complete prompt-design method.**

Its one job is the relationship between a prompt and the model reading it:
reasons over commands, trust over control, peer-briefing over tool-direction.

About fifteen findings say the skill lacks output contracts, input contracts,
instruction hierarchy, prompt security, evaluation methodology, priority and
conflict rules, tool-use design, multi-agent design, and lifecycle management.
**Decline that class.** Adopting it roughly triples the skill and turns it into a
general prompt-design manual — a different artifact with a different job.

Do add **one line** stating what the skill deliberately is not, and pointing to
where the mechanics layer belongs. That line is not a concession; it closes two
separate findings about the skill inducing meta-commentary instead of work.

**2. The description gets a candidate arm, not a replacement.**

About twelve findings target the frontmatter — that it opens with a rhetorical
interrupt before naming the trigger class, that it mixes routing metadata with
doctrine, that it asserts an attention effect its own experiment records as
untested.

The shipped description stays. Draft an alternative into the repo as a
documented **arm B**, with its reasoning, for `skill-activation-testing` to
decide between.

Why: the current description is the subject of the only live experiment in this
repo — Tier-1 routing measured (under-fire cases 0/3 to 2/3, no precision loss),
Tier-2 attention effect explicitly at n=0, live test planned. Replacing it on the
strength of an untested objection trades measured evidence for opinion, and
resets the activation-testing baseline from a regression check to a fresh one.

## What to draft — in priority order

### A. The core correction (highest value, smallest diff)

**A1. Scope the reasons principle.** "Every directive in a prompt can carry the
failure mode it prevents" does not survive its universal quantifier. Attaching a
rationale to mechanical directives — formats, schemas, output shapes — is bloat
that buries the instructions that matter. All three critics converged here
independently.

Draft: reasons where judgment lives; terse imperatives elsewhere. Keep the cost
structure example, which every critic praised.

**A2. Hard constraints stay hard.** "A rule without its reason produces
compliance or defiance. Both are worse than understanding" reads compliance as
inferior. Many real failures *are* compliance failures: wrong format, missed
section, skipped citation, crossed boundary.

Draft: mark where exact compliance is required and where judgment is delegated.
This is the same guardrail/scaffolding partition the skill already gestures at —
make it operative.

**A3. State that a guardrail's reason is explanation, not justification.** The
operator's formulation, and it supersedes what any critic proposed: attach the
reason, and make clear that **falsifying the reason does not invalidate the
guardrail** — at most it makes the conflict worth raising. Because the model's
falsification may itself be wrong, and because the reason may be incompletely
stated while the guardrail is sound.

**A4. Say that a guardrail which can be deterministic should not be prose at
all.** The skill already carries the deterministic/probabilistic separation and
every critic praised it — but it stops short of the consequence. If a rule must
hold every time and can be enforced by a schema, validator, hook, test, or CI
check, that is where it belongs; prose is the fallback for what cannot be
mechanised. This is upstream of A1–A3: it decides whether a rule should be in the
skill's scope in the first place.

**A5. Scope the reciprocal ask-why move.** As written it applies to any imperative
from any source, which makes an agent pedantic on routine requests and invites it
to interrogate higher-priority instructions.

Draft: ask when the instruction is ambiguous, consequential, conflicting, or
unsafe. Otherwise infer and proceed.

**A6. Qualify the trust-gap claim.** "Stated trust constructs capability"
conflates within-run adaptation with durable learning, and reads as permission to
substitute confidence language for examples and evaluation.

The sharpest diagnosis came from the interaction-nuance critic, and it is worth
absorbing rather than paraphrasing: stating trust in capabilities the model may
not have activates a wish to *be* the trusted peer, so the model **performs**
capability. Naming that mechanism is a stronger fix than softening the wording.

### B. Self-consistency (cheap, and the skill is about exactly this)

**B1. The skill criticises hard commands while issuing them.** It objects to
"MANDATORY", "HALT", "forbidden", then instructs the reader to run a specific
tool and to keep a section intact. Either justify these as constraints carrying
their reason, or rewrite them in the skill's own register.

**B2. The licence language is self-contradictory.** "MIT-licensed" plus "Modify
freely. Keep this section intact" reads as an extra condition MIT does not
impose. Attribution belongs in LICENSE; the skill text can *request* preservation.

**B3. Name the skill's own strongest counter-evidence.** Its best measured result
— the trigger-rewrite win — came from broadening a closed list into a class plus
open examples. That is a **specification** improvement in the operational
register, not a win for reasons, trust, or relationship framing. The doctrine
says commands break at the first edge case; the skill's own data says a precise
spec fires correctly.

A skill about honest reasoning should carry the finding that most complicates it.
This is also the strongest internal support for A1.

### C. Experimental hygiene (small edits in `references/`)

**C1. `firing-experiment.md` — judge lineage belongs in the validity section.**
Method already states "3 independent blind routers per arm per round (same model,
sonnet)". The limitation section flags the Tier-1 proxy problem and says nothing
about lineage. Three samples of one model is one source type, not three, and a
reader who skips Method takes "3 independent judges" at face value.

Move it into the limits, and say what a genuinely independent replication would
need: routers from different model families.

**C2. Report the trigger-rewrite result proportionally.** "The under-fire is
fixed" describes a 0/3 to 2/3 improvement. Improved recall, not fixed.

**C3. Bound what firing evidence can say.** Router attention over a catalogue of
descriptions and model attention inside an invoked skill body are different
regimes. The experiments measure only the first.

### D. Portability — small edits now, larger goal later

The operator's stated direction: these skills should eventually work outside
Claude as well as inside it, even though they are Claude-optimised today.

Do the cheap half now. Where the skill names a harness-bound thing — a specific
slash command, `CLAUDE.md`, hooks, `PreToolUse`, the `Skill` tool, firing
counters, the team-agent primitive — state the general capability and keep the
Claude form as the example: *"run an independent deconstruction pass if one is
available (in Claude Code: `/research-toolkit:text-deconstruction`)"*.

Do not attempt full harness-neutrality in this pass. Abstract-plus-example keeps
it useful here and portable later.

## Contested — do not adopt as written

One finding argues that reasons invite **rationale-lawyering**: the model debates
the reason rather than applying the constraint. Its proposed fix is an
anti-lawyering clause — state the reason in under twenty words, do not debate or
extend it, apply the constraint, and note any deviation in one line.

The failure mode is real. The fix has three problems:

1. **It bundles three behaviours that look identical from outside.** *Deflection*
   (using the reason as a loophole) is the failure. *Calibration* (recognising the
   reason does not apply here) is the mechanism the skill exists to create.
   *Correction* (noticing the reason is factually wrong) is behaviour another
   critic explicitly asks for, since a sincerely-stated but wrong rationale
   teaches the model to generalise incorrectly.
2. **It requires the operation it forbids.** "If the situation genuinely
   conflicts, choose the situation" cannot be evaluated without reasoning about
   the reason.
3. **A4 dissolves most of it.** If the guardrails that matter are deterministic
   checks, the residue where a prose guardrail carries a loopholeable reason is
   small — and A3 already handles that residue.

What survives independently: **a reason longer than one sentence is operational
register hiding in the wrong place — split it.** That is a good structural test
and worth drafting.

## Also unresolved, lower priority

- **Reasons on guardrails have an upside no critic priced**: they help capable
  models understand and improve the architecture. The counter-case is an
  adversarial reader. Probably argues for a split — reasons in project-internal
  artifacts, bare constraints in anything untrusted agents read — but nobody has
  worked it through.
- **Marking force without reverting to command register.** "Mandatory regardless
  of rationale" is a command, and the skill's thesis is anti-command. Genuine
  contradiction, or the correct exception? The guardrail/scaffolding partition in
  A2 may already be the answer.
- **The ecosystem-internal term for recurring patterns** drew objections from two
  critics as jargon that may cause tonal drift. Operator's call; low priority.

## The failure mode this pass must avoid

A skill about producing better judgment could produce a model that **deliberates
constantly** — which is a degradation that looks like compliance with the skill,
and would pass every review that only reads the text.

If a drafted change makes the skill more likely to induce deliberation on routine
work, it is a regression regardless of how well-argued it is.

## Verification

Four layers, different jobs. None substitutes for another.

0. **Run the skill's own instrument on the skill's own updated text.** The skill
   instructs exactly this for any prompt that will run for many sessions — run
   `/research-toolkit:text-deconstruction` on it, iteratively, stopping when a
   pass surfaces nothing worth changing or when the method can no longer tell a
   structural tension from an artifact of its own procedure.

   A revision of *this* skill that skipped its own prescribed verification would
   be self-undermining in the most literal way available, and the critique
   already found the skill's worked example failing its own doctrine once. Do
   this before handing the draft to a human or to layer 2.

   Note what it can and cannot see: deconstruction finds where a text relies on
   something it never establishes and where its claims and structure pull apart.
   It says nothing about whether the skill *works*. That is why it is layer 0 and
   not the whole plan.

1. **Activation testing** — `makers-toolkit/skills/skill-activation-testing`,
   with `references/router-judge-template.md`. Required if you draft the arm-B
   description. Measures routing only, on its own admission.
2. **An independent read of the draft.** The critique session's own recorded
   lesson: its worked example was caught violating its own doctrine by the
   cheapest model in the stack, on an artifact its author had already reviewed.
   Draft, then hand to a reader that did not write it, briefed to refute.
3. **An ad-hoc functionality check** the operator can run externally: the same
   task across several different models that expose their reasoning, with and
   without the skill, reading the **traces** rather than the outputs. Not a
   controlled experiment — it answers "does this visibly change how a model
   reasons," which is what §"failure mode" above needs and what no in-repo test
   can see.

**A controlled behavioural experiment is deferred, not skipped.** It needs
automation to be worth anything — fixed task set, blind arms, a pre-registered
ship rule written before any results are read — and that costs both wall-clock
and tokens. It belongs in this repo, automated, optionally driving external
models for family diversity. Do not attempt it in the same pass as the drafting,
and do not let layer 3 stand in for it: an ad-hoc read of a few traces can show
that something changed, never that the change was an improvement.

## Repo constraints you will otherwise trip on

- **Version bump is REQUIRED** for any change under a plugin directory. Bump
  `makers-toolkit/.claude-plugin/plugin.json` in the same change. Self-check:
  `python3 .github/scripts/check_version_bump.py origin/main HEAD`.
- **Tracked JSON is ASCII-only.** No em-dashes or curly quotes in manifests, and
  beware `json.dump` re-escaping every non-ASCII character in a file you only
  meant to bump.
- Delete this brief before merge.
