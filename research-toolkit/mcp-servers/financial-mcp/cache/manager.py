"""
SQLite-based cache manager for ticker validation and company data.
Handles persistent storage with TTL expiration.

Lazy initialization: DB is created on first actual use, not at import time.
This avoids PermissionError in sandboxed environments.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .config import CACHE_DB_PATH, CACHE_DIR, VALID_TICKER_TTL_DAYS, FAILED_TICKER_TTL_DAYS


class CacheManager:
    """
    Persistent cache manager using SQLite.
    Handles ticker validation results and company data with TTL expiration.
    """

    def __init__(self):
        self._initialized = False

    def _lazy_init(self):
        """Initialize DB on first use, not at import time.

        Avoids PermissionError in sandboxed environments where
        ~/.cache/ may not be writable at import time.

        Not thread-safe by design — used in asyncio single-thread context.
        The race on _initialized is benign (os.makedirs exist_ok=True,
        CREATE TABLE IF NOT EXISTS) but callers should not use from threads.
        """
        if self._initialized:
            return
        os.makedirs(CACHE_DIR, exist_ok=True)
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ticker_cache (
                    symbol TEXT PRIMARY KEY,
                    valid BOOLEAN NOT NULL,
                    company_name TEXT,
                    sector TEXT,
                    industry TEXT,
                    error_message TEXT,
                    cache_type TEXT NOT NULL,  -- 'success', 'permanent_failure', 'temp_failure'
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    extra_data TEXT  -- JSON field for additional data
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON ticker_cache(expires_at)
            """)
            conn.commit()
        self._initialized = True

    def _calculate_expiry(self, cache_type: str) -> datetime:
        if cache_type == 'success':
            return datetime.now() + timedelta(days=VALID_TICKER_TTL_DAYS)
        elif cache_type in ['permanent_failure', 'temp_failure']:
            return datetime.now() + timedelta(days=FAILED_TICKER_TTL_DAYS)
        else:
            return datetime.now() + timedelta(days=1)

    def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Retrieve ticker data from cache if valid and not expired."""
        self._lazy_init()
        symbol = symbol.upper().strip()

        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM ticker_cache
                WHERE symbol = ? AND expires_at > ?
            """, (symbol, datetime.now().isoformat()))

            row = cursor.fetchone()
            if not row:
                return None

            result = {
                'symbol': row['symbol'],
                'valid': bool(row['valid']),
                'company_name': row['company_name'],
                'sector': row['sector'],
                'industry': row['industry'],
                'error_message': row['error_message'],
                'cache_type': row['cache_type'],
                'created_at': row['created_at'],
                'expires_at': row['expires_at']
            }

            if row['extra_data']:
                try:
                    result['extra_data'] = json.loads(row['extra_data'])
                except json.JSONDecodeError:
                    result['extra_data'] = {}

            return result

    def store_ticker(self, symbol: str, valid: bool, company_name: str = None,
                    sector: str = None, industry: str = None, error_message: str = None,
                    cache_type: str = 'success', extra_data: Dict = None):
        """Store ticker validation result in cache."""
        self._lazy_init()
        symbol = symbol.upper().strip()
        now = datetime.now()
        expires_at = self._calculate_expiry(cache_type)
        extra_json = json.dumps(extra_data) if extra_data else None

        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO ticker_cache
                (symbol, valid, company_name, sector, industry, error_message,
                 cache_type, created_at, expires_at, extra_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (symbol, valid, company_name, sector, industry, error_message,
                  cache_type, now.isoformat(), expires_at.isoformat(), extra_json))
            conn.commit()

    def cleanup_expired(self) -> int:
        """Remove expired cache entries. Returns count removed."""
        self._lazy_init()
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            cursor = conn.execute("""
                DELETE FROM ticker_cache WHERE expires_at <= ?
            """, (datetime.now().isoformat(),))
            removed_count = cursor.rowcount
            conn.commit()
            return removed_count

    def force_refresh(self, symbol: str):
        """Force removal of cached entry to trigger fresh validation."""
        self._lazy_init()
        symbol = symbol.upper().strip()
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute("DELETE FROM ticker_cache WHERE symbol = ?", (symbol,))
            conn.commit()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        self._lazy_init()
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            total = conn.execute("SELECT COUNT(*) FROM ticker_cache").fetchone()[0]
            valid = conn.execute("SELECT COUNT(*) FROM ticker_cache WHERE valid = 1").fetchone()[0]
            expired = conn.execute("""
                SELECT COUNT(*) FROM ticker_cache WHERE expires_at <= ?
            """, (datetime.now().isoformat(),)).fetchone()[0]
            types = conn.execute("""
                SELECT cache_type, COUNT(*) FROM ticker_cache GROUP BY cache_type
            """).fetchall()

            return {
                'total_entries': total,
                'valid_entries': valid,
                'invalid_entries': total - valid,
                'expired_entries': expired,
                'cache_types': dict(types),
                'cache_file': CACHE_DB_PATH
            }


# Global cache instance — lazy, no DB access until first method call
cache_manager = CacheManager()
