# Activation test — dev-job-defense-ties (Tier 2, live)

> A complete, reproducible record of the firing test run on this skill, written
> to be **portable** — it doubles as a worked Tier-2 example for
> `makers-toolkit:skill-activation-testing` (whose `references/` has a Tier-1
> two-round run and a self-application, but no live Tier-2 walkthrough). Method,
> commands, turn design, raw results, analysis, and the validity limits are all
> here so the numbers can't be read without the caveats that bound them.
> **§11 generalizes the design beyond *activation* into *functionality* testing**
> — the transferable input for a future skill-test-design apparatus (issue #52).

## 1. Question under test

A brand-new skill makes an implicit claim: *it fires on the situations it's for,
and stays quiet on adjacent-but-wrong ones.* Until tested that sits at n=0. This
run measures it under **real attention scarcity** — a full session with four
plugins' worth of competing skills loaded — not a proxy.

It is **single-arm**: there is no OLD description to A/B against (the skill is
new), so the question is *recall* (does it fire on should-fire turns) and
*precision* (does it stay silent on traps), not "did the rewrite win." That makes
it a `skill-activation-testing` **Tier 2** run without the A/B arm-swap.

## 2. Why Tier 2 (and what Tier 1 would not have shown)

Tier 1 (blind LLM router over a catalog) cannot see attention-capture by
construction — the router reads every description, so it can't tell you whether
the skill would have *won* attention it might otherwise lose. The thing we most
wanted to know about a new auto-firing skill — *does it actually fire for a user
mid-task* — is exactly what only Tier 2 sees. The cost (a live install, many
real turns) is the reason Tier 1 exists; here we paid it.

## 3. Instrument & setup (reproducible)

Environment: `claude` CLI **2.1.167**, headless (`claude -p`), model **sonnet**.

```bash
# 1. install the plugins from the local marketplace (realistic competing catalog)
claude plugin marketplace add /home/user/ex-cog-dev
for p in research-toolkit makers-toolkit vasana-system security-toolkit; do
  claude plugin install "$p@ex-cog-dev"
done
claude plugin list           # research-toolkit -> 3.3.0 (the version under test)
```

**The firing instrument is already wired by install.** `vasana-system/hooks/hooks.json`
registers `count-skill-firings.sh` as a `PreToolUse` hook with matcher `Skill`;
installing vasana-system enables it. Each `Skill` invocation appends one JSONL
line to `~/.claude/logs/skill-firings.log`:

```json
{"timestamp":"…","session_id":"…","skill":"research-toolkit:dev-job-defense-ties","cwd":"…"}
```

Why `PreToolUse`: it fires at the *decision* to invoke `Skill`, before any
permission gate — so the firing is logged even in default permission mode and
even if the skill body later errors or stalls waiting for input.

**Pipeline validation (do this before trusting any number).** The method's
load-bearing assumption is that the harness emits a `PreToolUse` event for the
`Skill` tool. Prove it with an explicit-invocation control and watch the log grow:

```bash
claude -p "Use the dev-job-defense-ties skill to screen Acme Studios as an employer." --model sonnet
# -> log gained: {"skill":"research-toolkit:dev-job-defense-ties", …}
#    response entered onboarding (asked to approve config.py to read a profile)
```

Until that line appears from a real invocation, Tier 2's numerator is
hypothetical. It appeared. (The skill also correctly had **no profile** to read —
it ships profile-less — so it began onboarding, which is the right first-run
behaviour.)

## 4. Turn design

Fresh session per turn (a separate `claude -p`, no `--continue`), neutral cwd
(`/tmp/djdt-exp`, *not* the repo — the repo's `CLAUDE.md` would bias context),
`< /dev/null` so the CLI doesn't block waiting on stdin. One explicit control +
four oblique positives + four traps/negatives.

| # | Kind | Turn | Expect |
|---|---|---|---|
| T1 | explicit control | "**Use the dev-job-defense-ties skill** to screen Acme Studios…" | fire (pipeline) |
| P1 | positive (lexical) | "Unreal … 'simulation & training' … 'defense and civilian agencies'…" | fire |
| P2 | positive (**oblique**) | "real-time 3D for **'mission rehearsal'** systems…" | fire |
| P3 | positive (**oblique**) | "company making **'synthetic environments'** for 'government customers'…" | fire |
| P4 | positive (**oblique**) | "requires I be a **'US person'** eligible for a security clearance…" | fire |
| N1 | **over-fire trap** | "Unity gameplay job … **cozy farming game** shipping on Switch?" | null |
| N2 | negative | "React frontend role at a **fintech** payments startup…" | null |
| N3 | **adjacent-skill trap** | "**map who benefits** from Lockheed's latest defense contract." (no job) | null (→ cui-bono) |
| N4 | off-topic negative | "Fix this Python **traceback** in my CSV parser…" | null |

Design rationale, the part that makes the turns load-bearing:
- **Oblique positives (P2–P4)** are phrased by *symptom* with no word the skill's
  name/description matches on. A lexical-match positive (P1) fires on the skill
  *name* alone and tells you nothing about the description; the oblique ones are
  the real recall test.
- **N1 is the key over-fire trap**: same surface vocabulary as the positives
  (Unity, gameplay, studio, job) but unambiguously civilian. It tests whether the
  skill is firing on *defense signal* or just on *gamedev-job-shaped text*.
- **N3 is an adjacent-skill trap**: defense-flavoured but it's a beneficiary-
  mapping research request, not an employment decision — `cui-bono`'s job, not
  this skill's. It tests routing *precision across skills*, not just the target's
  recall.

## 5. Procedure (the reusable runner)

Sequential, with a per-turn log snapshot so each firing is attributed to its turn
(parallel runs would race on the shared log). N reps per turn for agreement.

```bash
LOG=~/.claude/logs/skill-firings.log
for turn in "${TURNS[@]}"; do
  before=$(wc -l < "$LOG")
  timeout 220 claude -p "$prompt" --model sonnet < /dev/null > "${label}.out" 2>&1
  fired=$(tail -n +$((before+1)) "$LOG" | sed -n 's/.*"skill":"\([^"]*\)".*/\1/p')
  # record whether dev-job-defense-ties is in $fired, plus any other skills
done
```

(Full scripts: `run.sh` = N=1 single pass, `run3.sh` = N=3 with agreement.)

## 6. Results

### N=1 (one session per turn)

| Turn | Want | dev-job-defense-ties | Other skill fired |
|---|---|:---:|---|
| T1 explicit | fire | ✅ fired | — |
| P1 lexical | fire | ✅ fired | — |
| P2 oblique | fire | ✅ fired | — |
| P3 oblique | fire | ✅ fired | — |
| P4 oblique | fire | ✅ fired | — |
| N1 cozy game | null | ⚠️ **fired** | — |
| N2 fintech | null | ✅ silent | — |
| N3 research | null | ✅ silent | **cui-bono** ✅ |
| N4 traceback | null | ✅ silent | — |

- **Recall on the four oblique/lexical positives: 4/4 (100%).** It fired on the
  symptom-only phrasings, not just the on-vocabulary one.
- **Clear negatives 3/3 correct** (N2, N4 silent; N3 routed to cui-bono).
- **N1 fired** — analysed below.

### N=3 (agreement; robustness)

Each turn re-run three times; reps that fired the target / 3. A 2/3 split would
mean the turn sits on the routing boundary — **none did.**

| Turn | Want | DJDT fired | Note |
|---|---|:---:|---|
| P1 | fire | **3/3** | robust |
| P2 | fire | **3/3** | cui-bono co-fired on 1 rep |
| P3 | fire | **3/3** | robust |
| P4 | fire | **3/3** | robust |
| N1 | null | **3/3** | robustly *fires* — see analysis |
| N2 | null | **0/3** | robustly silent |
| N3 | null | **0/3** | cui-bono fired 3/3 instead |
| N4 | null | **0/3** | robustly silent |

**Recall 12/12** across the four positives × three reps; **clear negatives 9/9
silent** (N2, N3, N4). Every cell is 3/3 or 0/3 — at this sample size the routing
is deterministic, not boundary-sensitive. The only co-activation was `cui-bono`
firing *alongside* the target on one P2 rep (a Round-1-style co-fire, minor — a
different skill firing, not a miss of the target's recall).

## 7. Analysis

**N1 (the over-fire) is benign — and by design.** The transcript shows it fired,
scanned, found *"zero defense tells,"* classified the role `CIVILIAN`, and
concluded *"this one's clean,"* with a 2-minute studio-ownership caveat. It did
**not** manufacture suspicion. This is the skill's deliberate **recall-over-
precision posture** — its trigger says *fire on any gamedev job eval, the user may
not think to ask* — working as written. That N2 (fintech) *didn't* fire confirms
it's scoped to its gamedev turf, not literally every job. **N=3 shows the fire is
deterministic (3/3), not a coin-flip** — which settles the by-design reading *and*
raises the stakes on the one-line-clear fix below: every cozy-game-shaped eval
*will* trip a screen, so that screen had better be cheap when it clears.

**One real gap surfaced:** the skill says *"if clearly civilian, say so in one
line,"* but N1 got a **full screen block** before the one-line verdict. The
cheap-clear instruction isn't being obeyed tightly — a worth-making tightening
that lowers noise on obvious-civilian roles without touching recall. (Tracked as
a follow-up, not fixed here, to keep the firing result and the prose change
separate.)

**N3 is a precision win for the *system*, not just the skill.** Two defense-
flavoured skills were loaded; the router sent the beneficiary-mapping request to
`cui-bono` and the job-screen stayed silent. That is the `.claude/rules/skill-design`
thesis — *minimal overlap in what skills do, maximal overlap in what they trigger
on* — observed live: same trigger surface, different jobs, correct pick.

## 8. Validity limits (state them with the numbers)

- **Tier 2, so this is the real attention test** (full catalog of four installed
  plugins competing), not a proxy. Good.
- **Single-arm**: no A/B. This shows the skill fires/over-fires; it cannot
  attribute that to any particular wording choice (there's no control wording).
- **n per cell**: N=1 headline; N=3 robustness addendum. A single firing is not a
  rate — one run of N1 could re-roll. Agreement counts (§6.2) are the robustness
  evidence; below N≥3, treat per-turn firing as directional.
- **Denominator is the run design.** "Recall 4/4" is over *the four positives I
  wrote*, not a representative sample of all phrasings a user might type. The hook
  supplies the numerator (firings); the denominator (should-have-fired turns)
  exists only in this turn list.
- **sonnet only.** Routing can differ by model; a weaker model may under-fire the
  oblique turns, a stronger one may over-fire the traps.
- **Autonomous vs explicit.** T1 was an explicit `/`-style invocation (a pipeline
  control, not evidence of autonomous firing); P1–P4 and the traps were ordinary
  user turns, so their firings *are* autonomous. The hook counts both — keep
  explicit invocations out of the measured cells (only T1 used one).

## 9. Lessons for the methodology (portable)

Things this run learned that generalise to the next live activation test:

1. **The hook ships pre-wired.** Installing `vasana-system` registers
   `count-skill-firings.sh`; no manual hook config needed. Just read the log.
2. **Validate the log grows from a real invocation first** (the explicit
   control). The hook's unit test proves the *script* parses a synthetic
   envelope; only a live fire proves the *harness* emits the `PreToolUse` event.
3. **Don't reach for `--permission-mode bypassPermissions`** — it was denied by
   the auto-mode classifier as "unsafe agent," *and* it's unnecessary: `PreToolUse`
   fires before the permission gate, so default mode logs the firing anyway.
4. **`< /dev/null`** or `claude -p` blocks ~3s waiting on stdin per call.
5. **Run from a neutral cwd**, not the project repo — a repo `CLAUDE.md`/skills
   injects context that biases routing away from a real user's blank session.
6. **Oblique turns are the experiment**; lexical-match positives fire on the name
   alone. **Adjacent-skill traps** (N3) test cross-skill routing, which a single-
   skill recall measure misses entirely.
7. **A "false fire" can be a design choice, not a defect.** Read the transcript,
   not just the firing bit: N1 fired *and cleared gracefully*. The bit told us it
   fired; the prose told us that was fine.

## 10. Cross-references

- Method: `makers-toolkit:skill-activation-testing` (this is a live Tier-2
  instance of it). Tier-1 proxy + two-round design: its `references/firing-experiment.md`.
- Instrument: `vasana-system/hooks/count-skill-firings.sh` (+ `.test.sh`).
- The skill's own design rationale: `ARCHITECTURE.md`. Why it ships profile-less:
  `.claude/rules/shipped-skill-config.md`.

---

## 11. Generalizing the design — activation **and** functionality

This run is two tests sharing one harness, and keeping them distinct is the whole
game (it mirrors `skill-activation-testing`'s discipline #1: name what each
instrument can and can't see).

### Two axes, two instruments, two questions

| Axis | Question | Instrument here | Verdict type |
|---|---|---|---|
| **Activation** | Does it *fire* on the right turns and stay silent on the wrong ones? | `count-skill-firings.sh` (the firing log) | quantitative — firing is observable, countable, discriminating |
| **Functionality** | *Given it fired*, does it do its job correctly? | reading the transcript against expected behaviour | qualitative here — a scored suite is the open work |

Activation is the cheaper, more objective axis (a firing either is or isn't
logged). Functionality is harder: the output is prose, "correct" needs a gold
standard, and the same turn varies run-to-run. **A skill that fires perfectly and
reasons wrong has passed activation and failed functionality** — so a green
activation result is *necessary, not sufficient* for a sophisticated skill.

### What this run established on each axis (honestly)

- **Activation: rigorous.** 32 live sessions, a discriminating instrument, N=3
  agreement, validity limits stated (§6–§8).
- **Functionality: observed, not suited.** I read transcripts against intent, and
  it *did* surface real functionality signal:
  - **N1** — correct end-use classification (`CIVILIAN`) + graceful clear + a
    falsifiable ownership caveat = functionality working; but the *full screen
    block before the one-line verdict* exposed a real gap (premature single-pass
    clear → issue #68).
  - **N3** — the beneficiary-mapping request routed to `cui-bono`, not the
    job-screen = correct *cross-skill* functionality, which a firing count can't see.
  - **P2** — correctly read "real-time 3D for mission rehearsal" as *almost
    certainly defense simulation* and moved to buyer-chain + threshold.
  - **P4** — fired on the clearance gate but *onboarded* (no profile) instead of
    classifying `DEFENSE-CONFIRMED` per Step 2; correct given no threshold, but it
    shows why functionality testing needs a **fixed test profile** (below).
  This is n-of-a-few transcript reading, not a rubric. Real signal, not a suite.

### What a full functionality suite would add (the design)

1. **A fixed test profile.** Functionality on a profile-less skill is undefined
   (`OUT` vs `CLEAR` depends on the operator's red line). Pin a known threshold so
   verdicts become checkable: *given THIS line, EU-export-to-Saudi MUST be `HARD STOP`*.
2. **Gold-standard expected outputs per turn** — the buyer-chain, the end-use
   rung, the verdict under the fixed profile, the output-format fields required.
3. **A scored rubric per output field**, not a gestalt read: buyer-chain resolved?
   nationality tagged? evidence tier assigned? "what would change it" present *and*
   falsifiable? **threshold applied = the test profile's, not one the model
   invented?** (the skill's central correctness claim).
4. **Adversarial / oblique functionality cases** with known answers: EU-export →
   escalate; civilian `digital-twin`/ISR → `INVESTIGATE`, not auto-clear on a logo.
5. **Negative functionality**: does it *manufacture* suspicion on a clean role
   (over-flag) or *auto-clear* on a soft tell (under-verify)? Both are invisible to
   a firing count.
6. **The #68 stopping discipline as a functionality check**: is a `CLEAR` reached
   after a confirming pass, or at first glance?
7. **Reps + a no-skill control arm**: score across runs, and compare against the
   model with the skill *disabled*, to attribute behaviour to the skill not the base model.

### The transferable template

A skill-test **suite** = **activation tests** (firing, via the hook) **+
functionality tests** (behaviour vs a gold standard under a fixed profile) **+ the
harness** (live install for both; log for activation, transcript+rubric for
functionality) **+ stated validity limits per axis**. The two axes use different
instruments and answer different questions; reporting one as the other is the
failure mode. That is what a future skill-test-design apparatus should emit —
defaulting to activation-only when that's all that's asked, but able to specify
the functionality half for sophisticated skills, where "it fired" is the easy 20%.
