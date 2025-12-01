"""Utility functions for image processing."""

import os
import functools
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Callable, TypeVar, Any

T = TypeVar('T')


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


def with_timeout(timeout_seconds: int):
    """Decorator to add timeout to a function.
    
    Args:
        timeout_seconds: Maximum time in seconds to wait for function execution
    
    Returns:
        Decorated function that raises TimeoutError if execution exceeds timeout
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=timeout_seconds)
                except FutureTimeoutError:
                    raise TimeoutError(
                        f"函数 {func.__name__} 执行超时（超过 {timeout_seconds} 秒）"
                    )
        return wrapper
    return decorator






