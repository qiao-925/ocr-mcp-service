"""Recognition service for image-path validation and envelope shaping."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .. import __version__
from ..engines import PaddleOCREngine
from ..errors import EngineNotAvailableError, InvalidImageRequestError
from ..logger import get_logger
from ..models import ErrorPayload, OCRRequest, ResponseMeta, ToolResponse
from ..validation import validate_image


class RecognitionService:
    """Validate OCR requests and normalize them into the public envelope."""

    def __init__(self, engine: PaddleOCREngine | None = None) -> None:
        """Store the PaddleOCR engine dependency."""
        self._engine = engine or PaddleOCREngine()
        self._logger = get_logger("recognition")

    def recognize(self, image: dict[str, Any]) -> dict[str, Any]:
        """Handle one OCR request and return the public tool response."""
        request = OCRRequest(image=image)
        resolved_engine = "paddleocr"
        resolved_path: str | None = None

        try:
            image_path = self._resolve_image_path(request.image)
            validated_path = validate_image(str(image_path)).resolve()
            resolved_path = str(validated_path)
            result = self._engine.recognize(validated_path)
            meta = self._build_meta(
                request_id=request.request_id,
                resolved_engine=resolved_engine,
                resolved_image_path=resolved_path,
            )
            return self._build_success(data=result.to_dict(), meta=meta)
        except EngineNotAvailableError as exc:
            return self._build_error(
                code=exc.code,
                message=exc.message,
                retryable=exc.retryable,
                data=None,
                meta=self._build_meta(
                    request_id=request.request_id,
                    resolved_engine=resolved_engine,
                    resolved_image_path=resolved_path,
                ),
            )
        except FileNotFoundError as exc:
            return self._build_error(
                "file_not_found",
                str(exc),
                False,
                None,
                self._build_meta(request.request_id, resolved_engine, resolved_path),
            )
        except InvalidImageRequestError as exc:
            return self._build_error(
                exc.code,
                exc.message,
                exc.retryable,
                None,
                self._build_meta(request.request_id, resolved_engine, resolved_path),
            )
        except ValueError as exc:
            return self._build_error(
                "invalid_image",
                str(exc),
                False,
                None,
                self._build_meta(request.request_id, resolved_engine, resolved_path),
            )
        except Exception as exc:
            self._logger.exception("OCR 请求处理失败")
            return self._build_error(
                "internal_error",
                str(exc),
                False,
                None,
                self._build_meta(request.request_id, resolved_engine, resolved_path),
            )

    def _resolve_image_path(self, image: dict[str, Any]) -> Path:
        """Resolve the image payload to an absolute path."""
        if not isinstance(image, dict):
            raise InvalidImageRequestError("`image` must be an object and currently only supports `path`.")
        if "path" not in image:
            raise InvalidImageRequestError("`image.path` is required in current version.")
        if any(key not in {"path"} for key in image):
            raise InvalidImageRequestError("Current version only supports `image.path` input.")
        raw_path = image["path"]
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise InvalidImageRequestError("`image.path` must be a non-empty string.")
        parsed = Path(raw_path.strip()).expanduser()
        if not parsed.is_absolute():
            parsed = Path.cwd() / parsed
        return parsed.resolve(strict=False)

    def _build_meta(
        self,
        request_id: str,
        resolved_engine: str,
        resolved_image_path: str | None,
    ) -> ResponseMeta:
        """Build response metadata."""
        return ResponseMeta(
            timestamp=datetime.now(timezone.utc).isoformat(),
            runtime_version=__version__,
            request_id=request_id,
            resolved_engine=resolved_engine,
            resolved_image_path=resolved_image_path,
        )

    def _build_success(self, data: dict[str, Any], meta: ResponseMeta) -> dict[str, Any]:
        """Build a success envelope."""
        return ToolResponse(status="ok", data=data, error=None, meta=meta).to_dict()

    def _build_error(
        self,
        code: str,
        message: str,
        retryable: bool,
        data: dict[str, Any] | None,
        meta: ResponseMeta,
    ) -> dict[str, Any]:
        """Build an error envelope."""
        return ToolResponse(
            status="error",
            data=data,
            error=ErrorPayload(code=code, message=message, retryable=retryable),
            meta=meta,
        ).to_dict()
