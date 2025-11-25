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

**一键安装**：
```bash
make
```

这将自动完成：
- ✅ 检查Python环境
- ✅ 安装所有依赖
- ✅ 验证安装
- ✅ 生成配置文件模板

**配置Cursor**：
1. 打开生成的 `config_template.json` 文件
2. 将配置内容添加到Cursor的MCP设置中（详见下方配置说明）
3. 重启Cursor

**（可选）测试服务器**：
```bash
make start    # 手动测试服务器启动
```

**查看所有命令**：
```bash
make help
```

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

**方法1：使用生成的配置文件模板**

运行 `make ready` 后会生成 `config_template.json`，将其内容添加到Cursor的MCP配置中。

**方法2：手动配置**

在Cursor的MCP配置文件中添加以下内容（请替换为实际路径）：

```json
{
  "mcpServers": {
    "ocr-service": {
      "command": "python",
      "args": [
        "/path/to/mcp_ocr_server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/ocr-mcp-service"
      }
    }
  }
}
```

**配置文件位置**：
- Windows: `%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json` 或 `%USERPROFILE%\.cursor\mcp_settings.json`
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json` 或 `~/.cursor/mcp_settings.json`
- Linux: `~/.config/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json` 或 `~/.cursor/mcp_settings.json`

**重要提示**：
- 使用**绝对路径**，不要使用相对路径
- Windows路径使用正斜杠`/`或双反斜杠`\\`
- 配置完成后需要**重启Cursor**才能生效

#### 4. 验证配置

1. 保存配置文件
2. 重启Cursor（完全关闭并重新打开）
3. 测试OCR功能：在对话中提供一张包含文字的图片，要求AI识别图片中的文字

## 🛠️ Makefile命令

| 命令 | 说明 |
|------|------|
| `make` 或 `make all` | **一键安装**（安装依赖+验证+生成配置） |
| `make start` | 手动测试启动服务器（可选） |
| `make status` | 检查服务器运行状态 |
| `make stop` | 停止所有OCR MCP服务进程 |
| `make logs` | 查看最近的日志条目（最后50行） |
| `make logs-tail` | 实时跟踪日志文件 |
| `make help` | 显示所有可用命令 |

**完整使用流程**：
```bash
# 1. 一键安装（会自动完成所有配置）
make

# 2. 将生成的配置添加到Cursor MCP设置中
# （查看 config_template.json，添加到Cursor配置）

# 3. 重启Cursor，服务会自动启动

# （可选）查看服务状态和日志
make status      # 检查服务是否运行
make logs        # 查看日志
```

日志文件位置：`logs/mcp_ocr_server.log`

## 📊 监控和管理服务

### 检查服务运行状态

**查看服务是否在运行：**
```bash
make status
```

这会显示：
- 是否有进程在运行（如果有，显示进程ID和命令）
- 日志文件位置和大小
- 最后修改时间
- 服务运行状态（运行中/已停止）

**示例输出：**
```
[RUNNING] Found 2 process(es):
  PID: 20100
  Command: python D:/git repo/ocr-mcp-service/mcp_ocr_server.py
  PID: 23976
  Command: python D:/git repo/ocr-mcp-service/mcp_ocr_server.py

[LOG] Log file exists:
  Path: D:\git repo\ocr-mcp-service\logs\mcp_ocr_server.log
  Size: 2.62 KB
  Last modified: 2025-11-25 11:35:19
```

**如果未安装 psutil（可选依赖）：**
- 会提示安装方法
- 仍可以检查日志文件是否存在

### 停止服务

**停止所有OCR MCP服务进程：**
```bash
make stop
```

这会自动找到并停止所有运行中的OCR服务进程。

**手动停止特定进程（如果需要）：**

**Windows:**
```powershell
# 使用PID停止
taskkill /F /PID <pid>

# 例如，停止PID为20100的进程
taskkill /F /PID 20100
```

**Linux/Mac:**
```bash
# 使用PID停止
kill -9 <pid>

# 例如，停止PID为20100的进程
kill -9 20100
```

**使用脚本停止特定进程：**
```bash
# 停止指定PID的进程
python scripts/stop_service.py <pid>

