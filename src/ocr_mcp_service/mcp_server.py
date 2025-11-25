"""MCP服务器主文件。

配置FastMCP和工具注册。
"""

import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# 创建FastMCP服务器实例
mcp = FastMCP("OCR Service")

# 延迟导入工具函数以避免循环导入
# 工具函数会在首次使用时导入
def _register_tools() -> None:
    """注册所有工具函数。"""
    from ocr_mcp_service.tools import (
        auto_configure_mcp,
        get_mcp_config_info,
        recognize_text_from_path,
    )

    mcp.tool()(recognize_text_from_path)
    mcp.tool()(get_mcp_config_info)
    mcp.tool()(auto_configure_mcp)

# 立即注册工具
_register_tools()

