#!/usr/bin/env python3
"""检查MCP配置的独立脚本。

可以在服务外部运行，检查配置状态。
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ocr_mcp_service.config_manager import MCPConfigManager


def main() -> None:
    """主函数。"""
    print("=" * 60)
    print("OCR MCP Service - 配置检查工具")
    print("=" * 60)
    print()

    manager = MCPConfigManager()
    status = manager.check_ocr_service_config()

    print("📁 项目信息:")
    print(f"  项目根目录: {manager.project_root}")
    print()

    print("📋 配置文件状态:")
    if status["config_file"]:
        print(f"  ✓ 配置文件: {status['config_file']}")
    else:
        print("  ✗ 配置文件不存在")
        print("  可能的配置文件位置:")
        for path in manager.config_paths:
            print(f"    - {path}")
    print()

    print("🔧 OCR服务配置状态:")
    if status["configured"]:
        print("  ✓ OCR服务已配置")
        print(f"  当前配置:")
        config = status["current_config"]
        print(f"    命令: {config.get('command', 'N/A')}")
        print(f"    参数: {config.get('args', [])}")
    else:
        print("  ✗ OCR服务未配置或配置无效")
        if status.get("config_error"):
            print(f"  错误: {status['config_error']}")
    print()

    print("📦 可执行文件状态:")
    if status["entry_point_exists"]:
        print(f"  ✓ Entry Point存在: {manager.project_root / '.venv' / 'bin' / 'ocr-mcp-server'}")
    else:
        print("  ✗ Entry Point不存在")
        print("  建议运行: uv pip install -e .")

    if status["venv_python_exists"]:
        print(f"  ✓ 虚拟环境Python存在: {manager.project_root / '.venv' / 'bin' / 'python'}")
    else:
        print("  ✗ 虚拟环境Python不存在")
        print("  建议运行: uv sync")
    print()

    if status["recommended_config"]:
        print("💡 推荐配置:")
        rec_config = status["recommended_config"]
        print(f"  命令: {rec_config['command']}")
        print(f"  参数: {rec_config['args']}")
        print()
        print("  可以添加到Cursor配置文件中:")
        print("  {")
        print('    "mcpServers": {')
        print('      "ocr-service": {')
        print(f'        "command": "{rec_config["command"]}",')
        print(f'        "args": {rec_config["args"]},')
        print('        "env": {}')
        print("      }")
        print("    }")
        print("  }")
    print()

    print("=" * 60)
    print("提示: 可以使用以下方式自动配置:")
    print("  1. 在MCP服务中调用 auto_configure_mcp() 工具")
    print("  2. 手动编辑配置文件并重启Cursor")
    print("=" * 60)


if __name__ == "__main__":
    main()

