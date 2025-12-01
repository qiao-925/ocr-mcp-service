"""Progress tracking for OCR processing."""

import time
import threading
from typing import Optional, Callable, List, Dict
from dataclasses import dataclass


@dataclass
class ProgressUpdate:
    """Progress update record."""

    timestamp: float
    percentage: float
    stage: str
    message: str


class ProgressTracker:
    """Track OCR processing progress with heartbeat support."""

    def __init__(
        self,
        on_progress: Optional[Callable[[float, str, str], None]] = None,
        heartbeat_interval: float = 5.0
    ):
        """Initialize progress tracker.
        
        Args:
            on_progress: Callback function called on progress updates.
                       Signature: (percentage: float, stage: str, message: str) -> None
            heartbeat_interval: 心跳间隔（秒），用于在长时间操作中保持连接活跃
        """
        self.on_progress = on_progress
        self.history: List[ProgressUpdate] = []
        self._current_percentage = 0.0
        self._current_stage = ""
        self._current_message = ""
        self.heartbeat_interval = heartbeat_interval
        self.last_heartbeat = time.time()
        self._last_update_time = time.time()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._heartbeat_active = False

    def update(
        self,
        percentage: float,
        stage: str,
        message: str = ""
    ):
        """Update progress.
        
        Args:
            percentage: Progress percentage (0-100)
            stage: Current stage name
            message: Progress message
        """
        self._current_percentage = max(0.0, min(100.0, percentage))
        self._current_stage = stage
        self._current_message = message
        self._last_update_time = time.time()
        
        update = ProgressUpdate(
            timestamp=time.time(),
            percentage=self._current_percentage,
            stage=stage,
            message=message
        )
        self.history.append(update)

        if self.on_progress:
            try:
                self.on_progress(
                    self._current_percentage,
                    stage,
                    message
                )
                self.last_heartbeat = time.time()
            except Exception:
                # Silently ignore callback errors
                pass
    
    def send_heartbeat(self):
        """发送心跳进度更新，用于在长时间操作中保持连接活跃。
        
        即使进度没有变化，也会定期发送进度更新，防止客户端超时。
        """
        if not self.on_progress:
            return
        
        now = time.time()
        # 如果距离上次更新超过心跳间隔，发送心跳
        if now - self.last_heartbeat >= self.heartbeat_interval:
            try:
                # 发送当前进度作为心跳
                self.on_progress(
                    self._current_percentage,
                    self._current_stage,
                    f"处理中... ({self._current_message})"
                )
                self.last_heartbeat = now
            except Exception:
                # Silently ignore callback errors
                pass
    
    def start_heartbeat(self):
        """启动自动心跳线程，确保在长时间操作中持续发送心跳。
        
        防止连接因长时间无响应而中断。
        """
        if self._heartbeat_active or not self.on_progress:
            return
        
        self._heartbeat_active = True
        
        def heartbeat_loop():
            """心跳循环，定期发送进度更新。"""
            while self._heartbeat_active:
                try:
                    time.sleep(self.heartbeat_interval)
                    if self._heartbeat_active:
                        self.send_heartbeat()
                except Exception:
                    # 忽略心跳错误，继续运行
                    pass
        
        self._heartbeat_thread = threading.Thread(
            target=heartbeat_loop,
            daemon=True,  # 守护线程，主线程退出时自动退出
            name="ProgressHeartbeat"
        )
        self._heartbeat_thread.start()
    
    def stop_heartbeat(self):
        """停止自动心跳线程。"""
        self._heartbeat_active = False
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            # 等待线程结束（最多等待1秒）
            self._heartbeat_thread.join(timeout=1.0)

    def get_history(self) -> List[Dict]:
        """Get progress history as list of dicts.
        
        Returns:
            List of progress update dictionaries
        """
        return [
            {
                "timestamp": update.timestamp,
                "percentage": update.percentage,
                "stage": update.stage,
                "message": update.message
            }
            for update in self.history
        ]

    def get_current(self) -> Dict:
        """Get current progress.
        
        Returns:
            Current progress dictionary
        """
        return {
            "percentage": self._current_percentage,
            "stage": self._current_stage
        }

    def reset(self):
        """Reset progress tracker."""
        self.stop_heartbeat()
        self.history.clear()
        self._current_percentage = 0.0
        self._current_stage = ""
        self._current_message = ""

