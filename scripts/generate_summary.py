#!/usr/bin/env python3
"""生成批量OCR处理汇总报告。

从ocr_results目录读取所有OCR结果，生成汇总报告。
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.common import setup_script


def load_ocr_results(results_dir: Path) -> List[Dict]:
    """加载所有OCR结果。"""
    results = []
    
    for json_file in sorted(results_dir.glob("*_ocr.json")):
        try:
            # 尝试读取JSON文件
            result = None
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    result = json.load(f)
            except json.JSONDecodeError:
                # JSON解析失败，尝试从txt文件读取基本信息
                print(f"⚠️  JSON格式错误: {json_file.name}，尝试从txt文件读取...")
                txt_file = json_file.with_suffix(".txt")
                if txt_file.exists():
                    with open(txt_file, "r", encoding="utf-8") as f:
                        text = f.read()
                    # 创建基本结果
                    result = {
                        "text": text,
                        "engine": "unknown",
                        "confidence": 0.0,
                        "processing_time": 0.0,
                        "boxes": []
                    }
                else:
                    print(f"   ⏭️  跳过: {json_file.name}（无法读取）")
                    continue
            
            if result:
                result["source_file"] = json_file.stem.replace("_ocr", "")
                # 确保必要字段存在
                result.setdefault("text", "")
                result.setdefault("boxes", [])
                result.setdefault("confidence", 0.0)
                result.setdefault("processing_time", 0.0)
                result.setdefault("engine", "unknown")
                results.append(result)
                
        except Exception as e:
            print(f"⚠️  无法读取 {json_file.name}: {e}")
    
    return results


def generate_summary(results: List[Dict], output_file: Path):
    """生成汇总报告。"""
    total_images = len(results)
    total_text_length = sum(len(r.get("text", "")) for r in results)
    total_boxes = sum(len(r.get("boxes", [])) for r in results)
    total_processing_time = sum(r.get("processing_time", 0.0) for r in results)
    
    avg_confidence = (
        sum(r.get("confidence", 0.0) for r in results) / total_images
        if total_images > 0 else 0.0
    )
    
    # 统计信息
    summary = {
        "生成时间": datetime.now().isoformat(),
        "统计信息": {
            "总图片数": total_images,
            "总文本长度": total_text_length,
            "总文本块数": total_boxes,
            "总处理时间": f"{total_processing_time:.2f}秒",
            "平均置信度": f"{avg_confidence:.3f}",
            "平均处理时间": f"{total_processing_time / total_images:.2f}秒" if total_images > 0 else "0秒"
        },
        "详细结果": []
    }
    
    # 添加每张图片的详细信息
    for result in results:
        summary["详细结果"].append({
            "图片": result["source_file"],
            "引擎": result.get("engine", "unknown"),
            "文本长度": len(result.get("text", "")),
            "文本块数": len(result.get("boxes", [])),
            "置信度": result.get("confidence", 0.0),
            "处理时间": f"{result.get('processing_time', 0.0):.2f}秒"
        })
    
    # 保存JSON格式
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown格式
    md_file = output_file.with_suffix(".md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# OCR批量处理汇总报告\n\n")
        f.write(f"**生成时间**: {summary['生成时间']}\n\n")
        
        f.write("## 统计信息\n\n")
        stats = summary["统计信息"]
        f.write(f"- **总图片数**: {stats['总图片数']}\n")
        f.write(f"- **总文本长度**: {stats['总文本长度']} 字符\n")
        f.write(f"- **总文本块数**: {stats['总文本块数']}\n")
        f.write(f"- **总处理时间**: {stats['总处理时间']}\n")
        f.write(f"- **平均置信度**: {stats['平均置信度']}\n")
        f.write(f"- **平均处理时间**: {stats['平均处理时间']}\n\n")
        
        f.write("## 详细结果\n\n")
        f.write("| 图片 | 引擎 | 文本长度 | 文本块数 | 置信度 | 处理时间 |\n")
        f.write("|------|------|----------|----------|--------|----------|\n")
        
        for detail in summary["详细结果"]:
            f.write(f"| {detail['图片']} | {detail['引擎']} | "
                   f"{detail['文本长度']} | {detail['文本块数']} | "
                   f"{detail['置信度']:.3f} | {detail['处理时间']} |\n")
    
    print(f"✅ 汇总报告已生成:")
    print(f"  - JSON: {output_file}")
    print(f"  - Markdown: {md_file}")


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(
        description="生成批量OCR处理汇总报告"
    )
    
    parser.add_argument(
        "results_dir",
        type=str,
        nargs="?",
        default="ocr_results",
        help="OCR结果目录（默认：ocr_results）"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="输出文件路径（默认：results_dir/batch_summary）"
    )
    
    args = parser.parse_args()
    
    # 解析路径
    if Path(args.results_dir).is_absolute():
        results_dir = Path(args.results_dir)
    else:
        # 相对路径，尝试从当前目录和项目根目录查找
        current_dir = Path.cwd()
        project_root = Path(__file__).parent.parent
        
        for base_dir in [current_dir, project_root]:
            candidate = base_dir / args.results_dir
            if candidate.exists():
                results_dir = candidate
                break
        else:
            results_dir = Path(args.results_dir)
    
    if not results_dir.exists():
        print(f"❌ 错误: 目录不存在: {results_dir}")
        sys.exit(1)
    
    # 确定输出文件
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = results_dir / "batch_summary.json"
    
    # 加载结果
    print(f"📂 读取OCR结果: {results_dir}")
    results = load_ocr_results(results_dir)
    
    if not results:
        print("❌ 未找到OCR结果文件")
        sys.exit(1)
    
    print(f"✅ 找到 {len(results)} 个结果文件")
    
    # 生成汇总
    generate_summary(results, output_file)


if __name__ == "__main__":
    main()

