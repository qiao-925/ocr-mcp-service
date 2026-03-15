"""Validation helpers for image paths and image files."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


def validate_image_path(image_path: str) -> Path:
    """Validate and return an existing filesystem path."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {image_path}")
    return path


def is_image_file(path: Path) -> bool:
    """Return whether the path points to a readable image file."""
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def validate_image(image_path: str) -> Path:
    """Validate that the image exists and can be opened."""
    path = validate_image_path(image_path)
    if not is_image_file(path):
        raise ValueError(f"Invalid image file: {image_path}")
    return path
