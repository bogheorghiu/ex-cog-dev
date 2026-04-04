# Source Classifications - Operational Reference

This file tracks external data source assessments. See 00_TOOL_PROTOCOL.md Section 6 for methodology.

## Two-Layer Source Architecture

This file covers **Layer 1: Data Tools & APIs** — programmatic sources Claude can query.

For **Layer 2: Journalistic & Analytical Sources** — multi-perspective narrative triangulation for investigations — see `SOURCE_DIVERSITY_FRAMEWORK.md`. That file covers which journalistic outlets to read, what each outlet's position lets it see vs. hide, and how to triangulate across vantage points.

**Both layers apply simultaneously during investigations.** Data tools provide structured facts; journalistic sources provide context, framing analysis, and counter-narratives.

---

**Classification tiers (Layer 1):**
- **BANNED**: Do not use - fundamental credibility problems
- **PENDING INVESTIGATION**: Not yet assessed - apply framework before relying on
- **ASSESSED (No Issues Found)**: Protocol applied, no disqualifying issues identified (still use with documented coverage limits)
- **GAP ENTITIES**: Would be valuable but no convenient tool access
- **DOMAIN-SPECIFIC**: Niche tools, investigate only when domain relevant

---

## BANNED

### Candid (GuideStar/Foundation Center merger)

**Assessment Date:** December 2025

**Disqualifying Issues:**
- **Governance capture**: Board dominated by major foundations (Ford, Gates, Hewlett, MacArthur, Rockefeller) who are also primary funding sources and data subjects
- **Business model conflict**: Charges nonprofits for "verified" status while those same nonprofits are the data being evaluated
- **DAF opacity**: Actively promotes DAFs despite their role as dark money vehicles; does not surface DAF grant flows
- **Extractive model**: Aggregates free public data (990s), adds minimal processing, charges for access
- **Ideological filtering**: Rating systems embed assumptions favorable to institutional philanthropy

**Evidence:**
- Board composition publicly documented
- 990 data is public; Candid's primary value-add is aggregation
- No DAF grant tracing despite technical feasibility
- "Verified nonprofit" status requires payment

**Recommendation:** Use IRS EO BMF directly for nonprofit lookup. For 990 analysis, ProPublica Nonprofit Explorer is preferable (investigate first).

---

## PENDING INVESTIGATION

### HIGH PRIORITY (Currently in use or frequently encountered)

*None remaining - yfinance moved to ASSESSED WITH CAVEATS*

**Tomba (email finding tool)**
- Owner: Unknown (investigate)
- Concerns: Privacy implications, data sourcing methodology unclear
- MCP Status: ✅ Available in current environment
- **Action needed:** Full assessment including data sourcing ethics

**ProPublica Nonprofit Explorer**
- Owner: ProPublica (nonprofit investigative journalism)
- Initial assessment: Likely trustworthy - nonprofit mission alignment, transparent methodology
- MCP Status: ✅ propublica-mcp exists
- **Action needed:** Confirm no conflicts, document coverage limits

### MEDIUM PRIORITY (Would use if needed)

**Brave Search**
- Owner: Brave Software
- Concerns: Cryptocurrency ties (BAT token), potential for crypto-aligned bias
- MCP Status: Potentially available
- **Action needed:** Assess before enabling

**OpenSanctions**
- Owner: German nonprofit
- Initial assessment: Transparent methodology, likely trustworthy
- MCP Status: ⚠️ Partial (third-party mcp-sanctions OFAC-focused; robust API exists)
- **Action needed:** Confirm data freshness, assess lag times

**LexisNexis / RELX**
- Owner: RELX plc (publicly traded)
- Concerns: Surveillance capitalism business model, law enforcement contracts, data broker activities
- MCP Status: Unknown
- **Action needed:** Assess if power structure analysis requires their data

### LOWER PRIORITY (Specialized use cases)

**CrowdStrike**
- Owner: Publicly traded
- Concerns: Geopolitical actor in cybersecurity space, nation-state attribution business
- Use case: Cyber threat context in investigations
- **Action needed:** Assess bias in attribution claims

**Plaid**
- Owner: Private (Visa acquisition blocked by DOJ)
- Concerns: Bank account aggregation, data access scope
- Use case: Financial verification
- **Action needed:** Assess if needed for any current workflow

**Chronograph**
- Owner: Unknown (investigate)
- Use case: PE/VC industry data
- **Action needed:** Assess if PE fund analysis needed

**Tavily**
- Owner: VC-backed startup
- Concerns: "AI-optimized" search claims, VC incentives
- Use case: Alternative search
- **Action needed:** Assess if Brave/standard search insufficient

---

## ASSESSED WITH CAVEATS

*Sources assessed through investigation protocol. Usable but with documented limitations and recommendations.*

### Yahoo Finance / yfinance

**Assessment Date:** December 2025

**What it is:**
- **yfinance** = Open-source Python library by Ran Aroussi (MIT license)
- **Yahoo Finance** = Data source, owned 90% by Apollo Global Management since Sept 2021

**Ownership Chain:**
```
yfinance (open-source) → Yahoo Finance APIs → Yahoo Inc. (Apollo 90%, Verizon 10%) → Apollo Global Management (PE)
```

**Assessment:**

*Positive factors:*
- Library itself is open-source, community-maintained, not Apollo-controlled
- Stock price data is public, cross-verifiable from multiple sources
- No evidence of data manipulation
- Suitable for its stated purpose (research/educational)

