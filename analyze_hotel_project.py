#!/usr/bin/env python3.11
"""
酒店分析工具项目 - AI Agent团队深度分析脚本
"""

import requests
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

def analyze_project_structure():
    """分析项目结构"""
    project_path = Path("/Users/jx/Downloads/酒店分析工具")
    
    if not project_path.exists():
        return {"error": "项目路径不存在"}
    
    analysis = {
        "project_path": str(project_path),
        "total_files": 0,
        "file_types": {},
        "directory_structure": {},
        "key_files": []
    }
    
    # 统计文件信息
    for root, dirs, files in os.walk(project_path):
        for file in files:
            analysis["total_files"] += 1
            ext = Path(file).suffix.lower()
            analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
            
            # 识别关键文件
            if file in ["README.md", "requirements.txt", "main.py", "settings.py"]:
                analysis["key_files"].append(str(Path(root) / file))
    
    # 分析目录结构
    analysis["directory_structure"] = {
        "has_src": (project_path / "src").exists(),
        "has_tests": (project_path / "tests").exists(),
        "has_config": (project_path / "config").exists(),
        "has_api": (project_path / "src" / "api").exists(),
        "has_models": (project_path / "src" / "models").exists(),
        "has_services": (project_path / "src" / "services").exists(),
        "has_docs": (project_path / "docs").exists(),
        "has_data": (project_path / "data").exists(),
        "has_reports": (project_path / "reports").exists()
    }
    
    return analysis

def extract_project_info():
    """提取项目核心信息"""
    project_path = Path("/Users/jx/Downloads/酒店分析工具")
    
    info = {
        "name": "酒店分析工具",
        "description": "",
        "tech_stack": [],
        "business_goals": [],
        "features": [],
        "dependencies": []
    }
    
    # 读取README获取项目描述
    readme_path = project_path / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 提取描述信息
            if "## 项目概述" in content:
                desc_start = content.find("## 项目概述") + len("## 项目概述")
                desc_end = content.find("\n##", desc_start)
                if desc_end > 0:
                    info["description"] = content[desc_start:desc_end].strip()
    
    # 读取requirements.txt获取技术栈
    req_path = project_path / "requirements.txt"
    if req_path.exists():
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    pkg = line.split('==')[0].split('>=')[0].split('<=')[0]
                    info["dependencies"].append(pkg)
    
    # 分析技术栈
    tech_indicators = {
        "fastapi": "FastAPI Web框架",
        "sqlalchemy": "SQLAlchemy ORM",
        "pandas": "数据处理",
        "numpy": "数值计算", 
        "scikit-learn": "机器学习",
        "streamlit": "数据可视化",
        "redis": "缓存数据库",
        "pymysql": "MySQL数据库",
        "scrapy": "数据采集",
        "selenium": "Web自动化",
        "plotly": "交互式图表"
    }
    
    for dep in info["dependencies"]:
        if dep.lower() in tech_indicators:
            info["tech_stack"].append(tech_indicators[dep.lower()])
    
    # 核心业务功能
    info["business_goals"] = [
        "市场进入分析 - 评估目标城市供需关系",
        "投资回报预测 - ROI和回本周期计算",
        "经营监测 - 房价、入住率、RevPAR分析",
        "选址决策支持 - 半径5km市场环境分析"
    ]
    
    info["features"] = [
        "竞品监控 - 全季、汉庭、如家等品牌酒店数据追踪",
        "地理分析 - 基于高德地图的位置评估",
        "财务建模 - NPV、IRR、敏感性分析",
        "实时监控 - 关键指标预警系统",
        "数据可视化 - Streamlit/Dash交互式报表"
    ]
    
    return info

