"""
Get historical stock data implementation.
Single responsibility: fetch historical price data for a stock symbol.
"""

import yfinance as yf
import mcp.types as types
from .fetch_ticker import fetch_ticker


async def execute(arguments: dict) -> list[types.TextContent]:
    """
    Get historical stock data for a given symbol.
    
    Args:
        arguments: Dict containing 'symbol', optional 'period', 'start_date', 'end_date' keys
        
    Returns:
        List containing TextContent with historical data
    """
    symbol = arguments.get("symbol", "")
    period = arguments.get("period", "1mo")
    start_date = arguments.get("start_date")
    end_date = arguments.get("end_date")
    
    # Validate ticker first
    validation = fetch_ticker(symbol, calling_tool='get_stock_history')
    if not validation['valid']:
        return [types.TextContent(
            type="text",
            text=f"Invalid ticker: {validation['error']}" + 
                 (f"\nSuggestion: {validation['suggestion']}" if validation['suggestion'] else "")
        )]
    
    symbol = validation['symbol']  # Use cleaned symbol
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Use date range if provided, otherwise use period
        if start_date and end_date:
            hist = ticker.history(start=start_date, end=end_date)
            date_info = f"from {start_date} to {end_date}"
        else:
            hist = ticker.history(period=period)
            date_info = f"for {period}"
        
        if hist.empty:
            return [types.TextContent(
                type="text",
                text=f"No historical data available for {symbol} {date_info}"
            )]
        
        # Return full dataset with summary statistics
        total_rows = len(hist)
        date_range = f"{hist.index[0].strftime('%Y-%m-%d')} to {hist.index[-1].strftime('%Y-%m-%d')}"
        
        result = f"Historical data for {symbol} {date_info}:\n"
        result += f"Total data points: {total_rows}\n"
        result += f"Date range: {date_range}\n\n"
        
        # Show first 5 and last 5 rows for long datasets
        if total_rows > 10:
            result += "First 5 data points:\n"
            result += hist.head(5).to_string() + "\n\n"
            result += "...\n\n"
            result += "Last 5 data points:\n"
            result += hist.tail(5).to_string()
        else:
            result += hist.to_string()
        
        # Add basic statistics
        result += f"\n\nSummary Statistics:\n"
        result += f"Price Range: ${hist['Low'].min():.2f} - ${hist['High'].max():.2f}\n"
        result += f"Average Volume: {hist['Volume'].mean():,.0f}\n"
        result += f"Total Dividends: ${hist['Dividends'].sum():.2f}\n"
        result += f"Stock Splits: {hist['Stock Splits'].sum()}\n"
        
        return [types.TextContent(
            type="text",
            text=result
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error getting history for {symbol}: {str(e)}"
        )]