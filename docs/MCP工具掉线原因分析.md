# MCP工具掉线原因分析

## 🔍 问题概述

MCP工具在使用过程中容易出现掉线问题，导致工具无法正常调用。本文档分析了可能导致掉线的根本原因。

## 📋 主要问题

### 1. 缺少超时机制 ⚠️ **严重**

**问题描述**：
- OCR处理可能耗时很长（特别是大图片或复杂场景）
- 没有设置请求超时时间
- 客户端可能在等待过程中主动断开连接

**代码位置**：
```27:29:src/ocr_mcp_service/__main__.py
def main():
    """Run the MCP server."""
    mcp.run()
```

**影响**：
- 长时间OCR处理时，Cursor可能认为服务无响应而断开连接
- 没有超时保护，可能导致资源占用无法释放

**建议**：
- 为OCR处理添加超时机制（如60秒）
- 使用异步处理或后台任务
- 添加进度反馈机制（已有，但需要确保及时发送）

---

### 2. 缺少异常恢复机制 ⚠️ **严重**

**问题描述**：
- `main()`函数直接调用`mcp.run()`，没有异常处理
- 如果OCR引擎抛出未捕获的异常，会导致整个进程退出
- 进程退出后，Cursor需要重新启动服务，但可能不会立即重试

**代码位置**：
```27:29:src/ocr_mcp_service/__main__.py
def main():
    """Run the MCP server."""
    mcp.run()
```

**影响**：
- 任何未捕获的异常都会导致服务崩溃
- 服务崩溃后需要Cursor重新启动，存在延迟
- 用户体验差，工具突然不可用

**建议**：
- 添加全局异常处理
- 实现优雅的错误恢复机制
- 记录异常并尝试继续运行

---

### 3. 资源占用问题 ⚠️ **中等**

**问题描述**：
- OCR引擎（特别是DeepSeek OCR）占用大量内存（~7.8GB）
- 长时间运行可能导致内存泄漏
- 多个引擎同时加载会进一步增加内存占用

**代码位置**：
```733:758:src/ocr_mcp_service/ocr_engine.py
class OCREngineFactory:
    """Factory for creating OCR engines."""

    _engines: dict[str, OCREngine] = {}

    @classmethod
    def get_engine(cls, engine_type: str, **kwargs) -> OCREngine:
        """Get OCR engine instance (singleton).
        
        Args:
            engine_type: Type of engine ('paddleocr', 'easyocr', 'deepseek', 'paddleocr_mcp')
            **kwargs: Additional arguments for engine initialization
        """
        if engine_type not in cls._engines:
            if engine_type == "paddleocr":
                cls._engines[engine_type] = PaddleOCREngine()
            elif engine_type == "deepseek":
                cls._engines[engine_type] = DeepSeekOCREngine()
            elif engine_type == "paddleocr_mcp":
                cls._engines[engine_type] = PaddleOCRMCPEngine()
            elif engine_type == "easyocr":
                languages = kwargs.get('languages', None)
                cls._engines[engine_type] = EasyOCREngine(languages=languages)
            else:
                raise ValueError(f"Unknown engine type: {engine_type}")
        return cls._engines[engine_type]
```

**影响**：
- 内存不足可能导致OOM（Out of Memory）错误
- 进程被系统杀死，导致掉线
- 系统性能下降，影响其他应用

**建议**：
- 实现引擎懒加载（按需加载）
- 添加内存监控和清理机制
- 考虑引擎卸载策略（长时间未使用后释放）

---

### 4. 缺少心跳/保活机制 ⚠️ **中等**

**问题描述**：
- MCP服务器通过stdio通信，长时间无请求时连接可能被关闭
- 没有心跳机制保持连接活跃
- FastMCP可能不支持自动心跳

**代码位置**：
```1:7:src/ocr_mcp_service/mcp_server.py
"""MCP server setup."""

from fastmcp import FastMCP
from typing import Optional, Callable

# Create MCP server instance
mcp = FastMCP("OCR MCP Service")
```

**影响**：
- 长时间空闲后，连接可能被客户端或系统关闭
- 下次调用时发现连接断开，需要重新建立连接
- 用户感知为工具"掉线"

**建议**：
- 检查FastMCP是否支持心跳机制
- 如果支持，启用自动心跳
- 如果不支持，考虑定期发送空请求保持连接

---

### 5. 错误处理过于宽泛 ⚠️ **中等**

