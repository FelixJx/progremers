#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    import redis
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请先安装依赖: pip install psycopg2-binary redis sqlalchemy")
    sys.exit(1)

def setup_postgresql():
    """设置PostgreSQL数据库"""
    print("🔧 设置PostgreSQL数据库...")
    
    try:
        # 连接到默认数据库postgres
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="agent_user",
            password="agent_pass",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # 检查数据库是否已存在
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'agent_team_db'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute("CREATE DATABASE agent_team_db")
            print("✅ 数据库 agent_team_db 创建成功")
        else:
            print("✅ 数据库 agent_team_db 已存在")
        
        cur.close()
        conn.close()
        
        # 连接到目标数据库创建表
        engine = create_engine("postgresql://agent_user:agent_pass@localhost:5432/agent_team_db")
        
        # 创建基础表结构
        with engine.connect() as conn:
            # 项目表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS projects (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    type VARCHAR(50),
                    status VARCHAR(50) DEFAULT 'planning',
                    priority VARCHAR(20) DEFAULT 'medium',
                    budget INTEGER,
                    timeline VARCHAR(100),
                    requirements TEXT,
                    tech_stack TEXT,
                    business_goals TEXT,
                    assigned_agents TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Agent表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS agents (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    role VARCHAR(100) NOT NULL,
                    status VARCHAR(50) DEFAULT 'active',
                    current_task TEXT,
                    performance FLOAT DEFAULT 0.0,
                    capabilities TEXT,
                    llm_model VARCHAR(100),
                    project_id VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 任务表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id VARCHAR(50) PRIMARY KEY,
                    project_id VARCHAR(50) NOT NULL,
                    agent_id VARCHAR(50),
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'pending',
                    priority VARCHAR(20) DEFAULT 'medium',
                    task_type VARCHAR(100),
                    input_data TEXT,
                    output_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """))
            
            # 消息表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    project_id VARCHAR(50),
                    from_agent VARCHAR(50),
                    to_agent VARCHAR(50),
                    message_type VARCHAR(100),
                    content TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 内存/上下文表
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    id SERIAL PRIMARY KEY,
                    agent_id VARCHAR(50) NOT NULL,
                    project_id VARCHAR(50),
                    memory_type VARCHAR(50),
                    content TEXT,
                    importance FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.commit()
            print("✅ 数据库表结构创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL设置失败: {str(e)}")
        return False

def setup_redis():
    """设置Redis"""
    print("\n🔧 设置Redis缓存...")
    
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        
        # 清理可能存在的测试数据
        r.flushdb()
        
        # 设置一些基础配置
        r.hset("system:config", mapping={
            "version": "1.0.0",
            "initialized_at": "2025-07-29T22:56:00Z",
            "status": "ready"
        })
        
        # 初始化Agent状态
        agents = [
            {"id": "pm-001", "name": "PM-Agent", "role": "产品经理", "status": "active"},
            {"id": "arch-001", "name": "Architect-Agent", "role": "系统架构师", "status": "active"},
            {"id": "dev-001", "name": "Developer-Agent", "role": "开发工程师", "status": "active"},
            {"id": "qa-001", "name": "QA-Agent", "role": "质量保证", "status": "active"},
            {"id": "mgr-001", "name": "Manager-Agent", "role": "项目管理", "status": "active"}
        ]
        
        for agent in agents:
            r.hset(f"agent:{agent['id']}", mapping=agent)
        
        print("✅ Redis缓存设置成功")
        return True
        
    except Exception as e:
        print(f"❌ Redis设置失败: {str(e)}")
        return False

def insert_sample_data():
    """插入示例数据"""
    print("\n🔧 插入示例数据...")
    
    try:
        engine = create_engine("postgresql://agent_user:agent_pass@localhost:5432/agent_team_db")
        
        with engine.connect() as conn:
            # 插入示例Agent数据
            conn.execute(text("""
                INSERT INTO agents (id, name, role, status, current_task, performance, capabilities, llm_model)
                VALUES 
                    ('pm-001', 'PM-Agent', '产品经理', 'active', '需求分析', 92.5, '需求分析,用户故事,PRD撰写', 'DeepSeek'),
                    ('arch-001', 'Architect-Agent', '系统架构师', 'active', '架构设计', 88.7, '系统设计,技术选型,架构文档', 'Qwen-Max'),
                    ('dev-001', 'Developer-Agent', '开发工程师', 'busy', '代码开发', 85.3, '代码编写,MCP操作,单元测试', 'DeepSeek'),
                    ('qa-001', 'QA-Agent', '质量保证', 'active', '测试执行', 90.1, '测试设计,自动化测试,质量保证', 'Qwen-72B'),
                    ('mgr-001', 'Manager-Agent', '项目管理', 'active', '团队协调', 87.9, '任务分配,质量验证,团队协调', 'DeepSeek')
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    current_task = EXCLUDED.current_task,
                    performance = EXCLUDED.performance,
                    last_active = CURRENT_TIMESTAMP
            """))
            
            # 插入示例项目数据
            conn.execute(text("""
                INSERT INTO projects (id, name, description, type, status, priority, assigned_agents)
                VALUES 
                    ('demo-001', '演示项目', 'AI开发团队演示项目', 'web', 'in_progress', 'high', 'pm-001,arch-001,dev-001,qa-001,mgr-001')
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    updated_at = CURRENT_TIMESTAMP
            """))
            
            conn.commit()
            print("✅ 示例数据插入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 示例数据插入失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 AI Agent开发团队 - 数据库初始化")
    print("=" * 50)
    
    success_count = 0
    
    # 设置PostgreSQL
    if setup_postgresql():
        success_count += 1
    
    # 设置Redis
    if setup_redis():
        success_count += 1
    
    # 插入示例数据
    if insert_sample_data():
        success_count += 1
    
    print("\n" + "=" * 50)
    if success_count == 3:
        print("🎉 数据库初始化完全成功！")
        print("\n✅ 可以执行的操作:")
        print("   1. python3 smart_start.py - 启动完整系统")
        print("   2. python3 api_server.py - 启动API服务")
        print("   3. 访问 http://localhost:3000/launchpad - 开始创建项目")
    else:
        print(f"⚠️ 部分初始化成功 ({success_count}/3)")
        print("请检查错误信息并重新运行")

if __name__ == "__main__":
    main()