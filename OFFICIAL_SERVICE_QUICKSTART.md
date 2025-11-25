# PaddleOCR官方MCP服务快速开始

## ✅ 已完成的配置

官方服务已添加到Cursor配置中：

```json
{
  "mcpServers": {
    "ocr-service-official": {
      "command": "/home/qiao/Desktop/Git Repo/ocr-mcp-service/.venv/bin/paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
      }
    }
  }
}
```

## 🚀 使用步骤

### 1. 重启Cursor

配置更改后需要**完全重启Cursor**才能生效：
- 完全关闭Cursor（不是只关闭窗口）
- 重新打开Cursor

### 2. 验证服务连接

重启后，在Cursor中测试：

```
用户：列出可用的OCR工具
```

或直接测试OCR功能：

```
用户：使用OCR服务识别图片 /path/to/image.jpg
```

### 3. 查看服务状态

如果服务未连接，检查：
- Cursor日志（Help > Toggle Developer Tools > Console）
- 服务是否正常启动
- 配置文件路径是否正确

## 🔧 配置说明

### 当前配置（默认模式）

- **管道类型**：OCR（文字识别）
- **工作模式**：local（本地Python库）
- **传输方式**：STDIO（标准输入输出）

### 其他配置选项

**详细日志模式**（调试用）：
```json
{
  "command": "/home/qiao/Desktop/Git Repo/ocr-mcp-service/.venv/bin/paddleocr_mcp",
  "args": ["--verbose"],
  "env": {
    "PADDLEOCR_MCP_PIPELINE": "OCR",
    "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
  }
}
```

**HTTP模式**（远程访问）：
```json
{
  "command": "/home/qiao/Desktop/Git Repo/ocr-mcp-service/.venv/bin/paddleocr_mcp",
  "args": ["--http", "--host", "127.0.0.1", "--port", "8000"],
  "env": {
    "PADDLEOCR_MCP_PIPELINE": "OCR",
    "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
  }
}
```

## 📋 官方服务功能

### 工具函数

**`ocr`** - OCR文字识别
- 输入：文件路径、Base64编码、URL
- 输出模式：
  - `simple`：简洁文本（默认）
  - `detailed`：详细JSON（包含坐标、置信度）

### 使用示例

**简单模式**：
```
用户：识别图片 /path/to/image.jpg
AI：调用ocr工具，output_mode=simple
```

**详细模式**：
```
用户：识别图片 /path/to/image.jpg，需要详细结果
AI：调用ocr工具，output_mode=detailed
```

## 🔍 故障排查

### 问题1：服务未连接

**检查**：
1. Cursor是否完全重启
2. 配置文件路径是否正确
3. Entry Point是否存在

**验证**：
```bash
# 检查Entry Point
ls -lh /home/qiao/Desktop/Git\ Repo/ocr-mcp-service/.venv/bin/paddleocr_mcp

# 手动测试服务
cd /home/qiao/Desktop/Git\ Repo/ocr-mcp-service
uv run paddleocr_mcp --help
```

### 问题2：OCR初始化失败

**可能原因**：
- PaddleOCR模型下载失败
- 网络问题
- 磁盘空间不足

**解决**：
1. 检查网络连接
2. 确保磁盘空间充足
3. 查看详细日志：添加`--verbose`参数

### 问题3：工具不可用

**检查**：
- Cursor开发者工具中的错误信息
- 服务是否正常启动
- MCP协议版本兼容性

## 📚 参考文档

- [官方MCP文档](https://www.paddleocr.ai/v3.1.0/version3.x/deployment/mcp_server.html)
- [DUAL_SERVICE_SETUP.md](./DUAL_SERVICE_SETUP.md) - 双服务配置
- [IMPLEMENTATION_COMPARISON.md](./IMPLEMENTATION_COMPARISON.md) - 实现对比

## 🎯 下一步

1. **测试OCR功能**：在Cursor中尝试识别图片
2. **对比两种服务**：同时配置手动实现和官方服务
3. **学习官方实现**：查看源码了解实现细节

