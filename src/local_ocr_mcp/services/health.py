"""Health service for the simplified stdio-only MCP runtime."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from .. import __version__
from ..models import ResponseMeta, ServiceHealth, ToolResponse
class HealthService:
    """Track uptime for health-check requests."""

    def __init__(self) -> None:
        """Initialize health service state."""
        self._service_start_monotonic = time.monotonic()

    def build_response(self) -> dict[str, Any]:
        """Return the standardized health-check envelope."""
        health = ServiceHealth(
            status="healthy",
            uptime_ms=int((time.monotonic() - self._service_start_monotonic) * 1000),
            transport="stdio",
            runtime_version=__version__,
        )
        response = ToolResponse(
            status="ok",
            data=health.to_dict(),
            error=None,
            meta=ResponseMeta(
                timestamp=datetime.now(timezone.utc).isoformat(),
                runtime_version=__version__,
            ),
        )
        return response.to_dict()