**问题描述**：
- 很多地方捕获异常后只是记录日志，没有恢复机制
- 异常可能导致内部状态不一致
- 某些异常被静默忽略，可能导致后续调用失败

**代码位置示例**：
```32:37:src/ocr_mcp_service/mcp_server.py
    if _mcp_log_callback:
        try:
            _mcp_callback(level=level, logger=logger, data=data)
        except Exception:
            # Silently ignore errors to avoid breaking the app
            pass
```

**影响**：
- 错误被静默忽略，难以诊断问题
- 状态不一致可能导致后续调用失败
- 用户无法知道发生了什么问题

**建议**：
- 区分可恢复和不可恢复的错误
- 对于关键错误，应该记录并尝试恢复
- 提供更详细的错误信息给客户端

---

### 6. 配置路径问题 ⚠️ **轻微**

**问题描述**：
- `mcp_config.json`中还有Windows路径
- 路径错误会导致服务启动失败
- 启动失败时Cursor可能不会立即重试

**代码位置**：
```1:12:mcp_config.json
{
  "mcpServers": {
    "ocr-service": {
      "command": "python",
      "args": [
        "-m",
        "ocr_mcp_service"
      ],
      "cwd": "C:\\Users\\Q\\Desktop\\Github\\ocr-mcp-service"
    }
  }
}
```

**影响**：
- 服务无法启动，工具不可用
- 需要手动修复配置
- 用户体验差

**建议**：
- 使用`config_manager.py`自动生成正确的配置
- 添加配置验证机制
- 提供配置修复工具

---

### 7. 进程管理问题 ⚠️ **轻微**

**问题描述**：
- 如果进程崩溃，Cursor需要重新启动
- 没有自动重启机制
- 重启可能存在延迟

**影响**：
- 服务崩溃后需要等待Cursor重新启动
- 重启延迟期间工具不可用
- 用户可能认为工具"掉线"

**建议**：
- 实现进程监控和自动重启（如果可能）
- 添加健康检查机制
- 提供快速恢复策略

---

## 🎯 优先级修复建议

### 高优先级（立即修复）

1. **添加超时机制**
   - 为OCR处理设置超时（建议60秒）
   - 超时后返回错误而不是挂起

2. **添加异常恢复机制**
   - 在`main()`函数中添加全局异常处理
   - 确保异常不会导致进程退出

3. **修复配置路径**
   - 更新`mcp_config.json`使用正确的路径
   - 或使用`config_manager.py`重新生成

### 中优先级（近期修复）

4. **优化资源管理**
   - 实现引擎懒加载
   - 添加内存监控

5. **改进错误处理**
   - 区分错误类型
   - 提供更详细的错误信息

### 低优先级（长期优化）

6. **添加心跳机制**
   - 检查FastMCP支持情况
   - 实现保活机制

7. **进程管理优化**
   - 实现健康检查
   - 添加自动恢复机制

---

## 🔧 快速修复方案

### 方案1：添加超时和异常处理（推荐）

修改`__main__.py`：

```python
import signal
import sys
from .mcp_server import mcp
from .logger import get_logger

logger = get_logger("main")

def timeout_handler(signum, frame):
    """Handle timeout signal."""
    logger.error("OCR处理超时，终止操作")
    raise TimeoutError("OCR处理超时")

def main():
    """Run the MCP server with error handling."""
    try:
        # 设置超时（可选，根据实际需求调整）
        # signal.signal(signal.SIGALRM, timeout_handler)
        
        logger.info("MCP服务器启动")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"MCP服务器异常退出: {e}", exc_info=True)
        # 不立即退出，尝试继续运行
        # 或者优雅退出，让Cursor重新启动
        sys.exit(1)
```

### 方案2：修复配置路径

运行配置生成脚本：

```bash
python -m src.ocr_mcp_service.config_manager cursor --force
```

或手动更新`mcp_config.json`使用正确的路径。

---

## 📊 监控建议

1. **添加健康检查工具**
   - 定期检查服务状态
   - 记录掉线事件

2. **日志分析**
   - 分析日志中的错误模式
   - 识别常见掉线原因

3. **性能监控**
   - 监控内存使用
   - 监控处理时间
   - 监控连接状态

---

## 📝 总结

MCP工具掉线的主要原因包括：
1. **缺少超时机制** - 导致长时间等待
2. **缺少异常恢复** - 导致进程崩溃
3. **资源占用** - 导致OOM
4. **配置问题** - 导致启动失败

建议优先修复超时和异常处理问题，这些是最容易导致掉线的根本原因。

