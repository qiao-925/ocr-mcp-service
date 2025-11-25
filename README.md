# OCR MCP Service

基于PaddleOCR的图片文字识别MCP服务器，为AI Agent提供OCR能力。

## 📋 项目简介

本服务实现了Model Context Protocol (MCP)服务器，将PaddleOCR的OCR能力封装为标准化工具，使AI Agent能够自动识别图片中的文字内容。

**核心特性**：
- ✅ 支持中文识别（准确率约90%）
- ✅ 支持文件路径和base64两种输入方式
- ✅ 返回结构化结果（文本+置信度+位置信息）
- ✅ 基于FastMCP框架，易于维护
- ✅ 开源免费，无API调用成本

## 🚀 快速开始

### 方式一：使用Makefile（推荐）

**一键安装（类似 make install）**：
```bash
make
# 或
make install
```

**完整工作流**：
```bash
make ready    # 安装 + 验证 + 生成配置
make start    # 完整流程 + 启动服务器
```

**查看所有命令**：
```bash
make help
```

Makefile会自动完成：
- ✅ 检查Python环境
- ✅ 安装所有依赖
- ✅ 验证安装
- ✅ 生成配置文件模板

### 方式二：手动安装

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**注意**：首次安装PaddleOCR会自动下载模型文件，可能需要一些时间。

#### 2. 测试运行

```bash
python mcp_ocr_server.py
```

如果看到服务器启动信息，说明安装成功。按`Ctrl+C`退出。

#### 3. 配置Cursor

在Cursor设置中添加MCP服务器配置，详见[配置指南.md](./配置指南.md)。

## 📚 文档

- [配置指南.md](./配置指南.md) - 详细的安装和配置说明
- [使用指南.md](./使用指南.md) - 功能说明和使用场景
- [MCP架构原理与技术实现.md](./MCP架构原理与技术实现.md) - 技术实现细节

## 🛠️ Makefile命令

| 命令 | 说明 |
|------|------|
| `make` 或 `make all` | 默认：完整工作流（安装+验证+生成配置） |
| `make install` | 安装项目依赖 |
| `make verify` | 验证安装 |
| `make test` | 测试MCP服务器 |
| `make run` | 启动MCP服务器 |
| `make start` | 一键启动（完整流程+启动服务器） |
| `make ready` | 准备就绪（安装+验证+生成配置） |
| `make clean` | 清理生成的文件 |
| `make help` | 显示帮助信息 |

**推荐使用流程**：
```bash
make          # 一键安装和配置
make start    # 测试启动服务器
```

## 🛠️ 技术选型

**选择PaddleOCR的原因**：
- 开源免费，无API调用成本
- 90%准确率满足大多数场景
- 轻量级，资源消耗相对较低
- 支持中文识别，适合处理中文文档
- 社区活跃，维护良好

## 📝 工具说明

### 1. recognize_text_from_path

从图片文件路径识别文字。

**参数**：
- `image_path` (string): 图片文件的路径

**返回**：
```json
{
  "success": true,
  "text": "识别出的完整文本",
  "lines": [
    {
      "text": "单行文本",
      "confidence": 0.95,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ],
  "line_count": 1
}
```

### 2. recognize_text_from_base64

从base64编码的图片数据识别文字。

**参数**：
- `image_base64` (string): base64编码的图片数据

**返回**：同`recognize_text_from_path`

## 🔗 相关资源

- [MCP Python SDK文档](https://github.com/modelcontextprotocol/python-sdk)
- [PaddleOCR官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [MCP协议规范](https://modelcontextprotocol.io/)

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE) 文件

