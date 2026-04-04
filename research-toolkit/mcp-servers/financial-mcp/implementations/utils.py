"""
Utility functions for data validation and error handling.
Basic validation functions without caching or yfinance dependencies.
"""

import re
from datetime import datetime


def validate_symbol(symbol):
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


def validate_date(date_string):
    """
    Validate date string format (YYYY-MM-DD).
    
    Args:
        date_string: Date string to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not date_string:
        return True, None  # Optional parameter
    
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format"


def validate_period(period):
    """
    Validate period parameter.
    
    Args:
        period: Period string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    
    if period not in valid_periods:
        return False, f"Invalid period. Must be one of: {', '.join(valid_periods)}"
    
    return True, None


