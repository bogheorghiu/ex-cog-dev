#!/usr/bin/env python3
"""Portfolio login helper — run outside MCP (MCP stdin is the JSON-RPC channel).

Usage:
  python3 portfolio-snap.py --login --broker tradeville
  python3 portfolio-snap.py --login --broker ibkr

Opens a visible browser window for manual login, then saves session state to
~/.claude/local/portfolio/auth/{broker}-state.json (or $PORTFOLIO_DATA_DIR/auth/).

This script must run in a real terminal, not inside the MCP server.
"""

import argparse
import os
import sys
from pathlib import Path

DATA_DIR = Path(os.environ.get(
    "PORTFOLIO_DATA_DIR",
    str(Path.home() / ".claude" / "local" / "portfolio"),
))
AUTH_DIR = DATA_DIR / "auth"

BROKER_URLS = {
    "tradeville": "https://portal.tradeville.ro",
    "ibkr": "https://localhost:5000",
}


def login(broker: str) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    AUTH_DIR.mkdir(parents=True, exist_ok=True)
    state_file = AUTH_DIR / f"{broker}-state.json"
    login_url = BROKER_URLS[broker]

    print(f"Opening {broker} login page: {login_url}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=(broker == "ibkr"),  # IBKR gateway uses self-signed cert on localhost
        )
        page = context.new_page()
        page.goto(login_url)

        input("Log in manually in the browser window, then press Enter here...")

        context.storage_state(path=str(state_file))
        browser.close()

    print(f"Session saved: {state_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Portfolio broker login helper")
    parser.add_argument("--login", action="store_true", required=True, help="Perform login")
    parser.add_argument("--broker", required=True, choices=list(BROKER_URLS), help="Broker name")
    args = parser.parse_args()

    if args.login:
        login(args.broker)


if __name__ == "__main__":
    main()
