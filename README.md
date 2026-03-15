# Local OCR MCP

> 基于 `FastMCP` 与 `PaddleOCR` 的最小化本地 OCR MCP 服务，只保留 `stdio -> ocr_recognize -> PaddleOCR -> 统一响应 envelope` 这一条主路径，适合本地 IDE、Agent 和 MCP Client 直接接入。

---

## 1. 快速开始

**环境要求**

- `Python 3.10+`
- `uv`

**PyPI 发布状态**

- 已发布到 PyPI：`local-ocr-mcp==0.2.0`
- 项目页：<https://pypi.org/project/local-ocr-mcp/>

**1. 直接用 `uvx` 运行**

```bash
uvx --from "local-ocr-mcp[paddleocr]==0.2.0" local-ocr-mcp
```

适合直接接入 MCP 客户端，不需要手动创建虚拟环境。

首次运行会安装 `paddleocr`、`paddlepaddle`、`opencv` 等依赖，时间可能明显更长；后续复用缓存后会快很多。

如果你希望始终跟随最新发布版本，也可以省略固定版本号：

```bash
uvx --from "local-ocr-mcp[paddleocr]" local-ocr-mcp
```

**2. 本地开发运行**

```bash
git clone <repository-url>
cd local-ocr-mcp
uv sync --extra dev --extra paddleocr
uv run python -m local_ocr_mcp
```

**3. MCP 客户端配置示例**

```json
{
  "mcpServers": {
    "local-ocr-mcp": {
      "command": "uvx",
      "args": ["--from", "local-ocr-mcp[paddleocr]==0.2.0", "local-ocr-mcp"]
    }
  }
}
```

> 📖 仓库里也保留了一份同步后的配置样例 → [mcp_config.json](/home/q/Desktop/START/repos/AI/ML/local-ocr-mcp/mcp_config.json)

---

## 2. 核心特性

| 特性 | 说明 |
|------|------|
| **单路径主链路** | 只保留 `stdio -> ocr_recognize -> PaddleOCR`，没有传输分支和引擎路由 |
| **最小工具面** | 对外只暴露 `ocr_recognize` 与 `ocr_health_check` 两个工具 |
| **统一响应契约** | 所有工具统一返回 `status / data / error / meta` envelope |
| **固定输入模型** | 当前只接受本地图片路径 `image.path`，不支持 URL、base64 或上传流 |
| **稳定错误语义** | 用固定错误码暴露常见失败路径，便于客户端编排与恢复 |
| **低认知负担** | 不保留多引擎、analysis、progress、heartbeat、registry/factory 等扩展层 |

---

## 3. 技术栈

- **Python 3.10+** / **uv** - 运行时与依赖管理
- **FastMCP** - MCP 服务框架
- **PaddleOCR** - 固定 OCR 引擎
- **Pillow** - 图片合法性校验
- **pytest** - 最小契约测试

---

## 4. 架构概览

```text
┌──────────────────────────────────────────────────────┐
│                 MCP Client / IDE / Agent            │
├──────────────────────────────────────────────────────┤
│                     stdio transport                  │
├──────────────────────────────────────────────────────┤
│       FastMCP Tools: ocr_recognize / health_check   │
├──────────────────────────────────────────────────────┤
│  RecognitionService            HealthService         │
├──────────────────────────────────────────────────────┤
│                  PaddleOCREngine                    │
├──────────────────────────────────────────────────────┤
│          PaddleOCR / Filesystem / Image Validation   │
└──────────────────────────────────────────────────────┘
```

当前实现刻意保持单向依赖和短链路：

- CLI 只负责启动 `stdio`
- Tool 层只负责暴露 MCP 接口
- Service 层负责校验输入并整形成统一 envelope
- Engine 层只负责调用 `PaddleOCR` 并归一化结果

---

## 5. 工具契约

| 工具 | 说明 |
|------|------|
| `ocr_recognize` | 识别本地图片并返回统一 OCR 结果 |
| `ocr_health_check` | 返回轻量健康状态、运行时版本和启动时长 |

### `ocr_recognize` 请求示例

```json
{
  "image": {
    "path": "./example.png"
  }
}
```

### `ocr_recognize` 输入约束

- `image` 必须是对象
- `image.path` 必须是非空字符串
- 当前只允许 `image.path`
- 相对路径会按服务进程当前工作目录解析为绝对路径

### `ocr_recognize` 成功响应示例

