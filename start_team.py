#!/usr/bin/env python3.11
"""
AI开发团队启动脚本 - Python3.11兼容版
"""

import asyncio
import subprocess
import sys
import json
import time
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    required_modules = ['psycopg2', 'redis', 'fastapi', 'uvicorn']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing.append(module)
            print(f"❌ {module}")
    
    if missing:
        print(f"\n⚠️ 缺少依赖: {', '.join(missing)}")
        print("请运行: pip install --break-system-packages " + " ".join(missing))
        return False
    
    return True

def check_services():
    """检查服务状态"""
    print("\n🔍 检查服务状态...")
    
    # 检查Docker容器
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=agent_team'], 
                              capture_output=True, text=True)
        if 'agent_team_postgres' in result.stdout and 'agent_team_redis' in result.stdout:
            print("✅ 数据库服务运行中")
            return True
        else:
            print("❌ 数据库服务未运行")
            return False
    except:
        print("❌ Docker服务检查失败")
        return False

def start_backend():
    """启动后端服务"""
    print("\n🚀 启动后端API服务...")
    
    # 读取端口配置
    backend_port = 8080
    if Path('ports.json').exists():
        try:
            with open('ports.json', 'r') as f:
                config = json.load(f)
                backend_port = config.get('backend_port', 8080)
        except:
            pass
    
    print(f"📡 API服务将在端口 {backend_port} 启动")
    print(f"📚 访问 http://localhost:{backend_port}/docs 查看API文档")
    
    # 启动API服务器
    subprocess.Popen([
        sys.executable, 'api_server.py'
    ], cwd=Path(__file__).parent)
    
    return backend_port

def start_frontend():
    """启动前端服务"""
    print("\n🌐 准备前端服务...")
    
    frontend_port = 3000
    if Path('ports.json').exists():
        try:
            with open('ports.json', 'r') as f:
                config = json.load(f)
                frontend_port = config.get('frontend_port', 3000)
        except:
            pass
    
    # 检查前端文件
    frontend_dir = Path('frontend')
    if frontend_dir.exists():
        print(f"🎯 前端服务将在端口 {frontend_port} 启动")
        print("前端文件已准备就绪")
    else:
        print("⚠️ 前端文件不存在，仅启动API服务")
    
    return frontend_port

def print_startup_info(backend_port, frontend_port):
    """打印启动信息"""
    print("\n" + "="*60)
    print("🎉 AI Agent开发团队启动成功！")
    print("="*60)
    
    print(f"\n🔗 服务地址:")
    print(f"   📡 API服务:    http://localhost:{backend_port}")
    print(f"   📚 API文档:    http://localhost:{backend_port}/docs")
    print(f"   🌐 前端界面:   http://localhost:{frontend_port}")
    
    print(f"\n🎯 核心功能:")
    print(f"   🚀 项目启动台: http://localhost:{frontend_port}/launchpad")
    print(f"   🏠 系统仪表板: http://localhost:{frontend_port}/")
    print(f"   🤖 Agent监控:  http://localhost:{frontend_port}/agents")
    
    print(f"\n👥 AI开发团队 (5个Agent):")
    print("   👨‍💼 Manager-Agent   - 项目管理与团队协调")
    print("   📋 PM-Agent        - 产品需求与用户故事")
    print("   🏗️ Architect-Agent - 系统架构与技术设计")
    print("   👨‍💻 Developer-Agent - 代码开发与实现")
    print("   🔍 QA-Agent        - 质量保证与测试")
    
    print(f"\n⭐ 开始使用:")
    print(f"   1. 访问项目启动台创建新项目")
    print(f"   2. AI团队将自动分工协作")
    print(f"   3. 实时监控项目进展")
    
    print("\n💡 提示: 按 Ctrl+C 停止服务")
    print("="*60)

def main():
    """主函数"""
    print("🚀 AI Agent开发团队 - 系统启动")
    print("="*50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查服务
    if not check_services():
        print("\n⚠️ 数据库服务未启动，正在启动...")
        try:
            subprocess.run(['docker-compose', 'up', '-d', 'postgres', 'redis'], 
                         check=True)
            print("✅ 数据库服务启动成功")
            time.sleep(3)  # 等待服务完全启动
        except:
            print("❌ 无法启动数据库服务")
            print("请手动运行: docker-compose up -d postgres redis")
            sys.exit(1)
    
    # 启动后端
    backend_port = start_backend()
    
    # 启动前端
    frontend_port = start_frontend()
    
    # 等待服务启动
    time.sleep(2)
    
    # 显示启动信息
    print_startup_info(backend_port, frontend_port)
    
    try:
        # 保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 正在停止AI Agent开发团队...")
        print("谢谢使用！")

if __name__ == "__main__":
    main()