*Risk factors:*
- **Service degradation (HIGH)**: Historical data now requires Yahoo Finance premium subscription (2025 change); rate limiting increased early 2024
- **Technical reliability (HIGH)**: Unofficial scraping can break with any Yahoo site change; not intended for production use
- **Accuracy (MEDIUM)**: Documented issues for non-US markets, some price discrepancies vs Yahoo Finance website
- **PE ownership pattern**: Apollo's $52.7M SEC settlement for misleading investors; documented extraction patterns in healthcare sector suggest monetization pressure likely to continue

**Evidence Tier:** CREDIBLE (multiple independent sources, consistent patterns)

**Recommendation:**
1. Acceptable for research/educational use (original stated purpose)
2. Use as **optional enhancement**, not core dependency
3. Document limitations prominently in any distribution
4. For production/trading use: recommend Alpha Vantage (official NASDAQ vendor, 500 free calls/day) or Polygon.io

**Sources:**
- [Apollo Yahoo acquisition](https://www.apollo.com/insights-news/pressreleases/2021/09/apollo-funds-complete-acquisition-of-yahoo-161530593)
- [SEC enforcement action](https://www.sec.gov/newsroom/press-releases/2016-165)
- [yfinance GitHub issues](https://github.com/ranaroussi/yfinance/issues)
- [AFT Apollo healthcare report](https://www.aft.org/press-release/new-report-details-harm-caused-healthcare-industry-apollo-global-management)

---

## ASSESSED (No Issues Found)

*Sources that have been through Section 6.7 framework with no disqualifying issues identified. Still use with awareness of documented coverage limits.*

*(Currently empty - SEC EDGAR and others need proper protocol application before listing here)*

---

## GAP ENTITIES

Sources that would be valuable but lack convenient MCP integration.

| Source | Importance | Data Offered | Access Method |
|--------|------------|--------------|---------------|
| **OpenSanctions** | CRITICAL | Sanctions lists, PEPs, beneficial ownership | API (robust), web UI |
| **OpenCorporates** | HIGH | 200M+ companies, shell company tracing | API (limited free), web UI |
| **PACER / CourtListener** | HIGH | Federal court records, enforcement actions | PACER (paid), CourtListener (partial free) |
| **FEC Campaign Finance** | MEDIUM-HIGH | Political donations, revolving door indicators | API, web UI |
| **Lobbying Disclosures** | MEDIUM-HIGH | Lobbying registration, foreign agents | Senate/House databases, web UI |
| **Property Records** | MEDIUM | Asset tracing, real estate ownership | County-level, fragmented |
| **Import/Trade Data** | MEDIUM | Supply chain tracing, sanctions evasion | Customs databases vary by country |
| **State AG Registries** | MEDIUM | State-level charity registration, enforcement | State-by-state, no unified access |

**Note:** "No MCP" doesn't mean unusable—web search and direct web access can still retrieve data. MCP integration just makes it more efficient.

---

## DOMAIN-SPECIFIC

Specialized tools for niche domains. Investigate when domain becomes relevant.

| Tool | Domain | Status |
|------|--------|--------|
| **Enrichr** | Bioinformatics, gene analysis | Available - not assessed |
| **Synapse.org** | Scientific data repositories | Available - not assessed |
| **PopHIVE** | Public health data | Available - not assessed |
| **Crypto.com** | Cryptocurrency markets | Available - not assessed |

---

## Update Log

| Date | Source | Action | Rationale |
|------|--------|--------|-----------|
| 2025-12-28 | Yahoo Finance / yfinance | Moved to ASSESSED WITH CAVEATS | Full investigation: Apollo ownership verified, service degradation documented, acceptable for research use with limitations |
| 2025-12-05 | Candid | Added to BANNED | Governance capture, extractive model |
| 2025-12-05 | Multiple | Added to PENDING | Initial triage |
| 2025-12-05 | Multiple | Added to GAP ENTITIES | Coverage mapping |
| 2025-12-05 | Multiple | Added to DOMAIN-SPECIFIC | Available but not relevant |

---

## Next Actions

**Immediate (before next investigation relying on these):**
1. ~~Yahoo Finance / yfinance - full assessment~~ ✅ COMPLETED 2025-12-28
2. Tomba - full assessment (HIGH - available now)

**Near-term:**
3. ProPublica Nonprofit Explorer - confirm trustworthy assessment
4. OpenSanctions - verify methodology, assess lag times

**When needed:**
5. Domain-specific tools as relevant domains arise

---

## EVALUATED - NOT RELEVANT

Sources assessed and determined not relevant to our investigation work.

### Benevity

**Assessment Date:** December 2025

**What it is:** B2B corporate social responsibility (CSR) software - the plumbing that routes corporate charitable donations. Platform helps Fortune 1000 companies manage employee giving programs, volunteering, grant-making, and matching gifts.

**Ownership:** Hg Capital (UK-based PE firm, $75B AUM) acquired majority stake December 2020. Hg is partner-owned, spun out of Merrill Lynch in 2000, focused on software buyouts.

**Why not relevant:** Benevity is infrastructure for corporate philanthropy, not a nonprofit database or intelligence source. They're the pipes, not the intelligence. Unless investigating corporate CSR program flows specifically, orthogonal to financial/nonprofit power structure research.

**MCP Status:** ✅ Available in Claude AI environment

**Use case:** Only relevant if specifically investigating corporate giving programs at Fortune 1000 companies (Nike, Google, Apple, Microsoft are clients). Not a Candid alternative.
