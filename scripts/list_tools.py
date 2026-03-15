"""Print the MCP tools exposed by the simplified OCR service."""

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))


def main() -> None:
    """Print the currently registered MCP tool names."""
    from local_ocr_mcp.server import mcp, ocr_health_check, ocr_recognize

    tools = [
        ("ocr_recognize", ocr_recognize, "本地图片 OCR"),
        ("ocr_health_check", ocr_health_check, "运行时健康检查"),
    ]

    print("=" * 60)
    print(f"MCP Server: {mcp.name}")
    print("=" * 60)
    for index, (name, tool, description) in enumerate(tools, start=1):
        tool_name = getattr(tool, "name", getattr(tool, "__name__", name))
        print(f"{index}. {name}")
        print(f"   MCP Name: {tool_name}")
        print(f"   Description: {description}")
    print("=" * 60)
    print(f"Total: {len(tools)} tools")


if __name__ == "__main__":
    main()
