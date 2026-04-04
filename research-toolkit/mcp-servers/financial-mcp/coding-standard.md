# Financial MCP Server Coding Standards

## Architecture
- **Prefer modular structure** - separate files over monolithic code
- **Use generic `execute()` pattern** for consistent interfaces over specific function names
- **Dynamic imports** for extensibility (avoid manual registries when possible)

## Python Style
- Clear docstrings for all functions
- Error handling with try/catch blocks
- Type hints where helpful
- One responsibility per file/function

## Project Structure
```
project/
├── main_entry_point.py
├── definitions/            # Schemas/interfaces (like headers)
├── implementations/        # One file per function
└── requirements.txt
```

## Testing Preferences
- Test individual functions before integration
- Verify external dependencies (like yfinance) work before building on them

## Comments
- Add explanatory comments for complex logic
- Explain "why" not just "what"
- Document trade-offs and design decisions