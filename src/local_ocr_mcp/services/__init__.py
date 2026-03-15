"""Service-layer exports for the simplified Local OCR MCP runtime."""

from .health import HealthService
from .recognition import RecognitionService

__all__ = [
    "HealthService",
    "RecognitionService",
]
