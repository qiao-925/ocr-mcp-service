# PyPI / uvx 发布指南

本文档用于发布 Python 版 `local-ocr-mcp`，让用户通过 `uvx` 直接运行 MCP 服务，无需额外维护 `npm` 启动器。

## 目标形态

- 分发仓库：PyPI
- 用户入口：`uvx`
- MCP 客户端配置：`command = "uvx"` + `args = ["--from", "<pypi-spec>", "local-ocr-mcp"]`

推荐默认规格：

```bash
uvx --from "local-ocr-mcp[paddleocr]" local-ocr-mcp
```

若需固定版本：

```bash
uvx --from "local-ocr-mcp[paddleocr]==0.2.0" local-ocr-mcp
```

## 发布前检查

1. 确认 `pyproject.toml` 中的 `version` 已更新。
2. 确认 `README.md` 与迁移文档中的命令示例一致。
3. 确认 CLI 仍保持“固定 `stdio`、无额外 transport 参数”的最小约束。
4. 运行本地测试与构建检查：

```bash
uv run python -m pytest -q
uv run python -m local_ocr_mcp --help
uv build --no-sources
uv publish --dry-run
```

## 生成客户端配置

当前仓库没有 `scripts/clients/generate_mcp_configs.py` 一类配置生成器，发布时以 `README.md` 和仓库根目录的 `mcp_config.json` 为准。

```bash
cat mcp_config.json
```

如果要在文档里给出固定版本配置，直接把 `mcp_config.json` 中的 `--from` 规格改为带版本号的字符串，例如：

```json
{
  "mcpServers": {
    "local-ocr-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "local-ocr-mcp[paddleocr]==0.2.0",
        "local-ocr-mcp"
      ]
    }
  }
}
```

源码本地开发仍使用仓库环境：

```bash
uv sync --extra dev --extra paddleocr
uv run python -m local_ocr_mcp
```

## 发布到 PyPI

构建分发产物：

```bash
uv build --no-sources
```

发布前 dry-run：

```bash
uv publish --dry-run
```

正式发布：

```bash
uv publish
```

认证说明：

- 本地执行 `uv publish` 时，优先使用 `UV_PUBLISH_TOKEN`
- 如果是在 GitHub Actions 里发布，推荐改用 PyPI Trusted Publishing，而不是长期保存 token

## 发布后验证

1. 验证包已在 PyPI 可见：

```bash
curl -I https://pypi.org/project/local-ocr-mcp/
```

2. 验证 `uvx` 可解析并显示帮助：

```bash
uvx --from "local-ocr-mcp[paddleocr]==0.2.0" local-ocr-mcp --help
```

3. 验证仓库内配置样例与发布版本一致：

```bash
cat mcp_config.json
```

4. 验证 MCP 客户端配置可直接使用：

```json
{
  "mcpServers": {
    "local-ocr-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "local-ocr-mcp[paddleocr]==0.2.0",
        "local-ocr-mcp"
      ]
    }
  }
}
```

## MCP 配置示例

```json
{
  "mcpServers": {
    "local-ocr-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "local-ocr-mcp[paddleocr]==0.2.0",
        "local-ocr-mcp"
      ]
    }
  }
}
```

## 取舍说明

- `PyPI + uvx` 是 Python MCP 最自然的分发链路。
- 当前 CLI 固定以 `stdio` 运行，因此不再暴露 `--transport` 参数。
- 当前仓库不维护独立的客户端配置生成器，直接维护 `README.md` 和 `mcp_config.json` 更简单。
- `local` runtime 仅用于仓库源码开发与调试。
