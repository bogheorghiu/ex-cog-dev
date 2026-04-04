"""
Ticker fetching orchestrator.
Single responsibility: coordinate validation and caching for ticker operations.
"""

from .validation.ticker_validator import TickerValidator
from .validation.ticker_cache import TickerCache


def fetch_ticker(symbol, calling_tool=None, force_validation=False):
    """
    Comprehensive ticker validation with persistent caching.
    Orchestrates validation and caching modules.
    
    Args:
        symbol: Stock symbol string
        calling_tool: Optional tool name for context-specific suggestions
        force_validation: If True, bypass cache and fetch fresh data
        
    Returns:
        dict: {
            'valid': bool,
            'symbol': str (cleaned symbol if valid),
            'error': str (error message if invalid),
            'suggestion': str (optional suggestion for user),
            'cached': bool (whether data came from cache),
            'cache_timestamp': str (when data was cached, if applicable)
        }
    """
    # First validate format
    is_valid, cleaned_symbol, format_error = TickerValidator.validate_format(symbol)
    if not is_valid:
        return {
            'valid': False,
            'symbol': None,
            'error': format_error,
            'suggestion': None,
            'cached': False,
            'cache_timestamp': None
        }
    
    # Initialize cache handler
    ticker_cache = TickerCache()
    
    # Check cache first (unless force_validation is True)
    if not force_validation:
        cached_result = ticker_cache.get_cached_result(cleaned_symbol, calling_tool)
        if cached_result:
            return cached_result
    
    # No cache hit or force validation - fetch from yfinance
    validation_result = TickerValidator.validate_with_yfinance(cleaned_symbol)
    
    # Store result in cache
    ticker_cache.store_validation_result(cleaned_symbol, validation_result)
    
    # Build and return final result
    return ticker_cache.build_fresh_result(cleaned_symbol, validation_result, calling_tool)