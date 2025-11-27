"""Utility functions for image processing."""

import os
from pathlib import Path
from PIL import Image


def validate_image_path(image_path: str) -> Path:
    """Validate and return image path."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {image_path}")
    return path


def is_image_file(path: Path) -> bool:
    """Check if file is a valid image."""
    try:
        Image.open(path)
        return True
    except Exception:
        return False


def validate_image(image_path: str) -> Path:
    """Validate image file exists and is readable."""
    path = validate_image_path(image_path)
    if not is_image_file(path):
        raise ValueError(f"Invalid image file: {image_path}")
    return path






