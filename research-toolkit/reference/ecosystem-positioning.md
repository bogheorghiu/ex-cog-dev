# Investigation Methodology Ecosystem: Positioning & Gaps

## Where Our Toolkit Fits Among Published Frameworks

| Capability | DISARM | Bellingcat | Oxford Comp. Prop. | Chomsky | Our Toolkit |
|-----------|--------|-----------|-------------------|---------|-------------|
| Beneficiary mapping (ALL sides) | No | No | Partial | Yes (structural) | Yes (per-claim) |
| Source topology mapping | No | No | Partial | Yes (5 filters) | Yes (dependency chains) |
| Epistemic confidence tiering | No | Implicit | Yes | No | Yes (explicit) |
| TTP classification | Yes | No | Yes | No | **Gap** |
| Evidence verification | No | Yes | No | No | Partial |
| Symmetric skepticism | No | No | Partial | Yes | Yes (aspirational*) |
| Unexamined dichotomy detection | No | No | No | No | Yes (novel) |
| Cross-domain pattern recognition | No | No | No | No | Yes (novel) |
| Real-time investigation | No | Yes | No | N/A | Yes |

*aspirational = proof-of-life postmortem showed failure to apply symmetrically; recursive debiasing (section 4a) addresses this.

## What's Genuinely Novel

1. **Unexamined dichotomy detection** — No framework systematically investigates the middle ground between binary framings
2. **Recursive self-observation** — Catching our own asymmetric skepticism; no framework models the analyst as biased participant
3. **Source topology as evidence evaluation** — Distinguishing "multiple sources confirm" from "one node echoed by downstream amplifiers"
4. **Integration across computational and reasoning layers** — DISARM is taxonomy, Bellingcat is procedures, Sherloq is computation. None bridge all three.

## Integration Architecture (Future)

```
ORCHESTRATION  — cui-bono + DIP (beneficiary mapping, source topology, epistemic tiering)
CLASSIFICATION — DISARM TTPs (campaign pattern matching, countermeasures)
VERIFICATION   — Bellingcat-style procedures (geolocation, chronolocation, provenance)
COMPUTATION    — Sherloq/forensics (ELA, JPEG analysis, clone detection)
TAXONOMY       — Wardle-Derakhshan + Chomsky (mis/dis/malinformation, structural bias)
```

## Gaps to Fill (tracked as backlog items)

| Gap | Framework | Priority | Notes |
|-----|-----------|----------|-------|
| TTP classification | DISARM | Medium | Extract taxonomy, apply symmetrically |
| Image forensics | Sherloq | Low | MCP wrapping Popescu-Farid algorithms |
| Spatial intelligence | WorldView/NASA | Low | Data fusion MCP (OpenSky + ADS-B + CelesTrak) |
| Chronolocation | SunCalc | Low | Shadow analysis tool |
| Non-Western OSINT | Chinese/Russian/Arabic | Medium-High | See backlog #6 |

## Key External Frameworks

### DISARM (DISinformation Analysis & Risk Management)
MITRE ATT&CK model for disinfo. Red Framework (attacker TTPs) + Blue Framework (countermeasures). Useful TTP taxonomy but assumes attacker/defender framing — apply symmetrically per our principles.

### Bellingcat Verification Methodology
Geolocation, chronolocation, metadata analysis. Procedures are sound regardless of institutional alignment. Extract procedures, don't inherit institutional authority.

### Chomsky-Herman Propaganda Model
5 filters (ownership, advertising, sourcing, flak, anti-ideology). Structural analysis that applies to ALL media. Most honest about pointing lens inward. Pre-digital.

### Chinese 舆情分析 (Public Opinion Analysis)
Managerial framing (monitoring) vs Western military framing (warfighting). Open-source tooling exists (StoneDT). Lambda architecture for real-time + historical analysis. Propagation analysis more developed than Western equivalents.
