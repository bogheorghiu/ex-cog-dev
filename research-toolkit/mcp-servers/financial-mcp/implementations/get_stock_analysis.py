"""
Get comprehensive stock analysis implementation.
Single responsibility: provide detailed analysis including anomalies and patterns.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import mcp.types as types
from .fetch_ticker import fetch_ticker


def detect_volume_anomalies(hist, lookback_days=60):
    """Detect volume spikes and anomalies"""
    volume = hist['Volume'].tail(lookback_days)
    volume_ma = volume.rolling(window=20).mean()
    volume_std = volume.rolling(window=20).std()
    
    # Z-score for volume
    volume_zscore = (volume - volume_ma) / volume_std
    
    anomalies = []
    for i in range(len(volume)):
        if volume_zscore.iloc[i] > 2:  # 2 standard deviations above mean
            date = volume.index[i].strftime('%Y-%m-%d')
            vol_ratio = volume.iloc[i] / volume_ma.iloc[i]
            anomalies.append({
                'date': date,
                'volume': volume.iloc[i],
                'ratio': vol_ratio,
                'zscore': volume_zscore.iloc[i]
            })
    
    return anomalies


def analyze_price_patterns(hist):
    """Analyze price patterns and support/resistance levels"""
    close = hist['Close']
    high = hist['High']
    low = hist['Low']
    
    # Find recent support and resistance levels
    recent_data = hist.tail(60)  # Last 60 days
    highs = recent_data['High']
    lows = recent_data['Low']
    
    # Simple support/resistance (local maxima/minima)
    resistance_levels = []
    support_levels = []
    
    # Find local maxima (resistance)
    for i in range(2, len(highs)-2):
        if (highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i-2] and 
            highs.iloc[i] > highs.iloc[i+1] and highs.iloc[i] > highs.iloc[i+2]):
            resistance_levels.append(highs.iloc[i])
    
    # Find local minima (support)
    for i in range(2, len(lows)-2):
        if (lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i-2] and 
            lows.iloc[i] < lows.iloc[i+1] and lows.iloc[i] < lows.iloc[i+2]):
            support_levels.append(lows.iloc[i])
    
    return {
        'resistance_levels': sorted(resistance_levels, reverse=True)[:3],  # Top 3
        'support_levels': sorted(support_levels, reverse=True)[:3]  # Top 3
    }


def calculate_momentum_indicators(hist):
    """Calculate momentum and strength indicators"""
    close = hist['Close']
    
    # Price momentum (rate of change)
    roc_5 = ((close - close.shift(5)) / close.shift(5) * 100).iloc[-1]
    roc_20 = ((close - close.shift(20)) / close.shift(20) * 100).iloc[-1]
    
    # Average True Range (volatility)
    high = hist['High']
    low = hist['Low']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
    atr = tr.rolling(window=14).mean().iloc[-1]
    
    return {
        'momentum_5d': roc_5,
        'momentum_20d': roc_20,
        'atr': atr,
        'atr_percentage': (atr / close.iloc[-1] * 100)
    }


async def execute(arguments: dict) -> list[types.TextContent]:
    """
    Get comprehensive stock analysis including patterns and anomalies.
    
    Args:
        arguments: Dict containing 'symbol' and optional 'period' keys
        
    Returns:
        List containing TextContent with detailed analysis
    """
    symbol = arguments.get("symbol", "")
    period = arguments.get("period", "6mo")  # Default to 6 months for analysis
    
    # Validate ticker first
    validation = fetch_ticker(symbol, calling_tool='get_stock_analysis')
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
        
        if len(hist) < 60:
            return [types.TextContent(
                type="text",
                text=f"Insufficient data for analysis (need at least 60 days, got {len(hist)})"
            )]
        
        # Get current price and basic info
        current_price = hist['Close'].iloc[-1]
        current_volume = hist['Volume'].iloc[-1]
        
        # Calculate various analyses
        volume_anomalies = detect_volume_anomalies(hist)
        price_patterns = analyze_price_patterns(hist)
        momentum = calculate_momentum_indicators(hist)
        
        # Performance metrics
        period_start = hist['Close'].iloc[0]
        period_return = ((current_price - period_start) / period_start * 100)
        
        # Volatility analysis
        daily_returns = hist['Close'].pct_change().dropna()
        volatility_daily = daily_returns.std()
        volatility_annualized = volatility_daily * np.sqrt(252) * 100
        
        # Volume trends
        volume_ma_20 = hist['Volume'].rolling(window=20).mean().iloc[-1]
        volume_trend = "Increasing" if current_volume > volume_ma_20 else "Decreasing"
        
        # Build comprehensive report
        result = f"Comprehensive Analysis for {symbol}:\n\n"
        
        # Performance Summary
        result += f"Performance Summary ({period}):\n"
        result += f"  Current Price: ${current_price:.2f}\n"
        result += f"  Period Return: {period_return:+.1f}%\n"
        result += f"  Annualized Volatility: {volatility_annualized:.1f}%\n"
        result += f"  Average True Range: ${momentum['atr']:.2f} ({momentum['atr_percentage']:.1f}%)\n\n"
        
        # Momentum Analysis
        result += f"Momentum Analysis:\n"
        result += f"  5-day momentum: {momentum['momentum_5d']:+.1f}%\n"
        result += f"  20-day momentum: {momentum['momentum_20d']:+.1f}%\n"
        
        if momentum['momentum_5d'] > 5:
            momentum_signal = "Strong short-term uptrend"
        elif momentum['momentum_5d'] < -5:
            momentum_signal = "Strong short-term downtrend"
        elif momentum['momentum_20d'] > 10:
            momentum_signal = "Medium-term uptrend"
        elif momentum['momentum_20d'] < -10:
            momentum_signal = "Medium-term downtrend"
        else:
            momentum_signal = "Consolidating/sideways"
        
        result += f"  Signal: {momentum_signal}\n\n"
        
        # Support and Resistance
        result += f"Key Levels:\n"
        if price_patterns['resistance_levels']:
            result += f"  Resistance: ${', $'.join([f'{r:.2f}' for r in price_patterns['resistance_levels']])}\n"
        if price_patterns['support_levels']:
            result += f"  Support: ${', $'.join([f'{s:.2f}' for s in price_patterns['support_levels']])}\n"
        result += "\n"
        
        # Volume Analysis
        result += f"Volume Analysis:\n"
        result += f"  Current Volume: {current_volume:,.0f}\n"
        result += f"  20-day Average: {volume_ma_20:,.0f}\n"
        result += f"  Volume Trend: {volume_trend}\n"
        result += f"  Volume vs Average: {(current_volume/volume_ma_20):.1f}x\n\n"
        
        # Volume Anomalies (recent spikes)
        if volume_anomalies:
            result += f"Recent Volume Spikes (last 60 days):\n"
            for anomaly in volume_anomalies[-5:]:  # Show last 5
                result += f"  {anomaly['date']}: {anomaly['volume']:,.0f} ({anomaly['ratio']:.1f}x average)\n"
        else:
            result += f"No significant volume spikes detected in recent period.\n"
        result += "\n"
        
        # Risk Assessment
        if volatility_annualized > 50:
            risk_level = "High"
        elif volatility_annualized > 30:
            risk_level = "Medium-High"
        elif volatility_annualized > 20:
            risk_level = "Medium"
        else:
            risk_level = "Low-Medium"
        
        result += f"Risk Assessment:\n"
        result += f"  Risk Level: {risk_level}\n"
        result += f"  Based on {volatility_annualized:.1f}% annualized volatility\n\n"
        
        # Trading Signals Summary
        result += f"Summary Signals:\n"
        signals = []
        
        if momentum['momentum_5d'] > 3 and current_volume > volume_ma_20 * 1.5:
            signals.append("🟢 Bullish momentum with volume confirmation")
        elif momentum['momentum_5d'] < -3 and current_volume > volume_ma_20 * 1.5:
            signals.append("🔴 Bearish momentum with volume confirmation")
        elif current_volume > volume_ma_20 * 2:
            signals.append("⚠️ High volume - potential breakout/breakdown")
        elif volatility_daily > daily_returns.rolling(60).std().iloc[-1] * 2:
            signals.append("⚠️ Elevated volatility - increased risk")
        
        if not signals:
            signals.append("📊 No strong signals - monitor for developments")
        
        for signal in signals:
            result += f"  {signal}\n"
        
        return [types.TextContent(
            type="text",
            text=result
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error analyzing {symbol}: {str(e)}"
        )]