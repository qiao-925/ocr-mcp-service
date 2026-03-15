"""FastMCP server instance and the two public OCR tools."""

from __future__ import annotations

import asyncio
from typing import Any

from .services import HealthService, RecognitionService

try:
    from fastmcp import FastMCP
except ImportError:
    class FastMCP:  # type: ignore[override]
        """Fallback FastMCP stub for environments without fastmcp installed."""

        def __init__(self, name: str) -> None:
            self.name = name
            self.capabilities = {}

        def tool(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            """Return a decorator that annotates function name."""

            def decorator(func):  # type: ignore[no-untyped-def]
                func.name = func.__name__
                return func

            return decorator

        def run(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            """Fallback run behavior when fastmcp is unavailable."""
            raise RuntimeError("fastmcp is not installed. Install project dependencies first.")


mcp = FastMCP("Local OCR MCP")
recognition_service = RecognitionService()
health_service = HealthService()


@mcp.tool()
async def ocr_recognize(image: dict[str, Any]) -> dict[str, Any]:
    """Recognize text from one local image path via PaddleOCR."""
    return await asyncio.to_thread(recognition_service.recognize, image)


@mcp.tool()
def ocr_health_check() -> dict[str, Any]:
    """Return lightweight health status for the stdio runtime."""
    return health_service.build_response()
