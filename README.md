# OCR MCP Service

基于PaddleOCR 3.x的图片文字识别MCP服务器，为AI Agent提供OCR能力。

## 📋 项目简介

本服务实现了Model Context Protocol (MCP)服务器，将PaddleOCR的OCR能力封装为标准化工具，使AI Agent能够自动识别图片中的文字内容。

**核心特性**：
- ✅ 支持中文识别（使用PP-OCRv5_server模型，准确率约93%）
- ✅ 支持文件路径输入方式
- ✅ 返回结构化结果（文本+置信度+位置信息）
- ✅ 基于FastMCP框架，易于维护
- ✅ 使用uv管理依赖，现代化Python项目管理
- ✅ **自动MCP配置管理**：启动时检查配置，提供自动配置工具
- ✅ 开源免费，无API调用成本

## 📁 项目结构

```
ocr-mcp-service/
├── src/                          # 源代码目录
│   └── ocr_mcp_service/         # 主包目录
│       ├── __init__.py          # 包初始化文件
│       ├── config.py            # 配置管理模块
│       ├── config_manager.py    # MCP配置管理器（自动配置）
│       ├── utils.py             # 工具类模块（文件验证、日志配置）
│       ├── ocr_engine.py        # OCR引擎封装（PaddleOCR初始化）
│       ├── tools.py             # 工具函数模块（OCR识别+配置管理）
│       └── mcp_server.py         # MCP服务器主文件（FastMCP配置）
├── scripts/                      # 辅助脚本
│   └── check_mcp_config.py      # MCP配置检查脚本
├── tests/                        # 测试目录
│   └── test_images/             # 测试图片
├── mcp_ocr_server.py            # 主入口文件
├── pyproject.toml               # 项目配置和依赖（PEP 518/621标准）
├── uv.lock                      # 依赖锁文件
├── .gitignore                   # Git忽略文件
└── README.md                     # 项目文档
```

## 🔧 技术原理

### MCP协议

Model Context Protocol (MCP) 是一个标准化的协议，用于AI Agent与外部工具和服务进行通信。本服务通过MCP协议：

1. **通信方式**：使用stdio（标准输入输出）与Cursor等AI客户端通信
2. **工具注册**：将OCR识别功能注册为MCP工具
3. **数据格式**：使用JSON格式传递请求和响应

### PaddleOCR 3.x集成

本项目使用PaddleOCR 3.x版本，默认采用PP-OCRv5_server模型：

- **模型优势**：相比PP-OCRv4_server在多个场景中提升13个百分点
- **支持语言**：中文（ch）、英文（en）等
- **功能特性**：
  - 文本检测：定位图片中的文字区域
  - 文本识别：识别文字内容
  - 角度分类：自动检测和矫正文字方向

### 工作流程

```
用户请求（图片路径）
    ↓
MCP服务器接收请求
    ↓
验证文件路径
    ↓
初始化/获取OCR引擎（单例模式，延迟初始化）
    ↓
PaddleOCR识别图片
    ↓
解析识别结果（文本、置信度、位置）
    ↓
格式化返回结果
    ↓
返回JSON格式结果给AI Agent
```

## 🚀 快速开始

### 前置要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) 包管理器

### 安装uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 安装依赖

使用uv自动创建虚拟环境并安装依赖：

```bash
cd ocr-mcp-service
uv sync
```

这将自动：
- 创建虚拟环境（`.venv/`目录）
- 安装所有项目依赖
- 生成依赖锁文件（`uv.lock`）

### 安装项目（启用Entry Point）

安装项目后，可以使用 `ocr-mcp-server` 命令直接运行：

```bash
# 使用uv安装（开发模式）
uv pip install -e .

# 或使用传统pip
pip install -e .
```

安装后，可以在任何地方运行：
```bash
ocr-mcp-server
```

> 💡 **推荐**：Entry Point方式是Python标准实践，最简洁且适合生产环境。

### 配置Cursor

在Cursor的MCP配置文件中添加以下内容（请替换为实际路径）：

