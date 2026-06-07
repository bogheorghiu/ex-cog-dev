# Domain pack: dev (default)

> **Public OSINT reference — the *subject* the screen scans for, not an operator's profile or politics.** This is the **default domain**: field-agnostic, pre-scoped to software/creative dev and adjacent roles. It ships and works standalone. **Overlays** narrow or extend it for a specific field (see `domain-gamedev.md`); a user installs overlays into `<config>/domain/`. Changing the domain *away from dev entirely* warrants a fork — the skill is named for dev.
>
> Swap rule: keep the section headings (`## Lexicon`, `## Buyer …`, `## End-use ladder`, `## Verification`) so the mechanism and the efficiency test can find them.

## Lexicon (Step 1 — the 60-second scan)

None of these is individually disqualifying; they are the tells that re-route you to verification.

**Dead giveaways (mil-sim / defense terms of art):** LVC / "Live, Virtual, Constructive," "mission rehearsal," "wargaming," "C2 / command and control," "C4ISR," "ISR," "force-on-force," "effects-based operations," "kill chain," "targeting," "threat library."

**Soft tells (dual-use cover):** "digital twin" + sensor/telemetry/geospatial fusion, "decision support," "situational awareness," "autonomy," "edge," "resilience," "critical infrastructure & public safety," "deterrence," "national security," "mission-driven."

**Corporate-camouflage move:** "defense" slipped mid-list between civilian sectors — "logistics, telecom, **defense**, and infrastructure." The list is the disguise. Flag it.

**Clearance / nationality gate (Step 2 — the highest-signal filter):**
- **US:** "must be a US person," "SECRET/TS eligible," "FFRDC," "ITAR/EAR."
- **EU:** "NATO," "EU/NATO nationality required," "habilitación de seguridad," "I+D en defensa," "nulla osta di sicurezza."

A clearance or citizenship gate isn't name-smell — it's the buyer stating its own end-use outright. It confirms *military end-use* regardless of how the role reads.

## Buyer / prime name-list (Step 3), tagged by nationality

If the buyer-chain ends at any of these, it's defense regardless of title. Tag the nationality — it feeds the buyer-nationality axis, which the threshold evaluates.

- **US:** Lockheed Martin, RTX/Raytheon, Northrop, General Dynamics, Booz Allen, SAIC, Leidos, CACI, Anduril, Palantir, Shield AI, plus FFRDCs (Aerospace Corp, MITRE, APL).
- **Israel:** Elbit, IAI, Rafael, and their integrators/subsystems.
- **US-aligned Gulf / Middle East:** Saudi Arabia, UAE, Bahrain, Egypt, Qatar — these almost never appear as the *employer*; they appear as the *export customer* of a US or EU prime (the Navantia→Saudi corvette pattern).
- **Non-Western / non-NATO** *(under-represented here — English-language OSINT erases it; extend per your context):* China — AVIC, NORINCO, CASC, CETC; Russia — Rostec, Almaz-Antey, United Aircraft; Turkey — Aselsan, **Havelsan** (military simulation/training — squarely in this skill's lane), Baykar, Roketsan; South Korea — Hanwha, KAI, LIG Nex1; Gulf domestic — **EDGE Group** (UAE), **SAMI** (Saudi); India — HAL, BEL, Bharat Dynamics. They seldom recruit in the EU/US market as the *direct employer* (also check them as *parent owner* / *upstream subcontract*), but a sim or game-engine role for one is exactly what the West-heavy list above would miss.
- **EU/Spain:** Indra, GMV, Navantia (Sistemas), SENER, Escribano, Tess Defence, Airbus Defence & Space, Arquimea.
- **EU other:** Helsing, Rheinmetall, Hensoldt, Leonardo, Thales, Saab, KNDS, Tekever, Quantum Systems.

**Follow the chain to the end user, not the contracting prime.** The nationality that matters is who *operates* the deliverable; an EU prime's export sale can reach a different end user one layer down. The chain must run to the export customer before the threshold classifies it.

**Subsystem entanglement:** a platform may carry US (Aegis, Mk41, SPY-7) or Israeli (Elbit/Rafael) content inside an otherwise national program. Note which layer the *role* sits on — combat-system core vs. one layer up (trainer/visualization).

**Vantage & limits (this list is not neutral).** It's scoped to the **US/EU labour market** and built from **English-language open sources**, so it's granular on US/Israeli/EU primes and thin on everyone else — and public contract registries barely exist for non-Western buyers. The buyer-nationality map is **NATO-shaped by default**, and a non-Western defense employer can pass unflagged. So read a "no named match" as *absence of evidence, not a clear* (SKILL.md Step 0), and **extend the list with an overlay** for the field and region you actually operate in. (This is the asymmetric-skepticism bias `cui-bono` warns about, inherited here.)

## End-use ladder (Axis 1)

Place the role on the spectrum; don't binary it:

```
CIVILIAN ── DUAL-USE ── TRAINING/SIM ── ISR/SURVEILLANCE ── C2/TARGETING ── LETHALITY
```

- Crew/maintenance **training sims** sit near the benign end (teach operation, save fuel/ammo) but are still military end-use.
- **ISR / surveillance / data-fusion** is the ambiguous middle — where "civilian digital twin" most often launders.
- **Targeting / fire control / autonomy-for-effects** is the lethal end.

## Verification sources (Step 4)

Contract registries are primary sources and outrank any aggregator:
- **US:** USAspending.gov, SAM.gov.
- **EU:** TED (Tenders Electronic Daily); national defense procurement portals.

Plus the company's own Customers/Partners/About page (logos, case studies), leadership LinkedIn (ex-military / ex-prime / ex-MoD founders), and `[company] (defense OR military OR DARPA OR "Ministerio de Defensa" OR MoD OR contract)`.
