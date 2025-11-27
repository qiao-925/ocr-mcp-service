"""日志系统测试"""

import pytest
import tempfile
import os
import logging
from pathlib import Path
from unittest.mock import Mock, patch
from ocr_mcp_service.logger import (
    MCPLogHandler,
    OCRLogger,
    get_logger,
    initialize_logger,
    set_mcp_log_level,
    log_progress,
    PYTHON_TO_MCP_LEVEL,
)


def test_mcp_log_handler_init():
    """测试MCPLogHandler初始化"""
    handler = MCPLogHandler()
    assert handler.mcp_callback is None
    assert handler.min_level == logging.INFO


def test_mcp_log_handler_set_callback():
    """测试设置MCP回调"""
    handler = MCPLogHandler()
    callback = Mock()
    
    handler.set_mcp_callback(callback)
    assert handler.mcp_callback == callback


def test_mcp_log_handler_set_min_level():
    """测试设置最小日志级别"""
    handler = MCPLogHandler()
    
    handler.set_min_level(logging.DEBUG)
    assert handler.min_level == logging.DEBUG
    
    handler.set_min_level(logging.ERROR)
    assert handler.min_level == logging.ERROR


def test_mcp_log_handler_emit_with_callback():
    """测试emit方法（有回调）"""
    callback = Mock()
    handler = MCPLogHandler(callback)
    handler.set_min_level(logging.DEBUG)
    
    # 创建日志记录
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="test message",
        args=(),
        exc_info=None
    )
    
    handler.emit(record)
    
    # 验证回调被调用
    callback.assert_called_once()
    call_args = callback.call_args
    assert call_args.kwargs["level"] == "info"
    assert call_args.kwargs["logger"] == "test_logger"
    assert "message" in call_args.kwargs["data"]


def test_mcp_log_handler_emit_level_filter():
    """测试emit方法的日志级别过滤"""
    callback = Mock()
    handler = MCPLogHandler(callback)
    handler.set_min_level(logging.WARNING)
    
    # DEBUG级别应该被过滤
    record_debug = logging.LogRecord(
        name="test", level=logging.DEBUG,
        pathname="test.py", lineno=1, msg="debug", args=(), exc_info=None
    )
    handler.emit(record_debug)
    callback.assert_not_called()
    
    # WARNING级别应该通过
    record_warning = logging.LogRecord(
        name="test", level=logging.WARNING,
        pathname="test.py", lineno=1, msg="warning", args=(), exc_info=None
    )
    handler.emit(record_warning)
    callback.assert_called_once()


def test_mcp_log_handler_emit_extra_fields():
    """测试emit方法提取额外字段"""
    callback = Mock()
    handler = MCPLogHandler(callback)
    
    # 创建带额外字段的记录
    record = logging.LogRecord(
        name="test", level=logging.INFO,
        pathname="test.py", lineno=1, msg="test", args=(), exc_info=None
    )
    record.progress = 50.0
    record.stage = "processing"
    record.image_path = "/path/to/image.jpg"
    
    handler.emit(record)
    
    # 验证额外字段被提取
    call_args = callback.call_args
    data = call_args.kwargs["data"]
    assert data["progress"] == 50.0
    assert data["stage"] == "processing"
    assert data["image_path"] == "/path/to/image.jpg"


def test_mcp_log_handler_emit_callback_exception():
    """测试emit方法回调异常处理"""
    def failing_callback(**kwargs):
        raise Exception("Callback error")
    
    handler = MCPLogHandler(failing_callback)
    
    record = logging.LogRecord(
        name="test", level=logging.INFO,
        pathname="test.py", lineno=1, msg="test", args=(), exc_info=None
    )
    
    # 应该不会抛出异常
    handler.emit(record)


def test_ocr_logger_singleton():
    """测试OCRLogger单例模式"""
    # 重置单例状态
    OCRLogger._instance = None
    OCRLogger._initialized = False
    
    logger1 = OCRLogger()
    logger2 = OCRLogger()
    
    assert logger1 is logger2


