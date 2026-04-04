"""Transparency MCP Server — GovTrack, World Bank, ProPublica Nonprofit Explorer.

Three public-interest data sources for power-structure analysis (STONK).
All APIs are free, no keys required.

Data sources:
  - GovTrack: US Congress members, bills, voting records
  - World Bank: Development indicators by country
  - ProPublica: Nonprofit organizations and 990 filings
"""

from __future__ import annotations

import httpx
from mcp.server.fastmcp import FastMCP

# --- Config ---

GOVTRACK_BASE = "https://www.govtrack.us/api/v2"
WORLDBANK_BASE = "https://api.worldbank.org/v2"
PROPUBLICA_BASE = "https://projects.propublica.org/nonprofits/api/v2"

TIMEOUT = 15.0

# --- MCP Server ---

mcp = FastMCP(
    "transparency-mcp",
    instructions=(
        "Public transparency data: US Congress (GovTrack), "
        "World Bank development indicators, ProPublica nonprofit filings. "
        "All free APIs, no keys needed."
    ),
)

# --- HTTP Helpers ---


async def _govtrack_get(endpoint: str, params: dict | None = None) -> dict:
    """GET from GovTrack API. Returns parsed JSON."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{GOVTRACK_BASE}/{endpoint}", params=params or {})
        resp.raise_for_status()
        return resp.json()


async def _worldbank_get(path: str, params: dict | None = None) -> list:
    """GET from World Bank API. Returns parsed JSON (always a list: [metadata, data])."""
    base_params = {"format": "json", "per_page": "100"}
    if params:
        base_params.update(params)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{WORLDBANK_BASE}/{path}", params=base_params)
        resp.raise_for_status()
        return resp.json()


async def _propublica_get(path: str, params: dict | None = None) -> dict:
    """GET from ProPublica Nonprofit Explorer API. Returns parsed JSON."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{PROPUBLICA_BASE}/{path}", params=params or {})
        resp.raise_for_status()
        return resp.json()


def _fmt_number(value, prefix: str = "") -> str:
    """Format a number with magnitude suffix (e.g., 1.2T, 50M).

    Args:
        value: Numeric value to format.
        prefix: Optional prefix like '$' for monetary values.
    """
    if value is None:
        return "N/A"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(v) >= 1e12:
        return f"{prefix}{v / 1e12:.1f}T"
    if abs(v) >= 1e9:
        return f"{prefix}{v / 1e9:.1f}B"
    if abs(v) >= 1e6:
        return f"{prefix}{v / 1e6:.1f}M"
    if abs(v) >= 1e3:
        return f"{prefix}{v / 1e3:.0f}K"
    return f"{prefix}{v:,.2f}"


def _fmt_money(value) -> str:
    """Format a number as human-readable money (e.g., $1.2B, $50M)."""
    return _fmt_number(value, prefix="$")


# ==================== GovTrack Tools ====================


@mcp.tool()
async def govtrack_members(state: str = "", party: str = "", limit: int = 20) -> str:
    """Get current US Congress members from GovTrack.

    Args:
        state: Two-letter state code (e.g., CA, TX). Empty for all states.
        party: Filter by party (Democrat, Republican, Independent). Empty for all.
        limit: Max results (default 20, max 100).
    """
    params = {
        "current": "true",
        "limit": str(max(1, min(limit, 100))),
        "order_by": "person__lastname",
    }
    if state:
        params["state"] = state.upper()
    if party:
        params["party"] = party

    try:
        data = await _govtrack_get("role", params=params)
    except httpx.HTTPError as e:
        return f"Error contacting GovTrack API: {e}"

    members = data.get("objects", [])
    total = data.get("meta", {}).get("total_count", 0)

    if not members:
        return f"No members found (filters: state={state or 'all'}, party={party or 'all'})."

    lines = [f"US Congress Members ({len(members)} of {total} shown):", ""]
    for m in members:
        p = m.get("person", {})
        name = f"{p.get('firstname', '')} {p.get('lastname', '')}"
        role = m.get("role_type", "").replace("_", " ").title()
        st = m.get("state", "")
        pty = m.get("party", "")
        district = m.get("district")
        dist_str = f"-{district}" if district else ""
        lines.append(f"  {name} ({pty}) — {role}, {st}{dist_str}")

    return "\n".join(lines)


@mcp.tool()
async def govtrack_bills(query: str = "", congress: int | None = None, limit: int = 20) -> str:
    """Search US Congress bills on GovTrack.

    Args:
        query: Search term (e.g., "infrastructure", "healthcare"). Empty for recent bills.
        congress: Congress number (e.g., 118). None for current.
        limit: Max results (default 20, max 100).
    """
    params = {
        "limit": str(max(1, min(limit, 100))),
        "order_by": "-introduced_date",
    }
    if query:
        params["q"] = query
    if congress is not None:
        params["congress"] = str(congress)

    try:
        data = await _govtrack_get("bill", params=params)
    except httpx.HTTPError as e:
        return f"Error contacting GovTrack API: {e}"

    bills = data.get("objects", [])
    total = data.get("meta", {}).get("total_count", 0)

    if not bills:
        return f"No bills found for query '{query}'."

    lines = [f"Bills ({len(bills)} of {total} shown):", ""]
    for b in bills:
        title = b.get("title", "Untitled")
        if len(title) > 120:
            title = title[:117] + "..."
        bill_type = b.get("bill_type", "").replace("_", " ")
        number = b.get("number", "")
        cong = b.get("congress", "")
        status = b.get("current_status", "unknown").replace("_", " ")
        intro = b.get("introduced_date", "")
        lines.append(f"  [{bill_type} {number}, {cong}th Congress] {title}")
        lines.append(f"    Status: {status} | Introduced: {intro}")

    return "\n".join(lines)


