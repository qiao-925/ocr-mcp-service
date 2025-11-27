"""Entry point for OCR MCP Service."""

from .mcp_server import mcp, send_mcp_log, set_mcp_log_callback
from . import config
from .logger import initialize_logger, set_mcp_log_level

# Initialize logging system with MCP callback
def mcp_log_notification(level: str, logger: str, data: dict):
    """Send MCP log notification."""
    send_mcp_log(level, logger, data)

# Initialize logger with MCP callback
initialize_logger(mcp_log_notification)

# Import tools to register them with MCP server
from . import tools  # noqa: F401

# Preload engines if configured
for engine_type in config.PRELOAD_ENGINES:
    try:
        from .ocr_engine import OCREngineFactory
        OCREngineFactory.get_engine(engine_type)
    except Exception:
        pass  # Ignore preload errors


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()






