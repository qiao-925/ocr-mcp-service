"""错误处理测试"""

import pytest
import tempfile
import os
from pathlib import Path
from ocr_mcp_service.ocr_engine import OCREngineFactory
from ocr_mcp_service.utils import validate_image, validate_image_path
from ocr_mcp_service.models import OCRResult, BoundingBox


def test_validate_image_path_nonexistent():
    """测试验证不存在的图片路径"""
    with pytest.raises(FileNotFoundError):
        validate_image_path("nonexistent_file.jpg")


def test_validate_image_nonexistent():
    """测试validate_image对不存在文件的处理"""
    with pytest.raises(FileNotFoundError):
        validate_image("nonexistent_file.jpg")


def test_validate_image_invalid():
    """测试validate_image对无效文件的处理"""
    # 创建一个临时文本文件（不是图片）
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("not an image")
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError, match="Invalid image file"):
            validate_image(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_engine_factory_unknown_engine():
    """测试引擎工厂对未知引擎的处理"""
    with pytest.raises(ValueError, match="Unknown engine"):
        OCREngineFactory.get_engine("unknown_engine")


def test_engine_factory_missing_dependencies():
    """测试引擎工厂对缺失依赖的处理"""
    # 测试一个可能未安装的引擎
    try:
        engine = OCREngineFactory.get_engine("deepseek")
        # 如果成功，说明已安装
        assert engine is not None
    except ImportError:
        # 如果失败，应该抛出ImportError
        pass
    except RuntimeError:
        # 或者RuntimeError（如果依赖部分安装但不可用）
        pass


def test_ocr_result_to_dict():
    """测试OCRResult的to_dict方法"""
    result = OCRResult(
        text="test text",
        boxes=[BoundingBox(x1=0, y1=0, x2=10, y2=10)],
        confidence=0.95,
        engine="test",
        processing_time=1.0
    )
    
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict)
    assert result_dict["text"] == "test text"
    assert len(result_dict["boxes"]) == 1
    assert result_dict["confidence"] == 0.95
    assert result_dict["engine"] == "test"
    assert result_dict["processing_time"] == 1.0


def test_ocr_result_empty():
    """测试空的OCRResult"""
    result = OCRResult(
        text="",
        boxes=[],
        confidence=0.0,
        engine="test",
        processing_time=0.0
    )
    
    result_dict = result.to_dict()
    
    assert result_dict["text"] == ""
    assert result_dict["boxes"] == []
    assert result_dict["confidence"] == 0.0


def test_bounding_box():
    """测试BoundingBox模型"""
    box = BoundingBox(x1=10.5, y1=20.5, x2=30.5, y2=40.5)
    
    assert box.x1 == 10.5
    assert box.y1 == 20.5
    assert box.x2 == 30.5
    assert box.y2 == 40.5


def test_ocr_result_with_analysis():
    """测试带分析的OCRResult"""
    result = OCRResult(
        text="test text",
        boxes=[],
        confidence=0.95,
        engine="test",
        processing_time=1.0,
        analysis="Test analysis"
    )
    
    result_dict = result.to_dict()
    
    assert "analysis" in result_dict
    assert result_dict["analysis"] == "Test analysis"
    
    # 测试get_text_with_analysis方法
    text_with_analysis = result.get_text_with_analysis()
    assert "test text" in text_with_analysis
    assert "Test analysis" in text_with_analysis

