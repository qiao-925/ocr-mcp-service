"""CLI entrypoint for the stdio-only Local OCR MCP server."""

from __future__ import annotations

import asyncio
import sys

from .logger import get_logger
from .server import mcp


def build_argument_parser() -> "argparse.ArgumentParser":
    """Create the minimal CLI parser for the stdio-only runtime."""
    import argparse

    return argparse.ArgumentParser(description="Local OCR MCP")


def main() -> None:
    """Run the MCP server with stdio transport and basic error handling."""
    logger = get_logger("main")
    parser = build_argument_parser()
    parser.parse_args()

    try:
        logger.info("MCP服务器启动中... transport=stdio")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在优雅关闭服务器...")
        sys.exit(0)
    except asyncio.CancelledError:
        logger.info("服务器关闭完成")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as exc:
        logger.error(
            f"MCP服务器发生未捕获的异常: {exc}",
            exc_info=True,
            extra={"error_type": type(exc).__name__},
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
