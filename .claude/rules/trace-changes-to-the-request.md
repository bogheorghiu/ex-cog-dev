# Trace changes to the request — simplicity and surgical scope

(No `paths:` frontmatter on purpose — this governs *any* edit, code or prose, so it
loads every session, like `verify-claims.md`.)

The two failure modes this rule prevents are the two an LLM session produces most
readily when it edits anything:

1. **Speculative structure.** Output beyond what was asked: configurability nobody
   requested, abstractions for single-use logic, error handling for impossible
   scenarios, "while I'm here" features. The cost compounds in review — the reader
   must reverse-engineer which parts answer the request — and then compounds again
   in maintenance: machinery nobody needed gets maintained forever by people who
   can't tell it was never needed.
2. **Drive-by edits.** "Improving" adjacent code, comments, or formatting while
   passing through. The cost: the diff stops tracing to intent, review burden grows,
   regressions ride in on lines nobody asked to risk, and `git blame` attributes
   unrelated churn to your change.

**The one test that catches both: every changed line should trace directly to the
request — and the request, solved with the least structure that fully solves it.**

Boundaries, so the rule doesn't over-fire:

- **Clean up your own mess — only yours.** Remove imports, variables, and functions
  *your* change orphaned; leave pre-existing dead code in place and *mention* it.
- **Noticing is good; silent fixing is not.** Adjacent bugs, dead code, oddities:
  surface them (a sentence in the report, or an issue) instead of folding them into
  the diff. The reader of the diff is the constituency this rule protects.
- **Scope discipline, not minimalism worship.** When the asked-for change genuinely
  needs an abstraction or a broader touch, build it — and state the why (Rule 1),
  which is exactly what converts "speculative" into "justified."
- **Match existing style even where you'd choose differently.** Consistency is
  information for the next reader; a style island marks your diff forever.

**Provenance.** Distilled from rules 2–3 ("Simplicity First", "Surgical Changes") of
the Karpathy-derived viral CLAUDE.md (`multica-ai/andrej-karpathy-skills`), rewritten
to carry its reasons — a bare command breaks at the first edge case (e.g. "don't
refactor" alone would forbid a *justified* refactor); a reason adapts. That file's
rules 1 and 4 are deliberately not duplicated here: Rule 1 (state the why) plus
`verify-claims.md` already cover "think before coding," and the repos' testing
discipline covers "goal-driven execution."

**Twin.** A logic-identical copy lives in `bogheorghiu/wikipediai`
`.claude/rules/trace-changes-to-the-request.md` (cross-noted there) — keep the two in
step until the planned shared rules-template repo becomes the single source.
