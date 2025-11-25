"""基本功能测试。

测试模块导入和基本功能。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ocr_mcp_service.config import OCRConfig, default_config
from ocr_mcp_service.utils import format_bbox, setup_logging, validate_image_path


def test_config():
    """测试配置模块。"""
    assert default_config.use_angle_cls is True
    assert default_config.lang == "ch"
    assert default_config.log_dir.exists() or default_config.log_dir.parent.exists()
    print("✓ Config module test passed")


def test_utils():
    """测试工具模块。"""
    # 测试bbox格式化
    bbox = [[100.5, 50.3], [200.7, 50.3], [200.7, 80.9], [100.5, 80.9]]
    formatted = format_bbox(bbox)
    assert len(formatted) == 4
    assert formatted[0] == [round(100.5), round(50.3)]  # 四舍五入
    assert isinstance(formatted[0][0], int)
    assert isinstance(formatted[0][1], int)
    print("✓ Utils module test passed")


def test_validate_path():
    """测试路径验证。"""
    # 测试不存在的文件
    is_valid, error_msg, path = validate_image_path("/nonexistent/file.jpg")
    assert is_valid is False
    assert "不存在" in error_msg or "not found" in error_msg.lower()
    print("✓ Path validation test passed")


if __name__ == "__main__":
    print("Running basic tests...")
    test_config()
    test_utils()
    test_validate_path()
    print("\nAll basic tests passed!")

