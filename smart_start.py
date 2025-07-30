#!/usr/bin/env python3
"""
智能启动脚本 - 自动检测端口并启动系统
"""

import os
import sys
import json
import time
import signal
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

class SmartLauncher:
    """智能启动器"""
    
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.backend_port = 8080
        self.frontend_port = 3000
        self.load_port_config()
    
    def load_port_config(self):
        """加载端口配置"""
        try:
            if Path('ports.json').exists():
                with open('ports.json', 'r') as f:
                    config = json.load(f)
                    self.backend_port = config.get('backend_port', 8080)
                    self.frontend_port = config.get('frontend_port', 3000)
                    print(f"📋 加载端口配置: 后端={self.backend_port}, 前端={self.frontend_port}")
        except Exception as e:
            print(f"⚠️ 无法加载端口配置: {e}")
    
    def check_dependencies(self):
        """检查依赖"""
        print("📦 检查系统依赖...")
        
        # 检查Python依赖
        required_packages = ['fastapi', 'uvicorn']
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} 未安装，正在安装...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package])
        
        # 检查前端依赖
        if not Path('frontend/node_modules').exists():
            print("📦 安装前端依赖...")
            os.chdir('frontend')
            subprocess.run(['npm', 'install'])
            os.chdir('..')
    
    def update_api_config(self):
        """更新API配置"""
        api_server_path = Path('api_server.py')
        if api_server_path.exists():
            content = api_server_path.read_text()
            # 更新端口配置
            updated_content = content.replace(
                'port=8000',
                f'port={self.backend_port}'
            )
            # 更新CORS配置
            updated_content = updated_content.replace(
                'allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]',
                f'allow_origins=["http://localhost:{self.frontend_port}", "http://127.0.0.1:{self.frontend_port}"]'
            )
            api_server_path.write_text(updated_content)
            print(f"✅ 已更新API服务器配置，端口: {self.backend_port}")
    
    def update_frontend_config(self):
        """更新前端配置"""
        vite_config_path = Path('frontend/vite.config.ts')
        if vite_config_path.exists():
            content = vite_config_path.read_text()
            # 更新代理配置
            updated_content = content.replace(
                "target: 'http://localhost:8000'",
                f"target: 'http://localhost:{self.backend_port}'"
            ).replace(
                "port: 3000",
                f"port: {self.frontend_port}"
            )
            vite_config_path.write_text(updated_content)
            print(f"✅ 已更新前端配置，端口: {self.frontend_port}")
    
    def start_backend(self):
        """启动后端服务"""
        print(f"🔧 启动后端API服务 (端口: {self.backend_port})...")
        
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, 'api_server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务启动
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print(f"✅ 后端服务启动成功")
                return True
            else:
                print("❌ 后端服务启动失败")
                stdout, stderr = self.backend_process.communicate()
                print(f"错误信息: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ 启动后端服务失败: {e}")
            return False
    
    def start_frontend(self):
        """启动前端服务"""
        print(f"🎨 启动前端开发服务 (端口: {self.frontend_port})...")
        
        try:
            os.chdir('frontend')
            self.frontend_process = subprocess.Popen([
                'npm', 'run', 'dev'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.chdir('..')
            
            # 等待服务启动
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                print(f"✅ 前端服务启动成功")
                return True
            else:
                print("❌ 前端服务启动失败")
                stdout, stderr = self.frontend_process.communicate()
                print(f"错误信息: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ 启动前端服务失败: {e}")
            return False
    
    def cleanup(self):
        """清理进程"""
        print("\n🛑 正在停止服务...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process.wait()
            print("✅ 后端服务已停止")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("✅ 前端服务已停止")
    
    def launch(self):
        """启动系统"""
        print("🚀 AI Agent开发团队系统 - 智能启动")
        print("=" * 50)
        
        try:
            # 检查依赖
            self.check_dependencies()
            
            # 更新配置
            self.update_api_config()
            self.update_frontend_config()
            
            # 启动后端
            if not self.start_backend():
                return False
            
            # 启动前端
            if not self.start_frontend():
                self.cleanup()
                return False
            
            print("\n" + "=" * 50)
            print("✅ 系统启动完成！")
            print("=" * 50)
            print(f"🌐 前端界面: http://localhost:{self.frontend_port}")
            print(f"📡 API服务: http://localhost:{self.backend_port}")
            print(f"📚 API文档: http://localhost:{self.backend_port}/docs")
            print("")
            print("🎯 主要功能:")
            print(f"  • 🚀 项目启动台: http://localhost:{self.frontend_port}/launchpad")
            print(f"  • 🏠 仪表板: http://localhost:{self.frontend_port}/")
            print(f"  • 🤖 Agent监控: http://localhost:{self.frontend_port}/agents")
            print(f"  • 📊 系统评估: http://localhost:{self.frontend_port}/evaluation")
            print("")
            print("按 Ctrl+C 停止所有服务")
            print("=" * 50)
            
            # 设置信号处理
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # 等待用户中断
            try:
                while True:
                    time.sleep(1)
                    # 检查进程是否还在运行
                    if self.backend_process and self.backend_process.poll() is not None:
                        print("❌ 后端服务意外停止")
                        break
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        print("❌ 前端服务意外停止")
                        break
            except KeyboardInterrupt:
                pass
                
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
        finally:
            self.cleanup()
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n收到信号 {signum}，正在停止服务...")
        self.cleanup()
        sys.exit(0)

def main():
    """主函数"""
    launcher = SmartLauncher()
    launcher.launch()

if __name__ == "__main__":
    main()