"""OCR引擎综合验证脚本 - 用于手动验证和调试

注意：这是验证脚本，不是pytest单元测试。
pytest单元测试位于 tests/ 目录下。
"""

import sys
import glob
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add project root to path before importing scripts.common
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup script environment
from scripts.common import setup_script
setup_script()


def test_imports() -> bool:
    """测试所有模块导入"""
    print("=" * 60)
    print("1. 测试模块导入")
    print("=" * 60)
    
    try:
        from ocr_mcp_service import __version__
        print(f"  [OK] 包版本: {__version__}")
        
        from ocr_mcp_service.config import PADDLEOCR_LANG, DEEPSEEK_MODEL_NAME
        print(f"  [OK] 配置模块导入成功")
        
        from ocr_mcp_service.utils import validate_image_path
        print(f"  [OK] 工具模块导入成功")
        
        from ocr_mcp_service.models import OCRResult, BoundingBox
        print(f"  [OK] 数据模型导入成功")
        
        from ocr_mcp_service.ocr_engine import OCREngineFactory
        print(f"  [OK] OCR引擎模块导入成功")
        
        from ocr_mcp_service.mcp_server import mcp
        print(f"  [OK] MCP服务器导入成功")
        
        import ocr_mcp_service.tools
        print(f"  [OK] 工具模块导入成功")
        
        return True
    except Exception as e:
        print(f"  [FAIL] 导入错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_tools() -> bool:
    """测试MCP工具注册"""
    print("\n" + "=" * 60)
    print("2. 测试MCP工具注册")
    print("=" * 60)
    
    try:
        import ocr_mcp_service.tools
        from ocr_mcp_service.mcp_server import mcp
        
        expected_tools = [
            "recognize_image_paddleocr",
            "recognize_image_paddleocr_mcp",
            "recognize_image_easyocr",
            "recognize_image_deepseek",
        ]
        
        for tool_name in expected_tools:
            if hasattr(ocr_mcp_service.tools, tool_name):
                print(f"  [OK] {tool_name} 已定义")
            else:
                print(f"  [FAIL] {tool_name} 未找到")
                return False
        
        if hasattr(mcp, 'tool'):
            print(f"  [OK] MCP服务器工具装饰器可用")
        else:
            print(f"  [FAIL] MCP服务器缺少工具装饰器")
            return False
        
        return True
    except Exception as e:
        print(f"  [FAIL] 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_engine_availability(engine_type: str) -> tuple[bool, Optional[str], Optional[Any]]:
    """测试引擎可用性"""
    try:
        from ocr_mcp_service.ocr_engine import OCREngineFactory
        
        engine = OCREngineFactory.get_engine(engine_type)
        return True, None, engine
    except ImportError as e:
        return False, f"依赖未安装: {e}", None
    except RuntimeError as e:
        return False, f"引擎不可用: {e}", None
    except Exception as e:
        return False, f"错误: {e}", None


def test_all_engines_availability() -> Dict[str, bool]:
    """测试所有引擎的可用性"""
    print("\n" + "=" * 60)
    print("3. 测试引擎可用性")
    print("=" * 60)
    
    engines = {
        "paddleocr": "PaddleOCR",
        "paddleocr_mcp": "paddleocr-mcp",
        "easyocr": "EasyOCR",
        "deepseek": "DeepSeek OCR (不推荐，模型较大)",
    }
    
    results = {}
    
    for engine_type, engine_name in engines.items():
        print(f"\n测试 {engine_name} ({engine_type})...")
        available, error, engine = test_engine_availability(engine_type)
        
        if available:
            print(f"  [OK] {engine_name} 可用")
            results[engine_type] = True
        else:
            print(f"  [SKIP] {engine_name} 不可用: {error}")
            results[engine_type] = False
    
    return results


def test_engine_recognition(engine_type: str, image_path: str) -> Optional[Dict[str, Any]]:
    """测试引擎识别功能"""
    try:
        from ocr_mcp_service.ocr_engine import OCREngineFactory
        from ocr_mcp_service.utils import validate_image
        
        validate_image(image_path)
        
        start_time = time.time()
        engine = OCREngineFactory.get_engine(engine_type)
        result = engine.recognize_image(image_path)
        total_time = time.time() - start_time
        
        return {
            "success": True,
            "engine": engine_type,
            "text": result.text,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "total_time": total_time,
            "boxes_count": len(result.boxes),
            "text_length": len(result.text),
        }
    except Exception as e:
        return {
            "success": False,
            "engine": engine_type,
            "error": str(e),
        }


def test_single_image(image_path: str, engine_type: Optional[str] = None) -> None:
    """测试单张图片识别"""
    print("\n" + "=" * 60)
    print("4. 单张图片识别测试")
    print("=" * 60)
    print(f"图片: {image_path}")
    
    if engine_type:
        # 测试指定引擎
        print(f"引擎: {engine_type}")
        result = test_engine_recognition(engine_type, image_path)
        if result and result.get("success"):
            print(f"  [OK] 识别成功")
            print(f"  处理时间: {result['processing_time']:.2f}s")
            print(f"  总时间: {result['total_time']:.2f}s")
            print(f"  置信度: {result['confidence']:.2f}")
            print(f"  文本框数: {result['boxes_count']}")
            print(f"  文本长度: {result['text_length']} 字符")
            print(f"\n识别文本预览（前200字符）:")
            print(f"  {result['text'][:200]}...")
        else:
            print(f"  [FAIL] 识别失败: {result.get('error') if result else 'Unknown error'}")
    else:
        # 测试所有可用引擎
        print("测试所有可用引擎...")
        available_engines = test_all_engines_availability()
        
        results = {}
        for engine_type, available in available_engines.items():
            if available:
                print(f"\n测试 {engine_type}...")
                result = test_engine_recognition(engine_type, image_path)
                results[engine_type] = result
                
                if result and result.get("success"):
                    print(f"  [OK] 识别成功")
                    print(f"  处理时间: {result['processing_time']:.2f}s")
                    print(f"  置信度: {result['confidence']:.2f}")
                else:
                    print(f"  [FAIL] 识别失败: {result.get('error') if result else 'Unknown error'}")


def compare_engines(image_path: str, engines: Optional[List[str]] = None) -> Dict[str, Any]:
    """对比多个引擎"""
    print("\n" + "=" * 60)
    print("5. 多引擎对比测试")
    print("=" * 60)
    print(f"图片: {image_path}")
    
    if engines is None:
        # 自动检测可用引擎
        available = test_all_engines_availability()
        engines = [e for e, avail in available.items() if avail]
    
    if not engines:
        print("  [WARN] 没有可用的引擎进行对比")
        return {}
    
    print(f"对比引擎: {', '.join(engines)}")
    print()
    
    results = {}
    
    for engine_name in engines:
        print(f"测试 {engine_name}...")
        result = test_engine_recognition(engine_name, image_path)
        results[engine_name] = result
        
        if result and result.get("success"):
            print(f"  [OK] 成功 - 时间: {result['processing_time']:.2f}s, 置信度: {result['confidence']:.2f}")
        else:
            print(f"  [FAIL] 失败: {result.get('error') if result else 'Unknown error'}")
        print()
    
    # 对比总结
    successful = {k: v for k, v in results.items() if v and v.get("success")}
    
    if len(successful) > 1:
        print("=" * 60)
        print("对比总结")
        print("=" * 60)
        print(f"{'引擎':<20} {'处理时间(s)':<15} {'置信度':<12} {'文本长度':<12} {'文本框数':<12}")
        print("-" * 60)
        for name, result in successful.items():
            print(f"{name:<20} {result['processing_time']:<15.2f} {result['confidence']:<12.2f} {result['text_length']:<12} {result['boxes_count']:<12}")
        
        if len(successful) > 1:
            fastest = min(successful.items(), key=lambda x: x[1]['processing_time'])
            best_conf = max(successful.items(), key=lambda x: x[1]['confidence'])
            longest = max(successful.items(), key=lambda x: x[1]['text_length'])
            
            print(f"\n最快: {fastest[0]} ({fastest[1]['processing_time']:.2f}s)")
            print(f"最高置信度: {best_conf[0]} ({best_conf[1]['confidence']:.2f})")
            print(f"最长文本: {longest[0]} ({longest[1]['text_length']} 字符)")
    
    # 保存结果
    output_file = f"ocr_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "image_path": image_path,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: {output_file}")
    
    return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="统一的OCR引擎测试脚本")
    parser.add_argument(
        "--mode",
        choices=["imports", "tools", "availability", "test", "compare"],
        default="all",
        help="测试模式 (默认: all)"
    )
    parser.add_argument(
        "--image",
        type=str,
        help="测试图片路径"
    )
    parser.add_argument(
        "--engine",
        choices=["paddleocr", "paddleocr_mcp", "easyocr", "deepseek"],
        help="指定测试的引擎"
    )
    parser.add_argument(
        "--engines",
        nargs="+",
        choices=["paddleocr", "paddleocr_mcp", "easyocr", "deepseek"],
        help="对比测试的引擎列表"
    )
    
    args = parser.parse_args()
    
    # 自动查找测试图片
    if args.image:
        image_path = str(Path(args.image).resolve())
    else:
        # 尝试查找测试图片
        test_images = []
        test_images.extend(glob.glob("*.png"))
        test_images.extend(glob.glob("*.jpg"))
        test_images.extend(glob.glob("**/IMG_*.jpg", recursive=True))
        
        if test_images:
            image_path = str(Path(test_images[0]).resolve())
            print(f"自动检测到测试图片: {image_path}\n")
        else:
            image_path = None
    
    # 执行测试
    if args.mode == "all" or args.mode == "imports":
        if not test_imports():
            print("\n[FAIL] 模块导入测试失败")
            return 1
    
    if args.mode == "all" or args.mode == "tools":
        if not test_mcp_tools():
            print("\n[FAIL] MCP工具测试失败")
            return 1
    
    if args.mode == "all" or args.mode == "availability":
        test_all_engines_availability()
    
    if args.mode == "test" or args.mode == "compare":
        if not image_path:
            print("[ERROR] 需要指定测试图片 (--image)")
            return 1
        
        if args.mode == "test":
            test_single_image(image_path, args.engine)
        else:
            compare_engines(image_path, args.engines)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 测试完成！")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())



