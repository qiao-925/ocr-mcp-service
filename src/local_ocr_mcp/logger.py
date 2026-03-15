"""Basic logger setup used by the simplified Local OCR MCP service."""

from __future__ import annotations

import logging

from .config import LOG_LEVEL


def get_logger(name: str | None = None) -> logging.Logger:
    """Return one project logger."""
    logger_name = "local_ocr_mcp" if name is None else f"local_ocr_mcp.{name}"
    return logging.getLogger(logger_name)


def initialize_logger() -> None:
    """Initialize the process logger once."""
    root_logger = get_logger()
    if root_logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s")
    )
    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    root_logger.addHandler(handler)
    root_logger.propagate = False


initialize_logger()
