"""Shared pytest fixtures for the simplified OCR service."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def sample_image_path(tmp_path: Path) -> Path:
    """Create one valid image file for OCR tests."""
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (32, 16), color="white").save(image_path)
    return image_path


@pytest.fixture
def invalid_image_path(tmp_path: Path) -> Path:
    """Create one invalid image file for validation tests."""
    image_path = tmp_path / "invalid.txt"
    image_path.write_text("not an image", encoding="utf-8")
    return image_path
