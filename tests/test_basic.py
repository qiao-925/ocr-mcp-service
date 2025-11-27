"""Basic functionality tests."""

import pytest
from pathlib import Path
from ocr_mcp_service.ocr_engine import OCREngineFactory
from ocr_mcp_service.utils import validate_image


def test_engine_factory():
    """Test engine factory."""
    # Test that factory raises error for unknown engine
    with pytest.raises(ValueError):
        OCREngineFactory.get_engine("unknown_engine")


def test_validate_image_nonexistent():
    """Test image validation with non-existent file."""
    with pytest.raises(FileNotFoundError):
        validate_image("nonexistent.jpg")


def test_validate_image_invalid():
    """Test image validation with invalid file."""
    import tempfile
    import os
    # Create a temporary invalid file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("not an image")
        temp_path = f.name
    try:
        with pytest.raises(ValueError):
            validate_image(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.skipif(
    not Path("tests/test_images").exists(),
    reason="Test images directory not found"
)
def test_paddleocr_engine_if_installed():
    """Test PaddleOCR engine if installed."""
    try:
        engine = OCREngineFactory.get_engine("paddleocr")
        # Test with a sample image if available
        test_images = list(Path("tests/test_images").glob("*.jpg"))
        if test_images:
            result = engine.recognize_image(str(test_images[0]))
            assert result.text is not None
            assert result.engine == "paddleocr"
    except ImportError:
        pytest.skip("PaddleOCR not installed")


@pytest.mark.skipif(
    not Path("tests/test_images").exists(),
    reason="Test images directory not found"
)
def test_deepseek_engine_if_installed():
    """Test DeepSeek OCR engine if installed."""
    try:
        engine = OCREngineFactory.get_engine("deepseek")
        # Test with a sample image if available
        test_images = list(Path("tests/test_images").glob("*.jpg"))
        if test_images:
            result = engine.recognize_image(str(test_images[0]))
            assert result.text is not None
            assert result.engine == "deepseek"
    except ImportError:
        pytest.skip("DeepSeek OCR dependencies not installed")

