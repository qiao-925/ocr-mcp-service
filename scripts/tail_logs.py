#!/usr/bin/env python3
"""跨平台实时日志查看工具

这是一个完全跨平台的日志查看工具，在Windows、Linux、macOS上都可以使用。

使用方法:
    # 安装项目后
    ocr-tail-logs
    
    # 或直接运行
    python scripts/tail_logs.py
    
    # 或使用模块方式
    python -m scripts.tail_logs
"""

import sys
import time
import argparse
import re
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.ocr_mcp_service.config import LOG_FILE
except ImportError:
    # Fallback if not installed
    LOG_FILE = "logs/ocr_service.log"


# ANSI颜色代码（跨平台支持）
class Colors:
    """ANSI颜色代码"""
    DEBUG = "\033[36m"      # 青色
    INFO = "\033[32m"       # 绿色
    WARNING = "\033[33m"    # 黄色
    ERROR = "\033[31m"      # 红色
    CRITICAL = "\033[35m"   # 紫色
    RESET = "\033[0m"       # 重置
    
    @staticmethod
    def disable():
        """禁用颜色（Windows CMD可能不支持）"""
        Colors.DEBUG = ""
        Colors.INFO = ""
        Colors.WARNING = ""
        Colors.ERROR = ""
        Colors.CRITICAL = ""
        Colors.RESET = ""


def parse_log_line(line: str) -> Optional[dict]:
    """解析日志行"""
    pattern = re.compile(
        r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+) \[([^\]]+)\] (.+)'
    )
    match = pattern.match(line.strip())
    if match:
        timestamp, level, logger, message = match.groups()
        return {
            "timestamp": timestamp,
            "level": level,
            "logger": logger,
            "message": message,
            "raw": line.strip()
        }
    return None


def colorize_level(level: str, use_color: bool = True) -> str:
    """为日志级别添加颜色"""
    if not use_color:
        return level
    
    color_map = {
        "DEBUG": Colors.DEBUG,
        "INFO": Colors.INFO,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.ERROR,
        "CRITICAL": Colors.CRITICAL,
    }
    
    color = color_map.get(level.upper(), "")
    return f"{color}{level}{Colors.RESET}"


def should_show(entry: dict, level: Optional[str] = None,
                engine: Optional[str] = None, search: Optional[str] = None) -> bool:
    """判断是否应该显示该日志条目"""
    if level and entry["level"].upper() != level.upper():
        return False
    
    if engine and engine.lower() not in entry["logger"].lower():
        return False
    
    if search and search.lower() not in entry["message"].lower():
        return False
    
    return True


def tail_logs(log_file: Path, lines: int = 0, follow: bool = True,
              level: Optional[str] = None, engine: Optional[str] = None,
              search: Optional[str] = None, use_color: bool = True):
    """实时查看日志"""
    if not log_file.exists():
        print(f"错误: 日志文件不存在: {log_file}")
        print(f"请确保日志文件路径正确: {log_file.absolute()}")
        sys.exit(1)
    
    # 如果指定了行数，先显示最近的N行
    if lines > 0:
        print(f"显示最近 {lines} 行日志:\n" + "=" * 80)
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                for line in recent_lines:
                    entry = parse_log_line(line)
                    if entry and should_show(entry, level, engine, search):
                        colored_level = colorize_level(entry["level"], use_color)
                        print(f"[{entry['timestamp']}] {colored_level} [{entry['logger']}] {entry['message']}")
        except Exception as e:
            print(f"读取日志文件时出错: {e}")
            sys.exit(1)
        
        if follow:
            print("\n" + "=" * 80)
            print("实时监控模式 (按 Ctrl+C 退出):\n")
    
    # 实时监控模式
    if follow:
        try:
            # 打开文件并定位到末尾
            with open(log_file, "r", encoding="utf-8") as f:
                # 移动到文件末尾
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        entry = parse_log_line(line)
                        if entry and should_show(entry, level, engine, search):
                            colored_level = colorize_level(entry["level"], use_color)
                            print(f"[{entry['timestamp']}] {colored_level} [{entry['logger']}] {entry['message']}")
                    else:
                        time.sleep(0.1)  # 短暂休眠避免CPU占用过高
        except KeyboardInterrupt:
            print("\n\n已停止监控日志")
        except Exception as e:
            print(f"\n监控日志时出错: {e}")
            sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="跨平台实时查看OCR服务日志",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          # 实时查看所有日志
  %(prog)s --level ERROR            # 只查看错误日志
  %(prog)s --engine PaddleOCR       # 只查看PaddleOCR引擎日志
  %(prog)s --search "初始化"         # 搜索包含"初始化"的日志
  %(prog)s --lines 50               # 先显示最近50行，然后实时监控
  %(prog)s --no-follow --lines 100  # 只显示最近100行，不实时监控
  %(prog)s --no-color               # 禁用颜色输出
        """
    )
    
    parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="过滤日志级别（不区分大小写）"
    )
    
    parser.add_argument(
        "--engine",
        help="过滤引擎名称（不区分大小写，如: PaddleOCR, EasyOCR, DeepSeek）"
    )
    
    parser.add_argument(
        "--search",
        help="搜索关键词（不区分大小写）"
    )
    
    parser.add_argument(
        "--lines",
        type=int,
        default=0,
        help="先显示最近N行日志（默认: 0，不显示历史日志）"
    )
    
    parser.add_argument(
        "--no-follow",
        action="store_true",
        help="不实时监控，只显示历史日志"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="禁用颜色输出"
    )
    
    parser.add_argument(
        "--log-file",
        help=f"指定日志文件路径（默认: {LOG_FILE}）"
    )
    
    args = parser.parse_args()
    
    # 禁用颜色（如果指定或Windows CMD）
    use_color = not args.no_color
    if sys.platform == "win32" and not sys.stdout.isatty():
        use_color = False
    
    log_file = Path(args.log_file) if args.log_file else Path(LOG_FILE)
    
    tail_logs(
        log_file=log_file,
        lines=args.lines,
        follow=not args.no_follow,
        level=args.level,
        engine=args.engine,
        search=args.search,
        use_color=use_color
    )


if __name__ == "__main__":
    main()

