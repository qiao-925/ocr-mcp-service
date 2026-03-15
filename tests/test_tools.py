"""Tests for the two public OCR MCP tools."""

from __future__ import annotations

import asyncio
import inspect
from pathlib import Path

from local_ocr_mcp import server as server_module
from local_ocr_mcp.errors import EngineNotAvailableError
from local_ocr_mcp.models import BoundingBox, RecognitionResult
from local_ocr_mcp.services import RecognitionService


class FakeEngine:
    """Minimal fake PaddleOCR engine used by tool tests."""

    def __init__(
        self,
        result: RecognitionResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self._result = result
        self._error = error
        self.calls: list[Path] = []

    def recognize(self, image_path: Path) -> RecognitionResult:
        """Record the call and return or raise the configured outcome."""
        self.calls.append(image_path)
        if self._error is not None:
            raise self._error
        if self._result is None:
            raise AssertionError("FakeEngine result was not configured")
        return self._result


def _call_tool(tool, *args, **kwargs) -> dict:
    """Call a tool regardless of whether FastMCP wraps it."""
    if callable(tool):
        result = tool(*args, **kwargs)
    elif hasattr(tool, "fn"):
        result = tool.fn(*args, **kwargs)
    elif hasattr(tool, "_fn"):
        result = tool._fn(*args, **kwargs)
    else:
        raise TypeError("Unsupported tool object type")
    return asyncio.run(result) if inspect.isawaitable(result) else result


def _patch_recognition_service(monkeypatch, engine: FakeEngine) -> FakeEngine:
    """Patch the public tool to use one explicit recognition service."""
    monkeypatch.setattr(
        server_module,
        "recognition_service",
        RecognitionService(engine=engine),
    )
    return engine


def test_tool_registration() -> None:
    """The simplified server should expose exactly two public tools."""
    assert callable(server_module.ocr_recognize)
    assert callable(server_module.ocr_health_check)
    assert server_module.ocr_recognize.__name__ == "ocr_recognize"
    assert server_module.ocr_health_check.__name__ == "ocr_health_check"
    assert not hasattr(server_module, "ocr_list_engines")


def test_ocr_recognize_invalid_image_payload() -> None:
    """Recognize should reject non-object image payloads."""
    result = _call_tool(server_module.ocr_recognize, image="not-an-object")

    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_image"
    assert result["data"] is None
    assert result["meta"]["resolved_engine"] == "paddleocr"


def test_ocr_recognize_success_shape(monkeypatch, sample_image_path: Path) -> None:
    """Recognize should return the simplified success envelope."""
    engine = _patch_recognition_service(
        monkeypatch,
        FakeEngine(
            result=RecognitionResult(
                text="hello",
                boxes=[BoundingBox(x1=0, y1=0, x2=10, y2=10)],
                confidence=0.9,
                engine="paddleocr",
                processing_ms=123,
            )
        ),
    )

    result = _call_tool(server_module.ocr_recognize, image={"path": str(sample_image_path)})

    assert result["status"] == "ok"
    assert result["error"] is None
    assert result["data"]["text"] == "hello"
    assert result["data"]["engine"] == "paddleocr"
    assert result["data"]["processing_ms"] == 123
    assert result["meta"]["resolved_engine"] == "paddleocr"
    assert result["meta"]["resolved_image_path"] == str(sample_image_path.resolve())
    assert engine.calls == [sample_image_path.resolve()]


def test_ocr_recognize_file_not_found() -> None:
    """Missing files should map to the standardized file_not_found error."""
    result = _call_tool(server_module.ocr_recognize, image={"path": "missing-file.png"})

    assert result["status"] == "error"
    assert result["error"]["code"] == "file_not_found"
    assert result["data"] is None


def test_ocr_recognize_invalid_image_file(invalid_image_path: Path) -> None:
    """Existing non-image files should map to invalid_image."""
    result = _call_tool(server_module.ocr_recognize, image={"path": str(invalid_image_path)})

    assert result["status"] == "error"
    assert result["error"]["code"] == "invalid_image"
    assert result["meta"]["resolved_engine"] == "paddleocr"


def test_ocr_recognize_engine_unavailable(monkeypatch, sample_image_path: Path) -> None:
    """Engine initialization failures should map to engine_not_available."""
    _patch_recognition_service(
        monkeypatch,
        FakeEngine(error=EngineNotAvailableError("PaddleOCR is missing")),
    )

    result = _call_tool(server_module.ocr_recognize, image={"path": str(sample_image_path)})

    assert result["status"] == "error"
    assert result["error"]["code"] == "engine_not_available"
    assert result["error"]["message"] == "PaddleOCR is missing"
    assert result["meta"]["resolved_image_path"] == str(sample_image_path.resolve())


def test_ocr_health_check_lightweight_shape() -> None:
    """Health check should return lightweight status payload."""
    result = _call_tool(server_module.ocr_health_check)

    assert result["status"] == "ok"
    assert result["error"] is None
    assert result["data"]["status"] == "healthy"
    assert "uptime_ms" in result["data"]
    assert result["data"]["transport"] == "stdio"
