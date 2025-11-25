# Cursor 配置 PaddleOCR MCP Server 指南

## 📋 配置步骤

### 1. 安装 PaddleOCR MCP

根据 PaddleOCR 官方文档，选择一种安装方式：

**方式1：从 wheel 文件安装**
```bash
pip install https://paddle-model-ecology.bj.bcebos.com/paddlex/PaddleX3.0/mcp/paddleocr_mcp/releases/v0.2.1/paddleocr_mcp-0.2.1-py3-none-any.whl
```

**方式2：从源码安装**
```bash
git clone https://github.com/PaddlePaddle/PaddleOCR.git
cd PaddleOCR/mcp_server
pip install -e .
```

**方式3：使用 uvx（无需安装）**
```bash
# 先安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装 PaddleOCR（本地模式需要）

如果使用本地 Python 库模式，需要安装 PaddleOCR：

```bash
# 安装 PaddleOCR（CPU版本）
pip install paddleocr paddlepaddle

# 或使用 extras
pip install "paddleocr-mcp[local-cpu] @ https://paddle-model-ecology.bj.bcebos.com/paddlex/PaddleX3.0/mcp/paddleocr_mcp/releases/v0.2.1/paddleocr_mcp-0.2.1-py3-none-any.whl"
```

### 3. 配置 Cursor MCP

#### 配置文件位置

Cursor 的 MCP 配置文件可能位于以下位置之一：

- **Linux**: `~/.config/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json` 或 `~/.cursor/mcp_settings.json`
- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json` 或 `~/.cursor/mcp_settings.json`
- **Windows**: `%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json` 或 `%USERPROFILE%\.cursor\mcp_settings.json`

如果文件不存在，需要手动创建。

#### 配置内容

根据不同的工作模式，选择对应的配置：

##### 模式1：本地 Python 库模式（推荐用于离线/隐私场景）

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
      }
    }
  }
}
```

**如果 `paddleocr_mcp` 不在 PATH 中，使用绝对路径：**
```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "/path/to/venv/bin/paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
      }
    }
  }
}
```

##### 模式2：AI Studio 社区服务模式（适合快速测试）

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
        "PADDLEOCR_MCP_SERVER_URL": "https://xxxxxx.aistudio-hub.baidu.com",
        "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

**使用 uvx 方式（无需安装）：**
```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "uvx",
      "args": [
        "--from",
        "paddleocr-mcp@https://paddle-model-ecology.bj.bcebos.com/paddlex/PaddleX3.0/mcp/paddleocr_mcp/releases/v0.2.1/paddleocr_mcp-0.2.1-py3-none-any.whl",
        "paddleocr_mcp"
      ],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "aistudio",
        "PADDLEOCR_MCP_SERVER_URL": "https://xxxxxx.aistudio-hub.baidu.com",
        "PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

##### 模式3：自托管服务模式（适合定制化需求）

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "self_hosted",
        "PADDLEOCR_MCP_SERVER_URL": "http://127.0.0.1:8000"
      }
    }
  }
}
```

##### 使用 PP-StructureV3 管道（文档结构识别）

将 `PADDLEOCR_MCP_PIPELINE` 改为 `PP-StructureV3`：

```json
{
  "mcpServers": {
    "paddleocr-structure": {
      "command": "paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "PP-StructureV3",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
      }
    }
  }
}
```

### 4. 验证配置

1. **检查命令是否可用**：
```bash
paddleocr_mcp --help
```

2. **重启 Cursor**：配置完成后必须重启 Cursor 才能生效

3. **测试使用**：在 Cursor 的 AI 对话中，尝试：
   - "请识别这张图片中的文字：/path/to/image.jpg"
   - "使用 OCR 提取这个 PDF 中的内容：/path/to/file.pdf"

## 🔧 高级配置

### 自定义管道配置

如果需要调整模型配置（如使用轻量级模型），可以：

1. **导出配置**：
```python
from paddleocr import PPStructureV3

