"""Tests for the simplified PaddleOCR adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from local_ocr_mcp.engines.paddle import PaddleOCREngine


class _PredictResult:
    """Mimic the result object returned by PaddleOCR 3.x predict()."""

    def __init__(self, payload: dict[str, object]) -> None:
        self.json = payload


class _PredictClient:
    """Minimal PaddleOCR client exposing `predict()`."""

    def predict(self, image_path: str) -> list[_PredictResult]:
        """Return one documented-style prediction payload."""
        assert image_path == "image.png"
        return [
            _PredictResult(
                {
                    "res": {
                        "rec_texts": ["hello", "world"],
                        "rec_scores": [0.9, 0.8],
                        "rec_boxes": [
                            [0, 1, 10, 11],
                            [[20, 20], [30, 20], [30, 40], [20, 40]],
                        ],
                    }
                }
            )
        ]


class _LegacyClient:
    """Minimal PaddleOCR client exposing the legacy `ocr()` API."""

    def ocr(self, image_path: str, cls: bool = True) -> list[list[object]]:
        """Return one legacy PaddleOCR response payload."""
        assert image_path == "legacy.png"
        assert cls is True
        return [
            [
                [
                    [[0, 0], [12, 0], [12, 10], [0, 10]],
                    ("legacy text", 0.95),
                ]
            ]
        ]


def test_paddle_engine_parses_predict_payload(monkeypatch) -> None:
    """The adapter should parse the documented PaddleOCR 3.x payload shape."""
    engine = PaddleOCREngine()
    monkeypatch.setattr(engine, "_get_client", lambda: _PredictClient())

    result = engine.recognize(Path("image.png"))

    assert result.text == "hello\nworld"
    assert len(result.boxes) == 2
    assert result.boxes[0].x1 == 0.0
    assert result.boxes[1].y2 == 40.0
    assert result.confidence == pytest.approx(0.85)
    assert result.engine == "paddleocr"


def test_paddle_engine_falls_back_to_legacy_ocr(monkeypatch) -> None:
    """The adapter should still parse the legacy `ocr()` output shape."""
    engine = PaddleOCREngine()
    monkeypatch.setattr(engine, "_get_client", lambda: _LegacyClient())

    result = engine.recognize(Path("legacy.png"))

    assert result.text == "legacy text"
    assert len(result.boxes) == 1
    assert result.boxes[0].x2 == 12.0
    assert result.confidence == pytest.approx(0.95)
