"""Data models for the simplified OCR tool envelope."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class BoundingBox:
    """Axis-aligned bounding box for one OCR segment."""

    x1: float
    y1: float
    x2: float
    y2: float


    def to_dict(self) -> dict[str, float]:
        """Serialize the bounding box to the public response shape."""
        return {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
        }


@dataclass(frozen=True)
class OCRRequest:
    """Structured OCR request accepted by the public tool."""

    image: dict[str, Any]
    request_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class RecognitionResult:
    """Normalized OCR payload returned by the PaddleOCR adapter."""

    text: str
    boxes: list[BoundingBox]
    confidence: float
    engine: str
    processing_ms: int

    def to_dict(self) -> dict[str, Any]:
        """Serialize the OCR payload for the public tool response."""
        return {
            "text": self.text,
            "boxes": [box.to_dict() for box in self.boxes],
            "confidence": self.confidence,
            "engine": self.engine,
            "processing_ms": self.processing_ms,
        }


@dataclass(frozen=True)
class ErrorPayload:
    """Structured error payload used by MCP tools."""

    code: str
    message: str
    retryable: bool

    def to_dict(self) -> dict[str, Any]:
        """Serialize error payload."""
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }


@dataclass(frozen=True)
class ResponseMeta:
    """Metadata shared by success and error envelopes."""

    timestamp: str
    runtime_version: str
    request_id: str | None = None
    resolved_engine: str | None = None
    resolved_image_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize response metadata while omitting null fields."""
        meta = {
            "timestamp": self.timestamp,
            "runtime_version": self.runtime_version,
        }
        optional_fields = {
            "request_id": self.request_id,
            "resolved_engine": self.resolved_engine,
            "resolved_image_path": self.resolved_image_path,
        }
        for key, value in optional_fields.items():
            if value is not None:
                meta[key] = value
        return meta


@dataclass(frozen=True)
class ToolResponse:
    """Top-level MCP tool envelope."""

    status: str
    data: dict[str, Any] | None
    error: ErrorPayload | None
    meta: ResponseMeta

    def to_dict(self) -> dict[str, Any]:
        """Serialize response envelope."""
        return {
            "status": self.status,
            "data": self.data,
            "error": self.error.to_dict() if self.error else None,
            "meta": self.meta.to_dict(),
        }


@dataclass(frozen=True)
class ServiceHealth:
    """Lightweight health payload for the stdio runtime."""

    status: str
    uptime_ms: int
    transport: str
    runtime_version: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize service health payload."""
        return {
            "status": self.status,
            "uptime_ms": self.uptime_ms,
            "transport": self.transport,
            "runtime_version": self.runtime_version,
        }
