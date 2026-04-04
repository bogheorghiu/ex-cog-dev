# Claude Memory for Financial MCP Server

## Code Design Preferences

### Architecture
- **Prefer modular structure** - separate files over monolithic code
- **Use generic `execute()` pattern** for consistent interfaces over specific function names
- **Dynamic imports** for extensibility (avoid manual registries when possible)

### Python Style
- Clear docstrings for all functions
- Error handling with try/catch blocks
- Type hints where helpful
- One responsibility per file/function

### Project Structure
```
financial-mcp/
├── financial_server.py      # MCP protocol handler + main_sync() entry point
├── tool_definitions.py     # Function schemas (like headers)
├── pyproject.toml          # Package config — enables uvx/pip install
├── requirements.txt        # Dev dependencies
├── cache/                  # Self-contained SQLite cache (no external PYTHONPATH needed)
│   ├── __init__.py
│   ├── config.py           # TTL, CACHE_DIR (~/.cache/financial-mcp by default)
│   └── manager.py          # CacheManager with lazy DB init
└── implementations/        # One file per tool
```

## Testing Preferences
- Test individual functions before integration
- Verify external dependencies (like yfinance) work before building on them

## Comments
- Add explanatory comments for complex logic
- Explain "why" not just "what"
- Document trade-offs and design decisions