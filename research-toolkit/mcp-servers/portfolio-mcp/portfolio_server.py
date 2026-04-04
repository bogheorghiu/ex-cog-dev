"""Portfolio MCP Server — broker portfolio snapshots with permission-separated tools.

Tools per broker with distinct permission levels:
  - login:      Separate CLI script (not MCP — needs terminal stdin for manual auth).
  - discover:   Requires explicit approval. Opens browser for Claude to navigate.
  - navigate:   Playwright navigation tools (screenshot, click, goto, page text).
  - snapshot:   Auto-approvable. Loads saved URL, screenshots, saves, closes. No input.

Login/discover use a file-based sentinel pattern instead of input() because
MCP runs over stdio (input() would deadlock the JSON-RPC channel).

Data storage: ~/.claude/local/portfolio/ or configured via PORTFOLIO_DATA_DIR env var.
"""

import json
import os
import time
import urllib3
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # IBKR gateway uses self-signed cert

# --- Config ---

# Always use .claude/local/portfolio/ (gitignored, aligns with PII rules).
# _ensure_dirs() creates it if needed. Override with env var for testing.
DATA_DIR = Path(os.environ.get(
    "PORTFOLIO_DATA_DIR",
    str(Path.home() / ".claude" / "local" / "portfolio")
))
AUTH_DIR = DATA_DIR / "auth"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
CONFIG_DIR = DATA_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "urls.json"
SUBACCOUNTS_FILE = CONFIG_DIR / "sub-accounts.json"
VIEWPORT_W, VIEWPORT_H = 1920, 1080
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# --- Helpers ---

def _load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def _save_config(config: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def _get_broker_config(broker: str) -> dict:
    return _load_config().get(broker, {})


def _state_file(broker: str) -> Path:
    return AUTH_DIR / f"{broker}-state.json"


def _ensure_dirs():
    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _load_sub_accounts() -> list[dict]:
    """Load sub-accounts table. Each entry: {name, url, active, broker}."""
    if SUBACCOUNTS_FILE.exists():
        with open(SUBACCOUNTS_FILE) as f:
            return json.load(f)
    return []


def _save_sub_accounts(accounts: list[dict]):
    """Save sub-accounts table."""
    SUBACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SUBACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)


def _get_active_sub_account(broker: str) -> dict | None:
    """Get the active sub-account for a broker."""
    for acct in _load_sub_accounts():
        if acct.get("broker") == broker and acct.get("active"):
            return acct
    return None


# --- MCP Server ---

mcp = FastMCP(
    "portfolio-mcp",
    instructions="Broker portfolio snapshots (Tradeville, IBKR). Three permission levels: login (approval required), discover (approval required), snapshot (auto-approved).",
)


# ==================== TRADEVILLE ====================

@mcp.tool()
def tradeville_login() -> str:
    """Start Tradeville login — launches browser as a subprocess.

    REQUIRES EXPLICIT USER APPROVAL.
    This launches the portfolio-snap.py --login script as a separate process
    (not blocking the MCP server). The user logs in manually in the visible
    browser, then presses Enter in their terminal.

    Cannot run login inside MCP (stdin is the JSON-RPC channel).
    Returns instructions for the user to run the login script.
    """
    _ensure_dirs()
    state_file = _state_file("tradeville")

    # Login must happen outside MCP. Return instructions.
    snap_script = Path(__file__).parent / "scripts" / "portfolio-snap.py"
    return (
        "Tradeville login must be done in a terminal (MCP uses stdin for protocol).\n\n"
        "Run this in your terminal:\n"
        f"  python3 {snap_script} --login --broker tradeville\n\n"
        "The script launches a visible Chromium browser for manual login.\n"
        "After login, session state is saved automatically.\n"
        f"Auth file: {state_file}\n"
        f"Auth exists: {state_file.exists()}"
    )


# Module-level state for active browser sessions (between discover and finish_discover)
_active_sessions: dict = {}


