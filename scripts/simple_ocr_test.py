#!/usr/bin/env python3
"""简单的OCR测试脚本。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocr_mcp_service.tools import recognize_text_from_path

# 识别图片
images = [
    "tests/test_images/IMG_20251124_220948.jpg",
    "tests/test_images/IMG_20251124_220855.jpg",
]

for img_path in images:
    print(f"\n{'='*60}")
    print(f"识别: {Path(img_path).name}")
    print('='*60)
    
    result = recognize_text_from_path(img_path)
    
    if result['success']:
        print(f"\n✓ 成功！识别到 {result['line_count']} 行文字\n")
        print(result['text'])
    else:
        print(f"\n✗ 失败: {result.get('error', '未知错误')}")