**配置文件位置**：
- Windows: `%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json` 或 `%USERPROFILE%\.cursor\mcp_settings.json`
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json` 或 `~/.cursor/mcp_settings.json`
- Linux: `~/.config/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json` 或 `~/.cursor/mcp_settings.json`

**配置内容（推荐：Entry Point方式）**：

这是最简洁且符合Python生产实践的方式。安装项目后，直接使用命令名运行：

```json
{
  "mcpServers": {
    "ocr-service": {
      "command": "/absolute/path/to/ocr-mcp-service/.venv/bin/ocr-mcp-server",
      "args": [],
      "env": {}
    }
  }
}
```

**安装项目（如果尚未安装）**：
```bash
cd /absolute/path/to/ocr-mcp-service
uv pip install -e .
# 或使用传统方式
pip install -e .
```

**配置内容（备选方式1：Python模块方式）**：

```json
{
  "mcpServers": {
    "ocr-service": {
      "command": "/absolute/path/to/ocr-mcp-service/.venv/bin/python",
      "args": [
        "-m",
        "ocr_mcp_service"
      ],
      "env": {}
    }
  }
}
```

**配置内容（备选方式2：直接运行脚本）**：

```json
{
  "mcpServers": {
    "ocr-service": {
      "command": "/absolute/path/to/ocr-mcp-service/.venv/bin/python",
      "args": [
        "/absolute/path/to/ocr-mcp-service/mcp_ocr_server.py"
      ],
      "env": {}
    }
  }
}
```

**重要提示**：
- 使用**绝对路径**，不要使用相对路径
- Windows路径使用正斜杠`/`或双反斜杠`\\`
- 配置完成后需要**重启Cursor**才能生效

### 自动配置MCP（推荐）

项目提供了自动配置功能，可以通过以下方式使用：

**方式1：使用MCP工具自动配置（最简单）**

在Cursor中，AI Agent可以调用配置工具：

```
用户：请帮我配置OCR MCP服务
AI：我将检查并自动配置OCR MCP服务...
```

工具会自动：
- 检测配置文件位置
- 检查当前配置状态
- 自动添加或更新配置
- 使用Entry Point方式（最推荐）

**方式2：使用配置检查脚本**

```bash
# 检查配置状态
uv run python scripts/check_mcp_config.py

# 脚本会显示：
# - 配置文件位置
# - 当前配置状态
# - 推荐配置内容
```

**方式3：手动配置**

按照上面的配置内容手动编辑配置文件。

### 运行服务器（测试）

有多种方式可以运行服务器：

**方式1：Entry Point方式（⭐ 推荐，最简洁）**
```bash
# 先安装项目（开发模式）
uv pip install -e .

# 然后直接运行命令
ocr-mcp-server
```

**方式2：Python模块方式**
```bash
# 使用uv自动管理虚拟环境
uv run python -m ocr_mcp_service

# 或直接使用python（需要先激活虚拟环境）
source .venv/bin/activate  # Linux/Mac
python -m ocr_mcp_service
```

**方式3：使用Makefile**
```bash
make run
```

**方式4：直接运行脚本**
```bash
uv run python mcp_ocr_server.py
```

如果看到服务器启动信息，说明安装成功。按`Ctrl+C`退出。

> 💡 **推荐**：Entry Point方式（方式1）最符合Python生产实践，命令简洁，适合Cursor配置。

## 📖 使用示例

### 基本使用

在Cursor中，AI Agent可以自动调用OCR功能：

```
用户：请识别这张图片中的文字：/path/to/image.jpg
AI：我将使用OCR服务识别图片中的文字...
```

### MCP配置管理工具

项目提供了两个MCP工具用于配置管理：

**1. `get_mcp_config_info` - 获取配置信息**

查询当前MCP配置状态：
- 配置文件位置
- OCR服务是否已配置
- 当前配置内容
- 推荐配置

**2. `auto_configure_mcp` - 自动配置**

自动检测并配置OCR服务：
- 检测配置文件位置
- 检查配置状态
- 自动创建或更新配置
- 使用Entry Point方式（推荐）

使用示例：
```
用户：检查OCR MCP配置状态
AI：调用 get_mcp_config_info() 工具...

