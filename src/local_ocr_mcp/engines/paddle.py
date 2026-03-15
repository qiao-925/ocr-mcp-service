"""PaddleOCR adapter for the simplified stdio OCR runtime."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from ..config import PADDLEOCR_LANG
from ..errors import EngineNotAvailableError
from ..logger import get_logger
from ..models import RecognitionResult
from .paddle_parser import parse_paddle_result


class PaddleOCREngine:
    """Run OCR through the PaddleOCR Python package."""

    def __init__(self, lang: str = PADDLEOCR_LANG) -> None:
        """Store the PaddleOCR language and defer client initialization."""
        self._lang = lang
        self._client: Any | None = None
        self._logger = get_logger("paddle")

    def recognize(self, image_path: Path) -> RecognitionResult:
        """Recognize text from one local image path."""
        started_at = time.perf_counter()
        try:
            raw_result = self._run_prediction(image_path)
        except Exception:
            self._logger.exception("PaddleOCR 执行失败")
            raise
        text, boxes, confidence = parse_paddle_result(raw_result)
        processing_ms = int((time.perf_counter() - started_at) * 1000)
        return RecognitionResult(
            text=text,
            boxes=boxes,
            confidence=confidence,
            engine="paddleocr",
            processing_ms=processing_ms,
        )

    def _run_prediction(self, image_path: Path) -> Any:
        """Execute PaddleOCR using the current documented API with a legacy fallback."""
        client = self._get_client()
        if hasattr(client, "predict"):
            return client.predict(str(image_path))
        return client.ocr(str(image_path), cls=True)

    def _get_client(self) -> Any:
        """Return one lazily initialized PaddleOCR client."""
        if self._client is not None:
            return self._client
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise EngineNotAvailableError(
                "PaddleOCR is not installed. Install it with: uv sync --extra paddleocr"
            ) from exc
        try:
            self._client = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang=self._lang,
            )
        except TypeError:
            try:
                self._client = PaddleOCR(use_angle_cls=True, lang=self._lang)
            except Exception as exc:
                raise EngineNotAvailableError(f"Failed to initialize PaddleOCR: {exc}") from exc
        except Exception as exc:
            raise EngineNotAvailableError(f"Failed to initialize PaddleOCR: {exc}") from exc
        return self._client
