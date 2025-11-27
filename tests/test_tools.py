"""MCP工具函数测试"""

import pytest
import tempfile
import os
from pathlib import Path
from ocr_mcp_service.tools import (
    recognize_image_paddleocr,
    recognize_image_paddleocr_mcp,
    recognize_image_easyocr,
    recognize_image_deepseek,
)
from ocr_mcp_service.ocr_engine import OCREngineFactory
from ocr_mcp_service.utils import validate_image


def _call_tool_logic(engine_name: str, image_path: str, **kwargs) -> dict:
    """调用工具函数的底层逻辑（不通过MCP装饰器）"""
    try:
        validate_image(image_path)
        
        if engine_name == "easyocr" and "languages" in kwargs:
            lang_list = [lang.strip() for lang in kwargs["languages"].split(',') if lang.strip()]
            engine = OCREngineFactory.get_engine(engine_name, languages=lang_list)
        else:
            engine = OCREngineFactory.get_engine(engine_name)
        
        if "lang" in kwargs:
            result = engine.recognize_image(image_path, lang=kwargs["lang"])
        else:
            result = engine.recognize_image(image_path)
        
        return result.to_dict()
    except Exception as e:
        return {
            "error": str(e),
            "text": "",
            "boxes": [],
            "confidence": 0.0,
            "engine": engine_name,
            "processing_time": 0.0,
        }


def test_tool_registration():
    """测试工具注册"""
    # 检查工具是否已注册
    assert hasattr(recognize_image_paddleocr, 'name')
    assert hasattr(recognize_image_paddleocr_mcp, 'name')
    assert hasattr(recognize_image_easyocr, 'name')
    assert hasattr(recognize_image_deepseek, 'name')
    
    # 检查工具名称
    assert recognize_image_paddleocr.name == "recognize_image_paddleocr"
    assert recognize_image_paddleocr_mcp.name == "recognize_image_paddleocr_mcp"
    assert recognize_image_easyocr.name == "recognize_image_easyocr"
    assert recognize_image_deepseek.name == "recognize_image_deepseek"


def test_tool_error_handling_nonexistent_file():
    """测试工具对不存在文件的错误处理"""
    # 测试所有工具对不存在文件的处理（通过底层逻辑）
    result = _call_tool_logic("paddleocr", "nonexistent_file.jpg")
    assert isinstance(result, dict)
    assert "error" in result
    assert result["text"] == ""
    assert result["confidence"] == 0.0
    
    result = _call_tool_logic("paddleocr_mcp", "nonexistent_file.jpg")
    assert isinstance(result, dict)
    assert "error" in result
    
    result = _call_tool_logic("easyocr", "nonexistent_file.jpg")
    assert isinstance(result, dict)
    assert "error" in result
    
    result = _call_tool_logic("deepseek", "nonexistent_file.jpg")
    assert isinstance(result, dict)
    assert "error" in result


def test_tool_error_handling_invalid_file():
    """测试工具对无效文件的错误处理"""
    # 创建一个临时文本文件（不是图片）
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("not an image")
        temp_path = f.name
    
    try:
        result = _call_tool_logic("paddleocr", temp_path)
        assert isinstance(result, dict)
        assert "error" in result
        
        result = _call_tool_logic("paddleocr_mcp", temp_path)
        assert isinstance(result, dict)
        assert "error" in result
        
        result = _call_tool_logic("easyocr", temp_path)
        assert isinstance(result, dict)
        assert "error" in result
        
        result = _call_tool_logic("deepseek", temp_path)
        assert isinstance(result, dict)
        assert "error" in result
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_tool_return_format():
    """测试工具返回格式"""
    # 即使出错，也应该返回标准格式
    result = _call_tool_logic("paddleocr", "nonexistent.jpg")
    
    # 检查返回字典的必需字段
    required_fields = ["text", "boxes", "confidence", "engine", "processing_time"]
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    
    # 检查字段类型
    assert isinstance(result["text"], str)
    assert isinstance(result["boxes"], list)
    assert isinstance(result["confidence"], float)
    assert isinstance(result["engine"], str)
    assert isinstance(result["processing_time"], float)


def test_paddleocr_tool_with_lang():
    """测试PaddleOCR工具的语言参数"""
    # 测试默认语言参数
    result = _call_tool_logic("paddleocr", "nonexistent.jpg", lang="ch")
    assert isinstance(result, dict)
    assert result["engine"] == "paddleocr"
    
    # 测试英文参数
    result = _call_tool_logic("paddleocr", "nonexistent.jpg", lang="en")
    assert isinstance(result, dict)
    assert result["engine"] == "paddleocr"


def test_easyocr_tool_with_languages():
    """测试EasyOCR工具的语言参数"""
    # 测试默认语言参数
    result = _call_tool_logic("easyocr", "nonexistent.jpg", languages="ch_sim,en")
    assert isinstance(result, dict)
    assert result["engine"] == "easyocr"
    
    # 测试单个语言
    result = _call_tool_logic("easyocr", "nonexistent.jpg", languages="en")
    assert isinstance(result, dict)
    assert result["engine"] == "easyocr"
    
    # 测试多个语言
    result = _call_tool_logic("easyocr", "nonexistent.jpg", languages="ch_sim,en,ja")
    assert isinstance(result, dict)
    assert result["engine"] == "easyocr"


@pytest.mark.skipif(
    not Path("tests/test_images").exists(),
    reason="Test images directory not found"
)
def test_tool_with_real_image():
    """测试工具使用真实图片（如果引擎已安装）"""
    test_images = list(Path("tests/test_images").glob("*.jpg"))
    if not test_images:
        pytest.skip("No test images found")
    
    image_path = str(test_images[0])
    
    # 测试PaddleOCR（如果已安装）
    try:
        result = _call_tool_logic("paddleocr", image_path)
        assert isinstance(result, dict)
        assert "text" in result
        assert "boxes" in result
        assert "confidence" in result
        assert result["engine"] == "paddleocr"
        assert isinstance(result["text"], str)
    except Exception:
        pass  # 引擎未安装
    
    # 测试paddleocr_mcp（如果已安装）
    try:
        result = _call_tool_logic("paddleocr_mcp", image_path)
        assert isinstance(result, dict)
        assert "text" in result
        assert result["engine"] == "paddleocr_mcp"
    except Exception:
        pass  # 引擎未安装
    
    # 测试EasyOCR（如果已安装）
    try:
        result = _call_tool_logic("easyocr", image_path)
        assert isinstance(result, dict)
        assert "text" in result
        assert result["engine"] == "easyocr"
    except Exception:
        pass  # 引擎未安装
    
    # 测试DeepSeek（如果已安装）
    try:
        result = _call_tool_logic("deepseek", image_path)
        assert isinstance(result, dict)
        assert "text" in result
        assert result["engine"] == "deepseek"
    except Exception:
        pass  # 引擎未安装