@mcp.tool()
async def govtrack_votes(congress: int | None = None, chamber: str = "", limit: int = 20) -> str:
    """Get recent US Congress votes from GovTrack.

    Args:
        congress: Congress number (e.g., 118). None for current.
        chamber: 'house' or 'senate'. Empty for both.
        limit: Max results (default 20, max 100).
    """
    params = {
        "limit": str(max(1, min(limit, 100))),
        "order_by": "-created",
    }
    if congress is not None:
        params["congress"] = str(congress)
    if chamber:
        params["chamber"] = chamber.lower()

    try:
        data = await _govtrack_get("vote", params=params)
    except httpx.HTTPError as e:
        return f"Error contacting GovTrack API: {e}"

    votes = data.get("objects", [])
    total = data.get("meta", {}).get("total_count", 0)

    if not votes:
        return "No votes found."

    lines = [f"Congress Votes ({len(votes)} of {total} shown):", ""]
    for v in votes:
        question = v.get("question", "Unknown")
        if len(question) > 100:
            question = question[:97] + "..."
        result = v.get("result", "unknown")
        yea = v.get("total_plus", 0)
        nay = v.get("total_minus", 0)
        chamber_name = v.get("chamber", "").title()
        created = v.get("created", "")[:10]
        lines.append(f"  [{chamber_name} {created}] {question}")
        lines.append(f"    Result: {result} (Yea: {yea}, Nay: {nay})")

    return "\n".join(lines)


# ==================== World Bank Tools ====================


@mcp.tool()
async def worldbank_indicator(
    country: str, indicator: str, date_range: str = ""
) -> str:
    """Get World Bank indicator data for a country.

    Args:
        country: ISO 3166-1 alpha-2 country code (e.g., US, RO, CN) or 'all'.
        indicator: Indicator code (e.g., NY.GDP.MKTP.CD for GDP). Use worldbank_search to find codes.
        date_range: Optional year range (e.g., '2020:2023'). Empty for most recent data.
    """
    path = f"country/{country.upper()}/indicator/{indicator}"
    params = {}
    if date_range:
        params["date"] = date_range

    try:
        data = await _worldbank_get(path, params=params)
    except httpx.HTTPError as e:
        return f"Error contacting World Bank API: {e}"

    if not isinstance(data, list) or len(data) < 2 or data[1] is None:
        return f"No data found for {country}/{indicator}."

    meta = data[0]
    records = data[1]

    if not records:
        return f"No data found for {country}/{indicator}."

    ind_name = records[0].get("indicator", {}).get("value", indicator)
    country_name = records[0].get("country", {}).get("value", country)

    # Detect if indicator is monetary (contains currency keywords)
    ind_lower = ind_name.lower()
    is_monetary = any(kw in ind_lower for kw in ["us$", "usd", "current $", "constant $", "lcu", "ppp"])
    fmt = _fmt_money if is_monetary else _fmt_number

    lines = [f"{ind_name} — {country_name}", ""]
    for r in records:
        year = r.get("date", "?")
        val = r.get("value")
        if val is not None:
            lines.append(f"  {year}: {fmt(val)}")
        else:
            lines.append(f"  {year}: N/A")

    total = meta.get("total", len(records))
    if total > len(records):
        lines.append(f"\n  (Showing {len(records)} of {total} records)")

    return "\n".join(lines)


@mcp.tool()
async def worldbank_search(query: str, limit: int = 20) -> str:
    """Search World Bank indicators by keyword (server-side search).

    Use this to find indicator codes for worldbank_indicator.

    Args:
        query: Search term (e.g., 'GDP', 'inflation', 'CO2 emissions').
        limit: Max results to display (default 20, max 100).
    """
    try:
        data = await _worldbank_get(
            "indicator",
            params={"q": query, "per_page": str(max(1, min(limit, 100)))},
        )
    except httpx.HTTPError as e:
        return f"Error contacting World Bank API: {e}"

    if not isinstance(data, list) or len(data) < 2 or data[1] is None:
        return f"No indicators found for '{query}'."

    matches = data[1]
    total = data[0].get("total", len(matches)) if isinstance(data[0], dict) else len(matches)

    if not matches:
        return f"No indicators found matching '{query}'. Try broader terms."

    lines = [f"World Bank Indicators matching '{query}' ({min(len(matches), limit)} of {total} shown):", ""]
    for ind in matches[:limit]:
        code = ind.get("id", "?")
        name = ind.get("name", "Unknown")
        note = ind.get("sourceNote", "")
        if len(note) > 150:
            note = note[:147] + "..."
        lines.append(f"  {code}: {name}")
        if note:
            lines.append(f"    {note}")

    return "\n".join(lines)


