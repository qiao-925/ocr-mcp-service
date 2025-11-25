#!/usr/bin/env python3
"""识别图片脚本。"""

import sys
import json
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from ocr_mcp_service.tools import recognize_text_from_path


def main():
    """主函数。"""
    images = [
        "tests/test_images/IMG_20251124_220948.jpg",
        "tests/test_images/IMG_20251124_220855.jpg",
    ]

    results = []

    for i, image_path in enumerate(images, 1):
        print("=" * 60)
        print(f"识别图片 {i}: {Path(image_path).name}")
        print("=" * 60)
        print("正在处理，请稍候...\n")

        try:
            result = recognize_text_from_path(image_path)

            if result["success"]:
                print(f"✓ 识别成功！共识别 {result['line_count']} 行文字\n")
                print("识别文本：")
                print("-" * 60)
                print(result["text"])
                print("-" * 60)
                print()

                results.append(
                    {
                        "image": Path(image_path).name,
                        "success": True,
                        "text": result["text"],
                        "line_count": result["line_count"],
                        "lines": result["lines"][:10],  # 只保存前10行详细信息
                    }
                )
            else:
                print(f"✗ 识别失败: {result.get('error', '未知错误')}\n")
                results.append(
                    {
                        "image": Path(image_path).name,
                        "success": False,
                        "error": result.get("error", "未知错误"),
                    }
                )

        except Exception as e:
            print(f"✗ 处理出错: {e}\n")
            results.append(
                {
                    "image": Path(image_path).name,
                    "success": False,
                    "error": str(e),
                }
            )

    # 保存结果到JSON文件
    output_file = Path(__file__).parent.parent / "ocr_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print("识别完成！结果已保存到: ocr_results.json")
    print("=" * 60)


if __name__ == "__main__":
    main()



