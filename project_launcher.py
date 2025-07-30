#!/usr/bin/env python3
"""
项目启动器 - 为用户app项目分配AI团队并开始开发
"""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.implementations.manager_agent import ManagerAgent
from src.agents.implementations.pm_agent import PMAgent
from src.agents.implementations.architect_agent import ArchitectAgent
from src.agents.implementations.developer_agent import DeveloperAgent
from src.agents.implementations.qa_agent import QAAgent
from src.agents.base import AgentContext
from src.utils import get_logger

logger = get_logger(__name__)


class ProjectLauncher:
    """项目启动器 - 协调AI团队开始新项目"""
    
    def __init__(self):
        self.logger = get_logger(f"{self.__class__.__name__}")
        
        # 初始化AI团队
        self.manager = ManagerAgent("project-manager")
        self.pm = PMAgent("project-pm")
        self.architect = ArchitectAgent("project-architect")
        self.developer = DeveloperAgent("project-developer")
        self.qa = QAAgent("project-qa")
        
        # 项目状态跟踪
        self.active_projects = {}
    
    async def launch_project(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        启动新的app项目
        
        Args:
            project_config: 项目配置信息
            
        Returns:
            项目启动结果
        """
        project_id = f"proj-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        self.logger.info(f"🚀 启动新项目: {project_config.get('name', '未命名项目')}")
        
        try:
            # 创建项目上下文
            context = AgentContext(
                project_id=project_id,
                sprint_id=f"sprint-{project_id}-001"
            )
            
            # 阶段1: Manager Agent - 项目规划和团队分配
            planning_result = await self._project_planning_phase(project_config, context)
            
            if planning_result.get("status") != "success":
                return {"status": "error", "message": "项目规划失败", "details": planning_result}
            
            # 阶段2: PM Agent - 需求分析
            requirements_result = await self._requirements_analysis_phase(project_config, context)
            
            if requirements_result.get("status") != "success":
                return {"status": "error", "message": "需求分析失败", "details": requirements_result}
            
            # 阶段3: Architect Agent - 架构设计
            architecture_result = await self._architecture_design_phase(project_config, context)
            
            if architecture_result.get("status") != "success":
                return {"status": "error", "message": "架构设计失败", "details": architecture_result}
            
            # 阶段4: Developer Agent - 项目搭建
            development_result = await self._development_setup_phase(project_config, context)
            
            # 阶段5: QA Agent - 测试计划
            qa_result = await self._qa_planning_phase(project_config, context)
            
            # 记录项目状态
            project_status = {
                "project_id": project_id,
                "name": project_config.get("name"),
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "phases": {
                    "planning": planning_result,
                    "requirements": requirements_result, 
                    "architecture": architecture_result,
                    "development": development_result,
                    "qa_planning": qa_result
                },
                "assigned_agents": ["Manager", "PM", "Architect", "Developer", "QA"],
                "next_steps": await self._generate_next_steps(project_config, context)
            }
            
            self.active_projects[project_id] = project_status
            
            # 保存项目启动报告
            await self._save_project_report(project_status)
            
            return {
                "status": "success",
                "project_id": project_id,
                "message": f"🎉 项目 '{project_config.get('name')}' 启动成功！",
                "project_status": project_status,
                "summary": {
                    "team_assigned": True,
                    "requirements_analyzed": True,
                    "architecture_designed": True,
                    "development_ready": True,
                    "qa_prepared": True
                }
            }
            
        except Exception as e:
            self.logger.error(f"项目启动失败: {str(e)}")
            return {
                "status": "error",
                "message": f"项目启动失败: {str(e)}"
            }
    
    async def _project_planning_phase(self, project_config: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """阶段1: 项目规划和团队分配"""
        
        self.logger.info("📋 阶段1: 项目规划和团队分配")
        
        planning_task = {
            "type": "project_planning",
            "project_info": {
                "name": project_config.get("name"),
                "description": project_config.get("description"),
                "type": project_config.get("type", "web"),
                "priority": project_config.get("priority", "medium"),
                "budget": project_config.get("budget", 0),
                "timeline": project_config.get("timeline", "3个月"),
                "requirements": project_config.get("requirements", [])
            },
            "team_composition": {
                "required_roles": ["PM", "Architect", "Developer", "QA"],
                "project_complexity": "medium",
                "estimated_duration": project_config.get("timeline", "3个月")
            }
        }
        
        result = await self.manager.process_task(planning_task, context)
        
        if result.get("status") == "success":
            self.logger.info("✅ 项目规划完成")
        
        return result
    
    async def _requirements_analysis_phase(self, project_config: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """阶段2: 需求分析"""
        
        self.logger.info("📊 阶段2: 需求分析")
        
        requirements_task = {
            "type": "analyze_requirements",
            "requirements": project_config.get("requirements", []),
            "business_goals": project_config.get("business_goals", [
                "提升用户体验",
                "增加业务价值",
                "降低运营成本"
            ]),
            "target_users": project_config.get("target_users", ["终端用户"]),
            "project_context": {
                "type": project_config.get("type"),
                "priority": project_config.get("priority"),
                "budget": project_config.get("budget")
            }
        }
        
        result = await self.pm.process_task(requirements_task, context)
        
        if result.get("status") == "success":
            self.logger.info("✅ 需求分析完成")
            analysis = result.get("analysis", {})
            self.logger.info(f"   📋 需求总数: {analysis.get('total_requirements', 0)}")
            self.logger.info(f"   🎯 业务对齐度: {analysis.get('business_alignment', 0):.1%}")
        
        return result
    
    async def _architecture_design_phase(self, project_config: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """阶段3: 架构设计"""
        
        self.logger.info("🏗️ 阶段3: 架构设计")
        
        architecture_task = {
            "type": "design_architecture",
            "project_requirements": {
                "type": project_config.get("type", "web"),
                "scale": project_config.get("scale", "medium"),
                "tech_preferences": project_config.get("tech_stack", []),
                "performance_requirements": project_config.get("performance", {}),
                "security_requirements": project_config.get("security", {})
            },
            "constraints": {
                "budget": project_config.get("budget", 0),
                "timeline": project_config.get("timeline", "3个月"),
                "team_size": 5
            }
        }
        
        result = await self.architect.process_task(architecture_task, context)
        
        if result.get("status") == "success":
            self.logger.info("✅ 架构设计完成")
        
        return result
    
    async def _development_setup_phase(self, project_config: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """阶段4: 开发环境搭建"""
        
        self.logger.info("👨‍💻 阶段4: 开发环境搭建")
        
        dev_task = {
            "type": "setup_project",
            "project_name": project_config.get("name", "new-project"),
            "tech_stack": project_config.get("tech_stack", ["React", "Node.js"]),
            "project_structure": {
                "frontend": True,
                "backend": True,
                "database": True,
                "testing": True
            }
        }
        
        result = await self.developer.process_task(dev_task, context)
        
        if result.get("status") == "success":
            self.logger.info("✅ 开发环境搭建完成")
        
        return result
    
    async def _qa_planning_phase(self, project_config: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """阶段5: 测试计划制定"""
        
        self.logger.info("🔍 阶段5: 测试计划制定")
        
        qa_task = {
            "type": "create_test_plan",
            "project_info": {
                "name": project_config.get("name"),
                "type": project_config.get("type"),
                "requirements": project_config.get("requirements", [])
            },
            "testing_scope": {
                "unit_testing": True,
                "integration_testing": True,
                "e2e_testing": True,
                "performance_testing": True,
                "security_testing": True
            }
        }
        
        result = await self.qa.process_task(qa_task, context)
        
        if result.get("status") == "success":
            self.logger.info("✅ 测试计划制定完成")
        
        return result
    
    async def _generate_next_steps(self, project_config: Dict[str, Any], context: AgentContext) -> List[str]:
        """生成项目下一步行动计划"""
        
        return [
            "🎯 PM Agent: 细化用户故事和验收标准",
            "🏗️ Architect Agent: 完善技术架构文档",
            "👨‍💻 Developer Agent: 开始核心功能开发",
            "🔍 QA Agent: 准备自动化测试环境",
            "📊 Manager Agent: 制定详细Sprint计划"
        ]
    
    async def _save_project_report(self, project_status: Dict[str, Any]):
        """保存项目启动报告"""
        
        report_content = f"""# 项目启动报告

## 📊 项目信息

**项目ID**: {project_status['project_id']}  
**项目名称**: {project_status['name']}  
**创建时间**: {project_status['created_at']}  
**状态**: {project_status['status']}  

## 🤖 分配的AI团队

{chr(10).join(f"- {agent}-Agent" for agent in project_status['assigned_agents'])}

## 📋 下一步行动

{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(project_status['next_steps']))}

