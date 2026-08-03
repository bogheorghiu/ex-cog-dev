# Reserve prose for what code cannot say

(No `paths:` frontmatter on purpose — this governs any change that pairs an executable
artifact with prose about it: comments, READMEs, workflow files, test headers, skill
bodies. Like `no-drive-by-edits.md`, that is any edit, so it loads every session.)

**Naming.** An earlier working name was "the code is the documentation — but for prose";
renamed because a slogan names neither the action nor the boundary, and the imperative
names both halves: prose is *reserved for* — kept, obligatory — what code cannot carry,
and barred from restating what it can.

**The failure mode.** Prose that restates what an executable artifact already states — a
comment narrating a script's steps, a sentence duplicating a workflow's conditions, a
header enumerating which tests touch disk. Each copy is true the day it is written, and
nothing fires when the artifact changes: no compiler, no test, no diff-reviewer reads the
pair together. So the copy drifts silently and keeps *reading* as authoritative while
wrong. Structure cannot rot this way, because structure *is* the thing.

Measured, not hypothetical: PR #195 ran ~22 review rounds, and of its 47 posted findings
**~27 were prose restating what the code already said** — four separate copies of
"findings.json is the only writable path"; "a second public channel" while the file's own
header counted three; a test header enumerating disk-touching tests that was wrong twice
within one commit. Every one was true when written and falsified by a later commit.

## The discipline, in order

1. **First, try to make it discernible from the code itself** — naming, structure, a
   well-named guard, a test whose name states the invariant. A comment is what you write
   after trying this and failing, not the first move. In PR #195 a comment described a
   "collapse-then-redact" flow a later commit had removed, while the variable beside it
   was named `redacted_files` — which said the same thing correctly and could not go
   stale.

2. **Prefer changing the code so the sentence is unnecessary.** A comment justified
   `if-no-files-found: ignore` with a case the step's own `if:` condition already
   excluded — a wrong *reason*, the corpus's second class (~7 of 47). The fix was not a
   better sentence but a tighter condition that left nothing to explain. A stated reason
   is prose too and rots the same way; one that survives this step still gets the
   `verify-claims.md` re-read, because nothing else compiles it.

3. **When it genuinely cannot live in code, write it down — never abstain.** Why X was
   chosen over Y, a historical incident, a cost trade-off, a decision that binds a future
   reader: code by design cannot carry these, and leaving them unwritten loses them. This
   rule is not "fewer comments"; a session that reads it that way has made the rule worse
   than its absence.

4. **The check is independent and floor-model.** Hand the code, without the comment, to a
   reader who did not write it, at the floor model for the complexity — Sonnet where the
   judgement permits, escalating only where it genuinely needs more. Can that reader say
   what the comment says? Yes → duplication; cut it or push it into the code. No → the
   comment has earned its place. This is the rule's own falsification test: "the reason
   is discernible from the code" is a checkable claim, not a feeling.

5. **Sometimes the right home is a separate document, not a comment** — one file, or one
   folder, holding the few genuinely important things about what the code does that the
   code by design cannot hold (design rationale, the incident record, the trade-off
   ledger). Never bloat such a doc: every addition faces the same test as a comment. It
   always depends; when in doubt, delegate the call to a fresh reader (a Fable agent)
   rather than defaulting to accretion.

## Skills and agents are code here

A skill or agent definition is technically a document, but it is the non-deterministic
equivalent of code — the executable the harness runs. Prose elsewhere that restates what
a skill already says is the same duplication and rots the same way. The one copy itself
is governed by machine-scope `treat-prompts-like-code`; this rule forbids the second copy.

## Seam with Rule 1 — state the why

No contradiction: Rule 1 demands the why *exist*; this rule governs *where it lives*.
The preference order is: in the code (a guard named for its invariant IS a stated why),
then a comment, then a separate doc — never nowhere. A why that could not be pushed into
code is exactly what Rule 1 obliges you to write.

## What this rule does not prevent

Named so the rule is not oversold. Of PR #195's 47 findings, ~9 were real code bugs and
the remainder process findings — no prose rule touches those. This rule reaches the ~27
restatements directly and, through step 2, part of the ~7 wrong-reasons.

**Lineage.** The classic maxim "comments explain why, not what" (self-documenting code;
DRY applied across the code–prose boundary), extended one step: even the why is first
*attempted* in code, and an independent check — not the author's confidence — decides
when it can't be.

**Siblings.** `no-speculative-structure.md` / `no-drive-by-edits.md` (per-line
traceability of additions/modifications; this rule governs what surviving prose may
*say*); `verify-claims.md` (a stated reason is a claim — draft until re-read); machine-
scope `filesystem-is-the-catalog` and CLAUDE.md's "What's here" rationale (the same
drift logic applied to *inventories* — lists of what exists; this rule covers *logic and
reasons* — what code does and why).
