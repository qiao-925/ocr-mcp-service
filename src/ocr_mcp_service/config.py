"""Configuration management for OCR MCP Service."""

import os
from typing import Optional


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable."""
    return os.getenv(key, default)


# PaddleOCR configuration
PADDLEOCR_MODEL_DIR: Optional[str] = get_env("PADDLEOCR_MODEL_DIR")
PADDLEOCR_LANG: str = get_env("PADDLEOCR_LANG", "ch")

# DeepSeek OCR configuration
DEEPSEEK_MODEL_NAME: str = get_env("DEEPSEEK_MODEL_NAME", "deepseek-ai/deepseek-ocr")
# Default to CUDA if available, otherwise CPU
try:
    import torch
    DEEPSEEK_DEVICE: str = get_env("DEEPSEEK_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
except ImportError:
    # torch not installed, default to CPU
    DEEPSEEK_DEVICE: str = get_env("DEEPSEEK_DEVICE", "cpu")
# Hugging Face mirror for faster download in China
HF_ENDPOINT: Optional[str] = get_env("HF_ENDPOINT")  # e.g., "https://hf-mirror.com"
HF_MIRROR: Optional[str] = get_env("HF_MIRROR")  # Alternative mirror setting

# Engine preloading
PRELOAD_ENGINES: list[str] = [
    engine.strip()
    for engine in get_env("PRELOAD_ENGINES", "").split(",")
    if engine.strip()
]

# Logging configuration
LOG_LEVEL: str = get_env("LOG_LEVEL", "INFO")
LOG_FILE: str = get_env("LOG_FILE", "logs/ocr_service.log")
LOG_MAX_BYTES: int = int(get_env("LOG_MAX_BYTES", "10485760"))  # 10MB
LOG_BACKUP_COUNT: int = int(get_env("LOG_BACKUP_COUNT", "5"))

# Timeout configuration (in seconds)
# Base timeout - can be overridden based on image size
OCR_TIMEOUT: int = int(get_env("OCR_TIMEOUT", "120"))  # Default 120 seconds (2 minutes)

# Dynamic timeout thresholds (in bytes)
SMALL_IMAGE_SIZE: int = 1024 * 1024  # 1MB
MEDIUM_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB

# Timeout for different image sizes (in seconds)
SMALL_IMAGE_TIMEOUT: int = int(get_env("SMALL_IMAGE_TIMEOUT", "60"))  # 1 minute
MEDIUM_IMAGE_TIMEOUT: int = int(get_env("MEDIUM_IMAGE_TIMEOUT", "120"))  # 2 minutes
LARGE_IMAGE_TIMEOUT: int = int(get_env("LARGE_IMAGE_TIMEOUT", "180"))  # 3 minutes


def get_timeout_for_image(image_path: str) -> int:
    """根据图片大小返回合适的超时时间。
    
    Args:
        image_path: 图片文件路径
    
    Returns:
        超时时间（秒）
    """
    try:
        from pathlib import Path
        size = Path(image_path).stat().st_size
        if size < SMALL_IMAGE_SIZE:
            return SMALL_IMAGE_TIMEOUT
        elif size < MEDIUM_IMAGE_SIZE:
            return MEDIUM_IMAGE_TIMEOUT
        else:
            return LARGE_IMAGE_TIMEOUT
    except Exception:
        # 如果无法获取文件大小，使用默认超时
        return OCR_TIMEOUT