def test_ocr_logger_file_handler():
    """测试OCRLogger文件处理器"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test.log")
        
        # 重置单例状态
        OCRLogger._instance = None
        OCRLogger._initialized = False
        
        with patch("ocr_mcp_service.logger.get_env") as mock_get_env:
            mock_get_env.side_effect = lambda key, default: {
                "LOG_LEVEL": "INFO",
                "LOG_FILE": log_file,
                "LOG_MAX_BYTES": "10485760",
                "LOG_BACKUP_COUNT": "5"
            }.get(key, default)
            
            logger = OCRLogger()
            test_logger = logger.get_logger("test")
            test_logger.info("test message")
            
            # 关闭所有处理器以释放文件句柄
            for handler in logger.logger.handlers:
                handler.close()
            
            # 验证日志文件被创建
            assert os.path.exists(log_file)
            
            # 验证日志内容
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "test message" in content


def test_ocr_logger_set_mcp_callback():
    """测试OCRLogger设置MCP回调"""
    OCRLogger._instance = None
    OCRLogger._initialized = False
    
    callback = Mock()
    logger = OCRLogger()
    logger.set_mcp_callback(callback)
    
    # 验证回调被设置
    assert logger.mcp_handler.mcp_callback == callback


def test_ocr_logger_set_mcp_log_level():
    """测试OCRLogger设置MCP日志级别"""
    OCRLogger._instance = None
    OCRLogger._initialized = False
    
    logger = OCRLogger()
    logger.set_mcp_log_level("debug")
    assert logger.mcp_handler.min_level == logging.DEBUG
    
    logger.set_mcp_log_level("error")
    assert logger.mcp_handler.min_level == logging.ERROR


def test_ocr_logger_get_logger():
    """测试OCRLogger获取logger"""
    OCRLogger._instance = None
    OCRLogger._initialized = False
    
    logger = OCRLogger()
    test_logger = logger.get_logger("test_module")
    
    assert test_logger is not None
    assert test_logger.name == "ocr_mcp_service.test_module"


def test_ocr_logger_log_progress():
    """测试OCRLogger进度日志"""
    OCRLogger._instance = None
    OCRLogger._initialized = False
    
    callback = Mock()
    logger = OCRLogger()
    logger.set_mcp_callback(callback)
    
    logger.log_progress("test", 50.0, "Processing", stage="ocr")
    
    # 验证回调被调用
    callback.assert_called()
    call_args = callback.call_args
    data = call_args.kwargs["data"]
    assert data["progress"] == 50.0
    assert data["stage"] == "ocr"


def test_get_logger_function():
    """测试get_logger模块级函数"""
    # 重置全局实例
    import ocr_mcp_service.logger as logger_module
    logger_module._logger_instance = None
    
    test_logger = get_logger("test")
    assert test_logger is not None
    
    # 再次调用应该返回同一个实例
    test_logger2 = get_logger("test")
    assert test_logger2 is not None


def test_initialize_logger():
    """测试initialize_logger函数"""
    import ocr_mcp_service.logger as logger_module
    logger_module._logger_instance = None
    
    callback = Mock()
    initialize_logger(callback)
    
    # 验证回调被设置
    assert logger_module._logger_instance is not None
    assert logger_module._logger_instance.mcp_handler.mcp_callback == callback


def test_set_mcp_log_level_function():
    """测试set_mcp_log_level模块级函数"""
    import ocr_mcp_service.logger as logger_module
    logger_module._logger_instance = None
    
    set_mcp_log_level("warning")
    
    # 验证级别被设置
    assert logger_module._logger_instance is not None
    assert logger_module._logger_instance.mcp_handler.min_level == logging.WARNING


def test_log_progress_function():
    """测试log_progress模块级函数"""
    import ocr_mcp_service.logger as logger_module
    
    # 重置单例状态
    logger_module._logger_instance = None
    OCRLogger._instance = None
    OCRLogger._initialized = False
    
    callback = Mock()
    initialize_logger(callback)
    
    # 验证回调已设置
    assert logger_module._logger_instance is not None
    assert logger_module._logger_instance.mcp_handler.mcp_callback == callback
    
    log_progress("test", 75.0, "Almost done", stage="final")
    
    # 验证回调被调用（通过MCPLogHandler的emit方法）
    # 回调是通过logger.info() -> handler.emit() -> callback()调用的
    assert callback.called, "MCP callback should be called via handler.emit()"
    
    # 验证回调参数
    if callback.called:
        call_args = callback.call_args
        assert call_args.kwargs["level"] in ["info", "debug", "warning", "error"]
        data = call_args.kwargs["data"]
        assert data["progress"] == 75.0
        assert data["stage"] == "final"


def test_python_to_mcp_level_mapping():
    """测试Python到MCP日志级别映射"""
    assert PYTHON_TO_MCP_LEVEL[logging.DEBUG] == "debug"
    assert PYTHON_TO_MCP_LEVEL[logging.INFO] == "info"
    assert PYTHON_TO_MCP_LEVEL[logging.WARNING] == "warning"
    assert PYTHON_TO_MCP_LEVEL[logging.ERROR] == "error"
    assert PYTHON_TO_MCP_LEVEL[logging.CRITICAL] == "critical"

