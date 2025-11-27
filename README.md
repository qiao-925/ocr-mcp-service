# OCR MCP Service

统一的 OCR MCP 服务，支持多种 OCR 引擎，通过工具名称区分引擎。

## 🚀 快速开始

### 1. 安装

```bash
# 使用 uv（推荐）
uv venv
uv pip install -e ".[paddleocr]"

# 或使用 pip
pip install -e ".[paddleocr]"
```

### 2. 配置 Cursor

```bash
# 自动配置（推荐）
python scripts/setup_cursor.py

# 配置完成后，重启 Cursor 即可使用
```

### 3. 使用

在 Cursor 中直接调用工具：

```
请使用 recognize_image_paddleocr 工具识别图片：图片路径
```

---

## 📦 支持的引擎

| 引擎 | 工具名称 | 推荐度 | 说明 |
|------|---------|--------|------|
| **PaddleOCR** | `recognize_image_paddleocr` | ⭐⭐⭐⭐⭐ | 中文优秀，推荐使用 |
| **paddleocr-mcp** | `recognize_image_paddleocr_mcp` | ⭐⭐⭐⭐⭐ | 官方 MCP 实现 |
| **EasyOCR** | `recognize_image_easyocr` | ⭐⭐⭐⭐ | 支持 80+ 语言 |
| **DeepSeek OCR** | `recognize_image_deepseek` | ⭐⭐ | 模型较大（~7.8GB） |

## 🛠️ 可用工具

- `recognize_image_paddleocr` - PaddleOCR 识别（推荐）
- `recognize_image_paddleocr_mcp` - paddleocr-mcp 识别（推荐）
- `recognize_image_easyocr` - EasyOCR 识别（多语言）
- `recognize_image_deepseek` - DeepSeek OCR 识别（可选）
- `get_recent_logs` - 获取最近的日志记录

## 📋 常用命令

```bash
# 查看日志
ocr-tail-logs

# 检查配置
python scripts/check_mcp_config.py

# 验证引擎
python scripts/verify_engines.py
```

---

## 📚 详细文档

- **[完整文档](docs/README.md)** - 查看所有文档索引
- **[API 参考](docs/build_plan.md)** - 完整的工具 API 文档
- **[引擎对比](docs/archive/ENGINE_RECOMMENDATION.md)** - 引擎选择指南
- **[日志查看](docs/log_viewing.md)** - 日志查看方法

---

## 🔧 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/
ruff check src/
```

---

## 📄 许可证

MIT
