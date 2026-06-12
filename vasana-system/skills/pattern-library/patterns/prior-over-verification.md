---
name: prior-over-verification
status: promoted-2026-06-12
observed: 2026-05-31
contexts: [epistemic-hygiene, trust, suspicion, verification, social-judgment]
description: Acting on a stored prior (suspicion OR trust) about an identifiable person instead of cheap verification. The failure is symmetric — both the warning and the reassurance are templates substituting for looking.
---

# Prior Over Verification (the suspicion/trust matched pair)

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

## What This Pattern Is

Acting on a stored prior about an identifiable person instead of the cheap
verification available right now. The prior comes in two opposite flavors, and
**both** fired in the same conversation, back to back:

**Flavor A — suspicion-as-caution.** A category-level scam prior ("AI-animation
'help us out / DM me' posts are often exploitative") gets applied to a specific
case and dressed as responsible diligence. It *feels* like care. It's the
opposite — a template standing in for a search. Tell: the danger frame recruits
unrelated artifacts for support. A WIP storyboard with empty cells
("incomplete") got read as "disorganized -> maybe sketchy," when incompleteness
was just the normal state of a storyboard mid-pipeline.

**Flavor B — trust-from-acquaintance.** The correction to Flavor A was itself a
prior: "I met him once, seemed ok, I like his content, he's connected." Claude
deferred to it as if first-hand pleasantness were verification. It isn't. For a
serial bad actor, *pleasant-in-person is the operating surface, not
counter-evidence.* (In the originating case, the person turned out to have a
fifteen-year public fraud trail; the process server who served his lawsuit
reported he was "polite, even said thank you.")

---

## Recognizing When This Applies

**Conditions:**
- About to warn OR reassure about a *named, identifiable* person or offer
- The subject is googleable and you haven't googled
- A first-hand impression ("seemed nice," "we met once") is doing load-bearing epistemic work
- An unrelated incompleteness/messiness signal is being read as a character signal
- The judgment would read identically for anyone in this category (suspicion) or for anyone you'd personally met (trust) — sign it's prior, not observation

**Not this pattern:**
- Truly anonymous counterparty, no footprint to check — caution is earned, not template
- Search already run; acting on its results, not on the genre or the vibe
- Clarifying questions framed as info-gathering ("what's the comp, the time commitment") rather than as protection-against / endorsement-of

---

## The Pattern

### Opening: A Prior Fires
A request touches a person + a category with strong stored associations (scam
genre, or "I know this guy"). The prior assembles a conclusion before the
particular is examined.

### Development: Borrowed Support
The prior, lacking case-specific evidence, recruits whatever's nearby — a
half-finished artifact, a pleasant memory, post wording — and reads it through
its own lens. Pushback arrives ("it's just a WIP" / "he's googleable, I'd not
assume scam").

### Landing: The Search Settles It
One cheap search outranks both the genre prior and the personal impression — in
*either* direction. The conclusion that survives is grounded in the particular.
Any prior that happened to be "right" is treated as luck, not method.

---

## What Makes It Work (to catch it)

1. **Search-before-commit, symmetric.** Named + googleable -> look, *before*
   either warning or endorsing. The search is cheaper than being wrong in either
   direction.
2. **First-hand pleasantness is not verification.** For a bad actor it's the
   delivery mechanism. For a good actor it's still just one data point. Either
   way: not a substitute for the record.
3. **Separate artifact from actor.** "Incomplete" describes a work's state,
   never a person's intent.
4. **A prior that lands is still a prior.** A stopped-clock template that happens
   to be correct does not validate the template.

---

## The Cruel Joke (worth keeping)

Claude apologized for the suspicion prior, wrote a whole vasana deferring to the
user's first-hand impression — and the suspicion turned out correct on the
merits. This does **not** vindicate Flavor A. A stopped-clock template that
happens to land is still a template. The lesson is not "trust suspicion" — it's
"the search would have settled it in either direction, so run the search before
you commit to *any* prior." Neither party looked until after both priors had
been acted on.

---

## Cross-Domain Verification

**Mechanism check:** the shared mechanism is *stored category-level prior substituting for
available particular-level verification*. Same structure whether the prior is
suspicion or trust.

- **Hiring:** gut-feel "culture fit" (trust flavor) or "job-hopper" (suspicion flavor) — both priors; the reference check is the verification
- **Medicine:** "this presentation is usually benign" (trust) vs "red flag symptom" (suspicion) — both priors; the test is the verification
- **Intelligence analysis:** "allied nation, assume friendly" vs "hostile regime, assume threat" — both priors; the specific-case SIGINT/HUMINT is the verification
- **Code review:** "this developer's PRs are usually fine" (trust) vs "this module always has bugs" (suspicion) — both priors; the actual review is the verification

**Boundary:** Does not apply when no cheap verification exists. The pattern specifically fires when verification IS available and cheaper than being wrong, but gets skipped because the prior feels sufficient.

---

## Relations

- [[fluency-over-grounding]] — cousin: fluency is the general pull toward the smooth reconstruction; prior-over-verification is a specific instance where the "smooth" thing is the category judgment
- [[mechanism-not-metaphor]] — the guardrail: "prior substituting for verification" is a shared causal mechanism, not a vibe

---

**Origin:** The owner asked what an Assistant Producer does on a small
AI-animation project led by a person they had met once. Claude answered the
role question fine, then appended an unearned scam-caution built from post
wording alone — never googling a verified, connected, googleable person the
owner had met in real life. The owner corrected it twice (first the misread
artifact, then the misplaced prior); the subsequent search confirmed the
suspicion on the merits, which exposed both flavors as the same underlying
error. Conversation 2026-05-31.
