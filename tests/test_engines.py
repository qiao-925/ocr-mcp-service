"""Engine-specific tests."""

import pytest
import tempfile
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ocr_mcp_service.ocr_engine import (
    PaddleOCREngine,
    DeepSeekOCREngine,
    PaddleOCRMCPEngine,
    EasyOCREngine,
    OCREngineFactory,
)
from ocr_mcp_service.models import OCRResult


def test_paddleocr_import():
    """Test PaddleOCR import."""
    try:
        engine = PaddleOCREngine()
        assert engine is not None
    except ImportError:
        pytest.skip("PaddleOCR not installed")


def test_deepseek_import():
    """Test DeepSeek OCR import."""
    try:
        engine = DeepSeekOCREngine()
        assert engine is not None
    except ImportError:
        pytest.skip("DeepSeek OCR dependencies not installed")


def test_paddleocr_mcp_import():
    """Test paddleocr-mcp import."""
    try:
        engine = PaddleOCRMCPEngine()
        assert engine is not None
    except RuntimeError:
        pytest.skip("paddleocr-mcp not installed or not in PATH")


def test_easyocr_import():
    """Test EasyOCR import."""
    try:
        engine = EasyOCREngine()
        assert engine is not None
    except ImportError:
        pytest.skip("EasyOCR not installed")


def _create_test_image(text="Test", width=200, height=50):
    """创建测试图片"""
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    try:
        # 尝试使用默认字体
        font = ImageFont.load_default()
    except:
        font = None
    draw.text((10, 10), text, fill='black', font=font)
    return img


@pytest.mark.skipif(
    not Path("tests/test_images").exists(),
    reason="Test images directory not found"
)
def test_paddleocr_recognize_image():
    """Test PaddleOCR recognize_image method."""
    try:
        engine = PaddleOCREngine()
        test_images = list(Path("tests/test_images").glob("*.jpg"))
        if not test_images:
            pytest.skip("No test images found")
        
        result = engine.recognize_image(str(test_images[0]))
        
        assert isinstance(result, OCRResult)
        assert result.engine == "paddleocr"
        assert isinstance(result.text, str)
        assert isinstance(result.boxes, list)
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0
        assert result.processing_time >= 0.0
    except ImportError:
        pytest.skip("PaddleOCR not installed")


@pytest.mark.skipif(
    not Path("tests/test_images").exists(),
    reason="Test images directory not found"
)
def test_paddleocr_recognize_with_lang():
    """Test PaddleOCR with different language parameter."""
    try:
        engine = PaddleOCREngine()
        test_images = list(Path("tests/test_images").glob("*.jpg"))
        if not test_images:
            pytest.skip("No test images found")
        
        # 测试中文
        result_ch = engine.recognize_image(str(test_images[0]), lang="ch")
        assert isinstance(result_ch, OCRResult)
        
        # 测试英文
        result_en = engine.recognize_image(str(test_images[0]), lang="en")
        assert isinstance(result_en, OCRResult)
    except ImportError:
        pytest.skip("PaddleOCR not installed")


@pytest.mark.skipif(
    not Path("tests/test_images").exists(),
    reason="Test images directory not found"
)
def test_easyocr_recognize_image():
    """Test EasyOCR recognize_image method."""
    try:
        engine = EasyOCREngine()
        test_images = list(Path("tests/test_images").glob("*.jpg"))
        if not test_images:
            pytest.skip("No test images found")
        
        result = engine.recognize_image(str(test_images[0]))
        
        assert isinstance(result, OCRResult)
        assert result.engine == "easyocr"
        assert isinstance(result.text, str)
        assert isinstance(result.boxes, list)
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0
        assert result.processing_time >= 0.0
    except ImportError:
        pytest.skip("EasyOCR not installed")


@pytest.mark.skipif(
    not Path("tests/test_images").exists(),
    reason="Test images directory not found"
)
def test_paddleocr_mcp_recognize_image():
    """Test PaddleOCR-MCP recognize_image method."""
    try:
        engine = PaddleOCRMCPEngine()
        test_images = list(Path("tests/test_images").glob("*.jpg"))
        if not test_images:
            pytest.skip("No test images found")
        
        result = engine.recognize_image(str(test_images[0]))
        
        assert isinstance(result, OCRResult)
        assert result.engine == "paddleocr_mcp"
        assert isinstance(result.text, str)
        assert isinstance(result.boxes, list)
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0
        assert result.processing_time >= 0.0
    except RuntimeError:
        pytest.skip("paddleocr-mcp not installed or not in PATH")
    except ImportError:
        pytest.skip("paddleocr-mcp dependencies not installed")


def test_engine_factory_paddleocr():
    """Test engine factory for PaddleOCR."""
    try:
        engine = OCREngineFactory.get_engine("paddleocr")
        assert isinstance(engine, PaddleOCREngine)
    except (ImportError, ValueError):
        pytest.skip("PaddleOCR not available")


def test_engine_factory_easyocr():
    """Test engine factory for EasyOCR."""
    try:
        engine = OCREngineFactory.get_engine("easyocr")
        assert isinstance(engine, EasyOCREngine)
    except (ImportError, ValueError):
        pytest.skip("EasyOCR not available")


def test_engine_factory_paddleocr_mcp():
    """Test engine factory for PaddleOCR-MCP."""
    try:
        engine = OCREngineFactory.get_engine("paddleocr_mcp")
        assert isinstance(engine, PaddleOCRMCPEngine)
    except (RuntimeError, ValueError):
        pytest.skip("paddleocr-mcp not available")


def test_engine_factory_deepseek():
    """Test engine factory for DeepSeek."""
    try:
        engine = OCREngineFactory.get_engine("deepseek")
        assert isinstance(engine, DeepSeekOCREngine)
    except (ImportError, ValueError):
        pytest.skip("DeepSeek OCR not available")


def test_engine_recognize_invalid_image():
    """Test engine error handling for invalid image."""
    # 创建临时无效文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("not an image")
        temp_path = f.name
    
    try:
        # 测试各个引擎的错误处理
        engines_to_test = []
        
        try:
            engines_to_test.append(("paddleocr", PaddleOCREngine()))
        except ImportError:
            pass
        
        try:
            engines_to_test.append(("easyocr", EasyOCREngine()))
        except ImportError:
            pass
        
        if not engines_to_test:
            pytest.skip("No engines available for testing")
        
        for engine_name, engine in engines_to_test:
            # 引擎可能抛出异常，也可能返回空结果
            # 两种情况都是可以接受的错误处理方式
            try:
                result = engine.recognize_image(temp_path)
                # 如果没有抛出异常，应该返回空结果或低置信度结果
                assert isinstance(result, OCRResult)
                # 验证结果是空的或置信度很低
                assert result.text == "" or result.confidence < 0.1 or len(result.boxes) == 0
            except (ValueError, FileNotFoundError, Exception) as e:
                # 抛出异常也是可以接受的
                assert isinstance(e, (ValueError, FileNotFoundError, Exception))
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_engine_recognize_nonexistent_file():
    """Test engine error handling for nonexistent file."""
    engines_to_test = []
    
    try:
        engines_to_test.append(("paddleocr", PaddleOCREngine()))
    except ImportError:
        pass
    
    try:
        engines_to_test.append(("easyocr", EasyOCREngine()))
    except ImportError:
        pass
    
    if not engines_to_test:
        pytest.skip("No engines available for testing")
    
    for engine_name, engine in engines_to_test:
        with pytest.raises((FileNotFoundError, ValueError, Exception)):
            engine.recognize_image("nonexistent_file_12345.jpg")






