"""
Ticker validation logic separated from caching concerns.
Single responsibility: validate ticker format and existence via yfinance.
"""

import re
from datetime import datetime
import yfinance as yf


class TickerValidator:
    """
    Handles ticker symbol validation including format check and yfinance availability.
    Pure validation logic without caching dependencies.
    """
    
    @staticmethod
    def validate_format(symbol):
        """
        Validate stock symbol format.
        
        Args:
            symbol: Stock symbol string
            
        Returns:
            tuple: (is_valid, cleaned_symbol, error_message)
        """
        if not symbol:
            return False, None, "Symbol cannot be empty"
        
        symbol = symbol.strip().upper()
        
        # Basic symbol validation - alphanumeric and common separators
        if not re.match(r'^[A-Z0-9.\-]{1,10}$', symbol):
            return False, None, "Invalid symbol format (use letters, numbers, dots, hyphens only)"
        
        # Length check
        if len(symbol) > 10:
            return False, None, "Symbol too long (max 10 characters)"
        
        return True, symbol, None
    
    @staticmethod
    def validate_with_yfinance(symbol):
        """
        Validate ticker existence using yfinance API.
        
        Args:
            symbol: Cleaned stock symbol string
            
        Returns:
            dict: {
                'valid': bool,
                'company_name': str,
                'sector': str,
                'industry': str,
                'error': str (if invalid),
                'cache_type': str ('success', 'permanent_failure', 'temp_failure')
            }
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got meaningful data back
            if not info or len(info) <= 1 or 'symbol' not in info:
                return {
                    'valid': False,
                    'company_name': None,
                    'sector': None,
                    'industry': None,
                    'error': f"Ticker '{symbol}' not found or delisted",
                    'cache_type': 'permanent_failure'
                }
            
            # Ticker exists and has data
            company_name = info.get('longName') or info.get('shortName', 'Unknown Company')
            sector = info.get('sector')
            industry = info.get('industry')
            
            return {
                'valid': True,
                'company_name': company_name,
                'sector': sector,
                'industry': industry,
                'error': None,
                'cache_type': 'success'
            }
            
        except Exception as e:
            error_message = TickerValidator._handle_yfinance_errors(symbol, e)
            
            # Determine cache type based on error
            cache_type = 'temp_failure'  # Default to temporary
            error_lower = error_message.lower()
            if any(term in error_lower for term in ['no data found', 'delisted', 'invalid symbol']):
                cache_type = 'permanent_failure'
            
            return {
                'valid': False,
                'company_name': None,
                'sector': None,
                'industry': None,
                'error': error_message,
                'cache_type': cache_type
            }
    
    @staticmethod
    def _handle_yfinance_errors(symbol, error):
        """
        Convert yfinance errors to user-friendly messages.
        
        Args:
            symbol: Stock symbol
            error: Exception object
            
        Returns:
            str: User-friendly error message
        """
        error_str = str(error).lower()
        
        if 'no data found' in error_str or 'delisted' in error_str:
            return f"No data available for {symbol}. Symbol may be delisted or invalid."
        elif 'connection' in error_str or 'timeout' in error_str:
            return f"Network error retrieving data for {symbol}. Please try again."
        elif 'rate limit' in error_str or 'too many requests' in error_str:
            return f"Rate limit exceeded. Please wait before making more requests."
        else:
            return f"Error retrieving data for {symbol}: {str(error)}"