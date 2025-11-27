"""MCP tool definitions."""

import re
from pathlib import Path
from typing import Optional
from .mcp_server import mcp
from .ocr_engine import OCREngineFactory
from .utils import validate_image
from .config import LOG_FILE
from .logger import get_logger


@mcp.tool()
def recognize_image_paddleocr(image_path: str, lang: str = "ch") -> dict:
    """
    Recognize text in an image using PaddleOCR engine.
    
    Args:
        image_path: Path to the image file
        lang: Language code (default: 'ch' for Chinese)
    
    Returns:
        OCR result with text, bounding boxes, confidence, processing time, and technical analysis
    """
    try:
        # Validate image
        validate_image(image_path)
        
        # Get engine and recognize
        engine = OCREngineFactory.get_engine("paddleocr")
        result = engine.recognize_image(image_path, lang=lang)
        
        return result.to_dict()
    except Exception as e:
        return {
            "error": str(e),
            "text": "",
            "boxes": [],
            "confidence": 0.0,
            "engine": "paddleocr",
            "processing_time": 0.0,
        }


@mcp.tool()
def recognize_image_deepseek(image_path: str) -> dict:
    """
    Recognize text in an image using DeepSeek OCR engine.
    
    NOTE: This engine is NOT RECOMMENDED due to large model size (~7.8GB).
    Use recognize_image_paddleocr or recognize_image_paddleocr_mcp instead.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        OCR result with text, confidence, and processing time
    """
    try:
        # Validate image
        validate_image(image_path)
        
        # Get engine and recognize
        engine = OCREngineFactory.get_engine("deepseek")
        result = engine.recognize_image(image_path)
        
        return result.to_dict()
    except Exception as e:
        return {
            "error": str(e),
            "text": "",
            "boxes": [],
            "confidence": 0.0,
            "engine": "deepseek",
            "processing_time": 0.0,
        }


@mcp.tool()
def recognize_image_paddleocr_mcp(image_path: str) -> dict:
    """
    Recognize text in an image using paddleocr-mcp engine (subprocess).
    
    Args:
        image_path: Path to the image file
    
    Returns:
        OCR result with text, bounding boxes, confidence, and processing time
    """
    try:
        # Validate image
        validate_image(image_path)
        
        # Get engine and recognize
        engine = OCREngineFactory.get_engine("paddleocr_mcp")
        result = engine.recognize_image(image_path)
        
        return result.to_dict()
    except Exception as e:
        return {
            "error": str(e),
            "text": "",
            "boxes": [],
            "confidence": 0.0,
            "engine": "paddleocr_mcp",
            "processing_time": 0.0,
        }


@mcp.tool()
def recognize_image_easyocr(image_path: str, languages: str = "ch_sim,en") -> dict:
    """
    Recognize text in an image using EasyOCR engine.
    
    EasyOCR supports 80+ languages and is easy to use. Good for multilingual scenarios.
    
    Args:
        image_path: Path to the image file
        languages: Comma-separated language codes (default: 'ch_sim,en' for Chinese Simplified and English).
                  Common codes: 'en' (English), 'ch_sim' (Chinese Simplified), 'ch_tra' (Chinese Traditional),
                  'ja' (Japanese), 'ko' (Korean), 'fr' (French), 'de' (German), etc.
    
    Returns:
        OCR result with text, bounding boxes, confidence, and processing time
    """
    try:
        # Validate image
        validate_image(image_path)
        
        # Parse languages
        lang_list = [lang.strip() for lang in languages.split(',') if lang.strip()]
        
        # Get engine with specified languages
        engine = OCREngineFactory.get_engine("easyocr", languages=lang_list)
        result = engine.recognize_image(image_path)
        
        return result.to_dict()
    except Exception as e:
        return {
            "error": str(e),
            "text": "",
            "boxes": [],
            "confidence": 0.0,
            "engine": "easyocr",
            "processing_time": 0.0,
        }


@mcp.tool()
def get_recent_logs(
    lines: int = 100,
    level: Optional[str] = None,
    engine: Optional[str] = None,
    search: Optional[str] = None
) -> dict:
    """
    Get recent log entries from the OCR service log file.
    
    This tool provides a user-friendly way to view logs when MCP tools are being used.
    
    Args:
        lines: Number of recent log lines to return (default: 100, max: 1000)
        level: Filter by log level (debug/info/warning/error). Case insensitive.
        engine: Filter by OCR engine name (paddleocr/easyocr/deepseek/paddleocr_mcp). Case insensitive.
        search: Search for keyword in log messages. Case insensitive.
    
    Returns:
        Dictionary containing:
        - logs: List of log entries matching the filters
        - total: Total number of log entries read
        - filtered: Number of entries after filtering
    """
    try:
        log_file = Path(LOG_FILE)
        if not log_file.exists():
            return {
                "logs": [],
                "total": 0,
                "filtered": 0,
                "message": f"Log file not found: {LOG_FILE}"
            }
        
        # Read log file
        max_lines = min(lines, 1000)  # Cap at 1000 lines
        log_entries = []
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                # Get last N lines
                recent_lines = all_lines[-max_lines:] if len(all_lines) > max_lines else all_lines
        except Exception as e:
            logger = get_logger("tools")
            logger.error(f"Failed to read log file: {e}")
            return {
                "logs": [],
                "total": 0,
                "filtered": 0,
                "error": str(e)
            }
        
        # Parse log entries
        log_pattern = re.compile(
            r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+) \[([^\]]+)\] (.+)'
        )
        
        for line in recent_lines:
            line = line.strip()
            if not line:
                continue
            
            match = log_pattern.match(line)
            if match:
                timestamp, log_level, logger_name, message = match.groups()
                
                # Extract progress info if present
                progress = None
                stage = None
                if "progress=" in message:
                    progress_match = re.search(r'progress=(\d+(?:\.\d+)?)%', message)
                    if progress_match:
                        progress = float(progress_match.group(1))
                if "stage=" in message:
                    stage_match = re.search(r'stage=([^|]+)', message)
                    if stage_match:
                        stage = stage_match.group(1).strip()
                
                # Apply filters
                if level and log_level.upper() != level.upper():
                    continue
                
                if engine:
                    logger_lower = logger_name.lower()
                    engine_lower = engine.lower()
                    if engine_lower not in logger_lower:
                        continue
                
                if search and search.lower() not in message.lower():
                    continue
                
                log_entry = {
                    "timestamp": timestamp,
                    "level": log_level,
                    "logger": logger_name,
                    "message": message,
                }
                
                if progress is not None:
                    log_entry["progress"] = progress
                if stage:
                    log_entry["stage"] = stage
                
                log_entries.append(log_entry)
            else:
                # Handle non-standard log format
                if search and search.lower() not in line.lower():
                    continue
                log_entries.append({
                    "timestamp": "",
                    "level": "UNKNOWN",
                    "logger": "",
                    "message": line,
                })
        
        return {
            "logs": log_entries,
            "total": len(recent_lines),
            "filtered": len(log_entries)
        }
        
    except Exception as e:
        logger = get_logger("tools")
        logger.error(f"Error reading logs: {e}", exc_info=True)
        return {
            "logs": [],
            "total": 0,
            "filtered": 0,
            "error": str(e)
        }

