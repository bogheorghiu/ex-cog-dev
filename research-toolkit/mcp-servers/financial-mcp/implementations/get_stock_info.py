"""
Get comprehensive stock information implementation.
Single responsibility: fetch detailed company/stock information.
"""

import yfinance as yf
import mcp.types as types
from .fetch_ticker import fetch_ticker


async def execute(arguments: dict) -> list[types.TextContent]:
    """
    Get comprehensive stock information for a given symbol.
    
    Args:
        arguments: Dict containing 'symbol' key
        
    Returns:
        List containing TextContent with company information
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
        # Use cached company data if available, otherwise fetch fresh
        company_name = 'N/A'
        sector = 'N/A'
        industry = 'N/A'
        cache_info = ""
        
        if validation['cached'] and validation.get('company_name'):
            # Use cached company information
            company_name = validation['company_name']
            sector = validation.get('sector', 'N/A')
            industry = validation.get('industry', 'N/A')
            cache_date = validation['cache_timestamp'][:10]  # Extract date part
            cache_info = f"\n\n[Company info cached from {cache_date}. Use force_fetch_ticker to refresh.]"
        else:
            # Fetch fresh company data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            company_name = info.get('longName', info.get('shortName', 'N/A'))
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
        
        # Always fetch fresh financial data (not cached)
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get dividend and split history
        dividends = ticker.dividends
        splits = ticker.splits
        market_cap = info.get('marketCap', 'N/A')
        pe_ratio = info.get('trailingPE', 'N/A')
        pb_ratio = info.get('priceToBook', 'N/A')
        dividend_yield = info.get('dividendYield', 'N/A')
        beta = info.get('beta', 'N/A')
        
        # Financial metrics
        revenue = info.get('totalRevenue', 'N/A')
        profit_margin = info.get('profitMargins', 'N/A')
        debt_to_equity = info.get('debtToEquity', 'N/A')
        
        # Price metrics
        current_price = info.get('currentPrice', 'N/A')
        day_high = info.get('dayHigh', 'N/A')
        day_low = info.get('dayLow', 'N/A')
        week_52_high = info.get('fiftyTwoWeekHigh', 'N/A')
        week_52_low = info.get('fiftyTwoWeekLow', 'N/A')
        
        # Volume
        avg_volume = info.get('averageVolume', 'N/A')
        volume = info.get('volume', 'N/A')
        
        # Format large numbers
        def format_large_number(num):
            if isinstance(num, (int, float)):
                if num >= 1_000_000_000_000:
                    return f"${num / 1_000_000_000_000:.2f}T"
                elif num >= 1_000_000_000:
                    return f"${num / 1_000_000_000:.2f}B"
                elif num >= 1_000_000:
                    return f"${num / 1_000_000:.2f}M"
                else:
                    return f"${num:,.0f}"
            return num
        
        def format_percentage(num):
            if isinstance(num, (int, float)):
                return f"{num * 100:.2f}%"
            return num
        
        def format_number(num):
            if isinstance(num, (int, float)):
                return f"{num:,.0f}"
            return num
        
        # Format values
        market_cap = format_large_number(market_cap)
        revenue = format_large_number(revenue)
        profit_margin = format_percentage(profit_margin)
        dividend_yield = format_percentage(dividend_yield)
        avg_volume = format_number(avg_volume)
        volume = format_number(volume)
        
        # Dividend history analysis
        dividend_info = "No dividend history"
        if not dividends.empty:
            recent_dividends = dividends.tail(12)  # Last 12 payments
            total_div_last_year = recent_dividends.sum()
            last_dividend = dividends.iloc[-1]
            last_div_date = dividends.index[-1].strftime('%Y-%m-%d')
            dividend_info = f"Last: ${last_dividend:.2f} on {last_div_date}, Annual: ${total_div_last_year:.2f}"
        
        # Split history analysis
        split_info = "No stock splits"
        if not splits.empty:
            recent_splits = splits.tail(5)  # Last 5 splits
            last_split = splits.iloc[-1]
            last_split_date = splits.index[-1].strftime('%Y-%m-%d')
            split_info = f"Last: {last_split}:1 on {last_split_date}"
        
        result = f"""Comprehensive Stock Information for {symbol}:

Company Details:
  Name: {company_name}
  Sector: {sector}
  Industry: {industry}

Financial Metrics:
  Market Cap: {market_cap}
  Revenue (TTM): {revenue}
  Profit Margin: {profit_margin}
  Debt/Equity: {debt_to_equity if debt_to_equity != 'N/A' else 'N/A'}

Valuation Ratios:
  P/E Ratio: {pe_ratio if pe_ratio != 'N/A' else 'N/A'}
  P/B Ratio: {pb_ratio if pb_ratio != 'N/A' else 'N/A'}
  Beta: {beta if beta != 'N/A' else 'N/A'}

Price Information:
  Current Price: ${current_price if current_price != 'N/A' else 'N/A'}
  Day Range: ${day_low} - ${day_high}
  52-Week Range: ${week_52_low} - ${week_52_high}

Volume:
  Current Volume: {volume}
  Average Volume: {avg_volume}

Dividend Information:
  Yield: {dividend_yield}
  History: {dividend_info}

Stock Splits:
  {split_info}{cache_info}"""
        
        return [types.TextContent(
            type="text",
            text=result
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error getting info for {symbol}: {str(e)}"
        )]