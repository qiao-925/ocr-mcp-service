"""Domain errors for OCR request handling."""

from __future__ import annotations


class LocalOCRServiceError(Exception):
    """Base class for structured service-layer errors."""

    code = "internal_error"
    retryable = False

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidImageRequestError(LocalOCRServiceError):
    """Raised when the image payload or image file is invalid."""

    code = "invalid_image"


class EngineNotAvailableError(LocalOCRServiceError):
    """Raised when the requested OCR engine cannot be used."""

    code = "engine_not_available"