def create_ai_analysis_request():
    """创建AI Agent分析请求"""
    
    # 获取项目结构分析
    structure_analysis = analyze_project_structure()
    project_info = extract_project_info()
    
    # 构建详细的项目分析请求
    analysis_request = {
        "name": "酒店分析工具 - AI Agent深度评估",
        "description": """
针对中低端连锁酒店投资分析的商业智能工具，主要服务于江阴、昆山、上海金山、义乌、永康五个城市的酒店投资决策。

项目特点：
- 业务导向：专注酒店投资ROI分析和经营监测
- 技术全面：FastAPI后端 + Streamlit前端 + 机器学习算法
- 数据驱动：集成多个OTA平台数据和地理位置服务
- 功能完整：涵盖市场分析、投资计算、选址评估、运营监控

请AI Agent团队从以下维度进行深度分析：
1. 产品价值评估 - 商业模式和市场需求分析
2. 技术架构审查 - 代码质量、架构设计、技术选型评估
3. 功能完整性 - 核心功能实现程度和用户体验
4. 数据质量 - 数据采集、处理、存储的合理性
5. 可维护性 - 代码规范、文档完整性、测试覆盖
6. 可扩展性 - 架构弹性和未来发展潜力
7. 安全性 - 数据安全、API安全、系统安全评估
8. 性能优化 - 系统性能瓶颈和优化建议
9. 部署运维 - Docker化、CI/CD、监控日志
10. 商业化潜力 - 市场竞争力和盈利模式分析
        """,
        "type": "business_intelligence",
        "priority": "high",
        "budget": 1000000,
        "timeline": "6个月",
        "requirements": [
            "深度代码审查和架构分析",
            "业务逻辑合理性评估", 
            "数据采集和处理效率优化",
            "用户界面和体验改进",
            "系统性能和安全性评估",
            "商业价值和市场竞争力分析",
            "技术债务和风险评估",
            "未来发展路线图制定"
        ],
        "tech_stack": project_info["tech_stack"],
        "business_goals": project_info["business_goals"],
        "current_status": {
            "total_files": structure_analysis["total_files"],
            "key_components": list(structure_analysis["directory_structure"].keys()),
            "main_technologies": project_info["tech_stack"][:10],
            "business_features": project_info["features"]
        },
        "analysis_focus": [
            "代码质量和架构设计评估",
            "业务逻辑实现的合理性分析",
            "数据采集策略和数据质量评估",
            "用户体验和界面设计优化建议",
            "系统性能瓶颈识别和优化方案",
            "安全漏洞检查和防护建议",
            "技术债务清理和代码重构建议",
            "商业模式验证和市场定位分析",
            "竞争对手分析和差异化建议",
            "产品路线图和技术发展规划"
        ]
    }
    
    return analysis_request

