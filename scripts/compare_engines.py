"""多引擎对比验证脚本 - 对比不同OCR引擎的性能

注意：这是验证脚本，不是pytest单元测试。
pytest单元测试位于 tests/ 目录下。
"""
import sys
import glob
from pathlib import Path

# Add project root to path before importing scripts.common
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup script environment
from scripts.common import setup_script
setup_script()

# 查找测试图片
test_images = glob.glob('*/IMG_20251124_220855.jpg')
if not test_images:
    test_images = glob.glob('**/IMG_20251124_220855.jpg')

if not test_images:
    print("未找到测试图片")
    sys.exit(1)

image_path = Path(test_images[0]).resolve()
print("=" * 80)
print("多引擎 OCR 对比测试")
print("=" * 80)
print(f"测试图片: {image_path}")
print()

# 要测试的引擎列表
engines_to_test = ["paddleocr", "paddleocr_mcp", "deepseek"]

# 尝试添加 EasyOCR 和 Tesseract（如果可用）
try:
    from ocr_mcp_service.ocr_engine import OCREngineFactory
    test_engine = OCREngineFactory.get_engine("easyocr")
    engines_to_test.append("easyocr")
except:
    pass

try:
    test_engine = OCREngineFactory.get_engine("tesseract")
    engines_to_test.append("tesseract")
except:
    pass

print(f"将测试的引擎: {', '.join(engines_to_test)}")
print()

from ocr_mcp_service.ocr_engine import OCREngineFactory
from ocr_mcp_service.utils import validate_image
import time

# 验证图片
validate_image(str(image_path))

results = {}

for engine_name in engines_to_test:
    print("-" * 80)
    print(f"测试引擎: {engine_name}")
    print("-" * 80)
    
    try:
        start_time = time.time()
        
        # 加载引擎
        print(f"  加载 {engine_name} 引擎...")
        engine = OCREngineFactory.get_engine(engine_name)
        
        # 识别
        print(f"  开始识别...")
        result = engine.recognize_image(str(image_path))
        
        elapsed_time = time.time() - start_time
        
        results[engine_name] = {
            "success": True,
            "text": result.text,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "total_time": elapsed_time,
            "boxes_count": len(result.boxes),
            "text_length": len(result.text),
        }
        
        print(f"  ✓ 成功")
        print(f"  处理时间: {result.processing_time:.2f}s")
        print(f"  总时间: {elapsed_time:.2f}s")
        print(f"  置信度: {result.confidence:.2f}")
        print(f"  文本框数量: {len(result.boxes)}")
        print(f"  文本长度: {len(result.text)} 字符")
        print(f"  文本预览 (前200字符):")
        print(f"  {result.text[:200]}...")
        
    except Exception as e:
        results[engine_name] = {
            "success": False,
            "error": str(e)
        }
        print(f"  ✗ 失败: {e}")
    
    print()

# 对比总结
print("=" * 80)
print("对比总结")
print("=" * 80)

successful = {k: v for k, v in results.items() if v.get("success")}

if len(successful) > 0:
    print("\n性能对比:")
    print(f"{'引擎':<20} {'处理时间(s)':<15} {'总时间(s)':<15} {'置信度':<12} {'文本长度':<12} {'文本框数':<12}")
    print("-" * 80)
    for name, result in successful.items():
        print(f"{name:<20} {result['processing_time']:<15.2f} {result['total_time']:<15.2f} {result['confidence']:<12.2f} {result['text_length']:<12} {result['boxes_count']:<12}")
    
    if len(successful) > 1:
        # 找出最快的
        fastest = min(successful.items(), key=lambda x: x[1]['processing_time'])
        print(f"\n最快: {fastest[0]} ({fastest[1]['processing_time']:.2f}s)")
        
        # 找出置信度最高的
        best_conf = max(successful.items(), key=lambda x: x[1]['confidence'])
        print(f"最高置信度: {best_conf[0]} ({best_conf[1]['confidence']:.2f})")
        
        # 找出文本最长的（可能表示识别更完整）
        longest = max(successful.items(), key=lambda x: x[1]['text_length'])
        print(f"最长文本: {longest[0]} ({longest[1]['text_length']} 字符)")

print("\n" + "=" * 80)
print("详细结果")
print("=" * 80)

for engine_name, result in results.items():
    print(f"\n【{engine_name}】")
    if result.get("success"):
        print(f"文本内容:\n{result['text']}")
    else:
        print(f"错误: {result.get('error', 'Unknown error')}")


def main():
    """Main entry point for script execution."""
    # Script logic is already executed at module level
    pass


if __name__ == "__main__":
    main()

