"""MCP服务器测试"""

import pytest
from unittest.mock import Mock, patch
from ocr_mcp_service.mcp_server import (
    mcp,
    set_mcp_log_callback,
    send_mcp_log,
)


def test_mcp_instance():
    """测试MCP实例创建"""
    assert mcp is not None
    assert hasattr(mcp, "name") or hasattr(mcp, "__class__")


def test_set_mcp_log_callback():
    """测试设置MCP日志回调"""
    callback = Mock()
    
    # 设置回调
    set_mcp_log_callback(callback)
    
    # 发送日志应该调用回调
    send_mcp_log("info", "test_logger", {"message": "test"})
    
    # 验证回调被调用
    callback.assert_called_once()
    call_args = callback.call_args
    assert call_args.kwargs["level"] == "info"
    assert call_args.kwargs["logger"] == "test_logger"
    assert call_args.kwargs["data"]["message"] == "test"


def test_send_mcp_log_with_callback():
    """测试发送MCP日志（有回调）"""
    callback = Mock()
    set_mcp_log_callback(callback)
    
    # 发送不同级别的日志
    send_mcp_log("debug", "test", {"message": "debug message"})
    send_mcp_log("info", "test", {"message": "info message"})
    send_mcp_log("warning", "test", {"message": "warning message"})
    send_mcp_log("error", "test", {"message": "error message"})
    
    # 验证所有调用
    assert callback.call_count == 4


def test_send_mcp_log_without_callback():
    """测试发送MCP日志（无回调）"""
    # 清除回调
    set_mcp_log_callback(None)
    
    # 应该不会抛出异常
    send_mcp_log("info", "test", {"message": "test"})


def test_send_mcp_log_callback_exception():
    """测试回调异常时的静默处理"""
    def failing_callback(**kwargs):
        raise Exception("Callback error")
    
    set_mcp_log_callback(failing_callback)
    
    # 应该不会抛出异常，而是静默处理
    send_mcp_log("info", "test", {"message": "test"})


def test_send_mcp_log_data_format():
    """测试MCP日志数据格式"""
    callback = Mock()
    set_mcp_log_callback(callback)
    
    test_data = {
        "message": "test message",
        "progress": 50.0,
        "stage": "processing",
        "custom_field": "custom_value"
    }
    
    send_mcp_log("info", "test_logger", test_data)
    
    # 验证数据格式
    call_args = callback.call_args
    assert call_args.kwargs["level"] == "info"
    assert call_args.kwargs["logger"] == "test_logger"
    assert call_args.kwargs["data"] == test_data


def test_set_mcp_log_callback_replace():
    """测试替换MCP日志回调"""
    callback1 = Mock()
    callback2 = Mock()
    
    # 设置第一个回调
    set_mcp_log_callback(callback1)
    send_mcp_log("info", "test", {"message": "test1"})
    
    # 替换为第二个回调
    set_mcp_log_callback(callback2)
    send_mcp_log("info", "test", {"message": "test2"})
    
    # 验证只有第二个回调被调用
    assert callback1.call_count == 1
    assert callback2.call_count == 1

