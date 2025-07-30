#!/usr/bin/env python3
"""
端口检查工具 - 检查可用端口并自动分配
"""

import socket
import subprocess
import sys
from typing import List, Tuple

def check_port(port: int, host: str = 'localhost') -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # 如果连接失败，说明端口可用
    except:
        return False

def find_available_port(start_port: int, end_port: int = None) -> int:
    """查找可用端口"""
    if end_port is None:
        end_port = start_port + 100
    
    for port in range(start_port, end_port):
        if check_port(port):
            return port
    
    raise RuntimeError(f"No available ports found in range {start_port}-{end_port}")

def kill_process_on_port(port: int):
    """杀死占用指定端口的进程"""
    try:
        # 查找占用端口的进程
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                print(f"🔧 正在停止占用端口 {port} 的进程 (PID: {pid})")
                subprocess.run(['kill', '-9', pid])
                print(f"✅ 已停止进程 {pid}")
        return True
    except Exception as e:
        print(f"⚠️ 无法停止端口 {port} 上的进程: {e}")
        return False

def get_optimal_ports() -> Tuple[int, int]:
    """获取最佳的后端和前端端口"""
    
    print("🔍 检查端口可用性...")
    
    # 尝试常用端口
    preferred_backend_ports = [8000, 8001, 8080, 9000, 5000]
    preferred_frontend_ports = [3000, 3001, 8080, 9000, 5173]
    
    backend_port = None
    frontend_port = None
    
    # 检查后端端口
    for port in preferred_backend_ports:
        if check_port(port):
            backend_port = port
            print(f"✅ 后端端口: {port} (可用)")
            break
        else:
            print(f"❌ 端口 {port} 被占用")
    
    if backend_port is None:
        backend_port = find_available_port(8000)
        print(f"🔍 找到可用后端端口: {backend_port}")
    
    # 检查前端端口
    for port in preferred_frontend_ports:
        if port != backend_port and check_port(port):
            frontend_port = port
            print(f"✅ 前端端口: {port} (可用)")
            break
        else:
            print(f"❌ 端口 {port} 被占用或与后端冲突")
    
    if frontend_port is None:
        frontend_port = find_available_port(3000)
        while frontend_port == backend_port:
            frontend_port = find_available_port(frontend_port + 1)
        print(f"🔍 找到可用前端端口: {frontend_port}")
    
    return backend_port, frontend_port

def main():
    """主函数"""
    print("🚀 AI Agent开发团队 - 端口检查工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--kill":
            if len(sys.argv) > 2:
                port = int(sys.argv[2])
                kill_process_on_port(port)
            else:
                # 杀死常用端口上的进程
                for port in [3000, 8000, 8001, 8080]:
                    if not check_port(port):
                        kill_process_on_port(port)
            return
    
    try:
        backend_port, frontend_port = get_optimal_ports()
        
        print("\n🎯 推荐配置:")
        print(f"   后端API: http://localhost:{backend_port}")
        print(f"   前端界面: http://localhost:{frontend_port}")
        print(f"   API文档: http://localhost:{backend_port}/docs")
        
        # 保存端口配置到文件
        config = {
            "backend_port": backend_port,
            "frontend_port": frontend_port
        }
        
        import json
        with open('ports.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n💾 端口配置已保存到 ports.json")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()