@mcp.tool()
async def tradeville_discover() -> str:
    """Launch Tradeville with saved session for Claude to navigate.

    REQUIRES EXPLICIT USER APPROVAL — opens a visible browser.
    This tool returns immediately after launching the browser. It does NOT block.

    Workflow:
    1. This tool launches browser → returns status
    2. Claude calls tradeville_screenshot / tradeville_navigate / tradeville_page_text to explore
    3. Claude calls tradeville_save_sub_account for each sub-account found
    4. Claude calls tradeville_finish_discover to close browser + save session
    """
    _ensure_dirs()
    state_file = _state_file("tradeville")
    config = _get_broker_config("tradeville")
    portfolio_url = config.get("portfolio_url", "https://portal.tradeville.ro/portal/myaccount.htm")

    if not state_file.exists():
        return "ERROR: No saved auth. Run tradeville_login first."

    # Launch browser with async Playwright API (FastMCP runs inside asyncio).
    # The browser process stays open until tradeville_finish_discover closes it.
    try:
        # Outer try: catches import errors or async_playwright().start() failures.
        # Inner try below handles the full browser lifecycle with cleanup.
        from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

        # Quick session check: open browser, navigate, check for redirect, then keep it open
        p = await async_playwright().start()
        browser = None
        try:
            browser = await p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
                user_agent=USER_AGENT,
                storage_state=str(state_file),
                ignore_https_errors=False,
            )
            page = await context.new_page()

            try:
                await page.goto(portfolio_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)
            except PlaywrightTimeout:
                await browser.close()
                await p.stop()
                return "ERROR: Timeout loading portfolio. Session may have expired — run tradeville_login."

            if any(kw in page.url.lower() for kw in ["login", "signin", "auth"]):
                await browser.close()
                await p.stop()
                return f"ERROR: Session expired (redirected to {page.url}). Run tradeville_login."

            # Store browser/context/page refs for navigation tools + finish_discover
            _active_sessions["tradeville"] = {
                "playwright": p,
                "browser": browser,
                "context": context,
                "page": page,
                "state_file": str(state_file),
            }

            return (
                f"Browser open at {page.url}.\n"
                f"Use tradeville_screenshot, tradeville_navigate, tradeville_page_text to explore.\n"
                f"Find all sub-accounts (portfolios). For each one, call:\n"
                f"  tradeville_save_sub_account(name='...', url='...', set_active=True/False)\n"
                f"When done, call tradeville_finish_discover to close and save."
            )

        except Exception as e:
            # Clean up on unexpected errors to prevent resource leaks
            if browser:
                await browser.close()
            await p.stop()
            return f"ERROR: Unexpected error during discovery: {e}"

    except Exception as e:
        return f"ERROR launching browser: {e}"



@mcp.tool()
async def tradeville_finish_discover() -> str:
    """Close the discovery browser, save session state and screenshot.

    Call this after saving all sub-accounts via tradeville_save_sub_account.
    Closes the browser that tradeville_discover opened.
    """
    session = _active_sessions.pop("tradeville", None)
    if not session:
        return "No active discovery session. Run tradeville_discover first."

    page = session["page"]
    context = session["context"]
    browser = session["browser"]
    p = session["playwright"]

    try:
        # Save session state
        await context.storage_state(path=session["state_file"])

        # Screenshot
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        screenshot_path = SNAPSHOTS_DIR / f"tradeville-discovery-{timestamp}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        return f"Discovery complete. Session saved. Screenshot: {screenshot_path}"
    except Exception as e:
        return f"Error closing discovery browser: {e}"
    finally:
        await browser.close()
        await p.stop()


@mcp.tool()
async def tradeville_screenshot() -> str:
    """Take a screenshot of the current Tradeville page during discovery.

    Only works when a discover session is active (browser open via tradeville_discover).
    Saves screenshot to snapshots directory with timestamp. Returns file path.
    """
    session = _active_sessions.get("tradeville")
    if not session:
        return "ERROR: No active discover session. Run tradeville_discover first."

    page = session["page"]
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    screenshot_path = SNAPSHOTS_DIR / f"tradeville-nav-{timestamp}.png"

    try:
        await page.screenshot(path=str(screenshot_path), full_page=True)
        return f"Screenshot saved: {screenshot_path}"
    except Exception as e:
        return f"ERROR taking screenshot: {e}"