def submit_to_ai_team():
    """提交给AI开发团队分析"""
    
    base_url = "http://localhost:8080"
    
    try:
        # 检查API服务是否可用
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ AI开发团队服务未运行")
            print("请先启动: python3.11 start_team.py")
            return None
            
    except requests.exceptions.RequestException:
        print("❌ 无法连接到AI开发团队")
        print("请确保服务正在运行: python3.11 start_team.py")
        return None
    
    # 创建项目分析请求
    analysis_request = create_ai_analysis_request()
    
    print("🚀 正在提交酒店分析工具项目给AI开发团队...")
    print(f"📋 项目名称: {analysis_request['name']}")
    print(f"💰 分析预算: ¥{analysis_request['budget']:,}")
    print(f"⏰ 预计时间: {analysis_request['timeline']}")
    print("\n🎯 分析重点:")
    for i, focus in enumerate(analysis_request['analysis_focus'][:5], 1):
        print(f"   {i}. {focus}")
    print("   ...")
    
    try:
        # 提交项目创建请求
        response = requests.post(
            f"{base_url}/api/projects/create",
            json=analysis_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 项目提交成功!")
            print(f"📋 项目ID: {result['project_id']}")
            print(f"📊 状态: {result.get('status', 'unknown')}")
            
            # 显示分配的AI团队
            if 'project_status' in result and 'assigned_agents' in result['project_status']:
                print(f"\n👥 分配的AI专家团队:")
                agent_roles = {
                    'manager': '👨‍💼 项目管理 - 统筹分析流程和质量控制',
                    'pm': '📋 产品经理 - 业务需求和用户体验分析', 
                    'architect': '🏗️ 架构师 - 技术架构和系统设计评估',
                    'developer': '👨‍💻 开发工程师 - 代码质量和实现细节审查',
                    'qa': '🔍 质量保证 - 测试策略和质量标准评估'
                }
                
                for agent in result['project_status']['assigned_agents']:
                    role_desc = agent_roles.get(agent, f'🤖 {agent}')
                    print(f"   {role_desc}")
            
            print(f"\n🔄 AI团队正在分析中...")
            print(f"📊 可通过以下方式查看进展:")
            print(f"   - 仪表板: http://localhost:3000/")
            print(f"   - 项目详情: http://localhost:3000/projects/{result['project_id']}")
            
            return result['project_id']
            
        else:
            print(f"❌ 项目提交失败: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"错误详情: {error_detail}")
            except:
                print(f"错误信息: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，AI团队可能正忙")
        print("请稍后重试或检查服务状态")
        return None
    except Exception as e:
        print(f"❌ 提交过程中出现错误: {str(e)}")
        return None

def check_analysis_progress(project_id):
    """检查分析进展"""
    base_url = "http://localhost:8080"
    
    try:
        response = requests.get(f"{base_url}/api/projects/{project_id}")
        if response.status_code == 200:
            project = response.json()
            
            print(f"\n📊 酒店分析工具项目 - AI团队分析进展")
            print("=" * 60)
            print(f"📋 项目状态: {project['project']['status']}")
            print(f"📈 分析进度: {project['project'].get('progress', 0)}%")
            print(f"🕒 最后更新: {project['project'].get('last_update', 'N/A')}")
            
            if 'phases' in project and project['phases']:
                print(f"\n🔄 分析阶段:")
                phase_icons = {
                    'planning': '📋',
                    'analysis': '🔍', 
                    'review': '📝',
                    'optimization': '⚡',
                    'reporting': '📊'
                }
                
                for phase_name, phase_info in project['phases'].items():
                    icon = phase_icons.get(phase_name, '🔹')
                    status = "✅ 完成" if phase_info.get('completed') else "🔄 进行中"
                    print(f"   {icon} {phase_name}: {status}")
                    if phase_info.get('description'):
                        print(f"      └─ {phase_info['description']}")
            
            if 'next_steps' in project and project['next_steps']:
                print(f"\n📋 下一步计划:")
                for step in project['next_steps'][:3]:
                    print(f"   • {step}")
                    
        else:
            print(f"❌ 无法获取项目状态: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查进展时出现错误: {str(e)}")

def main():
    """主函数"""
    print("🏨 酒店分析工具项目 - AI Agent团队深度分析")
    print("=" * 60)
    
    # 检查项目是否存在
    project_path = Path("/Users/jx/Downloads/酒店分析工具")
    if not project_path.exists():
        print("❌ 项目路径不存在:")
        print(f"   {project_path}")
        print("请确认项目路径正确")
        return
    
    print(f"📁 项目路径: {project_path}")
    print("🔍 正在分析项目结构...")
    
    # 分析项目结构
    structure_analysis = analyze_project_structure()
    project_info = extract_project_info()
    
    print(f"\n📊 项目概况:")
    print(f"   📄 总文件数: {structure_analysis['total_files']}")
    print(f"   🛠️ 主要技术: {', '.join(project_info['tech_stack'][:5])}")
    print(f"   🎯 核心功能: {len(project_info['features'])} 个主要模块")
    print(f"   📦 依赖包数: {len(project_info['dependencies'])}")
    
    # 提交给AI团队分析
    print(f"\n🤖 准备提交给AI开发团队进行深度分析...")
    project_id = submit_to_ai_team()
    
    if project_id:
        # 等待一段时间后检查进展
        print(f"\n⏳ 等待AI团队开始分析...")
        import time
        time.sleep(3)
        
        # 检查分析进展
        check_analysis_progress(project_id)
        
        print(f"\n💡 建议:")
        print("   1. 访问 http://localhost:3000/launchpad 查看完整分析报告")
        print("   2. 关注AI团队的实时分析过程和建议")
        print("   3. 根据分析结果制定项目改进计划")
        
    else:
        print(f"\n❌ 提交失败，请检查:")
        print("   1. AI开发团队服务是否运行: python3.11 start_team.py")
        print("   2. 网络连接是否正常")
        print("   3. 系统资源是否充足")

if __name__ == "__main__":
    main()