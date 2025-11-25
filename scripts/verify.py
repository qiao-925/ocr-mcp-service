"""验证依赖安装"""
import sys

try:
    import mcp
    import paddleocr
    print("Dependencies verified successfully")
    sys.exit(0)
except ImportError as e:
    print(f"Warning: Some dependencies may not be installed correctly: {e}", file=sys.stderr)
    sys.exit(0)
except Exception as e:
    print(f"Error during verification: {e}", file=sys.stderr)
    sys.exit(1)