```json
{
  "status": "ok",
  "data": {
    "text": "示例文本",
    "boxes": [
      {"x1": 0.0, "y1": 0.0, "x2": 120.0, "y2": 32.0}
    ],
    "confidence": 0.98,
    "engine": "paddleocr",
    "processing_ms": 143
  },
  "error": null,
  "meta": {
    "timestamp": "2026-03-14T00:00:00+00:00",
    "runtime_version": "0.2.0",
    "request_id": "8c4c9d5c-6b4d-4f1f-b6df-4ff80e3ff6b6",
    "resolved_engine": "paddleocr",
    "resolved_image_path": "/abs/path/example.png"
  }
}
```

### `ocr_health_check` 响应示例

```json
{
  "status": "ok",
  "data": {
    "status": "healthy",
    "uptime_ms": 1234,
    "transport": "stdio",
    "runtime_version": "0.2.0"
  },
  "error": null,
  "meta": {
    "timestamp": "2026-03-14T00:00:00+00:00",
    "runtime_version": "0.2.0"
  }
}
```

---

## 6. 错误语义与运行约束

### 统一错误结构

```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "file_not_found|invalid_image|engine_not_available|internal_error",
    "message": "具体错误信息",
    "retryable": false
  },
  "meta": {
    "timestamp": "...",
    "runtime_version": "0.2.0",
    "request_id": "...",
    "resolved_engine": "paddleocr"
  }
}
```

### 错误码说明

- `file_not_found`：`image.path` 指向的文件不存在
- `invalid_image`：请求结构不合法，或文件存在但不是有效图片
- `engine_not_available`：`PaddleOCR` 未安装或初始化失败
- `internal_error`：识别链路内部出现未归类异常

### 当前运行约束

- 只支持 `stdio`
- 只支持 `PaddleOCR`
- 不会自动切换引擎
- 不支持 `streamable-http`
- 不支持 analysis、progress、heartbeat
- 不支持 URL、base64、上传流等非文件输入

### PaddleOCR 兼容行为

内部固定使用 `PaddleOCR`，但对其 Python API 保留最小兼容：

- 优先走较新的 `predict()`
- 如果安装版本只支持旧接口，则回退到 `ocr()`
- 对外继续返回统一响应结构

---

## 7. 配置与脚本

### 可选环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PADDLEOCR_LANG` | PaddleOCR 初始化语言 | `ch` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

示例：

```bash
PADDLEOCR_LANG=ch LOG_LEVEL=INFO uv run python -m local_ocr_mcp
```

### 辅助脚本

当前 `scripts/` 目录只保留和最小实现一致的两个脚本：

- `uv run python scripts/list_tools.py`
- `uv run python scripts/recognize_image.py path/to/image.png --json`

> 📖 详细说明 → [scripts/README.md](/home/q/Desktop/START/repos/AI/ML/local-ocr-mcp/scripts/README.md)

---

## 8. 开发与验证

常用命令：

```bash
uv run python -m pytest -q
uv run python -m local_ocr_mcp --help
uv run python scripts/list_tools.py
uv run python scripts/recognize_image.py path/to/image.png --json
```

CI 当前只覆盖最小必需验证：

- 编译检查
- 单元测试
- CLI `--help`
- `stdio` 启动烟测

---

## 9. 常见问题

### 1. 服务启动后为什么一直不退出？

因为它在等待 MCP 客户端通过 `stdio` 调用工具。这是正常行为。

### 2. 为什么返回 `engine_not_available`？

通常说明 `PaddleOCR` 或底层依赖没有正确安装。优先重新同步依赖：

```bash
uv sync --extra paddleocr
```

如果你是通过 `uvx` 启动，确认命令里包含：

```text
uvx --from local-ocr-mcp[paddleocr]==0.2.0 local-ocr-mcp
```

如果你故意选择跟随最新版本，也可以使用不带版本号的形式：

```text
uvx --from local-ocr-mcp[paddleocr] local-ocr-mcp
```

### 3. 为什么返回 `invalid_image`？

常见原因：

- 请求里没有 `image.path`
- `image.path` 不是字符串
- 文件存在，但不是合法图片

### 4. 相对路径为什么找不到文件？

相对路径是相对于服务进程当前工作目录解析的。最稳妥的做法是直接传绝对路径。

### 5. 为什么不保留多引擎和 HTTP？

因为当前版本明确选择“核心最小化”路线，只保留本地 OCR 主链路，不为未来扩展提前保留复杂结构。

---

**最后更新**: 2026-03-14  
**License**: MIT
