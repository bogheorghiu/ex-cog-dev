#!/bin/bash
# Fail-open wrapper for firing_filter.py. The engine needs python3; a host
# without it must lose the filter silently (passthrough) rather than error on
# every tool call — a safety layer that breaks the session gets the plugin
# uninstalled, which is total coverage loss. Same posture as the family's
# jq-fallback in count-skill-firings.sh.
set -u
if ! command -v python3 >/dev/null 2>&1; then
    printf '{}'
    exit 0
fi
exec python3 "$(dirname "$0")/firing_filter.py" "$@"
