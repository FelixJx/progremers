#!/usr/bin/env python3
"""
简化版数据库状态检查工具
"""

import socket
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

def check_port(host: str, port: int, timeout: int = 3) -> bool:
    """检查端口是否可连接"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

def check_postgresql():
    """检查PostgreSQL状态"""
    print("🔍 检查PostgreSQL...")
    
    result = {
        "available": False,
        "connected": False,
        "database_exists": False,
        "error": None
    }
    
    # 检查端口
    if not check_port("localhost", 5432):
        result["error"] = "PostgreSQL服务未运行 (端口5432不可达)"
        print("❌ PostgreSQL服务未运行")
        return result
    
    result["available"] = True
    print("✅ PostgreSQL服务运行中")
    
    # 尝试连接数据库
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="agent_user",
            password="agent_pass",
            database="agent_team_db"
        )
        result["connected"] = True
        result["database_exists"] = True
        print("✅ 数据库连接成功")
        
        # 检查表是否存在
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cur.fetchall()
            if tables:
                print(f"✅ 找到 {len(tables)} 个数据表")
            else:
                print("⚠️ 数据库中没有表")
        
        conn.close()
        
    except ImportError:
        result["error"] = "psycopg2模块未安装"
        print("❌ psycopg2模块未安装，请运行: pip install psycopg2-binary")
    except Exception as e:
        if "database" in str(e).lower() and "does not exist" in str(e).lower():
            result["error"] = "数据库 agent_team_db 不存在"
            print("❌ 数据库不存在")
        elif "authentication failed" in str(e).lower():
            result["error"] = "数据库认证失败"
            print("❌ 数据库认证失败")
        else:
            result["error"] = f"数据库连接错误: {str(e)}"
            print(f"❌ 数据库连接错误: {str(e)}")
    
    return result

def check_redis():
    """检查Redis状态"""
    print("\n🔍 检查Redis...")
    
    result = {
        "available": False,
        "connected": False,
        "error": None
    }
    
    # 检查端口
    if not check_port("localhost", 6379):
        result["error"] = "Redis服务未运行 (端口6379不可达)"
        print("❌ Redis服务未运行")
        return result
    
    result["available"] = True
    print("✅ Redis服务运行中")
    
    # 尝试连接Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        result["connected"] = True
        print("✅ Redis连接成功")
        
        # 检查基本信息
        info = r.info()
        print(f"   Redis版本: {info.get('redis_version', 'Unknown')}")
        print(f"   已用内存: {info.get('used_memory_human', 'Unknown')}")
        
    except ImportError:
        result["error"] = "redis模块未安装"
        print("❌ redis模块未安装，请运行: pip install redis")
    except Exception as e:
        result["error"] = f"Redis连接错误: {str(e)}"
        print(f"❌ Redis连接错误: {str(e)}")
    
    return result

def check_agent_files():
    """检查Agent文件是否存在"""
    print("\n🔍 检查Agent文件...")
    
    result = {
        "core_files_exist": False,
        "agent_files_exist": False,
        "config_files_exist": False,
        "missing_files": []
    }
    
    # 检查核心文件
    core_files = [
        "src/agents/base/base_agent.py",
        "src/agents/implementations/manager_agent.py",
        "src/agents/implementations/pm_agent.py",
        "src/core/communication/message_bus.py",
        "project_launcher.py"
    ]
    
    config_files = [
        "src/config/settings.py",
        "pyproject.toml"
    ]
    
    missing_files = []
    
    # 检查核心文件
    for file_path in core_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        result["core_files_exist"] = True
        result["agent_files_exist"] = True
        print("✅ Agent文件完整")
    else:
        print(f"❌ 缺失 {len(missing_files)} 个核心文件")
        for file in missing_files[:3]:  # 只显示前3个
            print(f"   - {file}")
    
    # 检查配置文件
    config_missing = []
    for file_path in config_files:
        if not Path(file_path).exists():
            config_missing.append(file_path)
    
    if not config_missing:
        result["config_files_exist"] = True
        print("✅ 配置文件完整")
    else:
        print(f"❌ 缺失配置文件: {config_missing}")
    
    result["missing_files"] = missing_files + config_missing
    return result

def suggest_solutions(pg_result, redis_result, files_result):
    """建议解决方案"""
    print("\n💡 解决方案建议:")
    print("=" * 40)
    
    # PostgreSQL解决方案
    if not pg_result["available"]:
        print("📦 安装PostgreSQL:")
        print("   macOS: brew install postgresql")
        print("   启动: brew services start postgresql")
        print("   或使用Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=agent_pass postgres:15")
    elif not pg_result["database_exists"]:
        print("🗄️ 创建数据库:")
        print("   createdb -U postgres agent_team_db")
        print("   或运行: python scripts/setup_database.py")
    
    # Redis解决方案
    if not redis_result["available"]:
        print("\n📦 安装Redis:")
        print("   macOS: brew install redis")
        print("   启动: brew services start redis")
        print("   或使用Docker: docker run -d -p 6379:6379 redis:7-alpine")
    
    # 文件缺失解决方案
    if files_result["missing_files"]:
        print("\n📄 修复文件问题:")
        print("   请检查项目完整性，可能需要重新克隆代码")
    
    # Docker一键解决方案
    print("\n🐳 Docker一键解决方案:")
    print("   docker-compose up -d postgres redis")
    print("   这将启动PostgreSQL和Redis服务")
    
    # 无数据库模式
    print("\n⚡ 无数据库模式 (快速测试):")
    print("   python smart_start.py")
    print("   系统将使用内存存储，适合演示和测试")

def main():
    """主函数"""
    print("🔍 AI Agent开发团队 - 数据库状态检查")
    print("=" * 50)
    
    # 检查PostgreSQL
    pg_result = check_postgresql()
    
    # 检查Redis
    redis_result = check_redis()
    
    # 检查Agent文件
    files_result = check_agent_files()
    
    # 总结状态
    print("\n📊 系统状态总结:")
    print("=" * 30)
    print(f"PostgreSQL: {'✅' if pg_result['connected'] else '❌'}")
    print(f"Redis: {'✅' if redis_result['connected'] else '❌'}")
    print(f"Agent文件: {'✅' if files_result['agent_files_exist'] else '❌'}")
    
    # 系统就绪状态
    if pg_result["connected"] and redis_result["connected"] and files_result["agent_files_exist"]:
        print("\n🎉 系统完全就绪！可以启动完整功能")
        ready_status = "full"
    elif files_result["agent_files_exist"]:
        print("\n⚡ 系统部分就绪，可以运行基础功能")
        ready_status = "basic"
    else:
        print("\n⚠️ 系统需要配置才能运行")
        ready_status = "needs_setup"
    
    # 建议解决方案
    if ready_status != "full":
        suggest_solutions(pg_result, redis_result, files_result)
    
    # 保存检查结果
    check_result = {
        "timestamp": datetime.now().isoformat(),
        "status": ready_status,
        "postgresql": pg_result,
        "redis": redis_result,
        "agent_files": files_result,
        "recommendations": get_recommendations(ready_status)
    }
    
    with open("database_check_result.json", "w", encoding='utf-8') as f:
        json.dump(check_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 检查结果已保存到 database_check_result.json")
    
    return check_result

def get_recommendations(status: str) -> list:
    """获取推荐操作"""
    if status == "full":
        return [
            "运行 python smart_start.py 启动完整系统",
            "访问 http://localhost:3000/launchpad 开始创建项目"
        ]
    elif status == "basic":
        return [
            "运行 docker-compose up -d postgres redis 启动数据库",
            "或直接运行 python smart_start.py 使用内存模式"
        ]
    else:
        return [
            "安装PostgreSQL和Redis数据库",
            "运行 docker-compose up --build 一键部署",
            "或使用 python smart_start.py 启动基础功能"
        ]

if __name__ == "__main__":
    main()