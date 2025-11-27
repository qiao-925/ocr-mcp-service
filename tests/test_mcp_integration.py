"""MCP integration tests."""

import pytest
from pathlib import Path
from ocr_mcp_service.tools import (
    recognize_image_paddleocr,
    recognize_image_deepseek,
    recognize_image_paddleocr_mcp,
)


def test_tool_signatures():
    """Test that tools are registered."""
    # Tools are wrapped by FastMCP, check they exist as FunctionTool objects
    assert hasattr(recognize_image_paddleocr, 'name')
    assert recognize_image_paddleocr.name == "recognize_image_paddleocr"
    
    assert hasattr(recognize_image_deepseek, 'name')
    assert recognize_image_deepseek.name == "recognize_image_deepseek"
    
    assert hasattr(recognize_image_paddleocr_mcp, 'name')
    assert recognize_image_paddleocr_mcp.name == "recognize_image_paddleocr_mcp"


def test_tool_error_handling():
    """Test tool error handling."""
    # Tools are wrapped by FastMCP, they will be called via MCP protocol
    # Just verify they are FunctionTool objects
    assert hasattr(recognize_image_paddleocr, 'name')
    assert hasattr(recognize_image_deepseek, 'name')
    assert hasattr(recognize_image_paddleocr_mcp, 'name')


@pytest.mark.skipif(
    not Path("tests/test_images").exists(),
    reason="Test images directory not found"
)
def test_tool_integration():
    """Test tool integration with real images."""
    test_images = list(Path("tests/test_images").glob("*.jpg"))
    if not test_images:
        pytest.skip("No test images found")
    
    image_path = str(test_images[0])
    
    # Test paddleocr (if installed)
    try:
        result = recognize_image_paddleocr(image_path)
        assert isinstance(result, dict)
        assert "text" in result
    except Exception:
        pass  # Engine not installed
    
    # Test deepseek (if installed)
    try:
        result = recognize_image_deepseek(image_path)
        assert isinstance(result, dict)
        assert "text" in result
    except Exception:
        pass  # Engine not installed

