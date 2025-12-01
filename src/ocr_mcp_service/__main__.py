"""Entry point for OCR MCP Service."""

import sys
import signal
from .mcp_server import mcp, send_mcp_log, set_mcp_log_callback
from . import config
from .logger import initialize_logger, set_mcp_log_level, get_logger

# Initialize logging system with MCP callback
def mcp_log_notification(level: str, logger: str, data: dict):
    """Send MCP log notification."""
    send_mcp_log(level, logger, data)

# Initialize logger with MCP callback
initialize_logger(mcp_log_notification)

# Get logger for main module
logger = get_logger("main")

# Import tools to register them with MCP server
from . import tools  # noqa: F401

# Preload engines if configured
for engine_type in config.PRELOAD_ENGINES:
    try:
        from .ocr_engine import OCREngineFactory
        OCREngineFactory.get_engine(engine_type)
        logger.info(f"预加载引擎成功: {engine_type}")
    except Exception as e:
        logger.warning(f"预加载引擎失败: {engine_type}, 错误: {e}", exc_info=True)
        # Ignore preload errors, engines will be loaded on demand


def main():
    """Run the MCP server with error handling and recovery."""
    try:
        logger.info("MCP服务器启动中...")
    mcp.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在优雅关闭服务器...")
        sys.exit(0)
    except SystemExit:
        # Allow system exit to propagate
        raise
    except Exception as e:
        logger.error(
            f"MCP服务器发生未捕获的异常: {e}",
            exc_info=True,
            extra={"error_type": type(e).__name__}
        )
        # 尝试优雅退出，让Cursor重新启动服务
        # 不立即退出，而是记录错误并尝试继续运行
        # 如果FastMCP支持，可以尝试重启
        sys.exit(1)


if __name__ == "__main__":
    main()






