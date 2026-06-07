#!/usr/bin/env python3
"""Authentication capture for Substack - interactive browser login.

This script launches a visible browser window for the user to log in manually.
After successful login, the browser state (cookies, localStorage) is saved
to a file for reuse in headless scraping sessions.

No password is stored — only the session state. That state contains live
session cookies (credential-equivalent), so it is saved with owner-only (0600)
permissions and belongs in a gitignored directory.
"""
import argparse
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from scripts.utils import ensure_dir


def capture_auth(substack_url: str, state_path: str, timeout_ms: int = 300000) -> bool:
    """Launch browser for manual login, save authenticated state.

    Args:
        substack_url: Base URL of the Substack (e.g., https://example.substack.com)
        state_path: Path to save browser state JSON
        timeout_ms: Maximum time to wait for login (default: 5 minutes)

    Returns:
        True if auth state was saved successfully.
    """
    # Ensure output directory exists
    ensure_dir(str(Path(state_path).parent))

    print(f"🌐 Opening browser for login to: {substack_url}")
    print("📝 Please log in manually. The browser will close after successful login.")
    print(f"⏱️  Timeout: {timeout_ms // 1000} seconds")
    print()

    with sync_playwright() as p:
        # Launch VISIBLE browser for manual login
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to sign-in page
        page.goto(f"{substack_url.rstrip('/')}/sign-in")

        # Wait for user to complete login
        # Substack redirects to home or dashboard after successful login
        try:
            # Wait for navigation away from sign-in page
            page.wait_for_url(
                lambda url: "/sign-in" not in url and substack_url.rstrip("/") in url,
                timeout=timeout_ms,
            )
            print("✅ Login detected!")

            # Small delay to ensure all cookies are set
            page.wait_for_timeout(2000)

            # Save the authenticated state
            context.storage_state(path=state_path)
            # The state file holds live session cookies (credential-equivalent),
            # so restrict it to owner read/write — don't leave it world-readable
            # on a shared machine. Best-effort: skip silently where chmod is a
            # no-op (e.g. some Windows filesystems).
            try:
                os.chmod(state_path, 0o600)
            except OSError:
                pass
            print(f"💾 Auth state saved to: {state_path}")

            browser.close()
            return True

        except Exception as e:
            print(f"❌ Login failed or timed out: {e}")
            browser.close()
            return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Capture authentication state for Substack scraping"
    )
    parser.add_argument(
        "url",
        help="Substack URL (e.g., https://example.substack.com)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="auth/browser_state.json",
        help="Path to save auth state (default: auth/browser_state.json)",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)",
    )

    args = parser.parse_args()

    success = capture_auth(
        substack_url=args.url,
        state_path=args.output,
        timeout_ms=args.timeout * 1000,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
