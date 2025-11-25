"""OCR MCP服务器主入口文件。

使用FastMCP框架实现，支持通过MCP协议为AI Agent提供OCR能力。
默认使用PP-OCRv5_server模型，相比PP-OCRv4_server在多个场景中提升13个百分点。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from ocr_mcp_service.config import default_config
from ocr_mcp_service.mcp_server import mcp
from ocr_mcp_service.utils import setup_logging

# 配置日志系统
setup_logging(
    log_file=default_config.log_file,
    log_level=default_config.log_level,
)

if __name__ == "__main__":
    # 运行MCP服务器（使用stdio传输）
    mcp.run()
