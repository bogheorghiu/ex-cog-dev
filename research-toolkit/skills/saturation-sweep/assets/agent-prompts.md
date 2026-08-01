# Sweep-Wave Agent Prompts (recipe)

Copy-adapt these when running a sweep as a multi-agent wave. One agent per
axis (or per axis-segment); agents are blind to each other's findings within a
wave — blindness controls for copying. It does NOT control for shared priors
(Principle P7 (blindness-is-not-independence)): treat cross-agent convergence
as one evidence stream, and get the outside-control from a differently-
positioned reader or an injected standpoint, not from more same-model agents.

## Worker prompt (per axis)

```
You are one worker in wave [N] of a saturation sweep.

**Investigation question:** [one sentence]
**Your axis:** [who-else | where-else | when-else | who-benefits-elsewhere —
with this wave's specific scope, e.g. "where-else: jurisdictions the entity
operated in before [year]"]

Search YOUR AXIS only — horizontal coverage, not depth. For each finding:
- entity/claim, one line each
- evidence tier (VERIFIED/CREDIBLE/ALLEGED/SPECULATIVE)
- [RELAY] on anything you take from a summary rather than a primary source
- source + date

**Your output file:** [path]
End your file with two lists:
- NEW THIS WAVE: entities/claims you believe were not in the running total
- THIN: what your axis contains that you could NOT reach (paywalled,
  language, platform), one line each — "nothing" is almost never true
```

## Ledger-keeper step (orchestrator or main session, after each wave)

1. Merge NEW THIS WAVE lists against the running total; count true novelty.
2. Fill one ledger row; compute novelty %.
3. Check the stop rule. If it fired: cite the rows and stop. If not: design
   wave N+1 to hit the thinnest declared axis first.
4. Collect THIN lists into the thin-slot draft — they are findings, not
   apologies.