@mcp.tool()
async def tradeville_navigate(action: str, target: str = "") -> str:
    """Perform a navigation action on the current Tradeville page during discovery.

    Only works when a discover session is active (browser open via tradeville_discover).

    Args:
        action: One of "click", "snapshot", "goto"
            - click: clicks element matching target text
            - snapshot: returns accessibility tree (text, not image)
            - goto: navigates to target URL
        target: For click — text content to match. For goto — URL. Ignored for snapshot.
    """
    session = _active_sessions.get("tradeville")
    if not session:
        return "ERROR: No active discover session. Run tradeville_discover first."

    page = session["page"]

    if action == "snapshot":
        try:
            tree = await page.accessibility.snapshot()
            return json.dumps(tree, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"ERROR getting accessibility snapshot: {e}"

    elif action == "click":
        if not target:
            return "ERROR: click action requires a target (text to click)."
        try:
            await page.get_by_text(target).first.click()
            await page.wait_for_timeout(2000)
            return f"Clicked '{target}'. Page URL: {page.url}"
        except Exception as e:
            return f"ERROR clicking '{target}': {e}"

    elif action == "goto":
        if not target:
            return "ERROR: goto action requires a target URL."
        try:
            await page.goto(target, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)
            return f"Navigated to {page.url}"
        except Exception as e:
            return f"ERROR navigating to '{target}': {e}"

    else:
        return f"ERROR: Unknown action '{action}'. Use: click, snapshot, goto."


@mcp.tool()
async def tradeville_page_text() -> str:
    """Return the full text content of the current Tradeville page during discovery.

    Only works when a discover session is active (browser open via tradeville_discover).
    Extracts body.innerText for Claude to parse portfolio data.
    """
    session = _active_sessions.get("tradeville")
    if not session:
        return "ERROR: No active discover session. Run tradeville_discover first."

    page = session["page"]

    try:
        body = await page.query_selector("body")
        if not body:
            return f"Page has no text content (empty body). URL: {page.url}"
        text = await body.inner_text()
        if not text.strip():
            return f"Page has no text content (empty body). URL: {page.url}"
        return f"Page URL: {page.url}\n\n{text[:100000]}"
    except Exception as e:
        return f"ERROR extracting page text: {e}"


@mcp.tool()
def tradeville_save_sub_account(name: str, url: str, set_active: bool = False) -> str:
    """Save a discovered Tradeville sub-account (portfolio) to the accounts table.

    Called by Claude during discovery mode after navigating to each sub-account.
    Sub-accounts are different portfolio views under the same login (no separate passwords).
    The active sub-account is used by tradeville_snapshot for routine snapshots.

    Args:
        name: Sub-account name as shown in Tradeville (e.g., "PERSONAL", "JOINT")
        url: The exact URL for this sub-account's portfolio page
        set_active: If True, mark this as the active sub-account for routine snapshots
    """
    accounts = _load_sub_accounts()

    # Update existing or add new
    found = False
    for acct in accounts:
        if acct["broker"] == "tradeville" and acct["name"].upper() == name.upper():
            acct["url"] = url
            if set_active:
                acct["active"] = True
            found = True
        elif set_active and acct["broker"] == "tradeville":
            acct["active"] = False  # Deactivate others when setting new active

    if not found:
        # Deactivate others if setting active
        if set_active:
            for acct in accounts:
                if acct["broker"] == "tradeville":
                    acct["active"] = False
        accounts.append({
            "broker": "tradeville",
            "name": name,
            "url": url,
            "active": set_active,
            "discovered_at": datetime.now().isoformat(),
        })

    _save_sub_accounts(accounts)

    active_name = None
    for acct in accounts:
        if acct["broker"] == "tradeville" and acct.get("active"):
            active_name = acct["name"]

    tv_accounts = [a for a in accounts if a["broker"] == "tradeville"]
    table = "\n".join(f"  {'*' if a.get('active') else ' '} {a['name']}: {a['url']}" for a in tv_accounts)
    return f"Saved sub-account '{name}'. Active: {active_name or 'none'}\n\nSub-accounts:\n{table}"


@mcp.tool()
def tradeville_set_active_account(name: str) -> str:
    """Set which Tradeville sub-account to use for routine snapshots.

    Args:
        name: Sub-account name (e.g., "PERSONAL")
    """
    accounts = _load_sub_accounts()
    found = False
    for acct in accounts:
        if acct["broker"] == "tradeville":
            if acct["name"].upper() == name.upper():
                acct["active"] = True
                found = True
            else:
                acct["active"] = False

    if not found:
        return f"ERROR: Sub-account '{name}' not found. Run tradeville_discover first."

    _save_sub_accounts(accounts)
    return f"Active sub-account set to '{name}'."


@mcp.tool()
def tradeville_list_sub_accounts() -> str:
    """List all discovered Tradeville sub-accounts.

    AUTO-APPROVABLE — read-only.
    """
    accounts = [a for a in _load_sub_accounts() if a["broker"] == "tradeville"]
    if not accounts:
        return "No sub-accounts discovered yet. Run tradeville_discover."

    lines = ["Tradeville sub-accounts:", ""]
    for a in accounts:
        marker = "*" if a.get("active") else " "
        lines.append(f"  {marker} {a['name']}: {a['url']}")
        if a.get("discovered_at"):
            lines.append(f"    discovered: {a['discovered_at']}")
    lines.append("")
    lines.append("* = active (used by tradeville_snapshot)")
    return "\n".join(lines)


@mcp.tool()
async def tradeville_snapshot() -> str:
    """Take a routine Tradeville portfolio snapshot. No user interaction.

    AUTO-APPROVABLE — navigates to portfolio page, optionally clicks to switch
    sub-account if using click-based navigation, takes screenshot, extracts
    page text, saves to snapshots directory, closes browser.

    Returns snapshot file paths on success.
    Returns error message if session expired (code SESSION_EXPIRED),
    page unexpected (code PAGE_UNEXPECTED), or sub-account switch failed.
    """
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

    _ensure_dirs()
    state_file = _state_file("tradeville")
    active = _get_active_sub_account("tradeville")

    if not state_file.exists():
        return "ERROR: No saved auth. Run tradeville_login first."
    if not active:
        return "ERROR: No active sub-account. Run tradeville_discover, then tradeville_set_active_account."

    sub_account_url = active["url"]
    base_url = _get_broker_config("tradeville").get(
        "portfolio_url", "https://portal.tradeville.ro/portal/myaccount.htm"
    )

    async with async_playwright() as p:
        # headless=False: intentional — user should see what happens with their broker
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            user_agent=USER_AGENT,
            storage_state=str(state_file),
            # No ignore_https_errors — production broker over public internet
        )
        page = await context.new_page()

        try:
            # Navigate to base portfolio URL first
            await page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
        except PlaywrightTimeout:
            await browser.close()
            return "SESSION_EXPIRED: Timeout loading portfolio. Run tradeville_login."

        # Session check
        if any(kw in page.url.lower() for kw in ["login", "signin", "auth"]):
            await browser.close()
            return f"SESSION_EXPIRED: Redirected to {page.url}. Run tradeville_login."

        # If sub-account uses click: prefix, click to switch sub-account
        if sub_account_url.startswith("click:"):
            click_text = sub_account_url[len("click:"):]
            try:
                # Open the sub-account dropdown and click the target.
                # Tradeville uses JS function schimbaSubcont() with div[gi="nume"]
                # elements inside a dropdown. The dropdown trigger is the visible
                # account-name div; sub-account items are hidden until opened.
                # Strategy: use JS to find and click the right sub-account div
                # directly, bypassing the dropdown visibility issue.
                switched = await page.evaluate(f"""() => {{
                    // Find all sub-account divs with the switch handler
                    const divs = document.querySelectorAll('div[onclick*="schimbaSubcont"]');
                    for (const div of divs) {{
                        if (div.textContent.trim() === {json.dumps(click_text)}) {{
                            div.click();
                            return true;
                        }}
                    }}
                    // Fallback: try partial match
                    for (const div of divs) {{
                        if (div.textContent.trim().includes({json.dumps(click_text.split('"')[1] if '"' in click_text else click_text)})) {{
                            div.click();
                            return true;
                        }}
                    }}
                    return false;
                }}""")
                if switched:
                    await page.wait_for_timeout(3000)
                else:
                    await browser.close()
                    return f"ERROR: Could not find sub-account '{click_text}'. Run tradeville_discover."
            except Exception as e:
                await browser.close()
                return f"ERROR clicking sub-account: {e}. Run tradeville_discover."
        else:
            # Regular URL — navigate directly
            try:
                await page.goto(sub_account_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(5000)
            except PlaywrightTimeout:
                await browser.close()
                return "SESSION_EXPIRED: Timeout loading sub-account page."

            # Verify we landed on the expected page
            if page.url.rstrip("/") != sub_account_url.rstrip("/"):
                await browser.close()
                return f"PAGE_UNEXPECTED: Landed on {page.url} instead of {sub_account_url}. Run tradeville_discover."

        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")

        # Screenshot
        screenshot_path = SNAPSHOTS_DIR / f"tradeville-{timestamp}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        # Extract page text
        body_el = await page.query_selector("body")
        body_text = await body_el.inner_text() if body_el else ""
        json_path = None
        if body_text and len(body_text) > 50:
            data = {
                "broker": "tradeville",
                "timestamp": datetime.now().isoformat(),
                "url": page.url,
                "raw_text": body_text[:100000],
            }
            json_path = SNAPSHOTS_DIR / f"tradeville-{timestamp}.json"
            with open(json_path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        # Refresh session
        await context.storage_state(path=str(state_file))
        await browser.close()

    result = f"Snapshot saved:\n  Screenshot: {screenshot_path}"
    if json_path:
        result += f"\n  Data: {json_path}"
    return result


# ==================== IBKR ====================

@mcp.tool()
def ibkr_login() -> str:
    """Instructions for IBKR Client Portal login.

    IBKR login must be done in a terminal (MCP uses stdin for protocol).
    Returns instructions for the user.
    """
    _ensure_dirs()
    state_file = _state_file("ibkr")
    snap_script = Path(__file__).parent / "scripts" / "portfolio-snap.py"
    return (
        "IBKR login must be done in a terminal (MCP uses stdin for protocol).\n\n"
        "Run this in your terminal:\n"
        f"  python3 {snap_script} --login --broker ibkr\n\n"
        "The IBKR Client Portal Gateway must be running at localhost:5000.\n"
        f"Auth file: {state_file}\n"
        f"Auth exists: {state_file.exists()}"
    )


@mcp.tool()
def ibkr_snapshot() -> str:
    """Fetch IBKR portfolio data via Client Portal REST API. No browser needed.

    AUTO-APPROVABLE — calls the locally-running IBKR Gateway API.
    Returns positions, account summary, and NAV.
    Gateway must be running and authenticated.
    """
    import requests

    _ensure_dirs()
    config = _get_broker_config("ibkr")
    gateway_url = config.get("gateway_url", "https://localhost:5000")
    api_prefix = "/v1/api"

    def api_get(endpoint):
        url = f"{gateway_url}{api_prefix}{endpoint}"
        try:
            resp = requests.get(url, verify=False, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.ConnectionError:
            return None
        except Exception as e:
            return {"error": str(e)}

    # Check auth
    auth = api_get("/iserver/auth/status")
    if auth is None:
        return f"ERROR: Cannot connect to IBKR Gateway at {gateway_url}. Is it running?"
    if not auth.get("authenticated"):
        return "SESSION_EXPIRED: IBKR Gateway not authenticated. Run ibkr_login."

    # Get accounts
    accounts = api_get("/portfolio/accounts")
    if not accounts or not isinstance(accounts, list):
        return f"ERROR: Could not fetch accounts. Response: {accounts}"

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    all_data = {"broker": "ibkr", "timestamp": datetime.now().isoformat(), "accounts": []}

    for acct in accounts:
        acct_id = acct.get("id", acct.get("accountId", "unknown"))
        positions = api_get(f"/portfolio/{acct_id}/positions/0") or []
        summary = api_get(f"/portfolio/{acct_id}/summary") or {}

        all_data["accounts"].append({
            "account_id": acct_id,
            "account_info": acct,
            "positions": positions,
            "summary": summary,
        })

    # Save
    json_path = SNAPSHOTS_DIR / f"ibkr-{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    pos_count = sum(len(a["positions"]) for a in all_data["accounts"])
    return f"IBKR snapshot saved: {json_path} ({len(all_data['accounts'])} accounts, {pos_count} positions)"


# ==================== Utility ====================

@mcp.tool()
def portfolio_status() -> str:
    """Check portfolio system status — auth state, config, recent snapshots.

    AUTO-APPROVABLE — read-only status check.
    """
    _ensure_dirs()
    config = _load_config()
    lines = ["Portfolio Status:", ""]

    for broker in ["tradeville", "ibkr"]:
        state = _state_file(broker)
        has_auth = state.exists()

        lines.append(f"  {broker}:")
        lines.append(f"    Auth: {'saved' if has_auth else 'MISSING — run login'}")

        # Show sub-accounts for this broker
        broker_accounts = [a for a in _load_sub_accounts() if a["broker"] == broker]
        if broker_accounts:
            lines.append(f"    Sub-accounts ({len(broker_accounts)}):")
            for a in broker_accounts:
                marker = "*" if a.get("active") else " "
                lines.append(f"      {marker} {a['name']}: {a['url']}")
        elif broker == "tradeville":
            lines.append(f"    Sub-accounts: none discovered — run discover")
        lines.append("")

    # Recent snapshots
    snapshots = sorted(SNAPSHOTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    if snapshots:
        lines.append("  Recent snapshots:")
        for s in snapshots:
            age_h = (time.time() - s.stat().st_mtime) / 3600
            lines.append(f"    {s.name} ({age_h:.1f}h ago)")
    else:
        lines.append("  No snapshots yet.")

    return "\n".join(lines)


# --- Entry point ---

def main_sync():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main_sync()
