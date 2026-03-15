# Scripts 使用说明

`scripts/` 现在只保留两个和当前最小实现一致的辅助脚本：

- `list_tools.py`：列出当前 MCP 服务实际暴露的工具
- `recognize_image.py`：直接按当前统一 envelope 调用本地识别链路

## 快速开始

列出工具：

```bash
uv run python scripts/list_tools.py
```

识别单张图片：

```bash
uv run python scripts/recognize_image.py path/to/image.png
uv run python scripts/recognize_image.py path/to/image.png --json
```

## 说明

- 这里只保留和当前 `stdio + PaddleOCR + image.path` 主链路完全一致的辅助脚本
- 自动化验证入口仍然是 `uv run python -m pytest -q`
- MCP 客户端配置示例请直接参考根目录 `README.md`
