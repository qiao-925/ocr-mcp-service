# OCR MCP Service

统一的 OCR MCP 服务，支持多种 OCR 引擎，通过工具名称区分引擎。

## 🚀 快速开始

### 1. 安装

**基础安装（必须）：**
```bash
# 使用 uv（推荐）
uv venv
uv pip install -e .

# 或使用 pip
pip install -e .
```

**安装 OCR 引擎（至少选择一个）：**

```bash
# PaddleOCR（推荐，中文优秀）
uv pip install -e ".[paddleocr]"
# 或
pip install -e ".[paddleocr]"

# EasyOCR（支持 80+ 语言）
uv pip install -e ".[easyocr]"
# 或
pip install -e ".[easyocr]"

# DeepSeek OCR（高准确率，模型较大 ~7.8GB）
uv pip install -e ".[deepseek]"
# 或
pip install -e ".[deepseek]"

# 安装多个引擎
uv pip install -e ".[paddleocr,easyocr]"
# 或
pip install -e ".[paddleocr,easyocr]"
```

> **注意**：`paddleocr-mcp` 工具使用 PaddleOCR 引擎，安装 `paddleocr` 后即可使用。

### 2. 配置 Cursor

```bash
# 自动配置（推荐）
python scripts/setup_cursor.py

# 配置完成后，重启 Cursor 即可使用
```

### 3. MCP 服务器启动

**重要说明**：MCP 服务器由 Cursor 自动启动，无需手动启动。

**工作原理**：
- Cursor 会根据配置文件（`~/.cursor/mcp.json`）自动启动 MCP 服务器
- 服务器通过 stdio（标准输入输出）与 Cursor 通信
- 当你在 Cursor 中调用工具时，Cursor 会自动启动服务器并发送请求

**手动测试服务器**（可选）：

如果你想手动测试服务器是否正常工作：

```bash
# 直接运行服务器（会通过 stdio 通信）
ocr-mcp-server

# 或使用 Python 模块方式
python -m ocr_mcp_service
```

**验证服务器配置**：

```bash
# 检查 MCP 配置是否正确
python scripts/check_mcp_config.py

# 验证服务器命令是否可用
which ocr-mcp-server
# 或
ocr-mcp-server --help
```

**故障排查**：

如果服务器无法启动，检查：
1. 是否已安装：`pip list | grep ocr-mcp-service`
2. 命令是否在 PATH 中：`which ocr-mcp-server`
3. 查看 Cursor 的 MCP 日志（在输出面板中选择 "MCP"）
4. 查看 OCR 服务日志：查看 `logs/ocr_service.log` 文件

### 4. 使用

在 Cursor 中直接调用工具：

```
请使用 recognize_image_paddleocr 工具识别图片：图片路径
```

**获取使用指南**：

```
# 获取完整的使用指南和技巧
请使用 get_usage_guide 工具获取使用说明
```

**使用示例Prompt模板**：

```
使用示例prompt模板识别这张图片：图片路径
```

或批量处理：

```
使用示例prompt模板识别这个文件夹：文件夹路径
```

---

## 💡 实际使用案例

### 案例 1：识别一张图片

假设你有一张图片 `东野圭吾图片测试集/IMG_20251124_220855.jpg`，在 Cursor 中直接说：

```
请使用 recognize_image_paddleocr 工具识别这张图片：东野圭吾图片测试集/IMG_20251124_220855.jpg
```

或者：

```
识别这张图片中的文字：东野圭吾图片测试集/IMG_20251124_220855.jpg
```

### 案例 2：使用不同引擎

**中文文档（推荐 PaddleOCR）：**
```
使用 recognize_image_paddleocr 识别：图片路径
```

**多语言文档（使用 EasyOCR）：**
```
使用 recognize_image_easyocr 识别：图片路径
```

**使用官方 MCP 实现：**
```
使用 recognize_image_paddleocr_mcp 识别：图片路径
```

### 案例 3：获取使用指南

```
请使用 get_usage_guide 工具获取使用说明和技巧
```

### 案例 4：使用示例Prompt模板

**单张图片：**
```
使用示例prompt模板识别这张图片：东野圭吾图片测试集/IMG_20251124_220855.jpg
```

**批量处理：**
```
使用示例prompt模板识别这个文件夹：东野圭吾图片测试集/
```

### 案例 6：查看日志

**在 Cursor 中查看 MCP 日志**：
- 打开输出面板（`Ctrl+Shift+U` / `Cmd+Shift+U`），选择 "MCP" 查看实时日志

**使用命令行查看日志**：

```bash
python scripts/tail_logs.py                    # 实时查看所有日志
python scripts/tail_logs.py --lines 50         # 显示最近50行
python scripts/tail_logs.py --level ERROR      # 只查看错误日志
python scripts/tail_logs.py --engine PaddleOCR # 只查看PaddleOCR引擎日志
python scripts/tail_logs.py --search "初始化"   # 搜索包含"初始化"的日志
```

---

## 🛠️ 可用工具

| 工具名称 | 用途 | 推荐场景 |
|---------|------|---------|
| `recognize_image_paddleocr` | PaddleOCR 识别 | 中文文档（推荐） |
| `recognize_image_paddleocr_mcp` | paddleocr-mcp 识别 | 官方 MCP 实现 |
| `recognize_image_easyocr` | EasyOCR 识别 | 多语言文档（80+语言） |
| `recognize_image_deepseek` | DeepSeek OCR 识别 | 高准确率需求（模型较大） |
| `get_prompt_template` | 获取通用 Prompt 模板 | 获取图片分析通用模板 |
| `get_usage_guide` | 获取使用指南 | 使用说明和技巧 |

---

## 📋 常用命令

```bash
# 查看日志
python scripts/tail_logs.py

# 检查 MCP 配置
python scripts/check_mcp_config.py

# 验证引擎是否正常
python scripts/verify_engines.py

# 列出所有可用工具
python scripts/list_tools.py
```

---

---

## 📚 了解更多

- **[Prompt 模板指南](prompt_template.md)** - 完整的图片分析工作流指南，包含通用模板和最佳实践
- **[详细文档](docs/README.md)** - 完整的文档索引，包含实现细节、方案对比、技术文档
- **[API 参考](docs/构建计划.md)** - 所有工具的详细 API 文档
- **[引擎对比](docs/OCR完整指南.md)** - 各引擎的详细对比和测试报告

### 📖 Prompt 模板使用

本工具提供了完整的图片分析 Prompt 指南，帮助你更好地使用 OCR 工具进行图片分析。指南包含：

- **架构说明**：三部分数据流（OCR技术结果、视觉识别、Agent总结）
- **统一处理流程**：单个图片视为批量处理中只有一个元素的情况
- **通用模板**：灵活的通用 Prompt 模板，可根据需求调整
- **结果存储**：文件夹结构和文件命名规范
- **快速参考**：最佳实践和使用技巧

**获取方式**：
- 在 Cursor 中使用 `get_prompt_template` 工具获取模板
- 或直接查看 `prompt_template.md` 文档

---

## 📄 许可证

MIT
