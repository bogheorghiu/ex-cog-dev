"""
Debug wrapper to track MCP communication issues.
Add logging to identify where BrokenPipeError occurs.
"""

import sys
import traceback
from datetime import datetime


def debug_log(message, level="INFO"):
    """Log debug messages with timestamp."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr, flush=True)


def safe_execute_wrapper(original_execute):
    """
    Wrap execute functions with debugging to catch MCP issues.
    """
    async def wrapped_execute(arguments):
        symbol = arguments.get('symbol', 'UNKNOWN')
        debug_log(f"Starting execution for symbol: {symbol}")
        
        try:
            debug_log(f"Calling original execute for {symbol}")
            result = await original_execute(arguments)
            
            debug_log(f"Execute completed for {symbol}, result length: {len(result[0].text) if result and len(result) > 0 else 0}")
            
            # Check for potential MCP serialization issues
            if result and len(result) > 0:
                text = result[0].text
                debug_log(f"Response preview for {symbol}: {text[:100]}...")
                
                # Test JSON serialization
                import json
                try:
                    json.dumps({"text": text})
                    debug_log(f"JSON serialization OK for {symbol}")
                except Exception as e:
                    debug_log(f"JSON serialization FAILED for {symbol}: {e}", "ERROR")
            
            debug_log(f"Returning result for {symbol}")
            return result
            
        except Exception as e:
            debug_log(f"Exception in execute for {symbol}: {type(e).__name__}: {e}", "ERROR")
            debug_log(f"Traceback: {traceback.format_exc()}", "ERROR")
            raise
    
    return wrapped_execute


# Example usage - this would be applied to tools that crash
def wrap_tool_for_debugging(tool_module):
    """Wrap a tool module's execute function with debugging."""
    original_execute = tool_module.execute
    tool_module.execute = safe_execute_wrapper(original_execute)
    return tool_module