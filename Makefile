# Makefile for OCR MCP Service
# 注意：Makefile必须使用TAB缩进，不能使用空格

# 默认目标：直接运行 make 将执行完整工作流
.DEFAULT_GOAL := all

.PHONY: help install test start stop clean all check-python check-pip verify generate-config status logs logs-tail

# ==================== 默认目标：一键安装 ====================

all: install verify generate-config
	@echo ""
	@echo "=================================="
	@echo "[OK] OCR MCP Service Ready!"
	@echo "=================================="
	@echo ""
	@echo "Installation completed:"
	@echo "  - Installed all dependencies"
	@echo "  - Verified installation"
	@echo "  - Generated configuration template"
	@echo ""
	@echo "Next step:"
	@echo "  1. Copy content from config_template.json"
	@echo "  2. Add to Cursor MCP settings (see README.md for location)"
	@echo "  3. Restart Cursor"
	@echo ""

# ==================== 帮助信息 ====================

help:
	@echo "=================================="
	@echo "OCR MCP Service - Makefile"
	@echo "=================================="
	@echo ""
	@echo "Quick Start:"
	@echo "  make                  - One-click install (install + verify + config)"
	@echo "  make start            - Test start server manually (optional)"
	@echo ""
	@echo "Install Commands:"
	@echo "  make install          - Install project dependencies"
	@echo "  make install-dev      - Install dev dependencies (includes colorama)"
	@echo ""
	@echo "Test Commands:"
	@echo "  make test             - Test MCP server"
	@echo "  make verify           - Verify installation and configuration"
	@echo ""
	@echo "Run Commands:"
	@echo "  make start            - Test start server manually (optional)"
	@echo ""
	@echo "Status & Logs:"
	@echo "  make status           - Check server running status"
	@echo "  make logs             - View recent log entries (last 50 lines)"
	@echo "  make logs-tail        - Tail log file (follow mode)"
	@echo ""
	@echo "Service Control:"
	@echo "  make stop             - Stop all OCR MCP service processes"
	@echo ""
	@echo "Clean Commands:"
	@echo "  make clean            - Clean generated files"
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
	@echo "[CHECK] Checking Python environment..."
	@python --version >nul 2>&1 || (echo "[ERROR] Python not found, please install Python 3.8+" && exit 1)
	@python --version
	@echo "[OK] Python environment check passed"
	@echo ""

check-pip: check-python
	@echo "[CHECK] Checking pip..."
	@python -m pip --version >nul 2>&1 || (echo "[ERROR] pip not found, please install pip" && exit 1)
	@echo "[OK] pip check passed"
	@echo ""

# ==================== 安装命令 ====================

install: check-pip
	@echo "[INSTALL] Installing dependencies..."
	@echo "[INFO] Installing packages, this may take a few minutes..."
	@python -m pip install --upgrade pip -q
	@python -m pip install -r requirements.txt
	@echo ""
	@echo "[OK] Dependencies installation complete"
	@echo ""

install-dev: install
	@echo "[INSTALL-DEV] Installing development dependencies..."
	@python -m pip install colorama -q || echo "[WARN] colorama installation failed (optional dependency)"
	@echo "[OK] Development dependencies installation complete"
	@echo ""

# ==================== 验证命令 ====================

verify: install
	@echo "[VERIFY] Verifying installation..."
	@python scripts/verify.py
	@echo "[OK] Verification complete"
	@echo ""

# ==================== 生成配置 ====================

generate-config:
	@echo "[CONFIG] Generating configuration file..."
	@python scripts/generate_config.py
	@echo ""

# ==================== 测试命令 ====================

test: verify
	@echo "[TEST] Testing MCP server..."
	@echo "[CHECK] Running syntax check..."
	@python -m py_compile mcp_ocr_server.py || (echo "[ERROR] Syntax check failed" && exit 1)
	@echo "[OK] Syntax check passed"
	@echo "[CHECK] Running import test..."
	@python -c "from mcp.server.fastmcp import FastMCP; print('[OK] MCP import test passed')" 2>nul || (echo "[WARN] MCP not installed, please run 'make install' first" && exit 1)
	@echo "[OK] Test complete"
	@echo ""


start: install verify
	@echo ""
	@echo "[START] Starting server for testing..."
	@echo "[INFO] Note: In production, Cursor will start the server automatically"
	@echo "[INFO] Press Ctrl+C to stop the server"
	@echo ""
	@python mcp_ocr_server.py

# ==================== 状态和日志命令 ====================

status:
	@echo "[STATUS] Checking OCR MCP service status..."
	@python scripts/check_status.py
	@echo ""

logs:
	@echo "[LOGS] Viewing recent log entries..."
	@python scripts/view_logs.py 50
	@echo ""

logs-tail:
	@echo "[LOGS] Tailing log file..."
	@python scripts/view_logs.py tail

# ==================== 服务控制命令 ====================

stop:
	@echo "[STOP] Stopping OCR MCP service..."
	@python scripts/stop_service.py
	@echo ""

# ==================== 清理命令 ====================

clean:
	@echo "[CLEAN] Cleaning generated files..."
	@if exist config_template.json del /f /q config_template.json 2>nul || rm -f config_template.json
	@if exist __pycache__ rmdir /s /q __pycache__ 2>nul || rm -rf __pycache__
	@if exist *.pyc del /f /q *.pyc 2>nul || rm -f *.pyc
	@if exist .pytest_cache rmdir /s /q .pytest_cache 2>nul || rm -rf .pytest_cache
	@if exist .mypy_cache rmdir /s /q .mypy_cache 2>nul || rm -rf .mypy_cache
	@echo "[OK] Cleanup complete"
	@echo ""

