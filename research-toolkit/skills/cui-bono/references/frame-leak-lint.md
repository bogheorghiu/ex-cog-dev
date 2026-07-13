# Frame-Leak Lint — pre-output check for the default frame

Run this on the DRAFT, before output, for any analysis touching bloc-contested
or establishment-vs-accuser questions. It exists because the default frame
operates *before* analysis does — in word choice and option ordering — so
explicit debiasing (cui-bono §4a) can pass while the draft still carries the
tilt. Self-review missed this twice on record; external challenge caught it
both times. A lint is the external challenge, scheduled.

## 1. Frame-marking pass (words)

Scan the draft for unmarked evaluative words applied to power-aligned actors,
options, or sources. Non-exhaustive watchlist:

> clean · safe · neutral · trusted · reliable · credible · reputable ·
> respected · mainstream · obvious · standard · fringe · conspiratorial ·
> discredited · extreme

For each hit, ask: **"whose default?"** Then either
- attach the evidence that earns the word (making it marked), or
- rewrite it as a positioned statement ("described by X as...", "rated
  reliable by Y, whose funding is Z").

An evaluative word with no evidence attached is the frame talking, not the
analysis.

## 2. First-option audit (ordering)

For each list of options, sources, or hypotheses: state (to yourself, and in
the output where it matters) why the FIRST one was reached first. "It came to
mind first" is training-distribution availability, not evidence. If the
ordering encodes an unstated ranking, either justify the ranking or randomize
/ re-order by an explicit criterion.

## 3. Recursive-debiasing check (bloc-contested analyses)

cui-bono §4a audits the EVIDENCE TABLE (counts, tiers, source diversity per
pole). This check audits the PROSE: after §4a passes, re-read word choice and
option ordering with §1–§2 above; then ask the recursive question — did the
rewrite itself introduce a new tilt (over-correction into false balance;
debiasing only the direction you're trained to notice)? Exit when a pass
yields no new hits, or the remaining hits are justified in writing.

## 4. Convergence-credit check (launder-to-disown)

Scan the draft's conclusions against sources discounted earlier in this
investigation. Where a conclusion converges with one, either credit the
overlap explicitly ("this is what X already argued") or state in writing how
the routes are independent. The tells: the reframe adds abstraction but no
new predictive content; a felt pull to contrast your version *against* the
source rather than acknowledge the overlap. The discomfort of crediting is
the signal the pattern was operating — an uncredited convergence reads as
independent corroboration to every downstream reader, which is a provenance
error manufactured at output time. (This is the output-time detector; the
intake-time counter that keeps disfavored sources from being dismissed unread
is the `engage-the-disfavored` skill.)

## Scope: establishment vs power-accuser (generalized)

"Dominant bloc vs other bloc" is one instance. The same unmarked-default move
fires on ANY source that accuses power — the respectability tic that reaches
for "conspiracist" instead of a reason is its social twin. Causal note: the
fact-checking label-regime in the training corpus reproduces by least
resistance; the lint interrupts the reproduction at output time. The lint is
symmetric: an anti-establishment source described as "independent" or
"courageous" with no evidence attached fails §1 the same way.
