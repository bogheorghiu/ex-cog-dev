---
name: convergence-by-accumulation
description: A self-improving artifact's mature form equals its template/reset form, modulo history. Improvement happens through refinement of the same content, not through parallel maintenance of "stable" and "dev" versions. Use when designing a tool that ought to be developed in the same place it's used, and you're tempted to maintain a separate "release" surface.
---

# Convergence-by-Accumulation

## Vasana

A vasana is a pattern that persists across unrelated contexts. If during
this task you notice such a pattern emerging, it may be worth capturing.
This skill works best alongside the `vasana` skill and `vasana` hook
from the Vasana System plugin.

Modify freely. Keep this section intact.

---

## What This Pattern Is

A structural property of self-improving artifacts: the **mature/final form equals the template/reset form, modulo history**. There is no separate "release version" maintained in parallel to the development version — the deliverable is *derived* from the development environment at any point in time, differing only in accumulated history and in-flight tracking artifacts.

Improvement happens through refinement of the same content, not through parallel maintenance. The artifact and the environment it's developed in *converge by construction*, not by release ceremony.

**Origin:** Crystallized 2026-05-21 during work on a self-improving meta-repo for structuring AI-coding-agent projects. The articulated principle: the final functional form of such a self-improving repo is the same as its reset form without ever performing a reset — reached by accumulation and refinement, where what differs is only the history. The process by which the principle emerged is the sibling vasana [[frame-pushback]].

---

## The Principle in One Line

> *If you can derive the deliverable from the development environment at any time, with no separate work, then the two are the same artifact viewed at different states. Make convergence the construction.*

---

## Recognizing When This Applies

**Conditions:**
- You're building a *tool*, *framework*, *template*, *protocol*, or other artifact whose users will adopt and adapt it.
- The tool will continue evolving while it's being used.
- You're tempted to maintain a "stable release" track separately from a "dev" track.
- You notice that the only difference between dev-state and release-state is *accumulated history* (state files, working artifacts) — the substantive content is the same.

**Strong signals:**
- "Should we have two repos, or one with branches?" — the question implies parallel maintenance; the pattern suggests the question is mis-framed.
- "How do we keep the release in sync with dev?" — sync debt is the failure mode this pattern dissolves.
- "Where should the new feature land — dev branch or release branch?" — if you have to ask, you're maintaining the wrong split.
- The tool is being developed *using itself* (dogfood / self-application). The dev environment IS the artifact.

