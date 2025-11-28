"""场景检测器：返回通用prompt模板。"""

from typing import Dict, Any
from .models import OCRResult


def detect_scenario(ocr_result: OCRResult) -> Dict[str, Any]:
    """返回通用prompt模板。
    
    Args:
        ocr_result: OCR识别结果
        
    Returns:
        包含通用prompt模板的字典
    """
    from .prompt_loader import get_scenario_template
    
    return {
        "scenario": "通用模板",
        "scenario_id": "通用",
        "confidence": 1.0,
        "prompt_template": get_scenario_template(),
        "reason": "使用通用模板",
        "usage_tip": "这是一个通用prompt模板，适用于各种图片分析场景。将模板中的图片路径替换为实际图片路径后即可使用。"
    }
