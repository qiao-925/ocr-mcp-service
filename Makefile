# Makefile for OCR MCP Service
# 提供常用的项目管理和运行命令

.PHONY: help install run test clean format check

# 默认目标
.DEFAULT_GOAL := help

help: ## 显示帮助信息
	@echo "OCR MCP Service - 可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 安装项目依赖（使用uv）
	@echo "安装项目依赖..."
	uv sync
	@echo "✓ 依赖安装完成"

install-dev: ## 安装开发依赖
	@echo "安装开发依赖..."
	uv sync --extra dev
	@echo "✓ 开发依赖安装完成"

run: ## 运行MCP服务器（模块方式）
	@echo "启动MCP服务器..."
	uv run python -m ocr_mcp_service

run-script: ## 运行MCP服务器（脚本方式）
	@echo "启动MCP服务器..."
	uv run python mcp_ocr_server.py

test: ## 运行测试
	@echo "运行测试..."
	uv run pytest tests/ -v

test-basic: ## 运行基本功能测试
	@echo "运行基本功能测试..."
	uv run python tests/test_basic.py

format: ## 格式化代码
	@echo "格式化代码..."
	uv run black src/ tests/ mcp_ocr_server.py
	@echo "✓ 代码格式化完成"

check: ## 检查代码质量
	@echo "检查代码..."
	uv run ruff check src/ tests/ mcp_ocr_server.py
	@echo "✓ 代码检查完成"

lint: check ## lint检查（check的别名）

type-check: ## 类型检查
	@echo "类型检查..."
	uv run mypy src/
	@echo "✓ 类型检查完成"

clean: ## 清理缓存文件
	@echo "清理缓存文件..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	@echo "✓ 清理完成"

clean-logs: ## 清理日志文件
	@echo "清理日志文件..."
	rm -f logs/*.log 2>/dev/null || true
	@echo "✓ 日志清理完成"

clean-all: clean clean-logs ## 清理所有生成文件

verify: ## 验证安装和配置
	@echo "验证项目配置..."
	@uv run python -c "from ocr_mcp_service import __version__; print(f'Version: {__version__}')"
	@uv run python -c "from ocr_mcp_service.config import default_config; print(f'Config OK: {default_config.lang}')"
	@echo "✓ 验证通过"

