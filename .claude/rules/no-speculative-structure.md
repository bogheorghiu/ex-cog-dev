# No speculative structure — build the least that fully solves the request

(No `paths:` frontmatter on purpose — this governs *any* edit, code or prose, so it
loads every session, like `verify-claims.md`.)

**The failure mode.** Output beyond what was asked: configurability nobody requested,
abstractions for single-use logic, error handling for impossible scenarios, "while
I'm here" features. An LLM session produces this readily because elaboration is cheap
to generate — but the costs land downstream, twice: the reviewer must
reverse-engineer which parts actually answer the request, and the unneeded machinery
then gets maintained forever by people who can't tell it was never needed.

**The test, applied per addition:** does this structure trace to the request — would
the request be *unsolved* without it? If a senior engineer would call it
overcomplicated, simplify before showing it.

**Boundary — scope discipline, not minimalism worship.** When the asked-for change
genuinely needs an abstraction or broader structure, build it — and state the why
(Rule 1). A stated reason is exactly what converts "speculative" into "justified";
a bare "keep it simple" command would wrongly forbid the justified case, which is
why this rule carries its reasons instead.

**Lineage.** The established name is **YAGNI** ("you aren't gonna need it", from
Extreme Programming) — named so the principle is checkable against prior art rather
than reinvented. Immediate source: rule 2 ("Simplicity First") of the
Karpathy-derived viral CLAUDE.md (`multica-ai/andrej-karpathy-skills`), rewritten to
carry its reasons.

**Sibling:** `no-drive-by-edits.md` — the same per-line traceability test applied to
*modifications* instead of *additions*. They fail independently (a session can
over-build without drive-by editing), hence two rules per `rule-design.md`'s
one-job-per-rule scoping.

**Twin:** a logic-identical copy lives in `bogheorghiu/wikipediai`
`.claude/rules/` — keep the two in step until the planned shared rules-template repo
becomes the single source.