pipeline = PPStructureV3(
    use_formula_recognition=False,
    use_table_recognition=False,
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
)
pipeline.export_paddlex_config_to_yaml("PP-StructureV3.yaml")
```

2. **在配置中指定配置文件路径**：
```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "PP-StructureV3",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local",
        "PADDLEOCR_MCP_PIPELINE_CONFIG": "/absolute/path/to/PP-StructureV3.yaml"
      }
    }
  }
}
```

### 命令行参数

也可以通过 `args` 传递参数：

```json
{
  "mcpServers": {
    "paddleocr-ocr": {
      "command": "paddleocr_mcp",
      "args": ["--pipeline", "OCR", "--ppocr_source", "local", "--verbose"],
      "env": {}
    }
  }
}
```

## 📝 参数参考

| 环境变量 | CLI 参数 | 说明 | 可选值 | 默认值 |
|---------|---------|------|--------|--------|
| `PADDLEOCR_MCP_PIPELINE` | `--pipeline` | 使用的管道 | `OCR`, `PP-StructureV3` | `OCR` |
| `PADDLEOCR_MCP_PPOCR_SOURCE` | `--ppocr_source` | PaddleOCR 来源 | `local`, `aistudio`, `self_hosted` | `local` |
| `PADDLEOCR_MCP_SERVER_URL` | `--server_url` | 服务 URL（aistudio/self_hosted 模式） | - | - |
| `PADDLEOCR_MCP_AISTUDIO_ACCESS_TOKEN` | `--aistudio_access_token` | AI Studio Token（aistudio 模式） | - | - |
| `PADDLEOCR_MCP_PIPELINE_CONFIG` | `--pipeline_config` | 管道配置文件路径（local 模式） | - | - |
| `PADDLEOCR_MCP_DEVICE` | `--device` | 推理设备（local 模式） | - | - |
| - | `--verbose` | 启用详细日志 | - | `False` |

## ⚠️ 注意事项

1. **路径问题**：
   - 如果 `paddleocr_mcp` 不在系统 PATH 中，必须使用绝对路径
   - 配置文件路径也必须使用绝对路径

2. **虚拟环境**：
   - 如果使用虚拟环境，确保使用虚拟环境中的 `paddleocr_mcp` 路径
   - 例如：`/path/to/venv/bin/paddleocr_mcp`

3. **权限问题**：
   - 确保 Cursor 有权限执行 `paddleocr_mcp` 命令
   - 确保有权限读取配置文件

4. **重启要求**：
   - 修改配置后必须重启 Cursor 才能生效

5. **Token 安全**：
   - 不要将 AI Studio Token 提交到版本控制系统
   - 使用环境变量或配置文件（确保配置文件权限正确）

## 🐛 故障排查

### 问题1：Cursor 无法找到命令

**解决方案**：
- 使用绝对路径：`which paddleocr_mcp` 或 `where paddleocr_mcp` 获取路径
- 检查虚拟环境是否正确激活

### 问题2：配置不生效

**解决方案**：
- 确认配置文件路径正确
- 确认 JSON 格式正确（可以使用 JSON 验证器）
- 重启 Cursor

### 问题3：本地模式初始化失败

**解决方案**：
- 检查 PaddleOCR 是否正确安装
- 检查网络连接（首次使用会下载模型）
- 查看日志文件

### 问题4：AI Studio 模式连接失败

**解决方案**：
- 检查服务 URL 是否正确（不要包含端点路径如 `/ocr`）
- 检查 Token 是否正确
- 检查网络连接

## 📚 参考资源

- [PaddleOCR MCP Server 官方文档](https://www.paddlepaddle.org.cn/documentation/docs/zh/guides/model_deploy/mcp_server/mcp_server.html)
- [PaddleOCR 安装文档](https://www.paddleocr.ai/main/version3.x/installation/installation.html)
- [MCP 协议文档](https://modelcontextprotocol.io/)




