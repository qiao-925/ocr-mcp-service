#!/usr/bin/env python3
"""批量保存 OCR 结果到文件"""

import json
from pathlib import Path

# OCR 结果数据（从之前的识别结果中提取）
ocr_data = {
    'IMG_20251124_220855': {
        'text': '1\n法\n福\n山\n新州卫地品\n长江出版社\nCHANGJIANGPRESS\nViVO\nS20\nle]',
        'confidence': 0.5232393205165863,
        'boxes': [
            {"x1": 1538.0, "y1": 2393.0, "x2": 1963.0, "y2": 2712.0},
            {"x1": 2045.0, "y1": 2559.0, "x2": 2069.0, "y2": 2592.0},
            {"x1": 1791.0, "y1": 2728.0, "x2": 1816.0, "y2": 2757.0},
            {"x1": 2137.0, "y1": 2728.0, "x2": 2449.0, "y2": 3039.0},
            {"x1": 3017.0, "y1": 2802.0, "x2": 3046.0, "y2": 3017.0},
            {"x1": 352.0, "y1": 3848.0, "x2": 773.0, "y2": 3930.0},
            {"x1": 366.0, "y1": 3930.0, "x2": 772.0, "y2": 3975.0},
            {"x1": 17.0, "y1": 4448.0, "x2": 297.0, "y2": 4536.0},
            {"x1": 337.0, "y1": 4442.0, "x2": 628.0, "y2": 4536.0},
            {"x1": 2355.0, "y1": 4492.0, "x2": 3071.0, "y2": 4536.0}
        ],
        'processing_time': 34.443774938583374
    },
    # 其他图片的数据...（由于数据量大，这里只保存关键信息）
}

def save_ocr_result(image_name, text, confidence, boxes=None, processing_time=None):
    """保存单张图片的 OCR 结果"""
    base_dir = Path(__file__).parent.parent / "东野圭吾图片测试集"
    ocr_dir = base_dir / "ocr_results"
    ocr_dir.mkdir(exist_ok=True)
    
    # 保存 JSON 格式
    json_data = {
        "source_image": f"东野圭吾图片测试集/{image_name}.jpg",
        "text": text,
        "boxes": boxes or [],
        "confidence": confidence,
        "engine": "paddleocr",
        "processing_time": processing_time or 0.0
    }
    
    json_path = ocr_dir / f"{image_name}_ocr.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # 保存 TXT 格式
    txt_path = ocr_dir / f"{image_name}_ocr.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"## 📷 源图片\n")
        f.write(f"- [{image_name}.jpg](东野圭吾图片测试集/{image_name}.jpg)\n\n")
        f.write(text)
    
    print(f"已保存: {image_name}")

if __name__ == "__main__":
    # 这里可以批量处理
    pass

