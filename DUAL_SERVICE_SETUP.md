# 双服务配置指南

同时配置手动实现的MCP服务和PaddleOCR官方MCP服务，方便对比和学习。

## 🎯 配置目标

在Cursor中同时配置两种OCR MCP服务：
1. **手动实现** (`ocr-service-custom`) - 学习用
2. **官方实现** (`ocr-service-official`) - 生产用

## 📋 前置准备

### 1. 安装手动实现服务

```bash
cd /home/qiao/Desktop/Git\ Repo/ocr-mcp-service
uv sync
uv pip install -e .
```

### 2. 安装官方服务

```bash
# 已通过 uv add paddleocr-mcp 安装
# 验证安装
uv run paddleocr_mcp --help
```

## 🔧 Cursor配置

编辑 `~/.cursor/mcp.json` 文件：

```json
{
  "mcpServers": {
    "ocr-service-custom": {
      "command": "/home/qiao/Desktop/Git Repo/ocr-mcp-service/.venv/bin/ocr-mcp-server",
      "args": [],
      "env": {},
      "_description": "手动实现的OCR MCP服务（学习用）"
    },
    "ocr-service-official": {
      "command": "paddleocr_mcp",
      "args": [],
      "env": {
        "PADDLEOCR_MCP_PIPELINE": "OCR",
        "PADDLEOCR_MCP_PPOCR_SOURCE": "local"
      },
      "_description": "PaddleOCR官方MCP服务（生产用）"
    }
  }
}
```

### 配置说明

**手动实现服务**：
- `command`: Entry Point路径（最简洁）
- `args`: 空数组
- `env`: 空对象

**官方服务**：
- `command`: `paddleocr_mcp`（全局命令）
- `args`: 空数组（使用默认参数）
- `env`: 环境变量配置
  - `PADDLEOCR_MCP_PIPELINE`: 管道类型（OCR/PP-StructureV3/PaddleOCR-VL）
  - `PADDLEOCR_MCP_PPOCR_SOURCE`: 来源（local/aistudio/self_hosted）

## 🧪 测试两种服务

### 测试手动实现服务

在Cursor中：
```
用户：使用ocr-service-custom识别图片 /path/to/image.jpg
```

### 测试官方服务

在Cursor中：
```
用户：使用ocr-service-official识别图片 /path/to/image.jpg
```

## 📊 功能对比测试

### 1. 基本OCR识别

**手动实现**：
- 工具名：`recognize_text_from_path`
- 输入：文件路径
- 输出：文本+置信度+位置

**官方实现**：
- 工具名：需查看官方文档
- 输入：文件路径/base64/URL
- 输出：文本+详细信息

### 2. 配置管理

**手动实现**：
- `get_mcp_config_info` - 查询配置
- `auto_configure_mcp` - 自动配置

**官方实现**：
- 通过命令行参数配置
- 通过环境变量配置

## 🔍 源码分析

### 查看官方实现

```bash
# 查看入口点
cat .venv/lib/python3.12/site-packages/paddleocr_mcp/__main__.py

# 查看管道处理
cat .venv/lib/python3.12/site-packages/paddleocr_mcp/pipelines.py | head -200

# 查看工具注册
grep -n "register_tools\|@mcp.tool\|mcp.tool()" .venv/lib/python3.12/site-packages/paddleocr_mcp/*.py
```

### 关键发现

1. **都使用FastMCP**
   - 官方：`from fastmcp import FastMCP`
   - 手动：`from mcp.server.fastmcp import FastMCP`
   - 注意：导入路径不同！

2. **工具注册方式**
   - 官方：通过handler统一注册
   - 手动：直接注册函数

3. **异步支持**
   - 官方：完全异步（`async_main`）
   - 手动：同步实现

## 📝 学习笔记

### FastMCP导入差异

**官方**：
```python
from fastmcp import FastMCP
```

**手动**：
```python
from mcp.server.fastmcp import FastMCP
```

**原因**：可能是FastMCP版本不同或API变化

### 异步vs同步

**官方实现**：
```python
async def async_main():
    mcp = FastMCP(...)
    pipeline_handler.register_tools(mcp)
    await mcp.run_async()
```

**手动实现**：
```python
def main():
    mcp = FastMCP(...)
    mcp.tool()(recognize_text_from_path)
    mcp.run()  # 同步运行
```

### 管道设计模式

官方使用管道抽象：
- `PipelineHandler` 基类
- 不同管道实现（OCR/PP-StructureV3/VL）
- 统一接口处理

手动实现：
- 直接使用PaddleOCR
- 简单直接
- 易于理解

## 🎓 学习建议

1. **先理解手动实现**
   - 代码简洁
   - 逻辑清晰
   - 易于调试

2. **再学习官方实现**
   - 架构设计
   - 异步处理
   - 管道模式

3. **对比差异**
   - 框架使用
   - 代码组织
   - 功能实现

4. **取长补短**
   - 学习官方架构
   - 保留手动灵活性
   - 结合两者优势

## 🔄 切换使用

可以根据需要切换使用：

**开发/学习**：使用手动实现
- 代码可见
- 易于修改
- 便于调试

**生产环境**：使用官方实现
- 功能完整
- 稳定可靠
- 官方支持

## 📚 参考文档

- [PaddleOCR官方MCP文档](https://www.paddleocr.ai/v3.1.0/version3.x/deployment/mcp_server.html)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [MCP协议文档](https://modelcontextprotocol.io/)

