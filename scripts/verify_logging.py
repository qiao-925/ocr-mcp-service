#!/usr/bin/env python
"""日志系统验证脚本 - 用于手动验证日志功能

注意：这是验证脚本，不是pytest单元测试。
pytest单元测试位于 tests/ 目录下。
"""

import sys
from pathlib import Path

# Add project root to path before importing scripts.common
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup script environment
from scripts.common import setup_script
setup_script()

print("=" * 60)
print("测试日志系统")
print("=" * 60)

try:
    from ocr_mcp_service.logger import initialize_logger, get_logger
    
    print("\n1. 初始化日志系统...")
    initialize_logger()
    print("   ✓ 日志系统初始化成功")
    
    print("\n2. 获取logger并写入测试消息...")
    logger = get_logger("test")
    logger.info("这是一条INFO级别的测试日志")
    logger.warning("这是一条WARNING级别的测试日志")
    logger.error("这是一条ERROR级别的测试日志")
    print("   ✓ 日志消息已写入")
    
    print("\n3. 检查日志文件...")
    log_file = Path("logs/ocr_service.log")
    if log_file.exists():
        print(f"   ✓ 日志文件已创建: {log_file.absolute()}")
        print(f"   ✓ 文件大小: {log_file.stat().st_size} 字节")
        
        print("\n4. 读取日志文件内容...")
        print("-" * 60)
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            print(content)
        print("-" * 60)
    else:
        print(f"   ✗ 日志文件未找到: {log_file.absolute()}")
        print(f"   ✗ 目录存在: {log_file.parent.exists()}")
        if log_file.parent.exists():
            print(f"   ✗ 目录内容: {list(log_file.parent.iterdir())}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def main():
    """Main entry point for script execution."""
    # Script logic is already executed at module level
    pass


if __name__ == "__main__":
    main()

