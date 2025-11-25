#!/bin/bash
# 生成当前环境的MCP配置信息

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${PROJECT_DIR}/.venv/bin/python"
ENTRY_POINT="${PROJECT_DIR}/.venv/bin/ocr-mcp-server"

echo "=========================================="
echo "OCR MCP Service - MCP配置生成器"
echo "=========================================="
echo ""
echo "项目路径: ${PROJECT_DIR}"
echo ""

# 检查entry point是否存在
if [ -f "${ENTRY_POINT}" ]; then
    echo "✓ Entry Point已安装: ${ENTRY_POINT}"
    RECOMMENDED_CONFIG="entry-point"
else
    echo "⚠ Entry Point未安装，请先运行: uv pip install -e ."
    RECOMMENDED_CONFIG="module"
fi

# 检查虚拟环境
if [ -f "${VENV_PYTHON}" ]; then
    echo "✓ 虚拟环境Python: ${VENV_PYTHON}"
else
    echo "⚠ 虚拟环境未找到，请先运行: uv sync"
    exit 1
fi

echo ""
echo "=========================================="
echo "推荐配置（Entry Point方式）"
echo "=========================================="
echo ""
cat <<EOF
{
  "mcpServers": {
    "ocr-service": {
      "command": "${ENTRY_POINT}",
      "args": [],
      "env": {}
    }
  }
}
EOF

echo ""
echo "=========================================="
echo "备选配置（Python模块方式）"
echo "=========================================="
echo ""
cat <<EOF
{
  "mcpServers": {
    "ocr-service": {
      "command": "${VENV_PYTHON}",
      "args": [
        "-m",
        "ocr_mcp_service"
      ],
      "env": {
        "PYTHONPATH": "${PROJECT_DIR}/src"
      }
    }
  }
}
EOF

echo ""
echo "=========================================="
echo "配置文件位置"
echo "=========================================="
echo ""
echo "Linux:   ~/.config/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json"
echo "        或 ~/.cursor/mcp_settings.json"
echo ""
echo "macOS:   ~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json"
echo "        或 ~/.cursor/mcp_settings.json"
echo ""
echo "Windows: %APPDATA%\\Cursor\\User\\globalStorage\\rooveterinaryinc.roo-cline\\settings\\cline_mcp_settings.json"
echo "        或 %USERPROFILE%\\.cursor\\mcp_settings.json"
echo ""
echo "=========================================="
echo "使用说明"
echo "=========================================="
echo "1. 复制上面的推荐配置"
echo "2. 添加到Cursor的MCP配置文件中"
echo "3. 重启Cursor"
echo ""

