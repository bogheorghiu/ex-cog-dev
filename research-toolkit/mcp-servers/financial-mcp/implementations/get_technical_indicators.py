"""
Get technical indicators implementation.
Single responsibility: calculate and return technical analysis indicators.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import mcp.types as types
from .fetch_ticker import fetch_ticker


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_moving_averages(prices):
    """Calculate various moving averages"""
    return {
        'MA_20': prices.rolling(window=20).mean(),
        'MA_50': prices.rolling(window=50).mean(),
        'MA_200': prices.rolling(window=200).mean()
    }


def calculate_volume_analysis(hist):
    """Calculate volume-based indicators"""
    volume = hist['Volume']
    price = hist['Close']
    
    # Volume moving averages
    vol_ma_20 = volume.rolling(window=20).mean()
    vol_ma_50 = volume.rolling(window=50).mean()
    
    # Volume relative to average
    vol_ratio_20 = volume / vol_ma_20
    vol_ratio_50 = volume / vol_ma_50
    
    # On-Balance Volume (OBV)
    obv = (volume * np.sign(price.diff())).cumsum()
    
    return {
        'volume_ma_20': vol_ma_20,
        'volume_ma_50': vol_ma_50,
        'volume_ratio_20': vol_ratio_20,
        'volume_ratio_50': vol_ratio_50,
        'obv': obv
    }


async def execute(arguments: dict) -> list[types.TextContent]:
    """
    Get technical indicators for a given symbol.
    
    Args:
        arguments: Dict containing 'symbol' and optional 'period' keys
        
    Returns:
        List containing TextContent with technical indicators
    """
    symbol = arguments.get("symbol", "")
    period = arguments.get("period", "1y")  # Default to 1 year for meaningful indicators
    
    # Validate ticker first
    validation = fetch_ticker(symbol, calling_tool='get_technical_indicators')
    if not validation['valid']:
        return [types.TextContent(
            type="text",
            text=f"Invalid ticker: {validation['error']}" + 
                 (f"\nSuggestion: {validation['suggestion']}" if validation['suggestion'] else "")
        )]
    
    symbol = validation['symbol']  # Use cleaned symbol
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return [types.TextContent(
                type="text",
                text=f"No historical data available for {symbol}"
            )]
        
        if len(hist) < 200:
            return [types.TextContent(
                type="text",
                text=f"Insufficient data for technical analysis (need at least 200 days, got {len(hist)})"
            )]
        
        close_prices = hist['Close']
        high_prices = hist['High']
        low_prices = hist['Low']
        
        # Calculate indicators
        rsi = calculate_rsi(close_prices)
        mas = calculate_moving_averages(close_prices)
        vol_analysis = calculate_volume_analysis(hist)
        
        # Get latest values
        latest_price = close_prices.iloc[-1]
        latest_rsi = rsi.iloc[-1]
        latest_ma_20 = mas['MA_20'].iloc[-1]
        latest_ma_50 = mas['MA_50'].iloc[-1]
        latest_ma_200 = mas['MA_200'].iloc[-1]
        
        # Calculate volatility (20-day rolling std)
        volatility = close_prices.rolling(window=20).std().iloc[-1]
        
        # 52-week high/low
        week_52_high = high_prices.tail(252).max() if len(hist) >= 252 else high_prices.max()
        week_52_low = low_prices.tail(252).min() if len(hist) >= 252 else low_prices.min()
        
        # Volume analysis
        latest_vol = hist['Volume'].iloc[-1]
        avg_vol_20 = vol_analysis['volume_ma_20'].iloc[-1]
        vol_ratio = vol_analysis['volume_ratio_20'].iloc[-1]
        
        # Format results
        result = f"Technical Indicators for {symbol}:\n\n"
        
        result += f"Current Price: ${latest_price:.2f}\n"
        result += f"52-Week Range: ${week_52_low:.2f} - ${week_52_high:.2f}\n"
        result += f"Distance from 52W High: {((latest_price - week_52_high) / week_52_high * 100):+.1f}%\n\n"
        
        result += f"Moving Averages:\n"
        result += f"  20-day MA: ${latest_ma_20:.2f} ({((latest_price - latest_ma_20) / latest_ma_20 * 100):+.1f}%)\n"
        result += f"  50-day MA: ${latest_ma_50:.2f} ({((latest_price - latest_ma_50) / latest_ma_50 * 100):+.1f}%)\n"
        result += f"  200-day MA: ${latest_ma_200:.2f} ({((latest_price - latest_ma_200) / latest_ma_200 * 100):+.1f}%)\n\n"
        
        result += f"Technical Signals:\n"
        result += f"  RSI (14): {latest_rsi:.1f}"
        if latest_rsi > 70:
            result += " (Overbought)"
        elif latest_rsi < 30:
            result += " (Oversold)"
        else:
            result += " (Neutral)"
        result += "\n"
        
        # Trend analysis
        if latest_price > latest_ma_20 > latest_ma_50 > latest_ma_200:
            trend = "Strong Uptrend (Above all MAs)"
        elif latest_price < latest_ma_20 < latest_ma_50 < latest_ma_200:
            trend = "Strong Downtrend (Below all MAs)"
        elif latest_price > latest_ma_20:
            trend = "Short-term Uptrend"
        elif latest_price < latest_ma_20:
            trend = "Short-term Downtrend"
        else:
            trend = "Sideways/Unclear"
        
        result += f"  Trend: {trend}\n\n"
        
        result += f"Volume Analysis:\n"
        result += f"  Current Volume: {latest_vol:,.0f}\n"
        result += f"  20-day Avg Volume: {avg_vol_20:,.0f}\n"
        result += f"  Volume vs Average: {vol_ratio:.1f}x"
        if vol_ratio > 2:
            result += " (High volume spike)"
        elif vol_ratio > 1.5:
            result += " (Above average volume)"
        elif vol_ratio < 0.5:
            result += " (Below average volume)"
        result += "\n\n"
        
        result += f"Risk Metrics:\n"
        result += f"  20-day Volatility: {volatility:.2f} ({(volatility/latest_price*100):.1f}%)\n"
        
        return [types.TextContent(
            type="text",
            text=result
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error calculating technical indicators for {symbol}: {str(e)}"
        )]