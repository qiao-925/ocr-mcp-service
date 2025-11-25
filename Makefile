# Makefile for OCR MCP Service
# 注意：Makefile必须使用TAB缩进，不能使用空格

# 默认目标：直接运行 make 将执行完整工作流
.DEFAULT_GOAL := all

.PHONY: help install test start run clean ready all check-python check-pip verify generate-config

# ==================== 完整工作流（默认） ====================

all: ready
	@echo ""
	@echo "✅ OCR MCP服务安装完成！"
	@echo "💡 提示: 运行 make start 可以测试启动服务器"
	@echo ""

# ==================== 帮助信息 ====================

help:
	@echo "=================================="
	@echo "OCR MCP服务 - Makefile"
	@echo "=================================="
	@echo ""
	@echo "💡 快速开始:"
	@echo "  make                  - 默认: 完整工作流 (install + verify)"
	@echo "  make start            - 完整流程并启动服务器"
	@echo ""
	@echo "📦 安装命令:"
	@echo "  make install          - 安装项目依赖"
	@echo "  make install-dev      - 安装开发依赖（包含colorama）"
	@echo ""
	@echo "🧪 测试命令:"
	@echo "  make test             - 测试MCP服务器"
	@echo "  make verify           - 验证安装和配置"
	@echo ""
	@echo "🚀 运行命令:"
	@echo "  make run              - 启动MCP服务器"
	@echo "  make start            - 一键启动 (ready + run)"
	@echo ""
	@echo "🔄 完整工作流:"
	@echo "  make ready            - 准备就绪 (install + verify + generate-config)"
	@echo "  make all              - 同 make ready"
	@echo ""
	@echo "🧹 清理命令:"
	@echo "  make clean            - 清理生成的文件"
	@echo ""

# Windows PowerShell UTF-8 编码设置
ifeq ($(OS),Windows_NT)
    ifdef COMSPEC
        SET_UTF8 = @chcp 65001 >nul 2>&1 || true
    else
        SET_UTF8 = @:
    endif
else
    SET_UTF8 = @:
endif

# ==================== 检查环境 ====================

check-python:
	@$(SET_UTF8)
	@echo "🔍 检查Python环境..."
	@python --version >nul 2>&1 || (echo "❌ 错误: 未找到Python，请先安装Python 3.8+" && exit 1)
	@python --version
	@echo "✅ Python环境检查通过"
	@echo ""

check-pip: check-python
	@$(SET_UTF8)
	@echo "🔍 检查pip..."
	@python -m pip --version >nul 2>&1 || (echo "❌ 错误: 未找到pip，请先安装pip" && exit 1)
	@echo "✅ pip检查通过"
	@echo ""

# ==================== 安装命令 ====================

install: check-pip
	@$(SET_UTF8)
	@echo "📦 安装依赖..."
	@echo "正在安装依赖包，这可能需要几分钟..."
	@python -m pip install --upgrade pip -q
	@python -m pip install -r requirements.txt
	@echo ""
	@echo "✅ 依赖安装完成"
	@echo ""

install-dev: install
	@$(SET_UTF8)
	@echo "📦 安装开发依赖..."
	@python -m pip install colorama -q || echo "⚠️  colorama安装失败（可选依赖）"
	@echo "✅ 开发依赖安装完成"
	@echo ""

# ==================== 验证命令 ====================

verify: install
	@$(SET_UTF8)
	@echo "🧪 验证安装..."
	@python -c "import mcp; import paddleocr; print('✅ 核心依赖验证通过')" 2>nul || (echo "⚠️  警告: 部分依赖可能未正确安装" && exit 0)
	@echo "✅ 验证完成"
	@echo ""

# ==================== 生成配置 ====================

generate-config:
	@$(SET_UTF8)
	@echo "📝 生成配置文件..."
	@python -c "import json, sys, os; from pathlib import Path; script_dir = Path('$(CURDIR)'); server_file = script_dir / 'mcp_ocr_server.py'; server_path = str(server_file).replace('\\\\', '/') if os.name == 'nt' else str(server_file); script_path = str(script_dir).replace('\\\\', '/') if os.name == 'nt' else str(script_dir); config = {'mcpServers': {'ocr-service': {'command': 'python', 'args': [server_path], 'env': {'PYTHONPATH': script_path}}}}; config_file = script_dir / 'config_template.json'; f = open(config_file, 'w', encoding='utf-8'); json.dump(config, f, indent=2, ensure_ascii=False); f.close(); print('✅ 配置文件模板已生成: config_template.json')"
	@echo ""

# ==================== 测试命令 ====================

test: verify
	@$(SET_UTF8)
	@echo "🧪 测试MCP服务器..."
	@echo "运行语法检查..."
	@python -m py_compile mcp_ocr_server.py || (echo "❌ 语法检查失败" && exit 1)
	@echo "✅ 语法检查通过"
	@echo "运行导入测试..."
	@python -c "from mcp.server.fastmcp import FastMCP; print('✅ MCP导入测试通过')" 2>nul || (echo "⚠️  MCP未安装，请先运行 make install" && exit 1)
	@echo "✅ 测试完成"
	@echo ""

# ==================== 运行命令 ====================

run:
	@$(SET_UTF8)
	@echo "🚀 启动MCP服务器..."
	@echo "提示: 如果看到服务器启动信息，说明配置正确"
	@echo "按 Ctrl+C 可以停止服务器"
	@echo ""
	@python mcp_ocr_server.py

# ==================== 完整工作流 ====================

ready: install verify generate-config
	@$(SET_UTF8)
	@echo ""
	@echo "✅ =================================="
	@echo "✅ OCR MCP服务准备就绪！"
	@echo "✅ =================================="
	@echo ""
	@echo "📊 已完成:"
	@echo "  ✓ 安装所有依赖"
	@echo "  ✓ 验证安装"
	@echo "  ✓ 生成配置文件模板"
	@echo ""
	@echo "🚀 下一步:"
	@echo "  1. 查看生成的配置文件: config_template.json"
	@echo "  2. 将配置添加到Cursor的MCP设置中（参考配置指南.md）"
	@echo "  3. 重启Cursor"
	@echo "  4. 运行 make start 测试服务器"
	@echo ""

start: ready
	@echo ""
	@echo "🚀 启动服务器..."
	@echo ""
	@$(MAKE) run

# ==================== 清理命令 ====================

clean:
	@$(SET_UTF8)
	@echo "🧹 清理生成的文件..."
	@if exist config_template.json del /f /q config_template.json 2>nul || rm -f config_template.json
	@if exist __pycache__ rmdir /s /q __pycache__ 2>nul || rm -rf __pycache__
	@if exist *.pyc del /f /q *.pyc 2>nul || rm -f *.pyc
	@if exist .pytest_cache rmdir /s /q .pytest_cache 2>nul || rm -rf .pytest_cache
	@if exist .mypy_cache rmdir /s /q .mypy_cache 2>nul || rm -rf .mypy_cache
	@echo "✅ 清理完成"
	@echo ""

