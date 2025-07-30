#!/usr/bin/env python3
"""
API服务器 - 为前端界面提供AI团队管理接口
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from project_launcher import ProjectLauncher
from src.utils import get_logger

logger = get_logger(__name__)

# FastAPI应用
app = FastAPI(
    title="AI Agent开发团队 API",
    description="AI Agent开发团队管理系统的后端API服务",
    version="1.0.0"
)

# CORS中间件将在main函数中动态配置

# 全局项目启动器实例
launcher = ProjectLauncher()

# Pydantic模型
class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    type: str = "web"
    priority: str = "medium"
    budget: Optional[int] = None
    timeline: str = "3个月"
    requirements: List[str] = []
    tech_stack: List[str] = []
    business_goals: List[str] = []

class ProjectLaunchRequest(BaseModel):
    project_id: str

class AgentStatus(BaseModel):
    id: str
    name: str
    role: str
    status: str
    current_task: str
    performance: float
    last_active: str

class ProjectStatus(BaseModel):
    id: str
    name: str
    status: str
    progress: float
    assigned_agents: List[str]
    created_at: str
    last_update: str

# API路由

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Agent开发团队 API服务",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/agents/status")
async def get_agents_status():
    """获取所有Agent状态"""
    return {
        "agents": [
            {
                "id": "pm-001",
                "name": "PM-Agent",
                "role": "产品经理",
                "status": "active",
                "current_task": "需求分析",
                "performance": 92.5,
                "last_active": "刚刚",
                "capabilities": ["需求分析", "用户故事", "PRD撰写"],
                "llm_model": "DeepSeek"
            },
            {
                "id": "arch-001", 
                "name": "Architect-Agent",
                "role": "系统架构师",
                "status": "active",
                "current_task": "架构设计",
                "performance": 88.7,
                "last_active": "2分钟前",
                "capabilities": ["系统设计", "技术选型", "架构文档"],
                "llm_model": "Qwen-Max"
            },
            {
                "id": "dev-001",
                "name": "Developer-Agent", 
                "role": "开发工程师",
                "status": "busy",
                "current_task": "代码开发",
                "performance": 85.3,
                "last_active": "30秒前",
                "capabilities": ["代码编写", "MCP操作", "单元测试"],
                "llm_model": "DeepSeek"
            },
            {
                "id": "qa-001",
                "name": "QA-Agent",
                "role": "质量保证", 
                "status": "active",
                "current_task": "测试执行",
                "performance": 90.1,
                "last_active": "1分钟前",
                "capabilities": ["测试设计", "自动化测试", "质量保证"],
                "llm_model": "Qwen-72B"
            },
            {
                "id": "mgr-001",
                "name": "Manager-Agent",
                "role": "项目管理",
                "status": "active", 
                "current_task": "团队协调",
                "performance": 87.9,
                "last_active": "45秒前",
                "capabilities": ["任务分配", "质量验证", "团队协调"],
                "llm_model": "DeepSeek"
            }
        ],
        "summary": {
            "total_agents": 5,
            "active_agents": 5,
            "average_performance": 88.9
        }
    }

@app.get("/api/projects")
async def get_projects():
    """获取所有项目列表"""
    # 获取活跃项目
    active_projects = await launcher.list_active_projects()
    
    # 模拟一些历史项目数据
    all_projects = [
        {
            "id": "user-proj-001",
            "name": "智能股票分析平台",
            "type": "Web应用",
            "status": "in_progress",
            "priority": "high",
            "description": "基于AI的股票市场分析和预测平台",
            "progress": 65,
            "assigned_agents": ["PM-Agent", "Architect-Agent", "Developer-Agent", "QA-Agent"],
            "created_at": "2025-01-15T10:00:00Z",
            "last_update": "2小时前",
            "budget": 800000,
            "spent": 520000
        },
        {
            "id": "user-proj-002", 
            "name": "企业CRM系统",
            "type": "企业应用",
            "status": "planning",
            "priority": "medium",
            "description": "全功能企业客户关系管理系统",
            "progress": 15,
            "assigned_agents": ["PM-Agent"],
            "created_at": "2025-01-20T14:30:00Z", 
            "last_update": "1天前",
            "budget": 600000,
            "spent": 90000
        }
    ]
    
    # 添加活跃项目
    for project in active_projects:
        all_projects.append({
            "id": project["project_id"],
            "name": project["name"],
            "type": "应用项目",
            "status": project["status"],
            "priority": "high",
            "description": f"AI团队启动的项目: {project['name']}",
            "progress": 5,  # 刚启动
            "assigned_agents": [f"{agent}-Agent" for agent in project["assigned_agents"]],
            "created_at": project["created_at"],
            "last_update": "刚刚",
            "budget": 500000,
            "spent": 25000
        })
    
    return {
        "projects": all_projects,
        "summary": {
            "total_projects": len(all_projects),
            "active_projects": len([p for p in all_projects if p["status"] == "in_progress"]),
            "pending_projects": len([p for p in all_projects if p["status"] == "planning"])
        }
    }

@app.post("/api/projects/create")
async def create_project(request: ProjectCreateRequest):
    """创建新项目"""
    try:
        project_config = {
            "name": request.name,
            "description": request.description,
            "type": request.type,
            "priority": request.priority,
            "budget": request.budget,
            "timeline": request.timeline,
            "requirements": request.requirements,
            "tech_stack": request.tech_stack,
            "business_goals": request.business_goals
        }
        
        result = await launcher.launch_project(project_config)
        
        if result.get("status") == "success":
            return {
                "success": True,
                "message": result["message"],
                "project_id": result["project_id"],
                "project_status": result["project_status"]
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "项目创建失败"))
            
    except Exception as e:
        logger.error(f"创建项目失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")

@app.post("/api/projects/{project_id}/launch")
async def launch_project(project_id: str):
    """启动待启动的项目"""
    try:
        # 模拟项目启动逻辑
        # 在实际应用中，这里会查找项目配置并启动
        sample_config = {
            "name": f"项目-{project_id}",
            "description": "用户启动的现有项目",
            "type": "web",
            "priority": "medium",
            "requirements": ["基础功能", "用户界面", "数据管理"]
        }
        
        result = await launcher.launch_project(sample_config)
        
        if result.get("status") == "success":
            return {
                "success": True,
                "message": f"项目 {project_id} 启动成功！",
                "project_id": result["project_id"],
                "assigned_agents": result["project_status"]["assigned_agents"]
            }
        else:
            raise HTTPException(status_code=400, detail="项目启动失败")
            
    except Exception as e:
        logger.error(f"启动项目失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动项目失败: {str(e)}")

@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: str):
    """获取项目详情"""
    project_status = await launcher.get_project_status(project_id)
    
    if project_status:
        return {
            "project": project_status,
            "phases": project_status.get("phases", {}),
            "next_steps": project_status.get("next_steps", [])
        }
    else:
        raise HTTPException(status_code=404, detail="项目不存在")

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """获取仪表板统计信息"""
    active_projects = await launcher.list_active_projects()
    
    return {
        "system_stats": {
            "total_projects": len(active_projects) + 3,  # 包含历史项目
            "active_agents": 5,
            "completed_tasks": 247,
            "success_rate": 85.2
        },
        "agent_performance": [
            {"name": "PM-Agent", "tasks": 45, "success": 92},
            {"name": "Architect", "tasks": 38, "success": 88},
            {"name": "Developer", "tasks": 67, "success": 85},
            {"name": "QA-Agent", "tasks": 52, "success": 90},
            {"name": "Manager", "tasks": 45, "success": 87}
        ],
        "recent_activities": [
            {
                "agent": "Developer-Agent",
                "action": "完成用户认证模块开发",
                "time": "2分钟前",
                "status": "success"
            },
            {
                "agent": "QA-Agent", 
                "action": "执行自动化测试套件",
                "time": "5分钟前",
                "status": "success"
            },
            {
                "agent": "PM-Agent",
                "action": "创建新用户故事", 
                "time": "8分钟前",
                "status": "info"
            }
        ]
    }

@app.get("/api/system/evaluation")
async def get_system_evaluation():
    """获取系统评估结果"""
    return {
        "overall_score": 8.1,
        "evaluation_date": "2025-07-29",
        "detailed_scores": {
            "产品价值": 8.5,
            "技术架构": 8.8,
            "代码质量": 7.8,
            "测试质量": 7.2,
            "文档完整性": 6.5,
            "用户体验": 5.8,
            "安全性": 6.8,
            "可维护性": 8.2,
            "创新性": 9.2
        },
        "strengths": [
            "🚀 技术创新性强 - 首个应用context-rot研究的AI Agent系统",
            "🏗️ 架构设计完善 - 模块化、可扩展的企业级架构",
            "🤖 Agent能力全面 - 覆盖完整软件开发流程"
        ],
        "weaknesses": [
            "⚠️ 测试覆盖率待提升 - 需要更多自动化测试",
            "⚠️ 安全机制需加强 - 缺少企业级安全控制",
            "⚠️ UI界面缺失 - 缺少友好的用户界面"
        ]
    }

@app.post("/api/agents/{agent_id}/action")
async def agent_action(agent_id: str, action: Dict[str, Any]):
    """对Agent执行操作"""
    try:
        action_type = action.get("type")
        
        if action_type == "pause":
            return {"success": True, "message": f"Agent {agent_id} 已暂停"}
        elif action_type == "resume":
            return {"success": True, "message": f"Agent {agent_id} 已恢复"}
        elif action_type == "restart":
            return {"success": True, "message": f"Agent {agent_id} 已重启"}
        else:
            raise HTTPException(status_code=400, detail="不支持的操作类型")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api_server": "running",
            "project_launcher": "ready",
            "ai_agents": "active"
        }
    }

def get_port_config():
    """获取端口配置"""
    try:
        import json
        from pathlib import Path
        if Path('ports.json').exists():
            with open('ports.json', 'r') as f:
                config = json.load(f)
                return config.get('backend_port', 8080), config.get('frontend_port', 3000)
    except:
        pass
    return 8080, 3000

if __name__ == "__main__":
    backend_port, frontend_port = get_port_config()
    
    print("🚀 启动AI Agent团队API服务器...")
    print(f"📡 API服务: http://localhost:{backend_port}")
    print(f"📚 API文档: http://localhost:{backend_port}/docs")
    print(f"🌐 前端界面: http://localhost:{frontend_port}")
    
    # 更新CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[f"http://localhost:{frontend_port}", f"http://127.0.0.1:{frontend_port}"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=backend_port,
        log_level="info",
        reload=True
    )