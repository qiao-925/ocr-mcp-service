"""Progress tracking for OCR processing."""

import time
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
    """Track OCR processing progress."""

    def __init__(
        self,
        on_progress: Optional[Callable[[float, str, str], None]] = None
    ):
        """Initialize progress tracker.
        
        Args:
            on_progress: Callback function called on progress updates.
                       Signature: (percentage: float, stage: str, message: str) -> None
        """
        self.on_progress = on_progress
        self.history: List[ProgressUpdate] = []
        self._current_percentage = 0.0
        self._current_stage = ""

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
            except Exception:
                # Silently ignore callback errors
                pass

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
        self.history.clear()
        self._current_percentage = 0.0
        self._current_stage = ""

