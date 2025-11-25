"""停止OCR MCP服务"""
import os
import sys
from pathlib import Path

def stop_by_pid(pid):
    """根据PID停止进程"""
    try:
        import psutil
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            print(f"[OK] Sent termination signal to process {pid}")
            # 等待进程结束
            proc.wait(timeout=5)
            print(f"[OK] Process {pid} stopped successfully")
            return True
        except psutil.NoSuchProcess:
            print(f"[INFO] Process {pid} does not exist (already stopped)")
            return True
        except psutil.AccessDenied:
            print(f"[ERROR] Permission denied. Cannot stop process {pid}")
            print("  Try running with administrator/sudo privileges")
            return False
        except psutil.TimeoutExpired:
            print(f"[WARN] Process {pid} did not stop gracefully, forcing kill...")
            try:
                proc.kill()
                print(f"[OK] Process {pid} force killed")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to kill process: {e}")
                return False
    except ImportError:
        # Fallback to OS command
        print(f"[INFO] psutil not available, using OS command...")
        if os.name == 'nt':  # Windows
            os.system(f'taskkill /F /PID {pid}')
            print(f"[OK] Sent kill signal to process {pid}")
        else:  # Linux/Mac
            os.system(f'kill -9 {pid}')
            print(f"[OK] Sent kill signal to process {pid}")
        return True

def stop_all_ocr_services():
    """停止所有OCR MCP服务进程"""
    script_name = "mcp_ocr_server.py"
    found_pids = []
    
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any(script_name in str(arg) for arg in cmdline):
                    found_pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not found_pids:
            print("[INFO] No OCR MCP service processes found")
            return True
        
        print(f"[INFO] Found {len(found_pids)} OCR MCP service process(es)")
        all_stopped = True
        for pid in found_pids:
            print(f"\nStopping process {pid}...")
            if not stop_by_pid(pid):
                all_stopped = False
        
        return all_stopped
        
    except ImportError:
        print("[ERROR] psutil not installed, cannot find processes automatically")
        print("  Install with: pip install psutil")
        print("  Or manually stop by PID using:")
        if os.name == 'nt':
            print("    taskkill /F /PID <pid>")
        else:
            print("    kill -9 <pid>")
        return False

def main():
    if len(sys.argv) > 1:
        # Stop specific PID
        try:
            pid = int(sys.argv[1])
            print(f"Stopping OCR MCP service (PID: {pid})...")
            stop_by_pid(pid)
        except ValueError:
            print(f"[ERROR] Invalid PID: {sys.argv[1]}")
            print("Usage: python stop_service.py [pid]")
            print("       python stop_service.py        (stop all)")
            sys.exit(1)
    else:
        # Stop all
        print("Stopping all OCR MCP service processes...")
        print("=" * 50)
        stop_all_ocr_services()

if __name__ == "__main__":
    main()

