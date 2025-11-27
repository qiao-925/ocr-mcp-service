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




