"""Data models for OCR results."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class BoundingBox:
    """Bounding box for text detection."""

    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class OCRResult:
    """OCR recognition result."""

    text: str
    boxes: List[BoundingBox]
    confidence: float
    engine: str
    processing_time: float
    analysis: Optional[str] = None
    progress_history: List[Dict[str, Any]] = field(default_factory=list)
    prompt_suggestion: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "text": self.text,
            "boxes": [
                {"x1": b.x1, "y1": b.y1, "x2": b.x2, "y2": b.y2}
                for b in self.boxes
            ],
            "confidence": self.confidence,
            "engine": self.engine,
            "processing_time": self.processing_time,
        }
        if self.analysis:
            result["analysis"] = self.analysis
        if self.progress_history:
            result["progress_history"] = self.progress_history
        if self.prompt_suggestion:
            result["prompt_suggestion"] = self.prompt_suggestion
        return result

    def get_text_with_analysis(self) -> str:
        """Get text with analysis appended."""
        parts = [self.text]
        
        if self.analysis:
            parts.append(f"\n\n--- 技术解析 ---\n\n{self.analysis}")
        
        return "\n".join(parts)






