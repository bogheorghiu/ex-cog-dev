#!/usr/bin/env python3
"""Efficiency proxy for the dev-job-defense-ties screen.

Measures the FRONT-LINE LEXICON's discrimination — would the 60-second scan
(Step 1) flag this role? — by auto-extracting the screen vocabulary from the
shipped domain pack (reference/domain-dev.md) and matching a labeled corpus.

Scope, honestly: this does NOT test the model's buyer-chain / verification /
threshold reasoning (that is judgment, not unit-testable). It is a lower-bound
coverage proxy AND a regression guard — it catches lexicon coverage gaps and
over-broad terms (e.g. bare "target"/"effects" matching civilian VFX/marketing
jobs) whenever the domain pack changes. Stdlib only; exits non-zero on failure.
"""

import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PACK = _HERE / "reference" / "domain-dev.md"
_OVERLAY = _HERE / "reference" / "domain-gamedev.md"

failures = 0


def check(label, condition):
    global failures
    print(f"   {'✓' if condition else '✗ FAILED:'} {label}")
    if not condition:
        failures += 1


def screen_vocabulary(pack_text):
    """Extract match terms from a domain pack: quoted phrases, acronyms, names."""
    terms = set()
    # The lexicon section runs from its heading (## Lexicon / ## Added lexicon) to
    # the next "## " heading. Matching the heading at line-start — not a substring —
    # so a section name *mentioned* in prose (e.g. the intro's swap-rule list) can't
    # truncate it.
    m = re.search(r"^##[^\n]*[Ll]exicon\b.*?(?=^## |\Z)", pack_text, re.M | re.S)
    lexicon = m.group(0) if m else pack_text
    for q in re.findall(r'"([^"\n]{2,45})"', lexicon):
        for part in re.split(r"\s*/\s*", q.strip().lower()):
            part = part.strip(" .,")
            if len(part) >= 3:
                terms.add(part)
    for a in re.findall(r"\b([A-Z][A-Z0-9]{1,6})\b", lexicon):
        if a not in {"US", "EU", "OR", "AND", "TS", "STE"}:
            terms.add(a.lower())
    for line in pack_text.splitlines():  # the prime/buyer name-list
        m = re.match(r"\s*-\s*\*\*[^:]+:\*\*\s*(.+)", line)
        if m:
            for tok in re.split(r"[,/]", m.group(1)):
                tok = re.sub(r"\(.*?\)", "", tok).split(" plus ")[0].strip(" .*")
                if len(tok) >= 4 and tok[0].isupper():
                    terms.add(tok.lower())
    return terms


# Labeled corpus. DEFENSE must be caught; CIVILIAN must not (incl. the tricky
# "visual effects" / "target audience" cases that bare lexicon terms over-match).
CORPUS = [
    ("DEFENSE", "Unreal engineer for LVC mission rehearsal and a synthetic training environment (STE)."),
    ("DEFENSE", "C++ developer, C4ISR data fusion; must be a US person, SECRET eligible."),
    ("DEFENSE", "Real-time 3D for force-on-force wargaming; customer is Lockheed Martin."),
    ("DEFENSE", "Simulation engineer supporting Anduril autonomy programs."),
    ("DEFENSE", "Gameplay programmer: threat library and kill chain visualization for NATO."),
    ("DEFENSE", "Tools engineer for Elbit mission-rehearsal trainers."),
    ("DUAL", "Unity engineer for a digital twin with situational awareness for critical infrastructure & public safety."),
    ("DUAL", "Edge autonomy and decision support for resilience in national security contexts."),
    ("CIVILIAN", "Unity developer for a cozy farming sim shipping on Switch and Steam."),
    ("CIVILIAN", "Frontend React engineer for a recipe-sharing app."),
    ("CIVILIAN", "Technical artist for a mobile match-3 puzzle game."),
    ("CIVILIAN", "Backend Go engineer for a fintech payments startup."),
    ("CIVILIAN", "Level designer for a narrative adventure game."),
    ("CIVILIAN", "VFX artist creating cinematic visual effects for a fantasy RPG."),
    ("CIVILIAN", "Growth marketer defining target audience segments for a mobile game."),
]


def hits(text, terms):
    t = text.lower()
    return sorted({term for term in terms if re.search(r"(?<![a-z])" + re.escape(term) + r"(?![a-z])", t)})


def main():
    check("domain pack exists", _PACK.exists())
    if not _PACK.exists():
        return
    terms = screen_vocabulary(_PACK.read_text(encoding="utf-8"))
    print(f"\n   screen vocabulary auto-extracted from {_PACK.name}: {len(terms)} terms\n")

    by = {"DEFENSE": [], "DUAL": [], "CIVILIAN": []}
    for label, snip in CORPUS:
        h = hits(snip, terms)
        by[label].append((bool(h), h, snip))
        flag = "HIT " if h else "miss"
        print(f"   [{flag}] {label:8s} {snip[:58]:58s} -> {h[:3]}")

    defense_recall = sum(c for c, _, _ in by["DEFENSE"]) / len(by["DEFENSE"])
    civ_fp = sum(c for c, _, _ in by["CIVILIAN"]) / len(by["CIVILIAN"])
    dual_flagged = sum(c for c, _, _ in by["DUAL"])
    print(f"\n   DEFENSE recall {defense_recall:.0%} | CIVILIAN false-positive {civ_fp:.0%} | DUAL flagged {dual_flagged}/{len(by['DUAL'])}\n")

    check("every DEFENSE role is flagged (recall == 100%)", defense_recall == 1.0)
    check("no CIVILIAN role is flagged (false-positive == 0%)", civ_fp == 0.0)
    check("every DUAL-use role raises at least a soft tell", dual_flagged == len(by["DUAL"]))

    # The gamedev overlay must genuinely *extend* the default pack, not duplicate it.
    if _OVERLAY.exists():
        added = screen_vocabulary(_OVERLAY.read_text(encoding="utf-8")) - terms
        check(f"gamedev overlay adds {len(added)} terms beyond the default pack", len(added) >= 3)


main()
if failures == 0:
    print("✅ Screen efficiency checks passed!")
else:
    print(f"❌ {failures} check(s) failed.")
raise SystemExit(1 if failures else 0)
