"""Setup script to add OCR MCP service to Cursor configuration."""

import sys
from pathlib import Path

# Add project root to path before importing scripts.common
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup script environment
from scripts.common import setup_script
setup_script()

from ocr_mcp_service.config_manager import add_to_cursor_config


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Add OCR MCP service to Cursor configuration"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing configuration"
    )
    parser.add_argument(
        "--name",
        default="ocr-service",
        help="Service name (default: ocr-service)"
    )
    
    args = parser.parse_args()
    
    success = add_to_cursor_config(service_name=args.name, force=args.force)
    
    if success:
        print("\nSetup complete!")
        return 0
    else:
        print("\nSetup incomplete. Please check the messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())






