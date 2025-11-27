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
    logger = get_logger("tools.recognize_image_paddleocr")
    try:
        logger.info(f"MCP工具调用开始: recognize_image_paddleocr, 图片路径: {image_path}, 语言: {lang}")
        
        # Validate image
        validate_image(image_path)
        
        # Get engine and recognize
        engine = OCREngineFactory.get_engine("paddleocr")
        result = engine.recognize_image(image_path, lang=lang)
        
        # Log result summary
        result_dict = result.to_dict()
        text_length = len(result_dict.get("text", ""))
        boxes_count = len(result_dict.get("boxes", []))
        confidence = result_dict.get("confidence", 0.0)
        processing_time = result_dict.get("processing_time", 0.0)
        
        logger.info(
            f"MCP工具调用成功: recognize_image_paddleocr, "
            f"识别文本长度: {text_length}字符, "
            f"文本块数量: {boxes_count}, "
            f"平均置信度: {confidence:.2f}, "
            f"处理时间: {processing_time:.2f}秒"
        )
        
        return result_dict
    except Exception as e:
        logger.error(f"MCP工具调用失败: recognize_image_paddleocr, 错误: {e}", exc_info=True)
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
    logger = get_logger("tools.recognize_image_deepseek")
    try:
        logger.info(f"MCP工具调用开始: recognize_image_deepseek, 图片路径: {image_path}")
        
        # Validate image
        validate_image(image_path)
        
        # Get engine and recognize
        engine = OCREngineFactory.get_engine("deepseek")
        result = engine.recognize_image(image_path)
        
        # Log result summary
        result_dict = result.to_dict()
        text_length = len(result_dict.get("text", ""))
        boxes_count = len(result_dict.get("boxes", []))
        confidence = result_dict.get("confidence", 0.0)
        processing_time = result_dict.get("processing_time", 0.0)
        
        logger.info(
            f"MCP工具调用成功: recognize_image_deepseek, "
            f"识别文本长度: {text_length}字符, "
            f"文本块数量: {boxes_count}, "
            f"平均置信度: {confidence:.2f}, "
            f"处理时间: {processing_time:.2f}秒"
        )
        
        return result_dict
    except Exception as e:
        logger.error(f"MCP工具调用失败: recognize_image_deepseek, 错误: {e}", exc_info=True)
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
    logger = get_logger("tools.recognize_image_paddleocr_mcp")
    try:
        logger.info(f"MCP工具调用开始: recognize_image_paddleocr_mcp, 图片路径: {image_path}")
        
        # Validate image
        validate_image(image_path)
        
        # Get engine and recognize
        engine = OCREngineFactory.get_engine("paddleocr_mcp")
        result = engine.recognize_image(image_path)
        
        # Log result summary
        result_dict = result.to_dict()
        text_length = len(result_dict.get("text", ""))
        boxes_count = len(result_dict.get("boxes", []))
        confidence = result_dict.get("confidence", 0.0)
        processing_time = result_dict.get("processing_time", 0.0)
        
        logger.info(
            f"MCP工具调用成功: recognize_image_paddleocr_mcp, "
            f"识别文本长度: {text_length}字符, "
            f"文本块数量: {boxes_count}, "
            f"平均置信度: {confidence:.2f}, "
            f"处理时间: {processing_time:.2f}秒"
        )
        
        return result_dict
    except Exception as e:
        logger.error(f"MCP工具调用失败: recognize_image_paddleocr_mcp, 错误: {e}", exc_info=True)
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
    logger = get_logger("tools.recognize_image_easyocr")
    try:
        logger.info(f"MCP工具调用开始: recognize_image_easyocr, 图片路径: {image_path}, 语言: {languages}")
        
        # Validate image
        validate_image(image_path)
        
        # Parse languages
        lang_list = [lang.strip() for lang in languages.split(',') if lang.strip()]
        
        # Get engine with specified languages
        engine = OCREngineFactory.get_engine("easyocr", languages=lang_list)
        result = engine.recognize_image(image_path)
        
        # Log result summary
        result_dict = result.to_dict()
        text_length = len(result_dict.get("text", ""))
        boxes_count = len(result_dict.get("boxes", []))
        confidence = result_dict.get("confidence", 0.0)
        processing_time = result_dict.get("processing_time", 0.0)
        
        logger.info(
            f"MCP工具调用成功: recognize_image_easyocr, "
            f"识别文本长度: {text_length}字符, "
            f"文本块数量: {boxes_count}, "
            f"平均置信度: {confidence:.2f}, "
            f"处理时间: {processing_time:.2f}秒"
        )
        
        return result_dict
    except Exception as e:
        logger.error(f"MCP工具调用失败: recognize_image_easyocr, 错误: {e}", exc_info=True)
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
    logger = get_logger("tools.get_recent_logs")
    try:
        filter_info = []
        if level:
            filter_info.append(f"级别={level}")
        if engine:
            filter_info.append(f"引擎={engine}")
        if search:
            filter_info.append(f"搜索={search}")
        filter_str = ", ".join(filter_info) if filter_info else "无过滤"
        logger.info(f"MCP工具调用开始: get_recent_logs, 行数={lines}, 过滤条件: {filter_str}")
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
        
        result = {
            "logs": log_entries,
            "total": len(recent_lines),
            "filtered": len(log_entries)
        }
        
        logger.info(
            f"MCP工具调用成功: get_recent_logs, "
            f"读取日志总数: {result['total']}, "
            f"过滤后数量: {result['filtered']}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"MCP工具调用失败: get_recent_logs, 错误: {e}", exc_info=True)
        return {
            "logs": [],
            "total": 0,
            "filtered": 0,
            "error": str(e)
        }

