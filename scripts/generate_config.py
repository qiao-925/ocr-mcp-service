"""生成配置文件模板"""
import json
import os
import sys
from pathlib import Path

# 获取脚本所在目录的父目录（项目根目录）
script_dir = Path(__file__).parent.parent.resolve()
server_file = script_dir / 'mcp_ocr_server.py'

# 处理路径（Windows使用正斜杠）
if os.name == 'nt':
    server_path = str(server_file).replace('\\', '/')
    script_path = str(script_dir).replace('\\', '/')
else:
    server_path = str(server_file)
    script_path = str(script_dir)

config = {
    "mcpServers": {
        "ocr-service": {
            "command": "python",
            "args": [server_path],
            "env": {
                "PYTHONPATH": script_path
            }
        }
    }
}

config_file = script_dir / 'config_template.json'
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"Config template generated: {config_file}")

