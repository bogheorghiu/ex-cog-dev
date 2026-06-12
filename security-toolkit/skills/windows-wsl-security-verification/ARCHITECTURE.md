# windows-wsl-security-verification — architecture & decisions

Why this skill has the shape it has, so a future edit changes it on purpose.

## Provenance: distilled from a lived workflow, not copied

The procedure was developed and run end-to-end on a real Windows + WSL2 dev box
(2026-06-08/09, in response to a real supply-chain campaign), result: a clean
machine and a set of hard-won reading rules. The skill ships the **mechanism and
the discriminators**, not the operator's working notes — those stay outside the
repo (they contain machine- and person-specific detail; this plugin is public,
and the repo rule is that nothing sensitive enters any branch's history). Worked
examples in SKILL.md are the lived cases with operator specifics stripped.

## Scope: verification only — hardening is a different skill (later)

The lived workflow had two halves. **Verification/triage + surface-reduction**
was completed end-to-end → it's encodable. **Hardening** (sandbox distro,
secrets isolation, egress control, containers, gVisor, microVM) was still mostly
*unlived* at authoring time → encoding it would freeze an abstraction before
practice has shaped it (the emergence-over-enforcement failure). The split also
passes the "does it earn its cost" test: verification fires on *"did I get hit /
what is this detection?"*; hardening fires on *"make this box safer"* — different
triggers, different working modes (one is a sweep, the other is interactive
system surgery), so two skills, with this one's NEXT pointer composing toward
the hardening track. Hardening is likely a *set* of skills (per isolation tier
or environment), not one — let that emerge when those paths are lived.

## OS scope: named in the skill name, on purpose

`windows-wsl-security-verification`, not `security-verification`. The checks are
tool-concrete (Autoruns, Defender-passive interplay, `code --list-extensions`,
WSL bridge model) and tool-concrete is the value — but it also means the skill
genuinely does not cover macOS or bare Linux. The plugin is public; over-claiming
OS coverage is the genre's standard failure. Sibling skills for other OSes hook
into the Integration table and trigger on the same turns when built.

## File split: discriminators in the body, checklists in packs

- **SKILL.md** carries the frame, the trigger surface, and the *reading rules*
  (filename-IOC via find-not-grep; VT named-family over aggregate; web-filter
  block ≠ infection; AV active/passive interplay) — the parts that make this
  more than a pasteable checklist, and the parts the model needs in view while
  reasoning about evidence.
- **reference/** carries the exhaustive, command-level material, loaded only
  when the corresponding step runs: `wsl-linux-ioc-checklist.md` (Step 1),
  `windows-checklist.md` (Steps 3/5), `interpreting-detections.md` (Step 4).
  Checklists change (new vectors, new tools) without touching the mechanism.

## No `scripts/`, no config — on purpose

- **No scripts:** most Windows-side steps are GUI- or host-side (an agent in WSL
  can't reach them) and the WSL-side commands are short one-liners whose value is
  in the *reading*, not the running. A script would add determinism nowhere it's
  currently lost. If repeated use shows the WSL sweep being fumbled, a triage
  script can earn its place then — not speculatively.
- **No per-user config:** the skill is pure procedure — no operator threshold,
  preference, or secret — so the shipped-skill-config machinery (self-locating
  config store) has nothing to store. If a configurable element appears (e.g. a
  per-user "known residents" allowlist to speed re-triage), ship it profile-less
  via that pattern at that point.

## Honest ceiling as a design element

"You cannot prove a machine clean" appears in Scope, in the verdict vocabulary
(`CLEAN-SO-FAR (confidence raised, not proof)`), and in Self-Reflexivity — three
places on purpose. IOC triage is asymmetric (hits meaningful, cleans only
confidence-raising), and a security skill that lets a tidy checklist run read as
proof is actively harmful. The RESIDUAL GAPS output line is mandatory for the
same reason.

## Known staleness vector

The named campaign/versions in the reference pack (LiteLLM 1.82.7/8, TeamPCP,
CVE-2026-33634) are worked examples of the *class* and will age. The skill's
instruction for any current incident is to fetch the advisory's own IOC list and
apply the same discriminators — the discriminators are the durable part.
