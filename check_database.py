#!/usr/bin/env python3
"""
数据库状态检查和初始化工具
"""

import asyncio
import sys
import subprocess
import socket
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import psycopg2
    import redis
    from src.config.settings import Settings
    from src.core.database.session import DatabaseManager
    from src.utils import get_logger
    logger = get_logger(__name__)
except ImportError as e:
    print(f"⚠️ 导入错误: {e}")
    print("请先安装依赖: pip install psycopg2-binary redis")
    # 使用标准库日志
    import logging
    logger = logging.getLogger(__name__)

class DatabaseChecker:
    """数据库状态检查器"""
    
    def __init__(self):
        self.settings = Settings()
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    def check_port(self, host: str, port: int, timeout: int = 3) -> bool:
        """检查端口是否可连接"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    def check_postgresql(self) -> Dict[str, Any]:
        """检查PostgreSQL状态"""
        print("🔍 检查PostgreSQL...")
        
        result = {
            "available": False,
            "connected": False,
            "database_exists": False,
            "tables_exist": False,
            "error": None
        }
        
        # 检查端口
        if not self.check_port("localhost", 5432):
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
                    result["tables_exist"] = True
                    print(f"✅ 找到 {len(tables)} 个数据表")
                else:
                    print("⚠️ 数据库中没有表")
            
            conn.close()
            
        except psycopg2.OperationalError as e:
            if "database" in str(e).lower() and "does not exist" in str(e).lower():
                result["error"] = "数据库 agent_team_db 不存在"
                print("❌ 数据库不存在")
            elif "authentication failed" in str(e).lower():
                result["error"] = "数据库认证失败"
                print("❌ 数据库认证失败")
            else:
                result["error"] = f"数据库连接错误: {str(e)}"
                print(f"❌ 数据库连接错误: {str(e)}")
        except Exception as e:
            result["error"] = f"未知错误: {str(e)}"
            print(f"❌ 未知错误: {str(e)}")
        
        return result
    
    def check_redis(self) -> Dict[str, Any]:
        """检查Redis状态"""
        print("\n🔍 检查Redis...")
        
        result = {
            "available": False,
            "connected": False,
            "error": None
        }
        
        # 检查端口
        if not self.check_port("localhost", 6379):
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
            
        except Exception as e:
            result["error"] = f"Redis连接错误: {str(e)}"
            print(f"❌ Redis连接错误: {str(e)}")
        
        return result
    
    async def check_agent_communication(self) -> Dict[str, Any]:
        """检查Agent通信状态"""
        print("\n🔍 检查Agent通信...")
        
        result = {
            "message_bus_available": False,
            "agents_initialized": False,
            "test_communication": False,
            "error": None
        }
        
        try:
            # 检查消息总线
            from src.core.communication.message_bus import MessageBus
            
            # 在没有Redis的情况下，使用内存模式
            try:
                bus = MessageBus()
                result["message_bus_available"] = True
                print("✅ 消息总线可用 (内存模式)")
            except Exception as e:
                result["error"] = f"消息总线初始化失败: {str(e)}"
                print(f"❌ 消息总线初始化失败: {str(e)}")
                return result
            
            # 检查Agent初始化
            try:
                from src.agents.implementations.manager_agent import ManagerAgent
                from src.agents.implementations.pm_agent import PMAgent
                
                manager = ManagerAgent("test-manager")
                pm = PMAgent("test-pm")
                
                result["agents_initialized"] = True
                print("✅ Agent初始化成功")
                
                # 简单通信测试
                from src.agents.base import AgentContext
                context = AgentContext(project_id="test-project", sprint_id="test-sprint")
                
                # 测试PM任务
                test_task = {
                    "type": "analyze_requirements",
                    "requirements": ["测试需求1", "测试需求2"],
                    "business_goals": ["测试目标"]
                }
                
                result_pm = await pm.process_task(test_task, context)
                if result_pm.get("status") == "success":
                    result["test_communication"] = True
                    print("✅ Agent通信测试成功")
                else:
                    print("⚠️ Agent通信测试部分成功")
                
            except Exception as e:
                result["error"] = f"Agent通信测试失败: {str(e)}"
                print(f"❌ Agent通信测试失败: {str(e)}")
        
        except Exception as e:
            result["error"] = f"通信检查失败: {str(e)}"
            print(f"❌ 通信检查失败: {str(e)}")
        
        return result
    
    def suggest_solutions(self, pg_result: Dict, redis_result: Dict, comm_result: Dict):
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
        
        # Docker一键解决方案
        print("\n🐳 Docker一键解决方案:")
        print("   docker-compose up -d postgres redis")
        print("   这将启动PostgreSQL和Redis服务")
        
        # 无数据库模式
        print("\n⚡ 无数据库模式 (快速测试):")
        print("   python smart_start.py")
        print("   系统将使用内存存储，适合演示和测试")
    
    async def run_full_check(self):
        """运行完整检查"""
        print("🔍 AI Agent开发团队 - 数据库状态检查")
        print("=" * 50)
        
        # 检查PostgreSQL
        pg_result = self.check_postgresql()
        
        # 检查Redis
        redis_result = self.check_redis()
        
        # 检查Agent通信
        comm_result = await self.check_agent_communication()
        
        # 总结状态
        print("\n📊 系统状态总结:")
        print("=" * 30)
        print(f"PostgreSQL: {'✅' if pg_result['connected'] else '❌'}")
        print(f"Redis: {'✅' if redis_result['connected'] else '❌'}")
        print(f"Agent通信: {'✅' if comm_result['test_communication'] else '⚠️'}")
        
        # 系统就绪状态
        if pg_result["connected"] and redis_result["connected"] and comm_result["test_communication"]:
            print("\n🎉 系统完全就绪！可以启动完整功能")
            ready_status = "full"
        elif comm_result["agents_initialized"]:
            print("\n⚡ 系统部分就绪，可以运行基础功能")
            ready_status = "basic"
        else:
            print("\n⚠️ 系统需要配置才能运行")
            ready_status = "needs_setup"
        
        # 建议解决方案
        if ready_status != "full":
            self.suggest_solutions(pg_result, redis_result, comm_result)
        
        # 保存检查结果
        check_result = {
            "timestamp": "2025-07-29T20:30:00Z",
            "status": ready_status,
            "postgresql": pg_result,
            "redis": redis_result,
            "agent_communication": comm_result,
            "recommendations": self._get_recommendations(ready_status)
        }
        
        with open("database_check_result.json", "w") as f:
            json.dump(check_result, f, indent=2)
        
        print(f"\n💾 检查结果已保存到 database_check_result.json")
        
        return check_result
    
    def _get_recommendations(self, status: str) -> list:
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

async def main():
    """主函数"""
    checker = DatabaseChecker()
    await checker.run_full_check()

if __name__ == "__main__":
    asyncio.run(main())