"""
Force fetch ticker implementation.
Single responsibility: validate stock ticker symbols with fresh data, bypassing cache.
"""

import mcp.types as types
from .fetch_ticker import fetch_ticker


async def execute(arguments: dict) -> list[types.TextContent]:
    """
    Force fresh validation of a ticker symbol, bypassing any cached data.
    
    Args:
        arguments: Dict containing 'symbol' key
        
    Returns:
        List containing TextContent with validation results and suggestions
    """
    symbol = arguments.get("symbol", "")
    
    if not symbol:
        return [types.TextContent(
            type="text",
            text="Error: No symbol provided. Please specify a ticker symbol to validate."
        )]
    
    # Force fresh validation (bypass cache)
    validation = fetch_ticker(symbol, force_validation=True)
    
    if validation['valid']:
        result = f"✓ Ticker '{validation['symbol']}' is valid and available.\n"
        result += f"Company: {validation['company_name']}"
        if validation['sector']:
            result += f"\nSector: {validation['sector']}"
        if validation['industry']:
            result += f"\nIndustry: {validation['industry']}"
        
        if validation['suggestion']:
            result += f"\n\nInfo: {validation['suggestion']}"
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    else:
        result = f"✗ Ticker validation failed: {validation['error']}"
        if validation['suggestion']:
            result += f"\n\nSuggestion: {validation['suggestion']}"
        
        return [types.TextContent(
            type="text",
            text=result
        )]