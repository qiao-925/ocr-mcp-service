"""Logging configuration for OCR MCP Service."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Callable, Any
from datetime import datetime

from .config import get_env

# MCP log level mapping
MCP_LOG_LEVELS = {
    "debug": "debug",
    "info": "info",
    "notice": "notice",
    "warning": "warning",
    "error": "error",
    "critical": "critical",
    "alert": "alert",
    "emergency": "emergency",
}

# Python logging to MCP level mapping
PYTHON_TO_MCP_LEVEL = {
    logging.DEBUG: "debug",
    logging.INFO: "info",
    logging.WARNING: "warning",
    logging.ERROR: "error",
    logging.CRITICAL: "critical",
}


class MCPLogHandler(logging.Handler):
    """Custom logging handler that sends logs via MCP notifications."""

    def __init__(self, mcp_notification_callback: Optional[Callable] = None):
        """Initialize MCP log handler.
        
        Args:
            mcp_notification_callback: Callback function to send MCP notifications.
                                     Should accept (level, logger, data) parameters.
        """
        super().__init__()
        self.mcp_callback = mcp_notification_callback
        self.min_level = logging.INFO  # Default minimum level

    def set_mcp_callback(self, callback: Callable):
        """Set the MCP notification callback."""
        self.mcp_callback = callback

    def set_min_level(self, level: int):
        """Set minimum log level."""
        self.min_level = level

    def emit(self, record: logging.LogRecord):
        """Emit a log record via MCP notification."""
        if record.levelno < self.min_level:
            return

        if self.mcp_callback:
            try:
                mcp_level = PYTHON_TO_MCP_LEVEL.get(
                    record.levelno, "info"
                )
                
                # Extract extra data from record
                data = {
                    "message": record.getMessage(),
                }
                
                # Add progress info if available
                if hasattr(record, "progress"):
                    data["progress"] = record.progress
                if hasattr(record, "stage"):
                    data["stage"] = record.stage
                if hasattr(record, "image_path"):
                    data["image_path"] = record.image_path
                
                # Add any other extra fields
                for key, value in record.__dict__.items():
                    if key not in [
                        "name", "msg", "args", "created", "filename",
                        "funcName", "levelname", "levelno", "lineno",
                        "module", "msecs", "message", "pathname",
                        "process", "processName", "relativeCreated",
                        "thread", "threadName", "exc_info", "exc_text",
                        "stack_info", "progress", "stage", "image_path"
                    ]:
                        data[key] = value

                self.mcp_callback(
                    level=mcp_level,
                    logger=record.name,
                    data=data
                )
            except Exception:
                # Silently ignore errors in MCP logging to avoid breaking the app
                pass


class OCRLogger:
    """OCR service logger with file and MCP support."""

    _instance: Optional["OCRLogger"] = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Configuration
        log_level = get_env("LOG_LEVEL", "INFO").upper()
        log_file = get_env("LOG_FILE", "logs/ocr_service.log")
        log_max_bytes = int(get_env("LOG_MAX_BYTES", "10485760"))  # 10MB
        log_backup_count = int(get_env("LOG_BACKUP_COUNT", "5"))

        # Create logs directory
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger("ocr_mcp_service")
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        self.logger.propagate = False  # Prevent duplicate logs

        # Clear existing handlers
        self.logger.handlers.clear()

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count,
            encoding="utf-8"
        )
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # MCP handler (callback will be set later)
        self.mcp_handler = MCPLogHandler()
        self.logger.addHandler(self.mcp_handler)

        self._initialized = True

    def set_mcp_callback(self, callback: Callable):
        """Set MCP notification callback."""
        self.mcp_handler.set_mcp_callback(callback)

    def set_mcp_log_level(self, level: str):
        """Set MCP log level.
        
        Args:
            level: MCP log level (debug, info, warning, error, etc.)
        """
        level_mapping = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "notice": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
            "alert": logging.CRITICAL,
            "emergency": logging.CRITICAL,
        }
        python_level = level_mapping.get(level.lower(), logging.INFO)
        self.mcp_handler.set_min_level(python_level)

    def get_logger(self, name: str = None) -> logging.Logger:
        """Get a logger instance.
        
        Args:
            name: Logger name (default: ocr_mcp_service)
        """
        if name:
            return logging.getLogger(f"ocr_mcp_service.{name}")
        return self.logger

    def log_progress(
        self,
        logger_name: str,
        percentage: float,
        message: str,
        stage: Optional[str] = None,
        **kwargs
    ):
        """Log progress information.
        
        Args:
            logger_name: Name of the logger
            percentage: Progress percentage (0-100)
            message: Progress message
            stage: Current stage name
            **kwargs: Additional context data
        """
        logger = self.get_logger(logger_name)
        extra = {
            "progress": percentage,
            "stage": stage,
            **kwargs
        }
        logger.info(
            f"{percentage:.0f}% - {message}",
            extra=extra
        )


def log_progress(
    logger_name: str,
    percentage: float,
    message: str,
    stage: Optional[str] = None,
    **kwargs
):
    """Log progress information (module-level function).
    
    Args:
        logger_name: Name of the logger
        percentage: Progress percentage (0-100)
        message: Progress message
        stage: Current stage name
        **kwargs: Additional context data
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = OCRLogger()
    _logger_instance.log_progress(logger_name, percentage, message, stage, **kwargs)


# Global logger instance
_logger_instance: Optional[OCRLogger] = None


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (e.g., "PaddleOCREngine")
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = OCRLogger()
    return _logger_instance.get_logger(name)


def initialize_logger(mcp_notification_callback: Optional[Callable] = None):
    """Initialize the logger system.
    
    Args:
        mcp_notification_callback: Callback function to send MCP notifications
    """
    global _logger_instance
    _logger_instance = OCRLogger()
    if mcp_notification_callback:
        _logger_instance.set_mcp_callback(mcp_notification_callback)


def set_mcp_log_level(level: str):
    """Set MCP log level.
    
    Args:
        level: MCP log level (debug, info, warning, error, etc.)
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = OCRLogger()
    _logger_instance.set_mcp_log_level(level)

