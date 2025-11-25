"""模块入口点。

支持通过 `python -m ocr_mcp_service` 方式运行。
"""

import sys
from pathlib import Path

# 确保可以导入模块（开发模式下）
if Path(__file__).parent.parent.parent not in [Path(p) for p in sys.path]:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging

from ocr_mcp_service.config import default_config
from ocr_mcp_service.mcp_server import mcp
from ocr_mcp_service.utils import setup_logging

logger = logging.getLogger(__name__)


def main(check_config: bool = False) -> None:
    """主函数入口。

    Args:
        check_config: 是否在启动时检查MCP配置，默认False
    """
    # 配置日志系统
    setup_logging(
        log_file=default_config.log_file,
        log_level=default_config.log_level,
    )

    # 可选：检查MCP配置
    if check_config:
        from ocr_mcp_service.config_manager import MCPConfigManager

        config_manager = MCPConfigManager()
        status = config_manager.check_ocr_service_config()
        if not status["configured"]:
            logger.warning("MCP配置未检测到或无效")
            logger.info("可以使用以下方式配置：")
            logger.info("1. 调用 auto_configure_mcp() 工具自动配置")
            logger.info("2. 调用 get_mcp_config_info() 工具查看配置信息")
            if status["recommended_config"]:
                logger.info(f"推荐配置: {status['recommended_config']}")

    # 运行MCP服务器（使用stdio传输）
    mcp.run()


if __name__ == "__main__":
    main()

