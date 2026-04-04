"""
Ticker caching logic separated from validation concerns.
Single responsibility: manage cached ticker validation results.
"""

from datetime import datetime
from cache.manager import cache_manager


class TickerCache:
    """
    Handles caching of ticker validation results.
    Manages cache retrieval, storage, and suggestion logic.
    """
    
    def __init__(self):
        self.cache_manager = cache_manager
    
    def get_cached_result(self, symbol, calling_tool=None):
        """
        Retrieve cached ticker validation result.
        
        Args:
            symbol: Cleaned stock symbol
            calling_tool: Optional tool name for suggestion context
            
        Returns:
            dict or None: Cached validation result with suggestions, or None if not cached
        """
        cached_data = self.cache_manager.get_ticker(symbol)
        if not cached_data:
            return None
        
        # Build response from cached data
        if cached_data['valid']:
            suggestion = f"Found: {cached_data['company_name']} ({symbol})."
            
            # Add cache timestamp info
            cache_date = datetime.fromisoformat(cached_data['created_at']).strftime('%Y-%m-%d')
            suggestion += f" (Cached data from {cache_date})"
            
            # No get_stock_info suggestion for cached data (already seen)
            return {
                'valid': True,
                'symbol': symbol,
                'error': None,
                'suggestion': suggestion,
                'cached': True,
                'cache_timestamp': cached_data['created_at'],
                'company_name': cached_data['company_name'],
                'sector': cached_data['sector'],
                'industry': cached_data['industry']
            }
        else:
            # Cached failure
            return {
                'valid': False,
                'symbol': symbol,
                'error': cached_data['error_message'],
                'suggestion': None,
                'cached': True,
                'cache_timestamp': cached_data['created_at']
            }
    
    def store_validation_result(self, symbol, validation_result):
        """
        Store validation result in cache.
        
        Args:
            symbol: Cleaned stock symbol
            validation_result: Result dict from TickerValidator
        """
        if validation_result['valid']:
            self.cache_manager.store_ticker(
                symbol=symbol,
                valid=True,
                company_name=validation_result['company_name'],
                sector=validation_result['sector'],
                industry=validation_result['industry'],
                cache_type=validation_result['cache_type']
            )
        else:
            self.cache_manager.store_ticker(
                symbol=symbol,
                valid=False,
                error_message=validation_result['error'],
                cache_type=validation_result['cache_type']
            )
    
    def build_fresh_result(self, symbol, validation_result, calling_tool=None):
        """
        Build result dict for fresh validation (not from cache).
        Includes context-aware suggestions.
        
        Args:
            symbol: Cleaned stock symbol
            validation_result: Result dict from TickerValidator
            calling_tool: Optional tool name for suggestion context
            
        Returns:
            dict: Complete result with suggestions
        """
        if validation_result['valid']:
            # Context-specific suggestions (only for fresh validations, not cached)
            suggestion = f"Found: {validation_result['company_name']} ({symbol})."
            
            # Only suggest get_stock_info for analysis tools, not for basic tools or info itself
            analysis_tools = ['get_stock_analysis', 'get_technical_indicators', 'get_stock_history']
            if calling_tool in analysis_tools:
                suggestion += " Consider getting basic company info first with get_stock_info for comprehensive context."
            
            return {
                'valid': True,
                'symbol': symbol,
                'error': None,
                'suggestion': suggestion,
                'cached': False,
                'cache_timestamp': None,
                'company_name': validation_result['company_name'],
                'sector': validation_result['sector'],
                'industry': validation_result['industry']
            }
        else:
            # Fresh validation failure
            return {
                'valid': False,
                'symbol': symbol,
                'error': validation_result['error'],
                'suggestion': "Check your internet connection and try again",
                'cached': False,
                'cache_timestamp': None
            }
    
    def force_refresh(self, symbol):
        """
        Force removal of cached entry to trigger fresh validation.
        
        Args:
            symbol: Stock symbol to refresh
        """
        self.cache_manager.force_refresh(symbol)