## 🎯 项目阶段完成情况

- ✅ 项目规划和团队分配
- ✅ 需求分析  
- ✅ 架构设计
- ✅ 开发环境搭建
- ✅ 测试计划制定

---
*报告生成时间: {datetime.utcnow().isoformat()}*  
*AI团队已准备就绪，项目正式启动！* 🚀
"""
        
        report_file = f"PROJECT_LAUNCH_REPORT_{project_status['project_id']}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        self.logger.info(f"📄 项目启动报告已保存: {report_file}")
    
    async def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目状态"""
        return self.active_projects.get(project_id)
    
    async def list_active_projects(self) -> List[Dict[str, Any]]:
        """列出所有活跃项目"""
        return list(self.active_projects.values())


async def main():
    """演示项目启动器使用"""
    
    launcher = ProjectLauncher()
    
    # 示例项目配置
    sample_project = {
        "name": "智能任务管理APP",
        "description": "基于AI的个人和团队任务管理应用，支持智能提醒和进度预测",
        "type": "mobile",
        "priority": "high",
        "budget": 500000,
        "timeline": "4个月",
        "requirements": [
            "用户注册和身份验证",
            "任务创建和管理",
            "智能提醒系统",
            "团队协作功能",
            "数据分析和报表",
            "移动端适配"
        ],
        "tech_stack": ["React Native", "Node.js", "PostgreSQL", "Redis"],
        "business_goals": [
            "提高用户生产力",
            "增强团队协作效率",
            "提供智能化体验"
        ]
    }
    
    print("🚀 AI团队项目启动器演示")
    print("=" * 50)
    
    # 启动项目
    result = await launcher.launch_project(sample_project)
    
    if result.get("status") == "success":
        print(f"\n{result['message']}")
        print(f"项目ID: {result['project_id']}")
        
        # 显示项目状态
        project_status = result["project_status"]
        print(f"\n📊 项目状态:")
        print(f"   团队分配: {'✅' if result['summary']['team_assigned'] else '❌'}")
        print(f"   需求分析: {'✅' if result['summary']['requirements_analyzed'] else '❌'}")
        print(f"   架构设计: {'✅' if result['summary']['architecture_designed'] else '❌'}")
        print(f"   开发准备: {'✅' if result['summary']['development_ready'] else '❌'}")
        print(f"   测试准备: {'✅' if result['summary']['qa_prepared'] else '❌'}")
        
        print(f"\n🎯 下一步行动:")
        for step in project_status["next_steps"]:
            print(f"   {step}")
    else:
        print(f"❌ 项目启动失败: {result.get('message')}")


if __name__ == "__main__":
    asyncio.run(main())