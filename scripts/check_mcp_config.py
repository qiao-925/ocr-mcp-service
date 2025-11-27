"""Check MCP configuration."""

import json
import sys
from pathlib import Path


def check_config(config_path: str = "mcp_config.json"):
    """Check MCP configuration file."""
    path = Path(config_path)
    
    if not path.exists():
        print(f"Configuration file not found: {config_path}")
        print("Creating default configuration...")
        generate_default_config(config_path)
        return
    
    try:
        with path.open("r", encoding="utf-8") as f:
            config = json.load(f)
        
        print(f"Configuration file: {config_path}")
        print("Valid JSON: OK")
        
        if "mcpServers" in config:
            print(f"MCP Servers: {len(config['mcpServers'])}")
            for name, server_config in config["mcpServers"].items():
                print(f"  - {name}:")
                print(f"    command: {server_config.get('command', 'N/A')}")
                print(f"    args: {server_config.get('args', [])}")
        else:
            print("Warning: 'mcpServers' key not found")
    
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading configuration: {e}")
        sys.exit(1)


def generate_default_config(output_path: str):
    """Generate default MCP configuration."""
    config = {
        "mcpServers": {
            "ocr-service": {
                "command": "ocr-mcp-server",
                "args": []
            }
        }
    }
    
    output = Path(output_path)
    with output.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Default configuration created: {output_path}")


def main():
    """Main entry point for script execution."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else "mcp_config.json"
    check_config(config_path)


if __name__ == "__main__":
    main()

