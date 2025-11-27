"""MCP server setup."""

from fastmcp import FastMCP
from typing import Optional, Callable

# Create MCP server instance
mcp = FastMCP("OCR MCP Service")

# MCP logging notification callback
_mcp_log_callback: Optional[Callable[[str, str, dict], None]] = None


def set_mcp_log_callback(callback: Callable[[str, str, dict], None]):
    """Set callback for sending MCP log notifications.
    
    Args:
        callback: Function to send MCP notifications.
                 Should accept (level: str, logger: str, data: dict) parameters.
    """
    global _mcp_log_callback
    _mcp_log_callback = callback


def send_mcp_log(level: str, logger: str, data: dict):
    """Send MCP log notification.
    
    Args:
        level: Log level (debug, info, warning, error, etc.)
        logger: Logger name
        data: Log data dictionary
    """
    if _mcp_log_callback:
        try:
            _mcp_log_callback(level=level, logger=logger, data=data)
        except Exception:
            # Silently ignore errors to avoid breaking the app
            pass


# Try to enable logging capability if FastMCP supports it
# Note: FastMCP may not directly support logging capability declaration,
# but we can still send notifications via the callback mechanism
try:
    # Check if FastMCP has capabilities support
    if hasattr(mcp, "capabilities"):
        # Declare logging capability
        if not hasattr(mcp.capabilities, "logging"):
            mcp.capabilities["logging"] = {}
except (AttributeError, TypeError):
    # FastMCP may not support capabilities directly
    # We'll handle logging via notifications instead
    pass






