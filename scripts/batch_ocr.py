#!/usr/bin/env python3
"""批量OCR处理脚本，支持重试、分批处理和汇总报告。

功能：
- 批量处理图片目录中的所有图片
- 自动重试失败的图片
- 分批处理，避免服务负载过高
- 生成详细的处理报告
- 支持断点续传（跳过已处理的图片）
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.common import setup_script


class BatchOCRProcessor:
    """批量OCR处理器，支持重试和分批处理。"""
    
    def __init__(
        self,
        image_dir: Path,
        output_dir: Optional[Path] = None,
        engine: str = "paddleocr",
        batch_size: int = 2,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        skip_existing: bool = True,
        lang: str = "ch"
    ):
        """初始化批量处理器。
        
        Args:
            image_dir: 图片目录
            output_dir: 输出目录（默认：image_dir/ocr_results）
            engine: OCR引擎类型
            batch_size: 每批处理的图片数量
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            skip_existing: 是否跳过已处理的图片
            lang: 语言代码
        """
        self.image_dir = Path(image_dir).resolve()
        self.output_dir = output_dir or (self.image_dir / "ocr_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.engine = engine
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.skip_existing = skip_existing
        self.lang = lang
        
        # 统计信息
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "retries": 0,
            "start_time": None,
            "end_time": None,
            "errors": []
        }
        
        # 支持的图片格式
        self.image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
    
    def find_images(self) -> List[Path]:
        """查找目录中的所有图片文件。"""
        images = []
        for ext in self.image_extensions:
            images.extend(self.image_dir.glob(f"*{ext}"))
            images.extend(self.image_dir.glob(f"*{ext.upper()}"))
        
        # 排序以确保处理顺序一致
        return sorted(images)
    
    def is_already_processed(self, image_path: Path) -> bool:
        """检查图片是否已经处理过。"""
        if not self.skip_existing:
            return False
        
        json_file = self.output_dir / f"{image_path.stem}_ocr.json"
        return json_file.exists()
    
    def process_image(self, image_path: Path) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """处理单张图片，带重试机制。
        
        Returns:
            (success, result_dict, error_message)
        """
        from ocr_mcp_service.ocr_engine import OCREngineFactory
        from ocr_mcp_service.utils import validate_image
        
        for attempt in range(self.max_retries + 1):
            try:
                # 验证图片
                validate_image(str(image_path))
                
                # 获取引擎并识别
                engine = OCREngineFactory.get_engine(self.engine)
                
                # 根据引擎类型传递参数
                if self.engine == "paddleocr":
                    result = engine.recognize_image(str(image_path), lang=self.lang)
                else:
                    result = engine.recognize_image(str(image_path))
                
                # 转换为字典
                result_dict = result.to_dict()
                
                return True, result_dict, None
                
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                
                # 检查是否是连接错误
                is_connection_error = (
                    "Not connected" in error_msg or
                    "Connection" in error_msg or
                    "timeout" in error_msg.lower() or
                    error_type == "TimeoutError"
                )
                
                if attempt < self.max_retries:
                    # 如果是连接错误，等待更长时间
                    wait_time = self.retry_delay * (attempt + 1) if is_connection_error else self.retry_delay
                    print(f"  ⚠️  尝试 {attempt + 1}/{self.max_retries + 1} 失败: {error_msg}")
                    print(f"  ⏳ 等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                    self.stats["retries"] += 1
                else:
                    # 最后一次尝试失败
                    return False, None, f"{error_type}: {error_msg}"
        
        return False, None, "Max retries exceeded"
    
    def save_result(self, image_path: Path, result_dict: Dict):
        """保存OCR结果。"""
        base_name = image_path.stem
        
        # 保存JSON格式
        json_file = self.output_dir / f"{base_name}_ocr.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        # 保存文本格式
        txt_file = self.output_dir / f"{base_name}_ocr.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(result_dict.get("text", ""))
    
    def process_batch(self, images: List[Path]) -> Dict:
        """处理一批图片。
        
        Returns:
            处理结果统计
        """
        batch_stats = {
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        for image_path in images:
            print(f"\n📷 处理: {image_path.name}")
            
            # 检查是否已处理
            if self.is_already_processed(image_path):
                print(f"  ⏭️  跳过（已处理）")
                batch_stats["skipped"] += 1
                self.stats["skipped"] += 1
                continue
            
            # 处理图片
            success, result_dict, error_msg = self.process_image(image_path)
            
            if success:
                # 保存结果
                self.save_result(image_path, result_dict)
                
                text_length = len(result_dict.get("text", ""))
                boxes_count = len(result_dict.get("boxes", []))
                processing_time = result_dict.get("processing_time", 0.0)
                
                print(f"  ✅ 成功: {text_length}字符, {boxes_count}个文本块, {processing_time:.2f}秒")
                batch_stats["success"] += 1
                self.stats["success"] += 1
            else:
                print(f"  ❌ 失败: {error_msg}")
                batch_stats["failed"] += 1
                self.stats["failed"] += 1
                self.stats["errors"].append({
                    "image": image_path.name,
                    "error": error_msg
                })
        
        return batch_stats
    
    def process_all(self):
        """处理所有图片。"""
        print("=" * 80)
        print("批量OCR处理")
        print("=" * 80)
        print(f"图片目录: {self.image_dir}")
        print(f"输出目录: {self.output_dir}")
        print(f"引擎: {self.engine}")
        print(f"批次大小: {self.batch_size}")
        print(f"最大重试: {self.max_retries}")
        print(f"跳过已处理: {self.skip_existing}")
        print("=" * 80)
        
        # 查找所有图片
        images = self.find_images()
        self.stats["total"] = len(images)
        self.stats["start_time"] = datetime.now().isoformat()
        
        if not images:
            print("❌ 未找到图片文件")
            return
        
        print(f"\n找到 {len(images)} 张图片")
        
        # 分批处理
        total_batches = (len(images) + self.batch_size - 1) // self.batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(images))
            batch_images = images[start_idx:end_idx]
            
            print(f"\n{'=' * 80}")
            print(f"批次 {batch_num + 1}/{total_batches} ({len(batch_images)} 张图片)")
            print(f"{'=' * 80}")
            
            # 处理批次
            batch_stats = self.process_batch(batch_images)
            
            print(f"\n批次统计: ✅ {batch_stats['success']} 成功, "
                  f"❌ {batch_stats['failed']} 失败, "
                  f"⏭️  {batch_stats['skipped']} 跳过")
            
            # 批次间等待，避免服务负载过高
            if batch_num < total_batches - 1:
                wait_time = 1.0
                print(f"\n⏳ 批次间等待 {wait_time} 秒...")
                time.sleep(wait_time)
        
        # 完成统计
        self.stats["end_time"] = datetime.now().isoformat()
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成处理报告。"""
        print("\n" + "=" * 80)
        print("处理完成")
        print("=" * 80)
        
        # 计算总时间
        if self.stats["start_time"] and self.stats["end_time"]:
            start = datetime.fromisoformat(self.stats["start_time"])
            end = datetime.fromisoformat(self.stats["end_time"])
            duration = (end - start).total_seconds()
            print(f"总耗时: {duration:.1f} 秒")
        
        print(f"\n统计:")
        print(f"  总计: {self.stats['total']}")
        print(f"  ✅ 成功: {self.stats['success']}")
        print(f"  ❌ 失败: {self.stats['failed']}")
        print(f"  ⏭️  跳过: {self.stats['skipped']}")
        print(f"  🔄 重试: {self.stats['retries']}")
        
        if self.stats["errors"]:
            print(f"\n失败列表:")
            for error in self.stats["errors"]:
                print(f"  - {error['image']}: {error['error']}")
        
        # 保存报告到JSON文件
        report_file = self.output_dir / "batch_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存: {report_file}")


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(
        description="批量OCR处理脚本，支持重试和分批处理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理当前目录的所有图片，每批2张
  python scripts/batch_ocr.py .

  # 处理指定目录，每批3张，最多重试5次
  python scripts/batch_ocr.py /path/to/images --batch-size 3 --max-retries 5

  # 使用easyocr引擎，不跳过已处理的图片
  python scripts/batch_ocr.py . --engine easyocr --no-skip-existing
        """
    )
    
    parser.add_argument(
        "image_dir",
        type=str,
        help="图片目录路径"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        help="输出目录（默认：image_dir/ocr_results）"
    )
    
    parser.add_argument(
        "--engine",
        choices=["paddleocr", "paddleocr_mcp", "easyocr", "deepseek"],
        default="paddleocr",
        help="OCR引擎类型（默认：paddleocr）"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help="每批处理的图片数量（默认：2）"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="最大重试次数（默认：3）"
    )
    
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=2.0,
        help="重试延迟（秒，默认：2.0）"
    )
    
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="不跳过已处理的图片"
    )
    
    parser.add_argument(
        "--lang",
        type=str,
        default="ch",
        help="语言代码（默认：ch，仅paddleocr）"
    )
    
    args = parser.parse_args()
    
    # 验证图片目录
    image_dir = Path(args.image_dir).resolve()
    if not image_dir.exists():
        print(f"❌ 错误: 目录不存在: {image_dir}")
        sys.exit(1)
    
    if not image_dir.is_dir():
        print(f"❌ 错误: 不是目录: {image_dir}")
        sys.exit(1)
    
    # 创建处理器
    processor = BatchOCRProcessor(
        image_dir=image_dir,
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
        engine=args.engine,
        batch_size=args.batch_size,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay,
        skip_existing=not args.no_skip_existing,
        lang=args.lang
    )
    
    # 处理所有图片
    try:
        processor.process_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        processor.generate_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        traceback.print_exc()
        processor.generate_report()
        sys.exit(1)


if __name__ == "__main__":
    main()

