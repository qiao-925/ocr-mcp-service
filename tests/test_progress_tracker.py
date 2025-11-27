"""进度跟踪测试"""

import pytest
import time
from unittest.mock import Mock
from ocr_mcp_service.progress_tracker import (
    ProgressUpdate,
    ProgressTracker,
)


def test_progress_update():
    """测试ProgressUpdate数据类"""
    update = ProgressUpdate(
        timestamp=1234567890.0,
        percentage=50.0,
        stage="processing",
        message="Half way done"
    )
    
    assert update.timestamp == 1234567890.0
    assert update.percentage == 50.0
    assert update.stage == "processing"
    assert update.message == "Half way done"


def test_progress_tracker_init_without_callback():
    """测试ProgressTracker初始化（无回调）"""
    tracker = ProgressTracker()
    
    assert tracker.on_progress is None
    assert tracker.history == []
    assert tracker._current_percentage == 0.0
    assert tracker._current_stage == ""


def test_progress_tracker_init_with_callback():
    """测试ProgressTracker初始化（有回调）"""
    callback = Mock()
    tracker = ProgressTracker(on_progress=callback)
    
    assert tracker.on_progress == callback
    assert tracker.history == []


def test_progress_tracker_update():
    """测试进度更新"""
    tracker = ProgressTracker()
    
    tracker.update(25.0, "stage1", "Starting")
    tracker.update(50.0, "stage2", "Half way")
    tracker.update(75.0, "stage3", "Almost done")
    
    assert len(tracker.history) == 3
    assert tracker._current_percentage == 75.0
    assert tracker._current_stage == "stage3"
    
    # 验证历史记录
    assert tracker.history[0].percentage == 25.0
    assert tracker.history[0].stage == "stage1"
    assert tracker.history[1].percentage == 50.0
    assert tracker.history[2].percentage == 75.0


def test_progress_tracker_update_with_callback():
    """测试进度更新（带回调）"""
    callback = Mock()
    tracker = ProgressTracker(on_progress=callback)
    
    tracker.update(30.0, "test_stage", "Test message")
    
    # 验证回调被调用
    callback.assert_called_once_with(30.0, "test_stage", "Test message")


def test_progress_tracker_update_boundary():
    """测试进度值边界处理"""
    tracker = ProgressTracker()
    
    # 测试负值（应该被限制为0）
    tracker.update(-10.0, "stage", "Negative")
    assert tracker._current_percentage == 0.0
    
    # 测试超过100的值（应该被限制为100）
    tracker.update(150.0, "stage", "Over 100")
    assert tracker._current_percentage == 100.0
    
    # 测试正常值
    tracker.update(50.0, "stage", "Normal")
    assert tracker._current_percentage == 50.0


def test_progress_tracker_update_callback_exception():
    """测试回调异常处理"""
    def failing_callback(*args):
        raise Exception("Callback error")
    
    tracker = ProgressTracker(on_progress=failing_callback)
    
    # 应该不会抛出异常
    tracker.update(50.0, "stage", "Test")
    
    # 验证历史记录仍然被保存
    assert len(tracker.history) == 1


def test_progress_tracker_get_history():
    """测试获取历史记录"""
    tracker = ProgressTracker()
    
    tracker.update(10.0, "stage1", "Message 1")
    tracker.update(20.0, "stage2", "Message 2")
    tracker.update(30.0, "stage3", "Message 3")
    
    history = tracker.get_history()
    
    assert len(history) == 3
    assert isinstance(history[0], dict)
    assert history[0]["percentage"] == 10.0
    assert history[0]["stage"] == "stage1"
    assert history[0]["message"] == "Message 1"
    assert "timestamp" in history[0]


def test_progress_tracker_get_current():
    """测试获取当前进度"""
    tracker = ProgressTracker()
    
    # 初始状态
    current = tracker.get_current()
    assert current["percentage"] == 0.0
    assert current["stage"] == ""
    
    # 更新后
    tracker.update(45.0, "current_stage", "Current message")
    current = tracker.get_current()
    assert current["percentage"] == 45.0
    assert current["stage"] == "current_stage"


def test_progress_tracker_reset():
    """测试重置进度跟踪器"""
    callback = Mock()
    tracker = ProgressTracker(on_progress=callback)
    
    # 更新一些进度
    tracker.update(50.0, "stage1", "Message 1")
    tracker.update(75.0, "stage2", "Message 2")
    
    assert len(tracker.history) == 2
    assert tracker._current_percentage == 75.0
    
    # 重置
    tracker.reset()
    
    assert len(tracker.history) == 0
    assert tracker._current_percentage == 0.0
    assert tracker._current_stage == ""
    # 回调应该仍然存在
    assert tracker.on_progress == callback


def test_progress_tracker_timestamp():
    """测试进度更新的时间戳"""
    tracker = ProgressTracker()
    
    before = time.time()
    tracker.update(50.0, "stage", "Test")
    after = time.time()
    
    assert len(tracker.history) == 1
    timestamp = tracker.history[0].timestamp
    assert before <= timestamp <= after


def test_progress_tracker_multiple_updates():
    """测试多次进度更新"""
    tracker = ProgressTracker()
    
    for i in range(10):
        tracker.update(i * 10.0, f"stage_{i}", f"Message {i}")
    
    assert len(tracker.history) == 10
    assert tracker._current_percentage == 90.0
    assert tracker._current_stage == "stage_9"


def test_progress_tracker_empty_message():
    """测试空消息"""
    tracker = ProgressTracker()
    
    tracker.update(50.0, "stage", "")
    
    assert len(tracker.history) == 1
    assert tracker.history[0].message == ""


def test_progress_tracker_history_format():
    """测试历史记录格式"""
    tracker = ProgressTracker()
    
    tracker.update(33.33, "test_stage", "Test message with special chars: !@#$%")
    
    history = tracker.get_history()
    assert len(history) == 1
    
    record = history[0]
    assert isinstance(record, dict)
    assert "timestamp" in record
    assert "percentage" in record
    assert "stage" in record
    assert "message" in record
    assert record["percentage"] == 33.33
    assert record["stage"] == "test_stage"
    assert record["message"] == "Test message with special chars: !@#$%"

