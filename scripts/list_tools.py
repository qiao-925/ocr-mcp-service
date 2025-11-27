"""List all OCR MCP tools."""

import sys
from pathlib import Path

# Add project root to path before importing scripts.common
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup script environment
from scripts.common import setup_script
setup_script()


def main():
    """List all OCR MCP tools."""
    print("=" * 60)
    print("OCR MCP Service - Available Tools")
    print("=" * 60)
    
    # Import to register tools
    from ocr_mcp_service.mcp_server import mcp
    import ocr_mcp_service.tools
    
    print(f"\nMCP Server: {mcp.name}")
    print("\n" + "-" * 60)
    print("Registered OCR Tools:")
    print("-" * 60)
    
    from ocr_mcp_service.tools import (
        recognize_image_paddleocr,
        recognize_image_deepseek,
        recognize_image_paddleocr_mcp,
        recognize_image_easyocr,
    )
    
    tools = [
        {
            "name": "recognize_image_paddleocr",
            "tool": recognize_image_paddleocr,
            "engine": "PaddleOCR",
            "status": "Available (installed)"
        },
        {
            "name": "recognize_image_paddleocr_mcp",
            "tool": recognize_image_paddleocr_mcp,
            "engine": "paddleocr-mcp",
            "status": "Registered (requires: pip install paddleocr-mcp)"
        },
        {
            "name": "recognize_image_easyocr",
            "tool": recognize_image_easyocr,
            "engine": "EasyOCR",
            "status": "Registered (requires: pip install -e '.[easyocr]')"
        },
        {
            "name": "recognize_image_deepseek",
            "tool": recognize_image_deepseek,
            "engine": "DeepSeek OCR",
            "status": "Registered (requires: pip install -e '.[deepseek]')"
        },
    ]
    
    for i, tool_info in enumerate(tools, 1):
        tool = tool_info["tool"]
        print(f"\n{i}. {tool_info['name']}")
        print(f"   Engine: {tool_info['engine']}")
        print(f"   Status: {tool_info['status']}")
        print(f"   MCP Name: {tool.name}")
        
        # Get description
        desc = tool.description if hasattr(tool, 'description') else "No description"
        if len(desc) > 100:
            desc = desc[:100] + "..."
        print(f"   Description: {desc}")
        
        # Get parameters (simplified)
        if hasattr(tool, 'parameters'):
            params = tool.parameters
            if params:
                print(f"   Parameters: {len(params)} parameter(s)")
    
    print("\n" + "=" * 60)
    print("Total: 4 OCR tools")
    print("=" * 60)


if __name__ == "__main__":
    main()

