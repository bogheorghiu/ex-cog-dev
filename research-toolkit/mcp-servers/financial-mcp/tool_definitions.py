"""
Tool definitions for financial MCP server.
This file defines the function signatures and schemas - like C++ headers.
"""

import mcp.types as types


def get_tool_definitions() -> list[types.Tool]:
    """
    Return list of all available tools with their schemas.
    This is the "header file" that tells Claude what functions exist.
    """
    return [
        types.Tool(
            name="get_stock_price",
            description="Get current stock price for a given symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT, GOOGL)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="get_stock_history",
            description="Get historical stock data with full dataset and summary statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT, GOOGL)"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
                        "default": "1mo"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (alternative to period)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (alternative to period)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="get_stock_info",
            description="Get comprehensive stock information including fundamentals, dividends, and splits",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT, GOOGL)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="get_technical_indicators",
            description="Get technical analysis indicators including RSI, moving averages, and volume analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT, GOOGL)"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period for analysis (3mo, 6mo, 1y, 2y, 5y)",
                        "default": "1y"
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="get_stock_analysis",
            description="Get comprehensive stock analysis including patterns, anomalies, and trading signals",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT, GOOGL)"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period for analysis (3mo, 6mo, 1y, 2y)",
                        "default": "6mo"
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="force_fetch_ticker",
            description="Force fresh validation of a stock ticker symbol, bypassing any cached data. Use this to refresh ticker information or when you suspect cached data may be outdated.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol to validate with fresh data (e.g., AAPL, MSFT, GOOGL)"
                    }
                },
                "required": ["symbol"]
            }
        )
    ]