用户：自动配置OCR服务
AI：调用 auto_configure_mcp() 工具...
```

### 返回结果格式

```json
{
  "success": true,
  "text": "识别出的完整文本\n换行分隔",
  "lines": [
    {
      "text": "识别出的文本",
      "confidence": 0.9876,
      "bbox": [[100, 50], [200, 50], [200, 80], [100, 80]]
    }
  ],
  "line_count": 1
}
```

### 错误处理

当识别失败时，返回格式：

```json
{
  "success": false,
  "error": "文件不存在: /path/to/image.jpg",
  "text": "",
  "lines": [],
  "line_count": 0
}
```

## 🔍 故障排查

### 问题1：uv命令未找到

**症状**：运行`uv sync`时提示命令未找到

**解决方案**：
1. 确认uv已正确安装
2. 检查PATH环境变量是否包含uv的安装路径
3. 重新安装uv：`curl -LsSf https://astral.sh/uv/install.sh | sh`

### 问题2：PaddleOCR初始化失败

**症状**：日志中出现"OCR引擎初始化失败"

**可能原因**：
1. 网络问题导致模型下载失败
2. 磁盘空间不足
3. 权限问题

**解决方案**：
1. 检查网络连接
2. 确保有足够的磁盘空间（模型文件约几百MB）
3. 检查文件权限
4. 查看日志文件：`logs/mcp_ocr_server.log`

### 问题3：文件路径识别失败

**症状**：返回"文件不存在"错误

**解决方案**：
1. 确认文件路径正确（使用绝对路径）
2. 检查文件权限
3. 确认文件格式支持（jpg, png, bmp等）

### 问题4：Cursor无法连接服务

**症状**：Cursor中无法使用OCR功能

**解决方案**：
1. 检查MCP配置文件路径和格式是否正确
2. 确认使用绝对路径
3. 重启Cursor
4. 检查日志文件查看错误信息

### 查看日志

日志文件位置：`logs/mcp_ocr_server.log`

```bash
# 查看最近50行日志
tail -n 50 logs/mcp_ocr_server.log

# 实时跟踪日志
tail -f logs/mcp_ocr_server.log
```

## 🛠️ 开发指南

### 代码规范

本项目遵循Python开发事实规范：

- ✅ PEP 8代码风格
- ✅ 类型注解（Type Hints）
- ✅ Google风格docstring
- ✅ 使用logging模块记录日志
- ✅ 具体异常类型捕获

### 项目依赖

主要依赖：
- `mcp>=1.0.0` - MCP Python SDK
- `paddleocr>=3.0.0` - OCR引擎
- `paddlepaddle>=3.0.0` - 深度学习框架
- `pillow>=10.0.0` - 图片处理
- `numpy>=1.24.0` - 数值计算

开发依赖：
- `black>=23.0.0` - 代码格式化
- `ruff>=0.1.0` - 代码检查
- `mypy>=1.0.0` - 类型检查
- `pytest>=7.0.0` - 测试框架

### 运行测试

```bash
# 安装测试依赖
uv sync --extra test

# 运行测试
uv run pytest
```

### 代码格式化

```bash
# 格式化代码
uv run black src/

# 检查代码
uv run ruff check src/
```

## 📚 参考文档

- [PaddleOCR 3.x 使用教程](https://www.paddleocr.ai/main/version3.x/pipeline_usage/OCR.html)
- [MCP协议文档](https://modelcontextprotocol.io/)
- [uv文档](https://github.com/astral-sh/uv)
- [Python项目运行方式指南](./PYTHON_RUNNING_GUIDE.md) - 详细了解Python项目的各种运行方式

## 📝 版本历史

### v0.1.0 (2025-01-XX)

- 初始版本
- 基于PaddleOCR 3.x（PP-OCRv5_server模型）
- 支持中文识别
- 模块化架构设计
- 使用uv管理依赖

## 📄 许可证

本项目采用开源许可证（具体许可证待定）

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**注意**：首次使用PaddleOCR会自动下载模型文件，可能需要一些时间。模型文件会缓存在`.paddleocr/`目录中。