# 例如，停止PID为20100的进程
python scripts/stop_service.py 20100
```

**方法总结：**

| 方法 | 命令 | 说明 |
|------|------|------|
| 停止所有 | `make stop` | 自动停止所有OCR服务进程（推荐） |
| 停止指定PID | `python scripts/stop_service.py <pid>` | 停止指定PID的进程 |
| Windows手动 | `taskkill /F /PID <pid>` | Windows系统手动停止 |
| Linux/Mac手动 | `kill -9 <pid>` | Linux/Mac系统手动停止 |

### 查看日志

**查看最近的日志（最后50行）：**
```bash
make logs
```

**查看更多日志行数（例如最后100行）：**
```bash
python scripts/view_logs.py 100
```

**实时跟踪日志（类似 tail -f）：**
```bash
make logs-tail
```

按 `Ctrl+C` 停止跟踪。

### 日志文件说明

**位置：** `logs/mcp_ocr_server.log`

**日志内容包含：**
- 服务启动和初始化信息
- OCR识别任务的详细信息
- 错误和异常信息
- 性能指标（识别时间、文本块数量等）

**日志格式示例：**
```
2025-01-XX 10:30:15 - __main__ - INFO - 日志文件位置: D:/git repo/ocr-mcp-service/logs/mcp_ocr_server.log
2025-01-XX 10:30:16 - __main__ - INFO - 初始化PaddleOCR...
2025-01-XX 10:30:20 - __main__ - INFO - PaddleOCR初始化完成
2025-01-XX 10:35:22 - __main__ - INFO - 开始OCR识别: D:/path/to/image.jpg
2025-01-XX 10:35:25 - __main__ - INFO - OCR识别完成，共识别 3 个文本块
```

### 服务运行方式说明

**在 Cursor 中的运行方式：**
- Cursor 会根据配置**自动启动** MCP 服务器
- 服务器通过 **stdio（标准输入输出）** 与 Cursor 通信
- 每次 Cursor 启动时会自动启动所有配置的 MCP 服务器
- 服务进程由 Cursor 管理，**无需手动启动**

**如何知道服务已启动？**
1. 运行 `make status` 查看进程列表
2. 检查日志文件是否存在且有内容
3. 在 Cursor 中使用 OCR 功能，如果能识别图片说明服务正常

**查看服务进程的方法：**

**Windows:**
```powershell
# 在 PowerShell 中查看
Get-Process python | Where-Object {$_.CommandLine -like "*mcp_ocr_server.py*"}

# 或使用任务管理器
# 打开任务管理器 → 详细信息 → 查找 python.exe 进程
```

**Linux/Mac:**
```bash
ps aux | grep mcp_ocr_server.py
```

**手动测试服务器（调试用）：**
```bash
make start    # 启动服务器进行测试（按 Ctrl+C 停止）
```

### 常见问题排查

**1. 服务未运行**
```bash
# 检查状态
make status

# 如果显示 [STOPPED]，检查：
# - 配置是否正确添加到 Cursor 的 MCP 设置
# - 路径是否正确（必须使用绝对路径）
# - 是否已重启 Cursor
```

**2. 查看错误日志**
```bash
# 查看最近的错误（Windows PowerShell）
make logs | Select-String -Pattern "error|ERROR|Error|exception|Exception"

# Linux/Mac
make logs | grep -i error

# 直接查看日志文件
# Windows: notepad logs\mcp_ocr_server.log
# Linux/Mac: cat logs/mcp_ocr_server.log
```

**3. 服务启动失败**
```bash
# 检查依赖
make verify

# 查看详细错误
make logs

# 手动测试启动
python mcp_ocr_server.py
```

**4. 日志文件为空或没有更新**
- 检查日志文件权限
- 确认服务是否真的在运行：`make status`
- 如果日志文件不存在，服务可能还没有启动过

### 实时监控示例

**场景：想知道 OCR 服务是否在响应请求**

```bash
# 终端1：实时跟踪日志
make logs-tail

# 终端2：在 Cursor 中使用 OCR 功能
# 你会看到日志中实时输出：
# - Processing request of type ListToolsRequest（Cursor查询可用工具）
# - 开始OCR识别: xxx（开始识别图片）
# - OCR识别完成，共识别 X 个文本块（识别结果）
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

