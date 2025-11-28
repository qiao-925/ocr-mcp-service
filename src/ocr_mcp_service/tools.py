"""MCP tool definitions."""

from pathlib import Path
from typing import Optional
from .mcp_server import mcp
from .ocr_engine import OCREngineFactory
from .utils import validate_image
from .logger import get_logger
from .prompt_loader import get_scenario_template
import re


@mcp.tool()
def recognize_image_paddleocr(image_path: str, lang: str = "ch") -> dict:
    """
    Recognize text in an image using PaddleOCR engine.
    
    This tool performs OCR recognition and returns the recognized text, bounding boxes,
    confidence scores, and technical analysis. For prompt templates/examples for image
    analysis, use the get_prompt_template tool separately.
    
    Args:
        image_path: Path to the image file
        lang: Language code (default: 'ch' for Chinese)
    
    Returns:
        OCR result dictionary containing:
        - text: Recognized text content
        - boxes: Bounding boxes for text regions
        - confidence: Average confidence score
        - engine: OCR engine name
        - processing_time: Processing time in seconds
        - analysis: Technical analysis (optional)
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
        OCR result dictionary containing:
        - text: Recognized text content
        - boxes: Bounding boxes for text regions
        - confidence: Average confidence score
        - engine: OCR engine name
        - processing_time: Processing time in seconds
        - analysis: Technical analysis (optional)
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
        OCR result dictionary containing:
        - text: Recognized text content
        - boxes: Bounding boxes for text regions
        - confidence: Average confidence score
        - engine: OCR engine name
        - processing_time: Processing time in seconds
        - analysis: Technical analysis (optional)
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
        OCR result dictionary containing:
        - text: Recognized text content
        - boxes: Bounding boxes for text regions
        - confidence: Average confidence score
        - engine: OCR engine name
        - processing_time: Processing time in seconds
        - analysis: Technical analysis (optional)
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
def get_prompt_template() -> dict:
    """
    Get general prompt template for image analysis.
    
    Returns:
        Dictionary with template.
    """
    logger = get_logger("tools.get_prompt_template")
    try:
        logger.info("MCP工具调用开始: get_prompt_template")
        template = get_scenario_template()
        logger.info("MCP工具调用成功: get_prompt_template")
        return {
            "template": template,
            "scenario_name": "通用模板"
        }
    except Exception as e:
        logger.error(f"MCP工具调用失败: get_prompt_template, 错误: {e}", exc_info=True)
        return {
            "error": str(e),
            "template": None
        }


def _get_usage_guide_file_path() -> Optional[Path]:
    """Get the path to the usage guide file."""
    # Try multiple locations
    try:
        # 1. In the installed package
        import importlib.resources
        with importlib.resources.files("ocr_mcp_service") as package_path:
            guide_path = package_path.parent.parent / "usage_guide.md"
            if guide_path.exists():
                return guide_path
    except Exception:
        pass
    
    # 2. In the project root (development mode)
    try:
        package_path = Path(__file__).parent.parent.parent
        guide_path = package_path / "usage_guide.md"
        if guide_path.exists():
            return guide_path
    except Exception:
        pass
    
    # 3. Try relative to current file
    try:
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        guide_path = project_root / "usage_guide.md"
        if guide_path.exists():
            return guide_path
    except Exception:
        pass
    
    return None


def _load_usage_guide_from_file() -> dict:
    """Load usage guide from file and parse into sections."""
    guide_path = _get_usage_guide_file_path()
    if guide_path is None:
        raise FileNotFoundError(
            "无法找到使用指南文件。请确保文件已正确安装或位于usage_guide.md"
        )
    
    try:
        with open(guide_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if not content.strip():
            raise ValueError("使用指南文件为空")
        
        # Split by "---" separator (markdown horizontal rule)
        # The file has three sections: guide, tips, examples
        parts = re.split(r'^---+$', content, flags=re.MULTILINE)
        
        if len(parts) >= 3:
            return {
                "guide": parts[0].strip(),
                "tips": parts[1].strip(),
                "examples": parts[2].strip()
            }
        elif len(parts) == 2:
            return {
                "guide": parts[0].strip(),
                "tips": parts[1].strip(),
                "examples": ""
            }
        else:
            # If no separator found, treat entire content as guide
            return {
                "guide": content.strip(),
                "tips": "",
                "examples": ""
            }
    except FileNotFoundError:
        raise
    except Exception as e:
        raise IOError(f"无法读取使用指南文件: {e}")


@mcp.tool()
def get_usage_guide() -> dict:
    """
    Get usage guide and tips for using OCR MCP service.
    
    This tool provides comprehensive usage instructions, tips, and examples
    for using the OCR MCP service effectively.
    
    Returns:
        Dictionary containing:
        - guide: Complete usage guide
        - tips: Usage tips and best practices
        - examples: Practical usage examples
    """
    logger = get_logger("tools.get_usage_guide")
    try:
        logger.info("MCP工具调用开始: get_usage_guide")
        
        # Load from file (will raise exception if file not found)
        guide = _load_usage_guide_from_file()
        
        logger.info("MCP工具调用成功: get_usage_guide")
        return guide
        
    except Exception as e:
        logger.error(f"MCP工具调用失败: get_usage_guide, 错误: {e}", exc_info=True)
        return {
            "error": str(e),
            "guide": None,
            "tips": None,
            "examples": None
        }

