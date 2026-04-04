"""
Cache configuration with environment variable support.
Global settings for TTL and cache behavior.
"""

import os
from pathlib import Path

# TTL Configuration (in days)
VALID_TICKER_TTL_DAYS = int(os.environ.get('CACHE_VALID_TTL_DAYS', 7))      # Company data expires after 7 days
FAILED_TICKER_TTL_DAYS = int(os.environ.get('CACHE_FAILED_TTL_DAYS', 30))   # Failed validations expire after 30 days

# Cache file location — default to ~/.cache/financial-mcp/ so it works
# whether running from source (PYTHONPATH), pip install, or uvx.
CACHE_DIR = os.environ.get('CACHE_DIR', str(Path.home() / ".cache" / "financial-mcp"))
CACHE_DB_PATH = os.path.join(CACHE_DIR, 'ticker_cache.db')
