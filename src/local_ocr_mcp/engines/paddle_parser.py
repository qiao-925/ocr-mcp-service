"""Helpers for parsing PaddleOCR prediction results into the public schema."""

from __future__ import annotations

from typing import Any

from ..models import BoundingBox


def parse_paddle_result(result: Any) -> tuple[str, list[BoundingBox], float]:
    """Convert PaddleOCR output into normalized text, boxes, and confidence."""
    pages = _normalize_pages(result)
    if not pages:
        return "", [], 0.0
    page_result = _extract_page_payload(pages[0])
    if isinstance(page_result, dict):
        return _parse_prediction_payload(page_result)
    if isinstance(page_result, (list, tuple)):
        return _parse_legacy_payload(page_result)
    raise ValueError("Unsupported PaddleOCR result format.")


def _normalize_pages(result: Any) -> list[Any]:
    """Normalize PaddleOCR output to a list of page payloads."""
    if result is None:
        return []
    if isinstance(result, list):
        return result
    if isinstance(result, tuple):
        return list(result)
    raise ValueError("Unsupported PaddleOCR result container.")


def _extract_page_payload(page_result: Any) -> Any:
    """Return the serializable payload for one PaddleOCR result page."""
    if isinstance(page_result, dict):
        return page_result.get("res", page_result)
    json_payload = getattr(page_result, "json", None)
    if isinstance(json_payload, dict):
        return json_payload.get("res", json_payload)
    return page_result


def _parse_prediction_payload(page_result: dict[str, Any]) -> tuple[str, list[BoundingBox], float]:
    """Parse PaddleOCR 3.x `predict()` payloads."""
    texts = page_result.get("rec_texts", [])
    scores = page_result.get("rec_scores", [])
    raw_boxes = (
        page_result.get("rec_boxes")
        or page_result.get("rec_polys")
        or page_result.get("dt_polys")
        or []
    )
    parts: list[str] = []
    boxes: list[BoundingBox] = []
    confidences: list[float] = []
    for index, text in enumerate(texts):
        normalized_text = str(text).strip()
        if not normalized_text:
            continue
        parts.append(normalized_text)
        boxes.append(_coerce_box(raw_boxes[index] if index < len(raw_boxes) else None))
        confidences.append(float(scores[index]) if index < len(scores) else 0.0)
    return "\n".join(parts), boxes, _average(confidences)


def _parse_legacy_payload(page_result: list[Any] | tuple[Any, ...]) -> tuple[str, list[BoundingBox], float]:
    """Parse legacy PaddleOCR `ocr()` payloads."""
    parts: list[str] = []
    boxes: list[BoundingBox] = []
    confidences: list[float] = []
    for detection in page_result:
        if detection and len(detection) >= 2:
            box, text_info = detection[0], detection[1]
            if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                text, confidence = text_info[0], text_info[1]
            else:
                text, confidence = str(text_info), 0.0
            if text and box and len(box) >= 4:
                parts.append(str(text))
                boxes.append(_coerce_box(box))
                confidences.append(float(confidence))
    return "\n".join(parts), boxes, _average(confidences)


def _coerce_box(raw_box: Any) -> BoundingBox:
    """Convert PaddleOCR box shapes into an axis-aligned bounding box."""
    if raw_box is None:
        return BoundingBox(0, 0, 0, 0)
    if _is_flat_box(raw_box):
        return BoundingBox(
            x1=float(raw_box[0]),
            y1=float(raw_box[1]),
            x2=float(raw_box[2]),
            y2=float(raw_box[3]),
        )
    if len(raw_box) < 4:
        return BoundingBox(0, 0, 0, 0)
    x_coords = [point[0] for point in raw_box]
    y_coords = [point[1] for point in raw_box]
    return BoundingBox(
        x1=float(min(x_coords)),
        y1=float(min(y_coords)),
        x2=float(max(x_coords)),
        y2=float(max(y_coords)),
    )


def _is_flat_box(raw_box: Any) -> bool:
    """Return whether the value already looks like `[x1, y1, x2, y2]`."""
    return (
        isinstance(raw_box, (list, tuple))
        and len(raw_box) == 4
        and all(isinstance(item, (int, float)) for item in raw_box)
    )


def _average(values: list[float]) -> float:
    """Return the arithmetic mean of the given list."""
    if not values:
        return 0.0
    return sum(values) / len(values)
