"""MCP configuration generator."""

import json
import os
import platform
from pathlib import Path
from typing import Optional


def find_cursor_mcp_config() -> Optional[Path]:
    """Find Cursor MCP configuration file."""
    system = platform.system()
    home = Path.home()
    
    # Cursor MCP config is typically at ~/.cursor/mcp.json (or %USERPROFILE%\.cursor\mcp.json on Windows)
    possible_paths = []
    
    if system == "Windows":
        # Windows paths
        possible_paths = [
            home / ".cursor" / "mcp.json",  # Primary location
            Path(os.getenv("APPDATA", "")) / "Cursor" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
            Path(os.getenv("APPDATA", "")) / "Cursor" / "User" / "settings.json",
            Path(os.getenv("LOCALAPPDATA", "")) / "Cursor" / "User" / "settings.json",
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            home / ".cursor" / "mcp.json",  # Primary location
            home / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
            home / "Library" / "Application Support" / "Cursor" / "User" / "settings.json",
        ]
    elif system == "Linux":
        possible_paths = [
            home / ".cursor" / "mcp.json",  # Primary location
            home / ".config" / "Cursor" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
            home / ".config" / "Cursor" / "User" / "settings.json",
        ]
    
    # First check if primary location exists, if not return it anyway (we'll create it)
    primary_path = home / ".cursor" / "mcp.json"
    if primary_path.exists():
        return primary_path
    
    # Check other possible locations
    for path in possible_paths:
        if path.exists():
            return path
    
    # Return primary location even if it doesn't exist (we'll create it)
    return primary_path


def get_ocr_service_config() -> dict:
    """Get OCR service configuration.
    
    Automatically detects the best configuration method:
    1. If ocr-mcp-server command exists, use it
    2. If venv exists, use venv/bin/python
    3. Otherwise, use python3 -m ocr_mcp_service with proper paths
    """
    import shutil
    from pathlib import Path
    
    # Check if ocr-mcp-server command exists
    if shutil.which("ocr-mcp-server"):
        return {
            "command": "ocr-mcp-server",
            "args": []
        }
    
    # Get project root (assuming this file is in src/ocr_mcp_service/)
    project_root = Path(__file__).parent.parent.parent
    src_dir = project_root / "src"
    
    # Check if virtual environment exists
    venv_python = project_root / "venv" / "bin" / "python"
    if venv_python.exists():
        # Use virtual environment Python (use absolute path without resolving symlinks)
        # This ensures we use the venv Python, not the system Python it points to
        venv_python_abs = project_root.resolve() / "venv" / "bin" / "python"
        return {
            "command": str(venv_python_abs),
            "args": [
                "-m",
                "ocr_mcp_service"
            ],
            "cwd": str(project_root.resolve()),
            "env": {
                "PYTHONPATH": str(src_dir.resolve())
            }
        }
    
    # Fallback: use system Python module with proper paths
    return {
        "command": "python3",
        "args": [
            "-m",
            "ocr_mcp_service"
        ],
        "cwd": str(project_root.resolve()),
        "env": {
            "PYTHONPATH": str(src_dir.resolve())
        }
    }


def add_to_cursor_config(service_name: str = "ocr-service", force: bool = False) -> bool:
    """Add OCR service to Cursor MCP configuration."""
    config_path = find_cursor_mcp_config()
    
    if not config_path:
        print("Cursor MCP configuration file not found.")
        print("Please manually add the following to your Cursor MCP settings:")
        print(json.dumps({
            "mcpServers": {
                service_name: get_ocr_service_config()
            }
        }, indent=2))
        return False
    
    print(f"Found Cursor config at: {config_path}")
    
    # Read existing config
    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        config = {}
    
    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Check if service already exists
    if service_name in config["mcpServers"]:
        if not force:
            print(f"Service '{service_name}' already exists in config.")
            print("Use force=True to overwrite.")
            return False
        print(f"Overwriting existing service '{service_name}'...")
    
    # Add OCR service
    config["mcpServers"][service_name] = get_ocr_service_config()
    
    # Backup original config
    backup_path = config_path.with_suffix(".json.bak")
    try:
        if config_path.exists():
            import shutil
            shutil.copy2(config_path, backup_path)
            print(f"Backup created: {backup_path}")
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")
    
    # Write updated config
    try:
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully added '{service_name}' to Cursor MCP configuration!")
        print(f"Config file: {config_path}")
        print("\nPlease restart Cursor for changes to take effect.")
        return True
    except Exception as e:
        print(f"Error writing config: {e}")
        return False


def generate_mcp_config(output_path: str = "mcp_config.json") -> None:
    """Generate MCP configuration file."""
    config = {
        "mcpServers": {
            "ocr-service": get_ocr_service_config()
        }
    }
    
    output = Path(output_path)
    with output.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"MCP configuration saved to: {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "cursor":
        force = "--force" in sys.argv
        add_to_cursor_config(force=force)
    else:
        generate_mcp_config()