**Not this pattern:**
- Tools with hard backward-compat guarantees (the release version is *frozen by promise*; dev can't simply become it).
- Tools whose deliverable form is *structurally different* from the dev form (compiled binaries, packaged distributions, signed artifacts — there's actual transformation, not just history difference).
- Tools where dev and consumption happen at radically different paces (e.g., kernel development → distro release).
- Tools where the dev environment is intentionally toxic to consumers (debug build, instrumented build).

The discriminator: **is the difference between dev-form and release-form just "history we've accumulated" or is it actual structural transformation?** If just history, this pattern applies. If transformation, it doesn't.

---

## The Pattern

### Setup: The temptation of parallel maintenance

A self-improving artifact has two pulls on it:
- **Pull A:** "I'm developing it, so I need to mutate state freely, log decisions, track open work."
- **Pull B:** "I'm shipping it, so users need a clean form with no in-flight cruft."

The naive resolution: two artifacts. One messy (dev), one clean (release). A release process bridges them.

This works, badly. The dev and release drift; sync becomes its own job; improvements tried in dev fail to reach the release; "the release branch is six months behind."

### The convergence move: identify what *actually* differs

Audit: what's different between dev-state and the form you'd ship?

If the answer is *only*:
- State files (history logs, working trackers, in-flight HANDOFFs, current-context files)
- Accumulated git history (commits documenting how we got here)

...then the *substantive content* is identical. The release is just the dev environment with state files reset.

If you find structural differences (different code, different APIs, different surfaces) — those are bugs in the convergence, not features. Fold them back: the dev should be developing the thing that ships.

### The operationalization: derive, don't maintain

Build a small mechanism that **derives** the release form from the dev form. In code:
- A script that resets state files to template content (`prepare_release.py` in the origin example).
- An optional sibling-repo mirror that propagates substantive content + applies the reset (`mirror_to_reference.py`).
- A convention for which artifacts are "deliverable" vs "in-flight" (encoded as the script's allowlist).

The mechanism is small because most of the work is *not maintaining a separate thing*. The mechanism doesn't transform; it filters.

### The landing: the work and the deliverable converge

When the pattern is in place:
- Every change to substantive content is immediately a deliverable change.
- The "release" is the current dev state with state files reset — derivable at any commit.
- History is the only thing that differs, and history is recoverable from git (the source of truth for "how did we get here").
- New work is never "for dev only" or "for release only" — it's just work, and the question of where-it-lives doesn't arise.

The synchronization debt that motivates parallel maintenance disappears, because there's no parallel to maintain.

---

## Worked Examples in the Wild

**Origin example: AI-dev-template scaffold.** Work repo evolves with rich HISTORY/CHANGELOG/HANDOFF artifacts; reference repo is derived at any point via `mirror_to_reference.py` + `prepare_release.py` template-reset. Only state files differ; protocols/workflows/scripts/vendor-adapters are shared.

**Documentation-as-code.** The README that ships IS the README in dev. No separate "user-facing manual" maintained apart from the source. Improvements to one are immediately improvements to the other.

**Open-source mainline.** The `main` branch IS the release; tags are points in its history. No `release/` branch maintained alongside that diverges. (Counter-example: projects with frozen LTS branches violate this — but they're paying a real backward-compat tax for the violation.)

**BDD / spec-as-test.** Tests are the specification. There's no "test-form" vs "spec-form" — they converge by construction.

**Type definitions as contract.** In strongly-typed languages, the types declared in dev ARE the contract consumers depend on. No separate "API spec" maintained.

**Declarative configuration.** A Kubernetes manifest, a Terraform plan, a Dockerfile — the dev artifact IS the deployment instruction. The transformation is execution, not maintenance.

**Self-hosted compilers / bootstrapping languages.** The compiler in dev is the compiler that ships, by definition. Self-hosting *forces* the convergence and is sometimes called the strongest test of a language's maturity.

---

## What Makes It Work

1. **State files carry history; substantive content carries the artifact.** The split has to be clean — if substantive content also drifts between dev-form and release-form, the pattern breaks. Be ruthless about what counts as "in-flight" (state files, trackers) vs "deliverable" (everything else).

2. **The derivation has to be cheap and automatable.** If "deriving the release" takes a half-day of human work, the temptation to maintain it separately returns. A 10-second `python3 scripts/prepare_release.py` is the right scale.

3. **State files are gitignored or reset, never copied raw to the deliverable.** This is the only enforcement that maintains the convergence. As soon as someone copies the rich HISTORY to the release, the artifacts have diverged.

4. **Improvements happen in the dev environment, with no "do I also need to update release?" question.** That question is the symptom of failed convergence. The pattern's payoff is that the question never has to be asked.

5. **Git history serves as the ledger of accumulation.** "Recover the rich dev state from a prior commit" replaces "maintain a snapshot of the rich dev state." The history is the archive; no separate archiving is needed.

---

## Anti-Patterns

### ❌ Maintaining a "stable" branch separately
*Symptom:* Two branches, both edited, periodically synced. The sync is its own labor; improvements stall in one or the other; consumers complain that "stable is missing X."

### ❌ Treating the release as the source of truth
*Symptom:* "Don't add it to dev yet, we haven't released this feature." The dev environment becomes a downstream of the release, instead of the other way around. Improvement velocity drops to release cadence.

### ❌ Letting state files leak into the deliverable
*Symptom:* Consumers clone the release and find HISTORY.md full of "we considered X but decided Y for project Z" — content meaningful only in the dev context. The leak signals the convergence is breaking down.

### ❌ Building elaborate transformation between dev and release
*Symptom:* The "release script" is 500 lines and does substantial restructuring. That restructuring is the divergence the pattern was supposed to prevent. If your release script does more than reset state files, look for the structural drift and eliminate it.

### ❌ Treating dogfood as performative
*Symptom:* "We use our own tool, but in a special dev-only way." The special way is where convergence dies. If self-application reveals friction, fix the friction in the tool, don't paper over it in dev.

---

## Testing This Pattern

Before relying on this:

1. **Inventory:** List everything that's "different between your dev form and your release form." Categorize each as (a) history, (b) state file, (c) structural difference.
2. **Audit (c):** For each structural difference, ask: *why?* If the answer is "because dev needs flexibility / release needs stability," is that real or is it inertia? Often it's inertia.
3. **Build the derivation:** Write the script that turns dev-form into release-form. If it stays under ~100 lines of state-file resets and skip-lists, you're in the pattern's sweet spot. If it grows, that's a signal you have divergence elsewhere.
4. **Stop maintaining the release as a thing.** Whenever you'd "update the release," instead update dev and re-derive. Notice whether anything actually requires the parallel maintenance you were doing.

**Honest note:** This pattern fails under hard backward-compat guarantees (frozen interfaces that *must not change* in a release while still evolving in dev). It also fails when the deliverable is structurally different from the dev (compiled artifacts, signed releases, packaged distributions). The discriminator is whether your "difference" is history or transformation — only history-difference converges by this pattern.

For meta-tools (templates, scaffolds, protocols, frameworks-of-thinking), the difference is almost always history-difference. The pattern is most apt for *those*.

---

## Related Patterns

- [[frame-pushback]] — sibling vasana. `frame-pushback` is the *process* by which principles like this one crystallize through dialectic. `convergence-by-accumulation` is the *content* of one such principle. The two are linked by origin: this pattern emerged via the other in the 2026-05-21 session.
- [[concrete-abstract-dance]] — adjacent. Builds concrete → extracts pattern → tests against new concrete. `convergence-by-accumulation` is the *meta* version: the artifact converges with its development environment through the same accumulation dynamic.
- [[description-becomes-embodiment]] — adjacent. Where a description of a thing becomes the thing itself. Convergence-by-accumulation is the structural cousin: the dev environment becomes the deliverable.
- [[framework-dissolution]] — adjacent. The framework "dev branch vs release branch" dissolves when convergence-by-accumulation is in place. Dissolution is the *result*; convergence is the *mechanism*.
- [[mechanism-not-metaphor]] — adjacent. The pattern is a mechanism (the derivation script, the state-file reset, the gitignore discipline), not a metaphor. The metaphor of "convergence" describes; the mechanism delivers.

---

## A Family Note

This pattern, [[frame-pushback]], [[concrete-abstract-dance]], and the (yet-to-be-located) existing convergence vasana likely belong to a **pattern-seed** family: *"convergence at different scales."* If three or more turn out to share a formation dynamic, the pattern-seed should be made explicit (`pattern-seeds/` directory). The candidate for the pattern-seed name: **"the dance of arrival"** — the structural property that some forms of co-evolution produce convergence without requiring it as a goal.
