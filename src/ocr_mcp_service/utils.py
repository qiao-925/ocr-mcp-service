"""工具类模块。

包含文件验证、日志配置等辅助函数。
"""

import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def setup_logging(
    log_file: Path,
    log_level: int = logging.INFO,
    format_string: str | None = None,
) -> None:
    """配置日志系统。

    Args:
        log_file: 日志文件路径
        log_level: 日志级别
        format_string: 日志格式字符串，默认使用标准格式
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 确保日志目录存在
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # 配置日志处理器
    handlers = [
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ]

    logging.basicConfig(
        level=log_level,
        format=format_string,
        handlers=handlers,
    )

    logger.info(f"日志系统已配置，日志文件: {log_file}")


def validate_image_path(image_path: str | Path) -> tuple[bool, str, Path | None]:
    """验证图片文件路径。

    Args:
        image_path: 图片文件路径

    Returns:
        tuple[bool, str, Path | None]: (是否有效, 错误信息, Path对象)
    """
    try:
        path = Path(image_path)

        if not path.exists():
            return False, f"文件不存在: {image_path}", None

        if not path.is_file():
            return False, f"路径不是文件: {image_path}", None

        # 检查文件扩展名（可选，但有助于提前发现问题）
        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif"}
        if path.suffix.lower() not in valid_extensions:
            logger.warning(f"文件扩展名可能不受支持: {path.suffix}")

        return True, "", path

    except Exception as e:
        return False, f"路径验证失败: {str(e)}", None


def format_bbox(bbox: list[Any] | tuple[Any, ...]) -> list[list[int]]:
    """格式化边界框坐标。

    Args:
        bbox: 边界框坐标，格式为 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

    Returns:
        格式化后的边界框坐标列表
    """
    formatted_bbox: list[list[int]] = []
    if isinstance(bbox, (list, tuple)):
        for point in bbox:
            if isinstance(point, (list, tuple)) and len(point) >= 2:
                try:
                    formatted_bbox.append([round(float(point[0])), round(float(point[1]))])
                except (ValueError, TypeError) as e:
                    logger.warning(f"格式化坐标点失败: {point}, 错误: {e}")
                    continue
    return formatted_bbox

