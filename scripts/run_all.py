#!/usr/bin/env python
"""统一脚本运行器 - 一键运行所有scripts脚本

用法:
    python scripts/run_all.py                    # 列出所有脚本
    python scripts/run_all.py --all              # 运行所有脚本（跳过需要参数的）
    python scripts/run_all.py --category config  # 运行配置类脚本
    python scripts/run_all.py --script list_tools  # 运行指定脚本
    python scripts/run_all.py --interactive      # 交互式选择
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path before importing scripts.common
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup script environment
from scripts.common import setup_script
setup_script()


# 脚本定义
SCRIPTS = {
    "config": {
        "setup_cursor": {
            "file": "setup_cursor.py",
            "description": "自动添加OCR MCP服务到Cursor配置",
            "requires_args": False,
            "default_args": [],
        },
        "check_mcp_config": {
            "file": "check_mcp_config.py",
            "description": "检查MCP配置文件格式和内容",
            "requires_args": False,
            "default_args": [],
        },
    },
    "verification": {
        "verify_engines": {
            "file": "verify_engines.py",
            "description": "OCR引擎综合验证脚本",
            "requires_args": False,
            "default_args": [],
        },
        "compare_engines": {
            "file": "compare_engines.py",
            "description": "多引擎对比验证脚本",
            "requires_args": False,
            "default_args": [],
        },
        "verify_logging": {
            "file": "verify_logging.py",
            "description": "日志系统验证脚本",
            "requires_args": False,
            "default_args": [],
        },
    },
    "tools": {
        "list_tools": {
            "file": "list_tools.py",
            "description": "列出所有OCR MCP工具",
            "requires_args": False,
            "default_args": [],
        },
        "recognize_image": {
            "file": "recognize_image.py",
            "description": "命令行OCR识别工具（需要图片路径）",
            "requires_args": True,
            "arg_help": "图片路径",
            "default_args": None,  # 必须提供
        },
    },
}


def get_script_path(script_file: str) -> Path:
    """获取脚本路径"""
    return Path(__file__).parent / script_file


def run_script(script_name: str, script_info: Dict, extra_args: List[str] = None) -> bool:
    """运行单个脚本"""
    script_path = get_script_path(script_info["file"])
    
    if not script_path.exists():
        print(f"✗ 脚本不存在: {script_path}")
        return False
    
    print(f"\n{'=' * 80}")
    print(f"运行脚本: {script_name}")
    print(f"文件: {script_info['file']}")
    print(f"描述: {script_info['description']}")
    print(f"{'=' * 80}\n")
    
    # 构建命令
    cmd = [sys.executable, str(script_path)]
    
    # 添加默认参数
    if script_info.get("default_args"):
        cmd.extend(script_info["default_args"])
    
    # 添加额外参数
    if extra_args:
        cmd.extend(extra_args)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            check=False,
            capture_output=False
        )
        
        if result.returncode == 0:
            print(f"\n✓ {script_name} 执行成功")
            return True
        else:
            print(f"\n✗ {script_name} 执行失败 (退出码: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"\n✗ 运行 {script_name} 时出错: {e}")
        return False


def list_all_scripts():
    """列出所有脚本"""
    print("=" * 80)
    print("可用脚本列表")
    print("=" * 80)
    
    for category, scripts in SCRIPTS.items():
        print(f"\n【{category.upper()}】")
        for name, info in scripts.items():
            requires = "需要参数" if info.get("requires_args") else "无需参数"
            print(f"  {name:20} - {info['description']} ({requires})")


def run_category(category: str, skip_requires_args: bool = True):
    """运行指定类别的所有脚本"""
    if category not in SCRIPTS:
        print(f"✗ 未知类别: {category}")
        print(f"可用类别: {', '.join(SCRIPTS.keys())}")
        return False
    
    scripts = SCRIPTS[category]
    results = {}
    
    print(f"\n运行类别: {category}")
    print(f"脚本数量: {len(scripts)}")
    
    for name, info in scripts.items():
        if skip_requires_args and info.get("requires_args"):
            print(f"\n⏭  跳过 {name} (需要参数)")
            results[name] = "skipped"
            continue
        
        success = run_script(name, info)
        results[name] = "success" if success else "failed"
    
    # 显示结果摘要
    print(f"\n{'=' * 80}")
    print(f"类别 {category} 执行结果")
    print(f"{'=' * 80}")
    for name, status in results.items():
        status_icon = "✓" if status == "success" else "✗" if status == "failed" else "⏭"
        print(f"  {status_icon} {name}: {status}")
    
    return all(status == "success" for status in results.values() if status != "skipped")


def run_all(skip_requires_args: bool = True):
    """运行所有脚本"""
    print("=" * 80)
    print("运行所有脚本")
    print("=" * 80)
    
    all_results = {}
    
    for category, scripts in SCRIPTS.items():
        print(f"\n\n处理类别: {category}")
        for name, info in scripts.items():
            if skip_requires_args and info.get("requires_args"):
                print(f"\n⏭  跳过 {name} (需要参数)")
                all_results[name] = "skipped"
                continue
            
            success = run_script(name, info)
            all_results[name] = "success" if success else "failed"
    
    # 显示总结果
    print(f"\n\n{'=' * 80}")
    print("所有脚本执行结果")
    print(f"{'=' * 80}")
    
    success_count = sum(1 for s in all_results.values() if s == "success")
    failed_count = sum(1 for s in all_results.values() if s == "failed")
    skipped_count = sum(1 for s in all_results.values() if s == "skipped")
    
    for name, status in sorted(all_results.items()):
        status_icon = "✓" if status == "success" else "✗" if status == "failed" else "⏭"
        print(f"  {status_icon} {name}: {status}")
    
    print(f"\n总计: ✓ {success_count} 成功, ✗ {failed_count} 失败, ⏭ {skipped_count} 跳过")
    
    return failed_count == 0


def run_single(script_name: str, extra_args: List[str] = None):
    """运行单个脚本"""
    # 在所有类别中查找脚本
    script_info = None
    for category, scripts in SCRIPTS.items():
        if script_name in scripts:
            script_info = scripts[script_name]
            break
    
    if not script_info:
        print(f"✗ 未找到脚本: {script_name}")
        print("\n可用脚本:")
        for category, scripts in SCRIPTS.items():
            for name in scripts.keys():
                print(f"  - {name}")
        return False
    
    return run_script(script_name, script_info, extra_args)


def interactive_mode():
    """交互式选择模式"""
    print("=" * 80)
    print("交互式脚本选择")
    print("=" * 80)
    
    # 列出所有脚本
    all_scripts = []
    for category, scripts in SCRIPTS.items():
        for name, info in scripts.items():
            all_scripts.append((name, info, category))
    
    print("\n可用脚本:")
    for i, (name, info, category) in enumerate(all_scripts, 1):
        requires = " [需要参数]" if info.get("requires_args") else ""
        print(f"  {i}. {name:20} ({category}){requires}")
        print(f"     {info['description']}")
    
    print(f"\n  {len(all_scripts) + 1}. 运行所有脚本（跳过需要参数的）")
    print(f"  {len(all_scripts) + 2}. 退出")
    
    try:
        choice = input("\n请选择 (输入数字): ").strip()
        
        if choice == str(len(all_scripts) + 1):
            return run_all(skip_requires_args=True)
        elif choice == str(len(all_scripts) + 2):
            print("退出")
            return True
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(all_scripts):
                name, info, _ = all_scripts[idx]
                
                if info.get("requires_args"):
                    arg_help = info.get("arg_help", "参数")
                    extra_args = input(f"请输入 {arg_help}: ").strip().split()
                    return run_single(name, extra_args)
                else:
                    return run_single(name)
            else:
                print("✗ 无效选择")
                return False
                
    except (ValueError, KeyboardInterrupt, EOFError):
        print("\n退出")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="统一脚本运行器 - 一键运行所有scripts脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 列出所有脚本
  %(prog)s --all              # 运行所有脚本（跳过需要参数的）
  %(prog)s --category config  # 运行配置类脚本
  %(prog)s --script list_tools # 运行指定脚本
  %(prog)s --interactive      # 交互式选择
        """
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="运行所有脚本（跳过需要参数的）"
    )
    
    parser.add_argument(
        "--category",
        choices=list(SCRIPTS.keys()),
        help="运行指定类别的所有脚本"
    )
    
    parser.add_argument(
        "--script",
        help="运行指定脚本"
    )
    
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="交互式选择模式"
    )
    
    parser.add_argument(
        "--args",
        nargs="+",
        help="传递给脚本的额外参数（与--script一起使用）"
    )
    
    args = parser.parse_args()
    
    # 如果没有参数，列出所有脚本
    if not any([args.all, args.category, args.script, args.interactive]):
        list_all_scripts()
        print("\n提示: 使用 --help 查看使用说明")
        return 0
    
    # 执行相应操作
    if args.interactive:
        success = interactive_mode()
        return 0 if success else 1
    elif args.all:
        success = run_all(skip_requires_args=True)
        return 0 if success else 1
    elif args.category:
        success = run_category(args.category, skip_requires_args=True)
        return 0 if success else 1
    elif args.script:
        success = run_single(args.script, args.args)
        return 0 if success else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

