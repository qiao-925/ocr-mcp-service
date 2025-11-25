"""检查MCP OCR服务运行状态"""
import os
import sys
from pathlib import Path

def check_process():
    """检查是否有Python进程在运行MCP服务器"""
    try:
        import psutil
    except ImportError:
        return None
    
    script_path = Path(__file__).parent.parent / "mcp_ocr_server.py"
    script_name = "mcp_ocr_server.py"
    
    found_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any(script_name in str(arg) for arg in cmdline):
                found_processes.append({
                    'pid': proc.info['pid'],
                    'cmdline': ' '.join(cmdline[:3]) + '...' if len(cmdline) > 3 else ' '.join(cmdline)
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return found_processes

def check_log_file():
    """检查日志文件是否存在及其大小"""
    log_file = Path(__file__).parent.parent / "logs" / "mcp_ocr_server.log"
    if log_file.exists():
        size = log_file.stat().st_size
        # 获取最后修改时间
        import datetime
        mtime = datetime.datetime.fromtimestamp(log_file.stat().st_mtime)
        return {
            'exists': True,
            'path': str(log_file),
            'size': size,
            'size_kb': round(size / 1024, 2),
            'last_modified': mtime.strftime('%Y-%m-%d %H:%M:%S')
        }
    return {'exists': False}

def main():
    print("=" * 50)
    print("OCR MCP Service Status Check")
    print("=" * 50)
    print()
    
    # 检查进程
    processes = check_process()
    if processes is None:
        print("[INFO] psutil not installed, cannot check processes")
        print("  Install with: pip install psutil")
        print("  Alternative: Check manually with Task Manager (Windows) or ps command (Linux/Mac)")
    elif processes:
        print(f"[RUNNING] Found {len(processes)} process(es):")
        for proc in processes:
            print(f"  PID: {proc['pid']}")
            print(f"  Command: {proc['cmdline']}")
    else:
        print("[STOPPED] No running process found")
    
    print()
    
    # 检查日志文件
    log_info = check_log_file()
    if log_info['exists']:
        print(f"[LOG] Log file exists:")
        print(f"  Path: {log_info['path']}")
        print(f"  Size: {log_info['size_kb']} KB")
        if 'last_modified' in log_info:
            print(f"  Last modified: {log_info['last_modified']}")
        print(f"  View logs: make logs")
    else:
        print("[LOG] Log file not found (service may not have started yet)")
        print("  Note: Log file will be created when service starts")
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    main()

