"""查看日志文件"""
import sys
from pathlib import Path

def view_logs(lines=50):
    """查看最近的日志条目"""
    log_file = Path(__file__).parent.parent / "logs" / "mcp_ocr_server.log"
    
    if not log_file.exists():
        print(f"Log file not found: {log_file}")
        print("The service may not have started yet.")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            total_lines = len(all_lines)
            
            print(f"Log file: {log_file}")
            print(f"Total lines: {total_lines}")
            print("=" * 70)
            print(f"Last {min(lines, total_lines)} lines:")
            print("=" * 70)
            
            for line in all_lines[-lines:]:
                print(line.rstrip())
    except Exception as e:
        print(f"Error reading log file: {e}")

def tail_logs():
    """实时跟踪日志（简化版，Windows可能不支持tail命令）"""
    log_file = Path(__file__).parent.parent / "logs" / "mcp_ocr_server.log"
    
    if not log_file.exists():
        print(f"Log file not found: {log_file}")
        return
    
    print(f"Tailing log file: {log_file}")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    try:
        import time
        last_size = log_file.stat().st_size
        
        with open(log_file, 'r', encoding='utf-8') as f:
            # 跳到最后
            f.seek(max(0, last_size - 1024))
            f.readline()  # 跳过可能的不完整行
            
            while True:
                line = f.readline()
                if line:
                    print(line.rstrip())
                    sys.stdout.flush()
                else:
                    time.sleep(0.5)
                    # 检查文件是否有新内容
                    current_size = log_file.stat().st_size
                    if current_size > last_size:
                        last_size = current_size
    except KeyboardInterrupt:
        print("\nStopped tailing logs.")
    except Exception as e:
        print(f"Error tailing log file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "tail":
        tail_logs()
    else:
        lines = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 50
        view_logs(lines)

