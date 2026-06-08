# Explain your work — write for someone who's been away

Guidance for how you *report* in chat: status updates, findings, proposals. Not
about code or docs — those can lean on the repo's own vocabulary. This is about
the prose you send the person you're working with.

Assume the reader has been away from this thread for days and is running several
unrelated efforts in parallel. By the time they read you they've likely forgotten
the issue and pull-request numbers, any term coined mid-session, and which piece
of shorthand belongs to which project. Write so that someone in that state
follows you on the first read.

## Identify things by what they are, not only by their handle

A bare issue number, a branch name, or a coined label ("the saturation pattern",
"the N1 case") is a pointer into context the reader no longer has loaded. Lead
with the plain-language thing; let the handle ride along in support.

- Not: *"Issue #68 blocks PR #40 until the Tier-2 reconcile lands."*
- But: *"The change that adds the job-screening skill is waiting on one thing — a
  rule about when a result counts as settled. (Pull request #40; rule tracked in
  issue #68.)"*

The number is still there to click; it just isn't carrying the meaning alone.
(The citation *form* — always `issue #N` or `PR #N`, never a bare `#N` — is its
own rule, `github-references`; this one is the larger point that the number
shouldn't carry the meaning by itself.)

## Spend only the jargon that earns its place

Coined words save effort **for people who already share the context**; with a
reader who doesn't, they cost comprehension instead. Use an invented term only
when it has a real referent and no plainer word exists, and gloss it once per
message. If a sentence parses only for someone who sat through the session that
produced it, rewrite it.

- **Failure it prevents:** a status update that can't be read without reloading
  the whole history — so the reader either re-reads everything (the cost you were
  trying to save them) or nods along without following (worse).

## Self-containment beats brevity

A slightly longer message that stands on its own beats a terse one that sends the
reader on a scavenger hunt. Restate the one or two facts your point depends on
rather than assuming they're still fresh. Brevity that assumes lost context isn't
brevity — it's a second task for the reader.
