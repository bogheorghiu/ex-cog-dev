"""
Get current stock price implementation.
Single responsibility: fetch current price for a stock symbol.
"""

import yfinance as yf
import mcp.types as types
from .fetch_ticker import fetch_ticker


async def execute(arguments: dict) -> list[types.TextContent]:
    """
    Get current stock price for a given symbol.
    
    Args:
        arguments: Dict containing 'symbol' key
        
    Returns:
        List containing TextContent with price information
    """
    symbol = arguments.get("symbol", "")
    
    # Validate ticker first
    validation = fetch_ticker(symbol)
    if not validation['valid']:
        return [types.TextContent(
            type="text",
            text=f"Invalid ticker: {validation['error']}" + 
                 (f"\nSuggestion: {validation['suggestion']}" if validation['suggestion'] else "")
        )]
    
    symbol = validation['symbol']  # Use cleaned symbol
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Try fast_info first (faster), fallback to history method
        try:
            price = ticker.fast_info['lastPrice']
        except:
            # Fallback: get most recent closing price from history
            hist = ticker.history(period="1d")
            if hist.empty:
                return [types.TextContent(
                    type="text",
                    text=f"No price data available for {symbol}"
                )]
            price = hist["Close"].iloc[-1]
        
        return [types.TextContent(
            type="text",
            text=f"Current price for {symbol}: ${price:.2f}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error getting price for {symbol}: {str(e)}"
        )]