# ==================== ProPublica Nonprofit Tools ====================


@mcp.tool()
async def nonprofit_search(query: str, state: str = "", limit: int = 20) -> str:
    """Search nonprofit organizations via ProPublica Nonprofit Explorer.

    Args:
        query: Organization name to search.
        state: Two-letter state code filter (e.g., NY, CA). Empty for all.
        limit: Max results (default 20).
    """
    params = {"q": query}
    if state:
        params["state[id]"] = state.upper()

    try:
        data = await _propublica_get("search.json", params=params)
    except httpx.HTTPError as e:
        return f"Error contacting ProPublica API: {e}"

    orgs = data.get("organizations", [])
    total = data.get("total_results", 0)

    if not orgs:
        return f"No nonprofits found for '{query}'."

    lines = [f"Nonprofit Organizations ({len(orgs[:limit])} of {total} shown):", ""]
    for org in orgs[:limit]:
        name = org.get("name", "Unknown")
        ein = org.get("ein", "?")
        city = org.get("city", "")
        st = org.get("state", "")
        revenue = _fmt_money(org.get("total_revenue"))
        assets = _fmt_money(org.get("total_assets"))
        lines.append(f"  {name} (EIN: {ein})")
        lines.append(f"    {city}, {st} | Revenue: {revenue} | Assets: {assets}")

    return "\n".join(lines)


@mcp.tool()
async def nonprofit_details(ein: str) -> str:
    """Get detailed nonprofit organization info by EIN, including 990 filings.

    Args:
        ein: Employer Identification Number (9 digits, e.g., '131760110').
    """
    ein_clean = ein.replace("-", "")

    try:
        data = await _propublica_get(f"organizations/{ein_clean}.json")
    except httpx.HTTPStatusError as e:
        return f"Error: Organization with EIN {ein} not found (HTTP {e.response.status_code})."
    except httpx.HTTPError as e:
        return f"Error contacting ProPublica API: {e}"

    org = data.get("organization", {})
    filings = data.get("filings_with_data", [])

    name = org.get("name", "Unknown")
    city = org.get("city", "")
    state = org.get("state", "")
    ntee = org.get("ntee_code", "?")
    ruling = org.get("ruling_date", "")
    income = _fmt_money(org.get("income_amount"))
    assets = _fmt_money(org.get("asset_amount"))

    lines = [
        f"{name} (EIN: {ein_clean})",
        f"  Location: {city}, {state}",
        f"  NTEE Code: {ntee}",
        f"  Ruling Date: {ruling}",
        f"  Latest Revenue: {income}",
        f"  Latest Assets: {assets}",
    ]

    if filings:
        lines.append(f"\n  Recent 990 Filings ({len(filings)}):")
        for f_data in filings[:5]:
            year = f_data.get("tax_prd_yr", "?")
            rev = _fmt_money(f_data.get("totrevenue"))
            exp = _fmt_money(f_data.get("totfuncexpns"))
            assets_end = _fmt_money(f_data.get("totassetsend"))
            liab = _fmt_money(f_data.get("totliabend"))
            lines.append(f"    {year}: Revenue {rev} | Expenses {exp} | Assets {assets_end} | Liabilities {liab}")

    return "\n".join(lines)


# ==================== Status Tool ====================


@mcp.tool()
async def transparency_status() -> str:
    """Check connectivity to all three data source APIs.

    Returns status for GovTrack, World Bank, and ProPublica.
    """
    results = {}

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # GovTrack
        try:
            resp = await client.get(f"{GOVTRACK_BASE}/role", params={"limit": "1"})
            resp.raise_for_status()
            results["GovTrack"] = "OK"
        except httpx.HTTPError as e:
            results["GovTrack"] = f"FAILED: {e}"

        # World Bank
        try:
            resp = await client.get(
                f"{WORLDBANK_BASE}/country/US/indicator/NY.GDP.MKTP.CD",
                params={"format": "json", "per_page": "1"},
            )
            resp.raise_for_status()
            results["World Bank"] = "OK"
        except httpx.HTTPError as e:
            results["World Bank"] = f"FAILED: {e}"

        # ProPublica
        try:
            resp = await client.get(
                f"{PROPUBLICA_BASE}/search.json",
                params={"q": "test"},
            )
            resp.raise_for_status()
            results["ProPublica"] = "OK"
        except httpx.HTTPError as e:
            results["ProPublica"] = f"FAILED: {e}"

    lines = ["Transparency MCP Status:", ""]
    for name, status in results.items():
        marker = "+" if status == "OK" else "-"
        lines.append(f"  [{marker}] {name}: {status}")

    all_ok = all(s == "OK" for s in results.values())
    lines.append(f"\nAll APIs {'operational' if all_ok else 'NOT all operational'}.")

    return "\n".join(lines)


# --- Entry point ---


def main_sync():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main_sync()
