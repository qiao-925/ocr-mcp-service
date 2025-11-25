"""工具函数模块。

包含OCR识别函数和结果格式化。
"""

import logging
from pathlib import Path
from typing import Any

from ocr_mcp_service.config import default_config
from ocr_mcp_service.config_manager import MCPConfigManager
from ocr_mcp_service.ocr_engine import OCREngine
from ocr_mcp_service.utils import validate_image_path

logger = logging.getLogger(__name__)

# 全局配置管理器实例
_config_manager = MCPConfigManager()


# 注意：recognize_text_from_path的@mcp.tool()装饰器在mcp_server.py中注册


def recognize_text_from_path(image_path: str) -> dict[str, Any]:
    """从图片文件路径识别文字。

    使用PaddleOCR 3.x（PP-OCRv5_server模型）识别图片中的文字，
    返回结构化结果，包括文本、置信度和位置信息。

    Args:
        image_path: 图片文件的路径（绝对路径或相对路径）

    Returns:
        包含识别结果的字典：
        - success: 是否成功
        - text: 识别出的完整文本（换行符分隔）
        - lines: 按行组织的识别结果列表，每行包含：
            - text: 识别的文本
            - confidence: 置信度（0-1）
            - bbox: 边界框坐标 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        - line_count: 识别到的文本行数
        - error: 错误信息（如果失败）

    Example:
        >>> result = recognize_text_from_path("/path/to/image.jpg")
        >>> if result["success"]:
        ...     print(result["text"])
        ...     print(f"识别到 {result['line_count']} 行文字")
    """
    try:
        # 验证文件路径
        is_valid, error_msg, path = validate_image_path(image_path)
        if not is_valid or path is None:
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "text": "",
                "lines": [],
                "line_count": 0,
            }

        logger.info(f"开始OCR识别: {image_path}")

        # 获取OCR实例并执行识别
        ocr = OCREngine.get_instance()
        # PaddleOCR 3.x使用predict方法，返回OCRResult对象列表
        result = ocr.predict(str(path))

        # 解析识别结果
        full_text, lines = OCREngine.parse_result(result)

        logger.info(f"OCR识别完成，共识别 {len(lines)} 个文本块")

        return {
            "success": True,
            "text": full_text,
            "lines": lines,
            "line_count": len(lines),
        }

    except FileNotFoundError as e:
        error_msg = f"文件未找到: {image_path}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "error": error_msg,
            "text": "",
            "lines": [],
            "line_count": 0,
        }
    except PermissionError as e:
        error_msg = f"文件访问权限不足: {image_path}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "error": error_msg,
            "text": "",
            "lines": [],
            "line_count": 0,
        }
    except RuntimeError as e:
        error_msg = f"OCR引擎错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "error": error_msg,
            "text": "",
            "lines": [],
            "line_count": 0,
        }
    except Exception as e:
        error_msg = f"OCR识别失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "error": error_msg,
            "text": "",
            "lines": [],
            "line_count": 0,
        }


def get_mcp_config_info() -> dict[str, Any]:
    """获取MCP配置信息。

    检查当前Cursor MCP配置状态，包括：
    - 配置文件位置
    - OCR服务是否已配置
    - 当前配置内容
    - 推荐配置

    Returns:
        包含配置信息的字典：
        - project_root: 项目根目录
        - config_status: 配置状态
        - possible_config_paths: 可能的配置文件路径列表
        - entry_point_path: Entry Point路径
        - venv_python_path: 虚拟环境Python路径
        - entry_point_exists: Entry Point是否存在
        - venv_python_exists: 虚拟环境Python是否存在
    """
    try:
        info = _config_manager.get_config_info()
        logger.info("MCP配置信息查询成功")
        return {
            "success": True,
            **info,
        }
    except Exception as e:
        logger.error(f"获取配置信息失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


def auto_configure_mcp(force: bool = False) -> dict[str, Any]:
    """自动配置MCP服务。

    自动检测并配置Cursor MCP服务，如果配置不存在或无效则自动创建/更新。

    Args:
        force: 是否强制更新现有配置，默认False

    Returns:
        配置结果字典：
        - success: 是否成功
        - action: 执行的操作（created/updated/skipped/failed）
        - config_file: 配置文件路径
        - message: 结果消息
    """
    try:
        result = _config_manager.auto_configure(force=force)
        logger.info(f"MCP自动配置完成: {result['action']}")
        return result
    except Exception as e:
        logger.error(f"自动配置失败: {e}", exc_info=True)
        return {
            "success": False,
            "action": "failed",
            "message": f"自动配置失败: {str(e)}",
            "config_file": None,
        }

