"""Minimal runtime configuration for the stdio-only PaddleOCR service."""

from __future__ import annotations

import os


def get_env(key: str, default: str | None = None) -> str | None:
    """Return one environment variable value."""
    return os.getenv(key, default)


PADDLEOCR_LANG = (get_env("PADDLEOCR_LANG", "ch") or "ch").strip() or "ch"
LOG_LEVEL = (get_env("LOG_LEVEL", "INFO") or "INFO").upper()

