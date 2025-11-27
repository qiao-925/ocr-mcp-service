"""公共工具模块 - 为所有脚本提供统一的初始化功能

这个模块提供了所有脚本需要的公共功能：
- 路径设置
- Windows 编码修复
- 统一的初始化函数
"""

import sys
from pathlib import Path


def setup_path():
    """添加 src 目录到 Python 路径"""
    scripts_dir = Path(__file__).parent
    src_dir = scripts_dir.parent / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))


def setup_windows_encoding():
    """修复 Windows 控制台编码问题"""
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, 
            encoding='utf-8', 
            errors='replace'
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, 
            encoding='utf-8', 
            errors='replace'
        )


def setup_script():
    """统一的脚本初始化函数
    
    调用此函数会：
    1. 添加 src 目录到 Python 路径
    2. 修复 Windows 控制台编码
    """
    setup_path()
    setup_windows_encoding()


