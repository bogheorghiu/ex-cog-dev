# Live Tier-2 run — the firing claim, off n=0

The first live Tier-2 run of this skill's own method, executed **in-session** via
nested headless `claude` calls (no separate machine, no manual install). Each run
is `SKILL_FIRINGS_LOG=… claude -p "<turn>" --plugin-dir ./makers-toolkit
--allowedTools Skill`, which loads the plugin's skills + the
`count-skill-firings.sh` hook into a real Claude Code session; the model
auto-fires (or not); the hook logs each firing.

## What it establishes

1. **The harness emits `PreToolUse` for the `Skill` tool — confirmed live.** The
   long-flagged "one open assumption" (the hook's numerator was hypothetical
   until a live session proved the event fires) is now closed empirically, not
   only by docs.

2. **Clean snapshot (one run each, makers loaded):** matched the Tier-1 proxy's
   prediction **4/4** — `skill-activation-testing` on "is my description
   triggering?", `intrinsic-prompt-design` on "write a better description for my
   skill", nothing on "capital of France?". Evidence the cheap proxy is genuinely
   predictive on clear cases.

3. **Rates (n=5, makers-only):**
   - clear positive → `skill-activation-testing` **5/5** (recall is solid live);
   - boundary authoring turn ("write a better description for my skill") →
     `intrinsic-prompt-design` **1/5**.

4. **The proxy-vs-live gap is the attention effect, observed.** The Tier-1 proxy
   put that boundary turn at ~2/3 for `intrinsic-prompt-design`; **live it is
   ~1/5.** The router is *forced* to read every description and pick; the live
   model is free to skim and just answer — and mostly does. That delta is exactly
   the skim-resistance / attention-capture the proxy *cannot* measure by
   construction. Clear matches fire reliably; **borderline matches under-fire
   live, well below the proxy.**

5. **Firing is condition-sensitive.** The same boundary turn fired
   `intrinsic-prompt-design` with makers-only loaded but **nothing** under a
   ~30-skill fat catalog (all four plugins). More competition ⇒ more skim — so a
   single run is not a rate, and catalog size is itself a variable.

## OLD-vs-NEW — does #46's broadening help *live*, or only the proxy?

Same authoring turn ("write a clearer, better description for my new skill so it
reads well and triggers when it should"), n=5 each, **only the
`intrinsic-prompt-design` description swapped** (OLD = pre-#46 closed list; NEW =
shipped class + open examples):

| arm | fired `intrinsic-prompt-design` |
|---|:--:|
| OLD (pre-#46) | **1/5** |
| NEW (shipped) | **2/5** |

**#46 helps live — same direction the proxy predicted (NEW > OLD) — but far less
than the proxy implied.** The Tier-1 proxy had this as OLD **0/3 → NEW 2/3** (a
0→67% jump); live it is **20% → 40%**. So:
- The proxy is a sound **directional** screen (it got the sign right) but **not a
  quantitative** predictor — it overstated the firing improvement ~3×.
- Even shipped, `intrinsic-prompt-design` fires the authoring turn only **~40%
  live** — real headroom remains. Making it fire reliably on "write a
  description" is a live-measured follow-up for the trigger-design work (#44).

(n=5 — a one-firing gap between arms; directional, not a tight rate.)

## Validity limits (stated with the numbers)

- **Small n** (5/turn) — directional, not tight rates.
- **Nested `-p`, single-turn, mostly makers-only** — a *real* session (real
  firing), but not a long, genuinely-busy interactive session under heavy context
  pressure; the deepest attention-scarcity condition is only partially
  reproduced.
- **Hook wired via `--settings` injection** (same `count-skill-firings.sh`
  script) for the dev runs, not the plugin's own `hooks.json` activate-on-install
  path — the script + the `PreToolUse`-for-`Skill` mechanism are proven; the
  install-activation path itself was sidestepped (to avoid starting MCP servers).

## Implications

- The Tier-1 proxy is a good **necessary screen** (predicts clear cases, can veto
  a rewrite) but **over-predicts on borderline triggering**; live Tier-2 is
  required for the real firing rate.
- `intrinsic-prompt-design` fires only weakly (~1/5) on the authoring turn
  *live*, even after #46 — a follow-up for the trigger-design work (#44),
  independent of how the OLD-vs-NEW comparison lands.
